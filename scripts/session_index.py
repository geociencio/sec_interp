#!/usr/bin/env python3
"""Session Index Generator (Gen 7).

Scans docs/maintenance/ for session logs and phase closures,
grouping them chronologically by version/phase.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from contextlib import suppress
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAINTENANCE_DIR = PROJECT_ROOT / "docs" / "maintenance"

# Mapping versions to phase ranges
PHASE_RANGES = [
    ("v3.7.0", re.compile(r"2026-05-2[3-9]|2026-05-3")),
    ("v3.6.0", re.compile(r"2026-05-0[5-9]|2026-05-1[0-8]")),
    ("v3.5.0", re.compile(r"2026-04-2[5-9]|2026-05-0[1-4]")),
    ("v3.4.0", re.compile(r"2026-04-1[5-9]|2026-04-2[0-4]")),
    ("v3.3.0", re.compile(r"2026-03-1[4-9]|2026-03-2|2026-04-0[1-9]|2026-04-1[0-4]")),
    ("v3.2.0", re.compile(r"2026-03-0[1-9]|2026-03-1[0-3]")),
    ("v3.0.x", re.compile(r"2026-02-")),
    ("v2.x", re.compile(r"2026-01-")),
    ("earlier", re.compile(r"2025-")),
]


def extract_date(filename: str) -> str | None:
    """Extract YYYY-MM-DD date from filename."""
    m = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
    return m.group(1) if m else None


def extract_topic(filename: str) -> str:
    """Extract topic from filename (after date)."""
    name = filename.replace(".md", "")
    m = re.match(r"(?:session_|phase_closure_)?(?:\d{4}-\d{2}-\d{2})_?(.*)", name)
    return m.group(1) if m and m.group(1) else name


def classify_phase(date_str: str) -> str:
    """Assign a file to a development phase."""
    for phase, pattern in PHASE_RANGES:
        if pattern.search(date_str):
            return phase
    return "unknown"


def index_sessions() -> list[dict]:
    """Scan and index all maintenance files."""
    entries = []

    if not MAINTENANCE_DIR.exists():
        return entries

    for filepath in sorted(MAINTENANCE_DIR.glob("*.md")):
        # Only include session logs and phase closures (files with date prefix)
        if not re.match(r"(session_|phase_closure_)\d{4}-\d{2}-\d{2}", filepath.name):
            continue
        date = extract_date(filepath.name)
        topic = extract_topic(filepath.name)
        phase = classify_phase(date) if date else "unknown"

        entry = {
            "file": filepath.name,
            "date": date or "unknown",
            "topic": topic,
            "phase": phase,
            "type": "phase_closure" if filepath.name.startswith("phase_closure") else "session",
        }
        entries.append(entry)

    return entries


def main():
    by_phase = "--by-phase" in sys.argv
    recent = None
    for i, arg in enumerate(sys.argv):
        if arg == "--recent" and i + 1 < len(sys.argv):
            with suppress(ValueError):
                recent = int(sys.argv[i + 1])

    entries = index_sessions()

    if not entries:
        print("No maintenance files found in docs/maintenance/")
        return

    print(f"# Session Index — {len(entries)} entries\n")

    if by_phase:
        # Group by phase
        grouped: dict[str, list[dict]] = defaultdict(list)
        for e in entries:
            grouped[e["phase"]].append(e)

        for phase in sorted(grouped.keys()):
            phase_entries = grouped[phase]
            print(f"## {phase} ({len(phase_entries)} entries)\n")
            print("| Date | Type | Topic |")
            print("| :--- | :--- | :--- |")
            for e in sorted(phase_entries, key=lambda x: x["date"]):
                icon = "🏁" if e["type"] == "phase_closure" else "📝"
                print(f"| {e['date']} | {icon} {e['type']} | {e['topic']} |")
            print()

    elif recent:
        recent_entries = sorted(entries, key=lambda x: x["date"], reverse=True)[:recent]
        print(f"## Last {recent} Sessions\n")
        print("| Date | Phase | Type | Topic |")
        print("| :--- | :--- | :--- | :--- |")
        for e in recent_entries:
            icon = "🏁" if e["type"] == "phase_closure" else "📝"
            print(f"| {e['date']} | {e['phase']} | {icon} | {e['topic']} |")

    else:
        print("| Date | Phase | Type | Topic |")
        print("| :--- | :--- | :--- | :--- |")
        for e in sorted(entries, key=lambda x: x["date"]):
            icon = "🏁" if e["type"] == "phase_closure" else "📝"
            print(f"| {e['date']} | {e['phase']} | {icon} | {e['topic']} |")

    print(f"\n*Generated from {len(entries)} files in docs/maintenance/*")


if __name__ == "__main__":
    main()
