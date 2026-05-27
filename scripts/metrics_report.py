#!/usr/bin/env python3
"""
Metrics Trend Report with ASCII Visualization (Gen 7)

Generates a Markdown report from agent_metrics.json with:
  - Quality score trend sparkline
  - i18n issue trend
  - CC gate history
  - Multi-metric ASCII bar chart comparison
  - Session-to-session delta analysis

Usage:
    uv run python scripts/metrics_report.py [--compact]
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

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


if __name__ == "__main__":
    compact = "--compact" in sys.argv
    generate_report(compact=compact)
