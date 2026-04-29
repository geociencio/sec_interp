#!/usr/bin/env python3
"""
Metrics Report Utility (Gen 6)
Generates a Markdown report from agent_metrics.json to track operational trends.
"""

import json
import sys
from pathlib import Path

# Configuration
METRICS_FILE = Path(".agent/memory/agent_metrics.json")


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

    print("# Agentic Operational Metrics Report")
    print(
        f"\n**Overall Effectiveness**: {summary.get('overall_effectiveness_score', 'N/A')}"
    )
    print(
        f"**Task Completion Rate (TCR)**: {summary.get('task_completion_rate', 'N/A')}"
    )
    print(f"**Average Retries**: {summary.get('avg_retries_per_session', 'N/A')}")
    print(f"**Total Sessions**: {summary.get('total_sessions', 'N/A')}")
    print(f"**Latest Quality Score**: {summary.get('quality_score_latest', 'N/A')}")

    print("\n## Session Trend (Last 10 sessions)")
    print("\n| Date | Session | TCR | Retries | Status |")
    print("| :--- | :--- | :--- | :--- | :--- |")

    # Show last 10 entries in history (descending order)
    for entry in history[-10:][::-1]:
        date = entry.get("date", "N/A")
        session = entry.get("session", "N/A")
        tcr = entry.get("task_completion_rate", 1.0)
        retries = entry.get("retries", 0)
        status = entry.get("status", "SUCCESS")

        # Format status as emoji
        status_emoji = (
            "✅" if status == "SUCCESS" else "🚀" if status == "release" else "⚠️"
        )

        print(
            f"| {date} | {session} | {tcr:.2f} | {retries} | {status_emoji} {status} |"
        )

    # Latest session details if available
    last_session = data.get("last_session")
    if last_session:
        print(f"\n## Latest Session Details ({last_session.get('date')})")
        print(f"- **Topic**: {last_session.get('topic')}")
        print(f"- **Files Modified**: {last_session.get('files_modified')}")
        print(f"- **Quality Score**: {last_session.get('quality_score')}")
        print("- **Completed Tasks**:")
        for task in last_session.get("tasks", []):
            print(f"  - {task}")

    print("\n\n*Generated automatically by SecInterp Metrics Engine.*")


if __name__ == "__main__":
    generate_report()
