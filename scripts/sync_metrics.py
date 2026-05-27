#!/usr/bin/env python3
"""
Unified Metrics Synchronizer (Gen 6 → Gen 7 bridge)

Runs all quality gates and writes a single, coherent metrics snapshot to
agent_metrics.json. Designed to be called from /start-session and /close-session
workflows so the agentic system never operates on stale data.

Usage:
    uv run python scripts/sync_metrics.py [--json] [--quiet]

Output:
    - Updates .agent/memory/agent_metrics.json summary section
    - Prints a compact status report to stdout
    - With --json: prints the summary as JSON (for programmatic use)
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── Configuration ──────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
METRICS_FILE = PROJECT_ROOT / ".agent" / "memory" / "agent_metrics.json"
CC_SCRIPT = PROJECT_ROOT / "scripts" / "check_cc.py"
I18N_SCRIPT = PROJECT_ROOT / "scripts" / "verify_i18n_hygiene.py"
ANALYZER_RESULTS = PROJECT_ROOT / "analysis_results" / "project_context.json"


def run_qgis_analyzer() -> dict:
    """Run qgis-analyzer and extract scores + issue counts."""
    try:
        result = subprocess.run(
            ["uv", "run", "qgis-analyzer", "analyze", "."],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = result.stdout + result.stderr
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

    total_issues = sum(issues.values()) if issues else None

    return {
        "scores": scores,
        "issues": issues,
        "total_issues": total_issues,
        "research": research,
    }


def run_check_cc() -> dict:
    """Run the CC gate script."""
    try:
        result = subprocess.run(
            ["uv", "run", "python", str(CC_SCRIPT)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        passed = result.returncode == 0
        return {
            "passed": passed,
            "output": result.stdout.strip().split("\n")[0] if result.stdout else "",
        }
    except Exception as e:
        return {"passed": None, "error": str(e)}


def run_verify_i18n() -> dict:
    """Run the AST-based i18n hygiene checker."""
    try:
        result = subprocess.run(
            ["uv", "run", "python", str(I18N_SCRIPT)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        passed = result.returncode == 0
        return {
            "passed": passed,
            "output": result.stdout.strip().split("\n")[-1] if result.stdout else "",
        }
    except Exception as e:
        return {"passed": None, "error": str(e)}


def check_module_sizes() -> dict:
    """Check for modules exceeding the 400-line size limit."""
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
        if lines > 400:
            large_modules.append({"path": path, "lines": lines})

    return {
        "passed": len(large_modules) == 0,
        "large_modules": large_modules,
        "count": len(large_modules),
    }


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
    cc = metrics.get("check_cc", {})
    i18n_ast = metrics.get("verify_i18n_hygiene", {})

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
    summary["test_count"] = summary.get("tests_ok", summary.get("test_count", "?"))
    summary["total_issues"] = analyzer.get("total_issues", summary.get("total_issues", "?"))

    module_sizes = metrics.get("module_sizes", {})
    if module_sizes:
        summary["module_size_gate"] = (
            "PASS" if module_sizes.get("passed") else
            f"FAIL ({module_sizes.get('count', 0)} modules > 400 lines)"
        )
        large = module_sizes.get("large_modules", [])
        if large:
            summary["large_modules"] = large

    research = analyzer.get("research", {})
    if "type_hint_params" in research:
        summary["type_hint_coverage_params"] = research["type_hint_params"]
    if "type_hint_returns" in research:
        summary["type_hint_coverage_returns"] = research["type_hint_returns"]
    if "docstring_coverage" in research:
        summary["docstring_coverage"] = research["docstring_coverage"]

    # Record issue breakdown
    issues = analyzer.get("issues", {})
    if issues:
        summary["issue_breakdown"] = issues

    # Add sync metadata
    ground_truth = data.setdefault("ground_truth_sources", {})
    ground_truth["sync_metrics"] = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "command": "uv run python scripts/sync_metrics.py",
        "cc_gate": "PASS" if cc.get("passed") else "FAIL",
        "i18n_ast_gate": "PASS" if i18n_ast.get("passed") else "FAIL",
    }

    data["meta"]["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    METRICS_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n")
    return True


def main():
    quiet = "--quiet" in sys.argv
    json_output = "--json" in sys.argv

    if not quiet:
        print("🔄 Syncing ground-truth metrics...")
        print("   → qgis-analyzer analyze .")

    analyzer = run_qgis_analyzer()

    if not quiet:
        print("   → check_cc.py")
    cc = run_check_cc()

    if not quiet:
        print("   → verify_i18n_hygiene.py")
    i18n = run_verify_i18n()

    if not quiet:
        print("   → check_module_sizes")
    module_sizes = check_module_sizes()

    metrics = {
        "qgis_analyzer": analyzer,
        "check_cc": cc,
        "verify_i18n_hygiene": i18n,
        "module_sizes": module_sizes,
    }

    updated = update_metrics_json(metrics)

    if json_output:
        summary = {
            "quality_score": analyzer.get("scores", {}).get("module_stability"),
            "maintainability": analyzer.get("scores", {}).get("maintainability"),
            "security": analyzer.get("scores", {}).get("security"),
            "cc_gate": "PASS" if cc.get("passed") else "FAIL",
            "i18n_ast_gate": "PASS" if i18n.get("passed") else "FAIL",
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
        print(f"🌐 i18n (AST):   {'✅ PASS' if i18n.get('passed') else '❌ FAIL'}")
        size_passed = module_sizes.get("passed")
        if size_passed is False:
            print(f"📦 Module Size:  ⚠️ {module_sizes.get('count', 0)} modules > 400 lines")
            for m in module_sizes.get("large_modules", []):
                print(f"   {m['path']}: {m['lines']} lines")
        elif size_passed is True:
            print(f"📦 Module Size:  ✅ PASS")
        print(f"💾 Metrics JSON: {'✅ updated' if updated else '❌ failed'}")

    sys.exit(0 if updated else 1)


if __name__ == "__main__":
    main()
