#!/usr/bin/env python3
"""SecInterp metrics adapter for Agentic Forge.

Collects ground-truth metrics (qgis-analyzer scores, module sizes, test counts)
into ``agent_metrics.json`` and regenerates ``tests/TESTING_STATUS.md``.

The generic core (session rotation, cross-file consistency validation, trend
report) lives in the framework at ``.agent/tools/forge_metrics.py`` and is
re-exported here for backward compatibility.

Subcommands (chosen by first matching flag):
    (default)           sync ground-truth metrics into agent_metrics.json
    --report            generate Markdown trend report
    --validate          cross-file + internal metric consistency
    --testing-status    regenerate tests/TESTING_STATUS.md

Modifiers:
    --json              print sync summary as JSON
    --quiet             suppress progress output
    --from-context      skip the analyzer run and read analysis_results/project_context.json
    --tests-executed N  record the executed test count (the static count is always computed)
    --fix               (with --validate) auto-correct known stale values
    --close-session     rotate last_session into history (with --topic NAME)
    --compact           (with --report) compact report output
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent.parent / ".agent" / "tools"
if _TOOLS_DIR.is_dir():
    sys.path.insert(0, str(_TOOLS_DIR))

import forge_paths  # noqa: E402
from forge_metrics import (  # noqa: E402,F401
    _check_i18n_consistency,
    _check_issue_total,
    _check_score_sources,
    _check_session_date,
    _check_test_count,
    check_internal_consistency,
    generate_report,
    rotate_session_history,
    validate_main,
)

# ── Configuration ──────────────────────────────────────────────────────────
PROJECT_ROOT = forge_paths.PROJECT_ROOT
METRICS_FILE = forge_paths.METRICS_FILE
ANALYZER_RESULTS = PROJECT_ROOT / "analysis_results" / "project_context.json"

# Thresholds (single source of truth: forge.toml)
CC_THRESHOLD = forge_paths.MAX_CC
MODULE_SIZE_LIMIT = forge_paths.MODULE_SIZE_LIMIT

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    """Remove ANSI color escape sequences from analyzer output."""
    return _ANSI_RE.sub("", text)


def read_analyzer_context() -> dict:
    """Read scores and issue counts from the analyzer JSON artifact.

    ``project_context.json`` is the authoritative output of
    ``qgis-analyzer``: it contains every issue type (including the ones the
    console summary may omit) and the exact scores. Reading it avoids parsing
    the human-readable console output, which is fragile.

    Returns:
        A dict with ``scores``, ``issues`` (aggregated by type), ``total_issues``,
        ``research`` and ``analyzed_at``. Empty when the artifact is missing or
        unreadable.

    """
    if not ANALYZER_RESULTS.exists():
        return {}

    try:
        data = json.loads(ANALYZER_RESULTS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    metrics = data.get("metrics", {})
    findings = (
        data.get("qgis_compliance", {})
        .get("best_practices", {})
        .get("issues", [])
    )
    issues: dict[str, int] = {}
    for finding in findings:
        issue_type = finding.get("type", "UNKNOWN")
        issues[issue_type] = issues.get(issue_type, 0) + 1

    research = data.get("research_summary", {})
    return {
        "scores": {
            "module_stability": metrics.get("quality_score"),
            "maintainability": metrics.get("maintainability_score"),
            "security": metrics.get("security_score"),
        },
        "issues": issues,
        "total_issues": sum(issues.values()),
        "research": {
            "type_hint_params": research.get("type_hint_coverage"),
            "type_hint_returns": research.get("return_hint_coverage"),
            "docstring_coverage": research.get("docstring_coverage"),
        },
        "analyzed_at": data.get("analyzed_at"),
    }


def run_qgis_analyzer(use_context_only: bool = False) -> dict:
    """Run qgis-analyzer and extract scores + issue counts + CC gate.

    The ``--max-cc`` flag makes the analyzer exit non-zero when any function
    exceeds the threshold, which is exposed here as the ``cc_gate`` field.

    Args:
        use_context_only: Skip the analyzer run and read the existing
            ``project_context.json`` (useful for local re-syncs).

    """
    if use_context_only:
        context = read_analyzer_context()
        if not context:
            return {"error": "project_context.json not found"}
        return {**context, "cc_gate": None}

    try:
        result = subprocess.run(
            ["uv", "run", "qgis-analyzer", "analyze", ".", "--max-cc", str(CC_THRESHOLD)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = _strip_ansi(result.stdout + result.stderr)
        cc_gate = result.returncode == 0
    except FileNotFoundError:
        return {"error": "qgis-analyzer not found in environment"}
    except subprocess.TimeoutExpired:
        return {"error": "qgis-analyzer timed out"}

    # Read the artifact after the run so it reflects the new analysis.
    context = read_analyzer_context()
    scores = {}
    issues = {}

    # Parse the text output for scores
    for line in output.splitlines():
        line = line.strip()
        if "Module Stability Score:" in line:
            try:
                scores["module_stability"] = float(
                    line.split(":")[-1].strip().split("/")[0]
                )
            except (ValueError, IndexError):
                pass
        elif "Code Maintainability Score:" in line:
            try:
                scores["maintainability"] = float(
                    line.split(":")[-1].strip().split("/")[0]
                )
            except (ValueError, IndexError):
                pass
        elif "Security Score (Bandit):" in line:
            try:
                scores["security"] = float(
                    line.split(":")[-1].strip().split("/")[0]
                )
            except (ValueError, IndexError):
                pass

    # Parse issue statistics section
    in_issues = False
    for line in output.splitlines():
        if "Issue Statistics" in line:
            in_issues = True
            continue
        if in_issues:
            if line.startswith("-") and ":" in line:
                parts = line.strip("- ").rsplit(":", 1)
                if len(parts) == 2:
                    try:
                        issues[parts[0].strip()] = int(parts[1].strip())
                    except ValueError:
                        pass
            elif line.strip() and not line.startswith("-"):
                in_issues = False

    # Parse research metrics
    research = {}
    for line in output.splitlines():
        if "Type Hint Coverage (Params):" in line:
            try:
                research["type_hint_params"] = float(
                    line.split(":")[-1].strip().rstrip("%")
                )
            except (ValueError, IndexError):
                pass
        elif "Type Hint Coverage (Returns):" in line:
            try:
                research["type_hint_returns"] = float(
                    line.split(":")[-1].strip().rstrip("%")
                )
            except (ValueError, IndexError):
                pass
        elif "Docstring Coverage:" in line:
            try:
                research["docstring_coverage"] = float(
                    line.split(":")[-1].strip().rstrip("%")
                )
            except (ValueError, IndexError):
                pass

    # Prefer the machine-readable artifact: it carries every issue type and
    # the canonical scores, while the console summary can omit categories.
    if context:
        scores.update(
            {key: value for key, value in context.get("scores", {}).items() if value is not None}
        )
        if context.get("issues"):
            issues = dict(context["issues"])
        research.update(
            {
                key: value
                for key, value in context.get("research", {}).items()
                if value is not None
            }
        )

    total_issues = sum(issues.values())

    return {
        "scores": scores,
        "issues": issues,
        "total_issues": total_issues,
        "research": research,
        "cc_gate": cc_gate,
        "analyzed_at": context.get("analyzed_at") if context else None,
    }


def check_module_sizes() -> dict:
    """Check for modules exceeding the module-size limit."""
    context_file = PROJECT_ROOT / "analysis_results" / "project_context.json"
    if not context_file.exists():
        return {"passed": None, "error": "project_context.json not found"}

    try:
        data = json.loads(context_file.read_text())
    except Exception as e:
        return {"passed": None, "error": str(e)}

    modules = data.get("modules", [])
    large_modules = []
    for mod in modules:
        path = mod.get("path", "?")
        lines = mod.get("lines", mod.get("total_lines", 0))
        if lines > MODULE_SIZE_LIMIT:
            large_modules.append({"path": path, "lines": lines})

    return {
        "passed": len(large_modules) == 0,
        "large_modules": large_modules,
        "count": len(large_modules),
    }


def count_total_tests() -> int:
    """Count test methods (``def test_``) across the CI test categories.

    Matches the categories counted by ``--testing-status`` (agentic, core, gui,
    exporters, integration) so ``agent_metrics.json`` and ``TESTING_STATUS.md``
    stay in sync.
    """
    test_dir = PROJECT_ROOT / "tests"
    categories = ["agentic", "core", "gui", "exporters", "integration"]
    total = 0
    for cat in categories:
        cat_dir = test_dir / cat
        if not cat_dir.is_dir():
            continue
        for root, _, files in os.walk(cat_dir):
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    try:
                        content = (Path(root) / file).read_text(encoding="utf-8")
                    except OSError:
                        continue
                    total += len(re.findall(r"def\s+test_", content))
    return total


def update_metrics_json(metrics: dict) -> bool:
    """Update the summary section of agent_metrics.json."""
    if not METRICS_FILE.exists():
        print(f"❌ {METRICS_FILE} not found", file=sys.stderr)
        return False

    try:
        data = json.loads(METRICS_FILE.read_text())
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {METRICS_FILE}: {e}", file=sys.stderr)
        return False

    analyzer = metrics.get("qgis_analyzer", {})
    cc = metrics.get("cc", {})
    i18n_ast = metrics.get("i18n", {})
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    summary = data.setdefault("summary", {})
    summary["quality_score_latest"] = analyzer.get("scores", {}).get(
        "module_stability", summary.get("quality_score_latest", "?"))
    summary["maintainability_score"] = analyzer.get("scores", {}).get(
        "maintainability", summary.get("maintainability_score", "?"))
    summary["security_score"] = analyzer.get("scores", {}).get(
        "security", summary.get("security_score", "?"))
    summary["quality_score_latest_note"] = (
        f"Module Stability Score from qgis-analyzer (synced {today})."
    )
    cc_passed = cc.get("passed")
    if cc_passed is not None:
        summary["cyclomatic_complexity_gate"] = "PASS" if cc_passed else "FAIL"
    summary["i18n_hygiene_gate"] = (
        "PASS" if i18n_ast.get("passed") else ("FAIL" if i18n_ast.get("passed") is False else "UNKNOWN")
    )

    # ``test_count``/``tests_ok`` are the legacy static baseline used by the
    # cross-file validator; ``tests_static`` is the current static count and
    # ``tests_executed`` records what the suite actually ran.
    tests_static = count_total_tests()
    tests_executed = metrics.get("tests_executed")
    if tests_executed is None:
        tests_executed = summary.get("tests_executed")
    summary["tests_static"] = tests_static
    summary["tests_executed"] = tests_executed
    summary["test_count"] = summary.get("test_count", tests_static)
    summary["tests_ok"] = summary.get("tests_ok", tests_static)
    summary["tests_ok_note"] = (
        "tests_ok/test_count are the legacy static baseline kept for cross-file "
        "consistency; tests_static is the current static 'def test_' count and "
        "tests_executed is the runtime suite (local or Docker)."
    )
    summary["total_issues"] = analyzer.get("total_issues", summary.get("total_issues", "?"))
    summary["total_sessions"] = len(data.get("history", []))

    module_sizes = metrics.get("module_sizes", {})
    if module_sizes:
        summary["module_size_gate"] = (
            "PASS" if module_sizes.get("passed") else
            f"FAIL ({module_sizes.get('count', 0)} modules > {MODULE_SIZE_LIMIT} lines)"
        )
        summary["large_modules"] = module_sizes.get("large_modules", [])

    research = analyzer.get("research", {})
    if "type_hint_params" in research:
        summary["type_hint_coverage_params"] = research["type_hint_params"]
    if "type_hint_returns" in research:
        summary["type_hint_coverage_returns"] = research["type_hint_returns"]
    if "docstring_coverage" in research:
        summary["docstring_coverage"] = research["docstring_coverage"]

    # Record every issue type reported by the analyzer (including the ones the
    # console summary omits, such as UNPRECISE_LAYER).
    issues = dict(analyzer.get("issues", {}))
    issues.setdefault("MISSING_I18N", 0)
    summary["issue_breakdown"] = issues
    summary["i18n_issues_qgis_analyzer"] = issues["MISSING_I18N"]

    # Refresh the qgis-analyzer ground-truth source so it stays coherent with
    # the summary scores (the internal consistency check compares them).
    ground_truth = data.setdefault("ground_truth_sources", {})
    gt_analyzer = ground_truth.setdefault("qgis_analyzer", {})
    gt_analyzer["date"] = today
    gt_analyzer["command"] = "uv run qgis-analyzer analyze . --max-cc 10"
    gt_analyzer["output"] = "analysis_results/"
    if analyzer.get("analyzed_at"):
        gt_analyzer["analyzed_at"] = analyzer["analyzed_at"]
    if analyzer.get("scores"):
        gt_analyzer["scores"] = {
            "module_stability": analyzer["scores"].get("module_stability"),
            "maintainability": analyzer["scores"].get("maintainability"),
            "security": analyzer["scores"].get("security"),
        }
    gt_analyzer["issues"] = {
        **issues,
        "total": sum(issues.values()),
    }

    if tests_executed is not None:
        ground_truth["tests_local"] = {
            "date": today,
            "command": "PYTHONPATH=.. .venv/bin/python -m unittest discover tests",
            "result": f"{tests_executed} ran OK",
            "note": (
                "Local mock-first suite; tests_static is the static 'def test_' "
                "count and Docker runs the grouped CI categories."
            ),
        }

    ground_truth["sync_metrics"] = {
        "date": today,
        "command": "uv run python scripts/sync_metrics.py",
        "cc_gate": (
            "PASS" if cc.get("passed") is True
            else "FAIL" if cc.get("passed") is False
            else "UNCHANGED"
        ),
        "i18n_gate": "PASS" if i18n_ast.get("passed") else "FAIL",
    }

    data.setdefault("meta", {})["last_updated"] = today
    data["meta"]["last_updated_by"] = "sync_metrics.py (metrics truth reconciliation)"

    METRICS_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n")
    return True


def refresh_total_sessions() -> None:
    """Recompute ``summary.total_sessions`` from the history array."""
    try:
        data = json.loads(METRICS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    data.setdefault("summary", {})["total_sessions"] = len(data.get("history", []))
    METRICS_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n")


def validate_against_analyzer_context() -> list[str]:
    """Compare ``agent_metrics.json`` with the analyzer JSON artifact.

    ``forge metrics validate`` checks cross-file consistency against
    ``agent_metrics.json``; this check validates that the file itself still
    matches the latest analyzer output (scores and every issue type).

    Returns:
        A list of human-readable mismatches; empty when the file is fresh.

    """
    if not METRICS_FILE.exists() or not ANALYZER_RESULTS.exists():
        return []

    try:
        data = json.loads(METRICS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read agent_metrics.json: {exc}"]

    context = read_analyzer_context()
    if not context:
        return []

    summary = data.get("summary", {})
    mismatches: list[str] = []

    if summary.get("total_issues") != context["total_issues"]:
        mismatches.append(
            f"summary.total_issues ({summary.get('total_issues')}) != "
            f"project_context issues ({context['total_issues']})"
        )

    gt_total = (
        data.get("ground_truth_sources", {})
        .get("qgis_analyzer", {})
        .get("issues", {})
        .get("total")
    )
    if gt_total is not None and gt_total != context["total_issues"]:
        mismatches.append(
            f"ground_truth_sources.qgis_analyzer.issues.total ({gt_total}) != "
            f"project_context issues ({context['total_issues']})"
        )

    for summary_key, score_key in (
        ("quality_score_latest", "module_stability"),
        ("maintainability_score", "maintainability"),
        ("security_score", "security"),
    ):
        found = summary.get(summary_key)
        expected = context.get("scores", {}).get(score_key)
        if found is not None and expected is not None and found != expected:
            mismatches.append(
                f"summary.{summary_key} ({found}) != project_context {score_key} ({expected})"
            )

    return mismatches


def sync_main():
    quiet = "--quiet" in sys.argv
    json_output = "--json" in sys.argv
    close_session = "--close-session" in sys.argv
    from_context = "--from-context" in sys.argv

    tests_executed = None
    if "--tests-executed" in sys.argv:
        try:
            tests_executed = int(sys.argv[sys.argv.index("--tests-executed") + 1])
        except (IndexError, ValueError):
            print("❌ --tests-executed requires an integer", file=sys.stderr)
            sys.exit(2)

    topic = None
    if "--topic" in sys.argv:
        try:
            topic = sys.argv[sys.argv.index("--topic") + 1]
        except IndexError:
            topic = None

    if not quiet:
        print("🔄 Syncing ground-truth metrics...")
        if from_context:
            print("   → analysis_results/project_context.json (no analyzer run)")
        else:
            print("   → qgis-analyzer analyze . --max-cc " + str(CC_THRESHOLD))

    analyzer = run_qgis_analyzer(use_context_only=from_context)

    if not quiet:
        print("   → check_module_sizes")
    module_sizes = check_module_sizes()

    issues = analyzer.get("issues", {})
    cc = {"passed": analyzer.get("cc_gate")}
    i18n = {"passed": issues.get("MISSING_I18N", 0) == 0}

    metrics = {
        "qgis_analyzer": analyzer,
        "cc": cc,
        "i18n": i18n,
        "module_sizes": module_sizes,
        "tests_executed": tests_executed,
    }

    updated = update_metrics_json(metrics)

    if close_session and not rotate_session_history(topic):
        updated = False
    if updated:
        refresh_total_sessions()

    if json_output:
        summary = {
            "quality_score": analyzer.get("scores", {}).get("module_stability"),
            "maintainability": analyzer.get("scores", {}).get("maintainability"),
            "security": analyzer.get("scores", {}).get("security"),
            "cc_gate": (
                "PASS" if cc.get("passed") is True
                else "FAIL" if cc.get("passed") is False
                else "UNCHANGED"
            ),
            "i18n_gate": "PASS" if i18n.get("passed") else "FAIL",
            "total_issues": analyzer.get("total_issues"),
            "tests_static": count_total_tests(),
            "tests_executed": tests_executed,
            "updated": updated,
        }
        print(json.dumps(summary, indent=2))
        sys.exit(0 if updated else 1)

    if not quiet:
        print()
        scores = analyzer.get("scores", {})
        issues = analyzer.get("issues", {})

        if scores:
            print("📊 QGIS Analyzer Scores:")
            for k, v in scores.items():
                print(f"   {k}: {v}/100")
        if issues:
            print(f"⚠️  Issues: {sum(issues.values())} total")
            for k, v in issues.items():
                print(f"   {k}: {v}")
        cc_label = (
            "✅ PASS" if cc.get("passed") is True
            else "❌ FAIL" if cc.get("passed") is False
            else "⏭️  UNCHANGED"
        )
        print(f"🔒 CC Gate:     {cc_label}")
        print(f"🌐 i18n Gate:    {'✅ PASS' if i18n.get('passed') else '❌ FAIL'}")
        size_passed = module_sizes.get("passed")
        if size_passed is False:
            print(f"📦 Module Size:  ⚠️ {module_sizes.get('count', 0)} modules > {MODULE_SIZE_LIMIT} lines")
            for m in module_sizes.get("large_modules", []):
                print(f"   {m['path']}: {m['lines']} lines")
        elif size_passed is True:
            print("📦 Module Size:  ✅ PASS")
        print(f"💾 Metrics JSON: {'✅ updated' if updated else '❌ failed'}")

    sys.exit(0 if updated else 1)


# =====================================================================
# Testing status updater
# =====================================================================
def count_tests_in_file(file_path):
    """Count test methods in a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return len(re.findall(r"def\s+test_", content))


