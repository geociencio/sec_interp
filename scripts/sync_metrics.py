#!/usr/bin/env python3
"""
Unified Metrics CLI (Gen 8) — single entry point for all metric tooling.

Subcommands (chosen by first matching flag):
    (default)           sync ground-truth metrics into agent_metrics.json
    --report            generate Markdown trend report (was metrics_report.py)
    --validate          cross-file + internal metric consistency (was validate_agent_metrics.py)
    --testing-status    regenerate tests/TESTING_STATUS.md (was update_testing_status.py)

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
from dataclasses import dataclass, field
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
        if "MISSING_I18N" in issues:
            summary["i18n_issues_qgis_analyzer"] = issues["MISSING_I18N"]

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


def rotate_session_history(topic: Optional[str] = None, metrics_file: Path = METRICS_FILE) -> bool:
    """Rotate the current last_session into history and start a fresh one.

    Prevents `last_session` from going stale across sessions by always
    advancing its date to today. The previous session is preserved in the
    `history` array (deduplicated by date+topic).
    """
    if not metrics_file.exists():
        print(f"❌ {metrics_file} not found", file=sys.stderr)
        return False

    try:
        data = json.loads(metrics_file.read_text())
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {metrics_file}: {e}", file=sys.stderr)
        return False

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    summary = data.get("summary", {})

    previous = data.get("last_session") or {}
    history = data.get("history", []) or []

    # Preserve the previous session in history (dedup by date+topic)
    if previous.get("date"):
        prev_topic = previous.get("topic") or previous.get("session") or ""
        prev_key = (previous["date"], prev_topic)
        existing_keys = {
            (h.get("date"), h.get("session") or h.get("topic") or "")
            for h in history
            if isinstance(h, dict)
        }
        if prev_key not in existing_keys:
            archived = dict(previous)
            if "topic" in archived and "session" not in archived:
                archived["session"] = archived.pop("topic")
            history.insert(0, archived)

    data["last_session"] = {
        "date": today,
        "topic": topic or "session",
        "tests_ok": summary.get("tests_ok", summary.get("test_count")),
        "quality_score": summary.get("quality_score_latest"),
        "task_completion_rate": None,
        "retries": 0,
        "stop_conditions_triggered": 0,
        "tasks": [],
        "status": "SUCCESS",
    }
    data["history"] = history

    metrics_file.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n")
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

    if close_session and not rotate_session_history(topic):
        updated = False

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



# =====================================================================
# Metrics trend report  (was metrics_report.py)
# =====================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
METRICS_FILE = PROJECT_ROOT / ".agent" / "memory" / "agent_metrics.json"

CHART_WIDTH = 30
BLOCKS = "▁▂▃▄▅▆▇█"


def trend_direction(values: list[float]) -> str:
    if len(values) < 2:
        return "⏸️  Stable (insufficient data)"
    first, last = values[0], values[-1]
    if last > first:
        return "📈 Improving"
    elif last < first:
        return "📉 Declining"
    return "⏸️  Stable"


def sparkline(values: list[float], width: int = CHART_WIDTH) -> str:
    """Generate an ASCII sparkline from a series of values."""
    if not values:
        return "(no data)"
    cleaned = [v for v in values if v is not None]
    if not cleaned:
        return "(no data)"
    vmin, vmax = min(cleaned), max(cleaned)
    if vmin == vmax:
        return "─" * min(len(cleaned), width)
    step = len(cleaned) / width if len(cleaned) > width else 1
    result = []
    for i in range(width):
        idx = min(int(i * step), len(cleaned) - 1)
        norm = (cleaned[idx] - vmin) / (vmax - vmin)
        block_idx = min(int(norm * (len(BLOCKS) - 1)), len(BLOCKS) - 1)
        result.append(BLOCKS[block_idx])
    return "".join(result)


def bar_chart(label: str, value: float, max_val: float = 100.0, width: int = 20) -> str:
    """Generate a single labeled ASCII bar."""
    bar_len = max(1, int((value / max_val) * width))
    bar = "█" * bar_len + "░" * (width - bar_len)
    return f"`{label:>16s}` {bar} {value:.1f}"


def extract_score_history(history: list[dict]) -> list[tuple[str, float]]:
    """Extract quality score timeline from session history."""
    entries = []
    for entry in history:
        qs = _find_score(entry)
        if qs is not None:
            entries.append((entry.get("date", "?"), qs))
    return entries


def _find_score(entry: dict) -> Optional[float]:
    """Try multiple keys for quality score."""
    for key in ("quality_score", "quality_score_latest", "score"):
        if key in entry and entry[key] is not None:
            try:
                return float(entry[key])
            except (ValueError, TypeError):
                pass
    return None


def generate_report(compact: bool = False):
    if not METRICS_FILE.exists():
        print(f"Error: {METRICS_FILE} not found.", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(METRICS_FILE.read_text())
    except Exception as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

    summary = data.get("summary", {})
    history = data.get("history", [])
    ground_truth = data.get("ground_truth_sources", {})

    print("# SecInterp Metrics Trend Report\n")
    print(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"**Data source**: `agent_metrics.json`")

    # ── KPI Dashboard ─────────────────────────────────────────────────
    print("\n## KPI Dashboard\n")
    qs = summary.get("quality_score_latest", "?")
    maint = summary.get("maintainability_score", "?")
    sec = summary.get("security_score", "?")
    cc = summary.get("cyclomatic_complexity_gate", "?")
    i18n = summary.get("i18n_hygiene_gate", "?")
    issues = summary.get("total_issues", "?")
    tcr = summary.get("task_completion_rate", "?")
    sessions = summary.get("total_sessions", "?")

    print("| KPI | Value |")
    print("| :--- | :--- |")
    print(f"| Module Stability | **{qs}/100** |")
    print(f"| Maintainability | **{maint}/100** |")
    print(f"| Security (Bandit) | **{sec}/100** |")
    print(f"| CC Gate | **{cc}** |")
    print(f"| i18n AST Gate | **{i18n}** |")
    print(f"| Total Issues | **{issues}** |")
    print(f"| Task Completion | **{tcr}** |")
    print(f"| Sessions Tracked | **{sessions}** |")

    # ── Quality Score Sparkline ──────────────────────────────────────
    qs_history = extract_score_history(history)
    if qs_history:
        scores = [s for _, s in qs_history]
        print("\n## Quality Score Trend\n")
        print(f"```\n{sparkline(scores, 40)}\n```")
        print(f"**Range**: {min(scores):.1f} → {max(scores):.1f}  |  "
              f"**Direction**: {trend_direction(scores)}")
        print(f"**Sessions tracked**: {len(qs_history)}")

        if not compact:
            print("\n| Session | Score | Bar |")
            print("| :--- | :--- | :--- |")
            for date, score in qs_history[-8:]:
                bar = "█" * max(1, int(score / 5))
                print(f"| {date} | {score:.1f} | {bar} |")

    # ── Multi-Metric Bar Chart ───────────────────────────────────────
    if not compact:
        print("\n## Multi-Metric Comparison\n")
        print("```")
        print(bar_chart("Stability", float(qs) if qs != "?" else 0))
        print(bar_chart("Maintainability", float(maint) if maint != "?" else 0))
        print(bar_chart("Security", float(sec) if sec != "?" else 0))
        print("```")

    # ── i18n Issue Trend ─────────────────────────────────────────────
    analyzer_i18n = summary.get("i18n_issues_qgis_analyzer")
    ast_i18n = summary.get("i18n_issues_i18n_hygiene")
    if analyzer_i18n is not None or ast_i18n is not None:
        print("\n## i18n Status\n")
        print("| Metric | Value |")
        print("| :--- | :--- |")
        print(f"| qgis-analyzer MISSING_I18N | {analyzer_i18n if analyzer_i18n is not None else '?'} |")
        print(f"| verify_i18n_hygiene violations | {ast_i18n if ast_i18n is not None else '?'} |")

    # ── Issue Breakdown ──────────────────────────────────────────────
    breakdown = summary.get("issue_breakdown", {})
    if breakdown and not compact:
        print("\n## Active Issues\n")
        print("| Category | Count |")
        print("| :--- | :--- |")
        for cat, count in sorted(breakdown.items(), key=lambda x: -x[1]):
            emoji = "🔴" if count > 50 else "🟡" if count > 10 else "🟢"
            print(f"| {cat} | {emoji} {count} |")

    # ── Session Trend ────────────────────────────────────────────────
    if history:
        print(f"\n## Session History (last {min(10, len(history))})\n")
        print("| Date | Session | TCR | Retries | Status |")
        print("| :--- | :--- | :--- | :--- | :--- |")
        for entry in history[-10:][::-1]:
            date = entry.get("date", "?")
            session = entry.get("session", "?")
            tcr_val = entry.get("task_completion_rate", 1.0)
            retries = entry.get("retries", 0)
            status = entry.get("status", "SUCCESS")
            emoji = "✅" if status == "SUCCESS" else "🚀" if status == "release" else "⚠️"
            print(f"| {date} | {session} | {tcr_val:.2f} | {retries} | {emoji} {status} |")

    # ── Session Delta ────────────────────────────────────────────────
    if len(history) >= 2:
        prev = history[-2]
        curr = history[-1]
        print("\n## Last Session Delta\n")
        prev_qs = _find_score(prev)
        curr_qs = _find_score(curr)
        prev_date = prev.get("date", "?")
        curr_date = curr.get("date", "?")
        print(f"**{prev_date} → {curr_date}**\n")
        if prev_qs is not None and curr_qs is not None:
            delta = curr_qs - prev_qs
            arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
            print(f"- Quality Score: {prev_qs:.1f} {arrow} {curr_qs:.1f} "
                  f"({'+' if delta > 0 else ''}{delta:.1f})")

    # ── Data Freshness ───────────────────────────────────────────────
    print("\n## Data Freshness\n")
    print("| Source | Last Run |")
    print("| :--- | :--- |")
    for source_name, source_data in ground_truth.items():
        if isinstance(source_data, dict):
            print(f"| {source_name} | {source_data.get('date', '?')} |")

    print(f"\n\n*Generated by SecInterp Metrics Engine (Gen 7) — "
          f"{datetime.now().strftime('%Y-%m-%d %H:%M')}*")




# =====================================================================
# Metric consistency validator  (was validate_agent_metrics.py)
# =====================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENT_DIR = PROJECT_ROOT / ".agent"
METRICS_FILE = AGENT_DIR / "memory" / "agent_metrics.json"
HISTORY_DIR = AGENT_DIR / "history"

# Patterns to extract embedded metrics from documentation files
TEST_PATTERNS = [
    (re.compile(r"\b(\d+)\s*tests?\s*(?:OK|pass|passing|ok)", re.IGNORECASE), "test_count"),
    (re.compile(r"tests?:\s*(\d+)"), "test_count"),
    (re.compile(r"total_?tests?:\s*(\d+)", re.IGNORECASE), "test_count"),
    (re.compile(r"(\d+)/\d+\s*\(100%\)", re.IGNORECASE), "test_count"),
    (re.compile(r"Achieve\s+(\d+)\+?\s*passing\s+tests?", re.IGNORECASE), "test_min"),
]

QUALITY_PATTERNS = [
    (re.compile(r"[Qq]uality\s*[Ss]core:?\s*(\d+\.?\d*)/?\d*"), "quality_score"),
    (re.compile(r"[Mm]odule\s*[Ss]tability:?\s*\*?\*?(\d+\.?\d*)/?\d*"), "quality_score"),
    (re.compile(r"[Ss]tability\s*[Ss]core:?\s*(\d+\.?\d*)/?\d*"), "quality_score"),
]

CC_PATTERNS = [
    (re.compile(r"CC\s*[><=]+\s*(\d+)"), "cc_threshold"),
    (re.compile(r"cyclomatic\s+complexity\s+(?:below|under)\s+(\d+)", re.IGNORECASE), "cc_threshold"),
    (re.compile(r"complexity\s*(?:>\s*(\d+)|<=?\s*(\d+))"), "cc_threshold"),
]

# Common stale→correct mappings for --fix mode
STALE_MAPPINGS = {
    "test_count": {
        535: 620, 572: 620,
    },
    "quality_score": {
        40.8: 52.3, 41.7: 52.3,
    },
    "cc_threshold": {
        15: 10,
    },
}


@dataclass
class MetricViolation:
    file: str
    line: int
    metric_type: str
    found_value: str
    expected_value: str
    context: str

    def __str__(self):
        return (
            f"  {self.file}:{self.line}  [{self.metric_type}] "
            f"found={self.found_value}  expected={self.expected_value}"
            f"\n    → {self.context.strip()}"
        )


@dataclass
class ValidationReport:
    violations: list[MetricViolation] = field(default_factory=list)
    files_scanned: int = 0

    @property
    def clean(self) -> bool:
        return len(self.violations) == 0


def load_ground_truth() -> dict:
    """Extract canonical metric values from agent_metrics.json."""
    if not METRICS_FILE.exists():
        return {}

    try:
        data = json.loads(METRICS_FILE.read_text())
    except json.JSONDecodeError:
        return {}

    truth = {}

    # Test count: try test_count first, then tests_ok
    summary = data.get("summary", {})
    if "test_count" in summary:
        truth["test_count"] = summary["test_count"]
    elif "tests_ok" in summary:
        truth["test_count"] = summary["tests_ok"]

    truth["quality_score"] = summary.get("quality_score_latest")
    truth["maintainability_score"] = summary.get("maintainability_score")
    truth["security_score"] = summary.get("security_score")

    # CC gate: always 10 in this project
    truth["cc_threshold"] = 10

    return truth


def _check_i18n_consistency(summary: dict, issues: list[str]) -> None:
    """Validate that the i18n analyzer count matches the issue breakdown."""
    breakdown = summary.get("issue_breakdown", {})
    i18n_analyzer = summary.get("i18n_issues_qgis_analyzer")
    i18n_breakdown = breakdown.get("MISSING_I18N")
    if i18n_analyzer is not None and i18n_breakdown is not None and i18n_analyzer != i18n_breakdown:
        issues.append(
            f"summary.i18n_issues_qgis_analyzer ({i18n_analyzer}) != "
            f"summary.issue_breakdown.MISSING_I18N ({i18n_breakdown})"
        )


def _check_issue_total(summary: dict, issues: list[str]) -> None:
    """Validate that total_issues equals the sum of the issue breakdown."""
    breakdown = summary.get("issue_breakdown", {})
    total_issues = summary.get("total_issues")
    if total_issues is None or not breakdown:
        return
    breakdown_sum = sum(v for v in breakdown.values() if isinstance(v, int))
    if total_issues != breakdown_sum:
        issues.append(
            f"summary.total_issues ({total_issues}) != sum(issue_breakdown) ({breakdown_sum})"
        )


def _check_test_count(summary: dict, issues: list[str]) -> None:
    """Validate that test_count and tests_ok agree."""
    test_count = summary.get("test_count")
    tests_ok = summary.get("tests_ok")
    if test_count is not None and tests_ok is not None and test_count != tests_ok:
        issues.append(f"summary.test_count ({test_count}) != summary.tests_ok ({tests_ok})")


def _check_score_sources(summary: dict, data: dict, issues: list[str]) -> None:
    """Validate that summary scores match the qgis-analyzer ground-truth source."""
    gt = data.get("ground_truth_sources", {}).get("qgis_analyzer", {}).get("scores", {})
    score_checks = [
        ("quality_score_latest", "module_stability"),
        ("maintainability_score", "maintainability"),
        ("security_score", "security"),
    ]
    for summary_key, gt_key in score_checks:
        summary_val = summary.get(summary_key)
        gt_val = gt.get(gt_key)
        if summary_val is not None and gt_val is not None and summary_val != gt_val:
            issues.append(
                f"summary.{summary_key} ({summary_val}) != "
                f"ground_truth_sources.qgis_analyzer.scores.{gt_key} ({gt_val})"
            )


def _check_session_date(data: dict, issues: list[str]) -> None:
    """Validate that last_session.date is not older than the newest history entry."""
    last_date = data.get("last_session", {}).get("date")
    history = data.get("history", [])
    dates = [h.get("date") for h in history if h.get("date")]
    if last_date and dates and max(dates) > last_date:
        issues.append(
            f"last_session.date ({last_date}) is older than newest history entry ({max(dates)})"
        )


def check_internal_consistency(metrics_file: Path = METRICS_FILE) -> list[str]:
    """Validate that agent_metrics.json is internally coherent.

    Returns a list of human-readable inconsistency descriptions. An empty
    list means the file is internally consistent.
    """
    if not metrics_file.exists():
        return ["agent_metrics.json not found"]

    try:
        data = json.loads(metrics_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [f"agent_metrics.json is not valid JSON: {exc}"]

    issues: list[str] = []
    summary = data.get("summary", {})
    _check_i18n_consistency(summary, issues)
    _check_issue_total(summary, issues)
    _check_test_count(summary, issues)
    _check_score_sources(summary, data, issues)
    _check_session_date(data, issues)
    return issues


def should_skip_file(filepath: Path) -> bool:
    """Skip history archives and non-markdown/json files."""
    if filepath.suffix not in (".md", ".json"):
        return True

    rel_path = str(filepath.relative_to(AGENT_DIR))
    if rel_path.startswith("history/"):
        return True
    if rel_path.startswith("architecture/"):
        return True

    # Skip the ground-truth file itself
    if filepath.resolve() == METRICS_FILE.resolve():
        return True

    return False


def extract_metrics_from_line(line: str) -> list[tuple[str, str, str]]:
    """Extract metric references from a single line.
    Returns list of (metric_type, raw_match, clean_value) tuples.
    """
    results = []

    for pattern, metric_type in TEST_PATTERNS:
        for m in pattern.finditer(line):
            raw = m.group(0)
            val = m.group(1)
            results.append((metric_type, raw, val))

    for pattern, metric_type in QUALITY_PATTERNS:
        for m in pattern.finditer(line):
            raw = m.group(0)
            val = m.group(1)
            results.append((metric_type, raw, val))

    for pattern, metric_type in CC_PATTERNS:
        for m in pattern.finditer(line):
            raw = m.group(0)
            val = m.group(1) or m.group(2)
            if val:
                results.append((metric_type, raw, val))

    return results


def normalize_value(val_str: str) -> Optional[float]:
    """Normalize a found metric value to float for comparison."""
    try:
        return float(val_str)
    except ValueError:
        return None


def detect_documented_triage(context: str, found_val: float, expected_val: float) -> bool:
    """Skip lines that explicitly document a discrepancy being triaged/resolved."""
    triage_markers = [
        "vs", "→", "conflicting", "verified", "RESOLVED",
        "resolved", "discrepancy", "confirmed",
    ]
    if not any(marker.lower() in context.lower() for marker in triage_markers):
        return False
    # Check if both values are mentioned in context (documenting the fix)
    if str(int(found_val)) in context and str(int(expected_val)) in context:
        return True
    return False


def is_archaic_reference(context: str, found_val: float, expected_val: float) -> bool:
    """Check if the line is describing a past state (e.g., 'v3.6.0 Baseline')."""
    archaic_markers = [
        "v3.6.0 Baseline", "v3.5.0", "v3.4.0", "v3.3.0",
        "v3.2.0", "v3.0.0", "v2.",
        "previously", "before phase", "was stale",
    ]
    return any(marker.lower() in context.lower() for marker in archaic_markers)


def validate_file(filepath: Path, ground_truth: dict) -> list[MetricViolation]:
    """Scan a single file for metric inconsistencies."""
    violations = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return violations

    lines = content.splitlines()
    for lineno, line in enumerate(lines, start=1):
        metrics = extract_metrics_from_line(line)
        for metric_type, raw_match, clean_val in metrics:
            found = normalize_value(clean_val)
            if found is None:
                continue

            expected = ground_truth.get(metric_type)
            if expected is None:
                continue

            if found == expected:
                continue

            # Exemptions
            if detect_documented_triage(line, found, expected):
                continue
            if is_archaic_reference(line, found, expected):
                continue

            violations.append(MetricViolation(
                file=str(filepath.relative_to(PROJECT_ROOT)),
                line=lineno,
                metric_type=metric_type,
                found_value=str(int(found) if found == int(found) else found),
                expected_value=str(int(expected) if expected == int(expected) else expected),
                context=line.strip(),
            ))

    return violations


def scan_agent_files(ground_truth: dict) -> ValidationReport:
    """Scan all relevant .agent/ files for metric consistency."""
    report = ValidationReport()

    if not AGENT_DIR.exists():
        return report

    for filepath in sorted(AGENT_DIR.rglob("*")):
        if not filepath.is_file():
            continue
        if should_skip_file(filepath):
            continue

        report.files_scanned += 1
        violations = validate_file(filepath, ground_truth)
        report.violations.extend(violations)

    return report


def auto_fix(filepath: Path, violations: list[MetricViolation]) -> bool:
    """Attempt to auto-fix known stale values inline."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return False

    modified = False
    for v in violations:
        mapping = STALE_MAPPINGS.get(v.metric_type, {})
        found_num = None
        try:
            found_num = float(v.found_value)
        except ValueError:
            continue
        found_int = int(found_num) if found_num == int(found_num) else found_num

        new_val = mapping.get(found_int)
        if new_val is None:
            continue

        new_str = str(new_val)
        old_str = str(v.found_value)
        if old_str in content:
            content = content.replace(old_str, new_str, 1)
            modified = True

    if modified:
        filepath.write_text(content, encoding="utf-8")

    return modified


