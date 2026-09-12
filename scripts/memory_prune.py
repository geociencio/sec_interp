#!/usr/bin/env python3
"""
Memory Pruning Utility (Gen 6)
Auto-prunes consolidated lessons older than 90 days from AGENT_LESSONS.md
and next_steps snapshots older than 90 days from .agent/history/next_steps/.
"""

import re
from datetime import date, datetime, timedelta
from pathlib import Path

import yaml

# Configuration
LESSONS_FILE = Path(".agent/memory/AGENT_LESSONS.md")
NEXT_STEPS_DIR = Path(".agent/history/next_steps")
PRUNE_DAYS = 90
NEXT_STEPS_RETENTION_DAYS = 90


def _parse_date(value):
    """Coerce a lesson date value into a datetime."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    return datetime.strptime(str(value), "%Y-%m-%d")


def prune_lessons() -> int:
    """Prune consolidated lessons older than PRUNE_DAYS. Returns count pruned."""
    if not LESSONS_FILE.exists():
        print(f"Error: {LESSONS_FILE} not found.")
        return 0

    content = LESSONS_FILE.read_text()

    # Extract YAML block
    yaml_match = re.search(r"```yaml\n(.*?)\n```", content, re.DOTALL)
    if not yaml_match:
        print("Error: Could not find YAML block in AGENT_LESSONS.md")
        return 0

    yaml_content = yaml_match.group(1)

    try:
        data = yaml.safe_load(yaml_content)
    except Exception as e:
        print(f"Error parsing YAML: {e}")
        return 0

    lessons = data.get("lessons", [])
    if not lessons:
        print("No lessons found in AGENT_LESSONS.md")
        return 0

    today = datetime.now()
    threshold = today - timedelta(days=PRUNE_DAYS)

    active_lessons = []
    new_pruned_entries = []

    pruned_count = 0
    for lesson in lessons:
        if not lesson:
            continue
        try:
            lesson_date = _parse_date(lesson.get("date"))
            consolidated = lesson.get("consolidated_in")

            if lesson_date < threshold and consolidated:
                # Prune this lesson
                topic = lesson.get("topic", "Unknown")
                category = lesson.get("category", "GENERAL")
                entry = (
                    f"  # [PRUNED] {lesson_date.strftime('%Y-%m-%d')} "
                    f"{category}/{topic} → {consolidated}"
                )
                new_pruned_entries.append(entry)
                pruned_count += 1
            else:
                active_lessons.append(lesson)
        except Exception as e:
            print(f"Warning: Skipping invalid lesson entry: {e}")
            active_lessons.append(lesson)

    if pruned_count == 0:
        print("No lessons meet the pruning criteria (consolidated & > 90 days).")
        return 0

    # Construct new YAML block
    header = "  # ─── ACTIVE LESSONS (< 90 days or not yet in a SKILL.md) ───────────────────\n"
    pruned_header = (
        "\n  # ─── PRUNED LESSONS (already in SKILL.md — kept as index only) ─────────────\n"
    )
    pruned_footer = (
        "  # The following entries have been fully absorbed into specialized skills.\n"
        "  # They are retained here as a consolidated index only.\n"
        "  #\n"
    )

    final_yaml = "lessons:\n\n" + header

    # Add active lessons YAML
    for lesson in active_lessons:
        # Convert date back to string for clean output
        if isinstance(lesson.get("date"), (datetime, date)):
            lesson["date"] = lesson["date"].strftime("%Y-%m-%d")

        lesson_yaml = yaml.dump(
            [lesson],
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
            indent=2,
        )
        # Prefix with two spaces
        indented = ""
        for line in lesson_yaml.splitlines():
            indented += "  " + line + "\n"
        final_yaml += indented

    # Add pruned section
    final_yaml += pruned_header + pruned_footer

    # Extract existing pruned entries from old content
    existing_pruned = re.findall(r"  # \[PRUNED\] .*", yaml_content)

    # Combine all pruned entries
    all_pruned = new_pruned_entries + existing_pruned
    # Sort by date descending (assuming format YYYY-MM-DD)
    all_pruned.sort(reverse=True)

    final_yaml += "\n".join(all_pruned)

    # Replace the old YAML block
    new_content = content.replace(yaml_content, final_yaml)

    LESSONS_FILE.write_text(new_content)
    print(f"Successfully pruned {pruned_count} lessons. Updated {LESSONS_FILE}")
    return pruned_count


def prune_next_steps_snapshots() -> int:
    """Prune next_steps snapshots older than NEXT_STEPS_RETENTION_DAYS."""
    if not NEXT_STEPS_DIR.exists():
        print(f"Info: {NEXT_STEPS_DIR} not found. Nothing to prune.")
        return 0

    threshold = datetime.now() - timedelta(days=NEXT_STEPS_RETENTION_DAYS)
    filename_pattern = re.compile(r"next_steps_(\d{4}-\d{2}-\d{2})")
    removed = 0

    for path in sorted(NEXT_STEPS_DIR.glob("next_steps_*.md")):
        match = filename_pattern.search(path.name)
        if match:
            try:
                file_date = datetime.strptime(match.group(1), "%Y-%m-%d")
            except ValueError:
                file_date = datetime.fromtimestamp(path.stat().st_mtime)
        else:
            file_date = datetime.fromtimestamp(path.stat().st_mtime)

        if file_date < threshold:
            path.unlink()
            removed += 1

    if removed:
        print(f"Successfully pruned {removed} next_steps snapshots from {NEXT_STEPS_DIR}")
    else:
        print("No next_steps snapshots meet the pruning criteria (> 90 days).")
    return removed


def main():
    prune_lessons()
    prune_next_steps_snapshots()


if __name__ == "__main__":
    main()
