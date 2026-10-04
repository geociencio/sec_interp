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


def run_qgis_analyzer() -> dict:
    """Run qgis-analyzer and extract scores + issue counts + CC gate.

    The ``--max-cc`` flag makes the analyzer exit non-zero when any function
    exceeds the threshold, which is exposed here as the ``cc_gate`` field.
    """
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
                parts = line.strip("- ").split(":", 1)
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

    total_issues = sum(issues.values())

    return {
        "scores": scores,
        "issues": issues,
        "total_issues": total_issues,
        "research": research,
        "cc_gate": cc_gate,
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

    summary = data.setdefault("summary", {})
    summary["quality_score_latest"] = analyzer.get("scores", {}).get(
        "module_stability", summary.get("quality_score_latest", "?"))
    summary["maintainability_score"] = analyzer.get("scores", {}).get(
        "maintainability", summary.get("maintainability_score", "?"))
    summary["security_score"] = analyzer.get("scores", {}).get(
        "security", summary.get("security_score", "?"))
    summary["cyclomatic_complexity_gate"] = (
        "PASS" if cc.get("passed") else ("FAIL" if cc.get("passed") is False else "UNKNOWN")
    )
    summary["i18n_hygiene_gate"] = (
        "PASS" if i18n_ast.get("passed") else ("FAIL" if i18n_ast.get("passed") is False else "UNKNOWN")
    )
    summary["test_count"] = count_total_tests()
    summary["tests_ok"] = summary["test_count"]
    summary["total_issues"] = analyzer.get("total_issues", summary.get("total_issues", "?"))

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

    # Record issue breakdown (empty dict when the analyzer is clean)
    issues = analyzer.get("issues", {})
    summary["issue_breakdown"] = issues
    summary["i18n_issues_qgis_analyzer"] = issues.get("MISSING_I18N", 0)

    # Refresh the qgis-analyzer ground-truth source so it stays coherent with
    # the summary scores (the internal consistency check compares them).
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ground_truth = data.setdefault("ground_truth_sources", {})
    gt_analyzer = ground_truth.setdefault("qgis_analyzer", {})
    gt_analyzer["date"] = today
    gt_analyzer["command"] = "uv run qgis-analyzer analyze . --max-cc 10"
    gt_analyzer["output"] = "analysis_results/"
    if analyzer.get("scores"):
        gt_analyzer["scores"] = {
            "module_stability": analyzer["scores"].get("module_stability"),
            "maintainability": analyzer["scores"].get("maintainability"),
            "security": analyzer["scores"].get("security"),
        }
    gt_analyzer["issues"] = {
        **issues,
        "MISSING_I18N": issues.get("MISSING_I18N", 0),
        "total": sum(issues.values()),
    }

    ground_truth["sync_metrics"] = {
        "date": today,
        "command": "uv run python scripts/sync_metrics.py",
        "cc_gate": "PASS" if cc.get("passed") else "FAIL",
        "i18n_gate": "PASS" if i18n_ast.get("passed") else "FAIL",
    }

    data["meta"]["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    METRICS_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n")
    return True


def sync_main():
    quiet = "--quiet" in sys.argv
    json_output = "--json" in sys.argv
    close_session = "--close-session" in sys.argv

    topic = None
    if "--topic" in sys.argv:
        try:
            topic = sys.argv[sys.argv.index("--topic") + 1]
        except IndexError:
            topic = None

    if not quiet:
        print("🔄 Syncing ground-truth metrics...")
        print("   → qgis-analyzer analyze . --max-cc " + str(CC_THRESHOLD))

    analyzer = run_qgis_analyzer()

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
    }

    updated = update_metrics_json(metrics)

    if close_session and not rotate_session_history(topic):
        updated = False

    if json_output:
        summary = {
            "quality_score": analyzer.get("scores", {}).get("module_stability"),
            "maintainability": analyzer.get("scores", {}).get("maintainability"),
            "security": analyzer.get("scores", {}).get("security"),
            "cc_gate": "PASS" if cc.get("passed") else "FAIL",
            "i18n_gate": "PASS" if i18n.get("passed") else "FAIL",
            "total_issues": analyzer.get("total_issues"),
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
        print(f"🔒 CC Gate:     {'✅ PASS' if cc.get('passed') else '❌ FAIL'}")
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
        validate_main()
    elif "--testing-status" in argv:
        testing_status_main()
    else:
        sync_main()


if __name__ == "__main__":
    main()
