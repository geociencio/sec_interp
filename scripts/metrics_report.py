#!/usr/bin/env python3
"""
Metrics Report Utility (Gen 7)
Generates a Markdown report from agent_metrics.json with trend analysis.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Configuration
METRICS_FILE = Path(".agent/memory/agent_metrics.json")


def trend_direction(values: list, n: int = 3) -> str:
    """Determine if recent trend is improving, declining, or stable."""
    if len(values) < 2:
        return "⏸️ Stable (insufficient data)"
    recent = values[-n:] if len(values) >= n else values
    if len(recent) < 2:
        return "⏸️ Stable"
    first, last = recent[0], recent[-1]
    if first is None or last is None:
        return "❓ Unknown"
    if last > first:
        return "📈 Improving"
    elif last < first:
        return "📉 Declining"
    return "⏸️ Stable"


def generate_report():
    if not METRICS_FILE.exists():
        print(f"Error: {METRICS_FILE} not found.")
        return

    try:
        data = json.loads(METRICS_FILE.read_text())
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return

    summary = data.get("summary", {})
    history = data.get("history", [])
    ground_truth = data.get("ground_truth_sources", {})

    # ── Header ──────────────────────────────────────────────────────
    print("# Agentic Operational Metrics Report")
    print(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"**Overall Effectiveness**: {summary.get('overall_effectiveness_score', 'N/A')}")
    print(f"**Task Completion Rate (TCR)**: {summary.get('task_completion_rate', 'N/A')}")
    print(f"**Average Retries**: {summary.get('avg_retries_per_session', 'N/A')}")
    print(f"**Total Sessions**: {summary.get('total_sessions', 'N/A')}")
    print(f"**Latest Quality Score**: {summary.get('quality_score_latest', 'N/A')}")
    print(f"**Maintainability**: {summary.get('maintainability_score', 'N/A')}")
    print(f"**Security**: {summary.get('security_score', 'N/A')}")
    print(f"**CC Gate**: {summary.get('cyclomatic_complexity_gate', 'N/A')}")
    print(f"**i18n AST Gate**: {summary.get('i18n_hygiene_gate', 'N/A')}")
    total_issues = summary.get('total_issues', 'N/A')
    print(f"**Total Issues**: {total_issues}")

    # ── Session Trend Table ─────────────────────────────────────────
    print("\n## Session Trend (Last 10 sessions)")
    print("\n| Date | Session | TCR | Retries | Status |")
    print("| :--- | :--- | :--- | :--- | :--- |")

    for entry in history[-10:][::-1]:
        date = entry.get("date", "N/A")
        session = entry.get("session", "N/A")
        tcr = entry.get("task_completion_rate", 1.0)
        retries = entry.get("retries", 0)
        status = entry.get("status", "SUCCESS")
        status_emoji = "✅" if status == "SUCCESS" else "🚀" if status == "release" else "⚠️"
        print(f"| {date} | {session} | {tcr:.2f} | {retries} | {status_emoji} {status} |")

    # ── Quality Score Trend ─────────────────────────────────────────
    print("\n## Quality Score Trend")
    qs_entries = []
    for entry in history:
        qs = entry.get("quality_score")
        if qs is not None:
            qs_entries.append((entry.get("date", "?"), qs))

    if qs_entries:
        print(f"\n**Direction**: {trend_direction([q for _, q in qs_entries])}")
        print("\n| Date | Quality Score |")
        print("| :--- | :--- |")
        for date, qs in qs_entries[-10:]:
            bar = "█" * max(1, int(qs / 5))
            print(f"| {date} | {qs} {bar} |")
    else:
        print("\nNo quality score history available.")

    # ── Retries Trend ───────────────────────────────────────────────
    print("\n## Retries Trend")
    retries_data = [
        (e.get("date", "?"), e.get("retries", 0))
        for e in history
    ]
    if retries_data:
        recent_retries = [r for _, r in retries_data[-5:]]
        avg_retries = sum(recent_retries) / len(recent_retries) if recent_retries else 0
        print(f"\n**5-session avg retries**: {avg_retries:.1f}")
        print(f"**Direction**: {trend_direction([r for _, r in retries_data])}")

    # ── Ground Truth Freshness ──────────────────────────────────────
    print("\n## Data Freshness")
    sources = []
    for source_name, source_data in ground_truth.items():
        if isinstance(source_data, dict):
            sources.append((source_name, source_data.get("date", "?")))
    if sources:
        print("\n| Source | Last Run |")
        print("| :--- | :--- |")
        for name, date in sources:
            print(f"| {name} | {date} |")

    # ── Latest Session ─────────────────────────────────────────────
    last_session = data.get("last_session")
    if last_session:
        print(f"\n## Latest Session Details ({last_session.get('date')})")
        print(f"- **Topic**: {last_session.get('topic')}")
        print(f"- **Files Modified**: {last_session.get('files_modified')}")
        print(f"- **Quality Score**: {last_session.get('quality_score')}")
        tasks = last_session.get("tasks", [])
        if tasks:
            print("- **Completed Tasks**:")
            for task in tasks:
                print(f"  - {task}")

    print("\n\n*Generated by SecInterp Metrics Engine (Gen 7).*")


if __name__ == "__main__":
    generate_report()