def get_test_inventory(test_dir):
    """Get a detailed list of tests for the inventory section."""
    inventory = []
    for root, dirs, files in os.walk(test_dir):
        for file in sorted(files):
            if file.startswith("test_") and file.endswith(".py"):
                path = Path(root) / file
                rel_path = path.relative_to(test_dir.parent)
                count = count_tests_in_file(path)
                if count > 0:
                    inventory.append(f"- **{rel_path}**: {count} tests")
    return "\n".join(inventory)


def update_section(content, section_id, new_value):
    """Update a specific section in the markdown content."""
    pattern = f"<!-- {section_id} -->.*?<!-- /{section_id} -->"
    replacement = f"<!-- {section_id} -->{new_value}<!-- /{section_id} -->"
    return re.sub(pattern, replacement, content, flags=re.DOTALL)


def testing_status_main():
    base_dir = Path(__file__).resolve().parent.parent
    test_dir = base_dir / "tests"
    status_file = test_dir / "TESTING_STATUS.md"

    if not status_file.exists():
        print(f"Error: {status_file} not found.")
        return

    with open(status_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Count tests by category
    categories = {
        "AGENT_COUNT": test_dir / "agentic",
        "CORE_COUNT": test_dir / "core",
        "GUI_COUNT": test_dir / "gui",
        "EXP_COUNT": test_dir / "exporters",
        "INT_COUNT": test_dir / "integration",
    }

    total_tests = 0
    for key, path in categories.items():
        cat_count = 0
        if path.exists():
            for root, _, files in os.walk(path):
                for file in files:
                    if file.startswith("test_") and file.endswith(".py"):
                        cat_count += count_tests_in_file(Path(root) / file)

        content = update_section(content, key, str(cat_count))
        total_tests += cat_count

    # 2. Update summary metrics
    content = update_section(content, "TOTAL_TESTS", str(total_tests))
    content = update_section(
        content, "LAST_UPDATE", datetime.now().strftime("%Y-%m-%d")
    )

    # 3. Update Detailed Inventory
    inventory = get_test_inventory(test_dir)
    pattern = "(<!-- START_INVENTORY -->).*?(<!-- END_INVENTORY -->)"
    content = re.sub(pattern, f"\\1\n{inventory}\n\\2", content, flags=re.DOTALL)

    with open(status_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Successfully updated {status_file} with {total_tests} tests.")


def main() -> None:
    """Dispatch to the requested metrics subcommand."""
    argv = sys.argv[1:]
    if "--report" in argv:
        generate_report(compact="--compact" in argv)
    elif "--validate" in argv:
        mismatches = validate_against_analyzer_context()
        if mismatches:
            print("❌ agent_metrics.json is stale against analysis_results/project_context.json:")
            for mismatch in mismatches:
                print(f"  - {mismatch}")
            sys.exit(1)
        validate_main()
    elif "--testing-status" in argv:
        testing_status_main()
    else:
        sync_main()


if __name__ == "__main__":
    main()