def validate_main():
    quiet = "--quiet" in sys.argv
    fix_mode = "--fix" in sys.argv

    internal_issues = check_internal_consistency()
    if internal_issues:
        if not quiet:
            print("❌ agent_metrics.json internal inconsistencies:")
            for issue in internal_issues:
                print(f"  - {issue}")
            print()

    ground_truth = load_ground_truth()
    if not ground_truth:
        print("❌ Cannot load ground truth from agent_metrics.json", file=sys.stderr)
        print("   Run: uv run python scripts/sync_metrics.py", file=sys.stderr)
        sys.exit(1)

    report = scan_agent_files(ground_truth)

    if not quiet:
        print(f"🔍 Scanned {report.files_scanned} files in .agent/")
        print(f"   Ground truth: tests={ground_truth.get('test_count', '?')}, "
              f"quality={ground_truth.get('quality_score', '?')}, "
              f"CC≤{ground_truth.get('cc_threshold', '?')}")

    if report.clean and not internal_issues:
        if not quiet:
            print("✅ All .agent/ files are metric-consistent with agent_metrics.json")
        sys.exit(0)

    if report.violations:
        if not quiet:
            print(f"❌ Found {len(report.violations)} metric inconsistencies:\n")

        fixes_applied = 0
        for v in report.violations:
            if not quiet:
                print(str(v))

            if fix_mode:
                filepath = PROJECT_ROOT / v.file
                if auto_fix(filepath, [v]):
                    fixes_applied += 1

        if fix_mode and fixes_applied > 0:
            if not quiet:
                print(f"\n🔧 Auto-fixed {fixes_applied} stale values. "
                      f"Run again to verify: uv run python scripts/sync_metrics.py --validate")
            sys.exit(0)

    sys.exit(1)




# =====================================================================
# Testing status updater  (was update_testing_status.py)
# =====================================================================

def count_tests_in_file(file_path):
    """Count test methods in a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Simple regex to count test_... methods
    return len(re.findall(r"def\s+test_", content))


def get_test_inventory(test_dir):
    """Get a detailed list of tests for the inventory section."""
    inventory = []
    for root, dirs, files in os.walk(test_dir):
        # Sort files to keep stable inventory
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
