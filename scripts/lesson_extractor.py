#!/usr/bin/env python3
"""Session Lesson Extractor (Gen 7).

Analyzes a session's git diff and AGENT_LESSONS.md to propose candidate
lessons for automated knowledge capture during /close-session.
"""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LESSONS_FILE = PROJECT_ROOT / ".agent" / "memory" / "AGENT_LESSONS.md"

# Patterns that signal a lesson-worthy event
SIGNAL_PATTERNS = {
    "error_resolution": [
        (re.compile(r"Traceback.*\n.*Error:", re.MULTILINE), "Error traceback found in session"),
        (re.compile(r"raise\s+effect", re.IGNORECASE), "Mock side_effect used (test error path)"),
    ],
    "code_patterns": [
        (re.compile(r"# no-i18n", re.IGNORECASE), "i18n suppression markers added"),
        (re.compile(r"self\.tr\(.+\)", re.IGNORECASE), "Translation wrapping added"),
        (re.compile(r"@staticmethod|@classmethod", re.IGNORECASE), "Decorator patterns modified"),
    ],
    "tooling_changes": [
        (re.compile(r"scripts/[\w_]+\.py", re.IGNORECASE), "Script created or modified"),
    ],
    "metric_changes": [
        (re.compile(r"(535|572).*(620)", re.IGNORECASE), "Stale metrics corrected"),
        (re.compile(r"(40\.8|41\.7).*(52\.3)", re.IGNORECASE), "Quality score updated"),
    ],
}


def get_session_diff(since: str = "HEAD~1") -> str:
    """Get the git diff for the current session."""
    try:
        result = subprocess.run(
            ["git", "diff", since, "--stat"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return result.stdout
    except Exception:
        return ""


def get_existing_categories() -> set[str]:
    """Extract existing lesson categories from AGENT_LESSONS.md."""
    categories = set()
    if not LESSONS_FILE.exists():
        return categories
    content = LESSONS_FILE.read_text(encoding="utf-8")
    for line in content.splitlines():
        m = re.search(r"category:\s*(\w+)", line)
        if m:
            categories.add(m.group(1))
    return categories


def detect_signals(diff_text: str) -> list[dict]:
    """Scan diff for lesson-worthy signals."""
    candidates = []

    for category, patterns in SIGNAL_PATTERNS.items():
        for pattern, description in patterns:
            matches = pattern.findall(diff_text)
            if matches:
                candidates.append({
                    "category": category,
                    "pattern": description,
                    "count": len(matches),
                })

    # Also detect files changed
    files_changed = re.findall(r"^\s*([\w/._-]+)\s+\|", diff_text, re.MULTILINE)
    file_categories = {
        ".agent/": "AGENTIC_SYSTEM",
        "scripts/": "TOOLING",
        "core/": "CORE",
        "gui/": "GUI",
        "tests/": "TESTING",
        "exporters/": "EXPORTERS",
    }
    area_counts: dict[str, int] = {}
    for f in files_changed:
        for prefix, area in file_categories.items():
            if f.startswith(prefix):
                area_counts[area] = area_counts.get(area, 0) + 1
                break

    if area_counts:
        dominant = max(area_counts, key=area_counts.get)  # type: ignore[arg-type]
        candidates.append({
            "category": "area_focus",
            "pattern": f"Session focused on {dominant} ({area_counts})",
            "count": sum(area_counts.values()),
        })

    return candidates


def propose_lessons(signals: list[dict], diff_text: str) -> list[dict]:
    """Generate candidate lesson entries from detected signals."""
    proposals = []

    # Determine dominant category from signals
    categories_seen: dict[str, int] = {}
    for s in signals:
        cat = s.get("category", "GENERAL")
        categories_seen[cat] = categories_seen.get(cat, 0) + s.get("count", 1)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Propose based on tolling changes (new scripts = tooling lesson)
    if "tooling_changes" in categories_seen:
        proposals.append({
            "date": today,
            "category": "TOOLING",
            "topic": "New automation scripts added",
            "lesson": "New scripts were created to extend the agentic system. "
                       "Document their purpose in QUICK_REFERENCE.md and add to relevant workflows.",
            "action": "Run `uv run python scripts/workflow_graph.py --validate` to confirm integration.",
        })

    # Propose based on metric corrections
    if "metric_changes" in categories_seen:
        proposals.append({
            "date": today,
            "category": "AGENTIC_SYSTEM",
            "topic": "Metric drift detected and corrected",
            "lesson": "Stale metric references (test counts, quality scores) were found across "
                       "multiple .agent/ files. Always run `validate_agent_metrics.py` at session "
                       "start/close to catch drift early.",
            "action": "Run `uv run python scripts/validate_agent_metrics.py` in /start-session and /close-session.",
        })

    # Propose based on i18n patterns
    for s in signals:
        if "i18n" in s.get("pattern", "").lower():
            proposals.append({
                "date": today,
                "category": "i18n",
                "topic": "Translation markers added/modified",
                "lesson": "User-facing strings were wrapped with self.tr() or tagged with # no-i18n. "
                           "Remember the dual-scope i18n strategy: verify_i18n_hygiene.py for AST gate, "
                           "qgis-analyzer for broader heuristic detection.",
                "action": "Run `uv run python scripts/verify_i18n_hygiene.py` before committing GUI changes.",
            })
            break

    return proposals


def main():
    propose_mode = "--propose" in sys.argv
    since = "HEAD~1"
    for i, arg in enumerate(sys.argv):
        if arg == "--since" and i + 1 < len(sys.argv):
            since = sys.argv[i + 1]

    diff_text = get_session_diff(since)
    if not diff_text:
        print("No git diff found for this session.", file=sys.stderr)
        sys.exit(0)

    signals = detect_signals(diff_text)

    print("## Session Lesson Extraction\n")
    print(f"**Source**: git diff {since}")
    print(f"**Date**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC\n")

    if not signals:
        print("No lesson-worthy signals detected in this session.\n")
        return

    print("### Detected Signals\n")
    for s in signals:
        print(f"- **{s['category']}**: {s['pattern']} (×{s['count']})")

    if not propose_mode:
        print("\n---\nRun with `--propose` to generate candidate YAML lesson entries.\n")
        return

    proposals = propose_lessons(signals, diff_text)
    if not proposals:
        print("\nNo candidate lessons to propose (all signals already covered or trivial).\n")
        return

    print("\n### Candidate Lessons\n")
    print("```yaml")
    for p in proposals:
        print(f"- date: {p['date']}")
        print(f"  category: {p['category']}")
        print(f"  topic: \"{p['topic']}\"")
        print(f"  lesson: \"{p['lesson']}\"")
        print(f"  action: \"{p['action']}\"")
        print("  source: auto-extracted")
    print("```")
    print(f"\nReview the above candidates and add relevant ones to `{LESSONS_FILE}`.")


if __name__ == "__main__":
    main()
