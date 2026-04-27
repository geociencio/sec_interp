#!/usr/bin/env python3
"""
Script to automatically prune consolidated lessons from AGENT_LESSONS.md.
Lessons older than 90 days with a 'consolidated_in' field are moved to the
PRUNED index at the bottom.
"""

import datetime
import re
from pathlib import Path

LESSONS_FILE = Path(".agent/memory/AGENT_LESSONS.md")
PRUNE_DAYS = 90


def prune_lessons() -> None:
    """Prune lessons older than PRUNE_DAYS and append to the pruned list."""
    if not LESSONS_FILE.exists():
        print(f"Error: {LESSONS_FILE} not found.")
        return

    content = LESSONS_FILE.read_text(encoding="utf-8")

    # We will process the content line by line inside the yaml block
    lines = content.splitlines()

    in_yaml = False
    new_lines = []

    pruned_entries = []

    current_lesson_lines = []
    current_lesson_date = None
    current_lesson_category = None
    current_lesson_topic = None
    current_lesson_consolidated = None

    # Helper to process a lesson block
    def process_lesson_block():
        nonlocal current_lesson_lines, current_lesson_date, current_lesson_category, current_lesson_topic, current_lesson_consolidated
        if not current_lesson_lines:
            return

        should_prune = False
        if current_lesson_date and current_lesson_consolidated:
            try:
                lesson_date = datetime.datetime.strptime(
                    current_lesson_date, "%Y-%m-%d"
                ).date()
                age = (datetime.date.today() - lesson_date).days
                if age > PRUNE_DAYS:
                    should_prune = True
            except ValueError:
                pass  # If date parsing fails, do not prune

        if should_prune:
            # Add to pruned list
            category = current_lesson_category or "UNKNOWN"
            topic = current_lesson_topic or "Unknown Topic"
            pruned_line = f"  # [PRUNED] {current_lesson_date} {category}/{topic} \u2192 {current_lesson_consolidated}"
            pruned_entries.append(pruned_line)
            print(f"Pruned: {current_lesson_date} - {topic}")
        else:
            # Keep the lesson
            new_lines.extend(current_lesson_lines)

        current_lesson_lines = []
        current_lesson_date = None
        current_lesson_category = None
        current_lesson_topic = None
        current_lesson_consolidated = None

    yaml_end_index = -1
    pruned_section_index = -1

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("```yaml"):
            in_yaml = True
            new_lines.append(line)
            i += 1
            continue

        if line.startswith("```") and in_yaml:
            in_yaml = False
            process_lesson_block()  # process the last block if any
            # Insert pruned entries right before the PRUNED LESSONS section or at the end of yaml
            # Wait, the pruned section is inside the yaml block!
            # Let's handle it differently.
            yaml_end_index = len(new_lines)
            new_lines.append(line)
            i += 1
            continue

        if in_yaml:
            if "─── PRUNED LESSONS" in line:
                process_lesson_block()
                pruned_section_index = len(new_lines)
                new_lines.append(line)
                i += 1
                continue

            if line.strip().startswith("- date:"):
                process_lesson_block()
                current_lesson_lines.append(line)
                m = re.match(r"\s*-\s*date:\s*(\d{4}-\d{2}-\d{2})", line)
                if m:
                    current_lesson_date = m.group(1)
            elif current_lesson_lines:
                current_lesson_lines.append(line)

                # Extract metadata
                cat_m = re.match(r"\s*category:\s*(.+)", line)
                if cat_m:
                    current_lesson_category = cat_m.group(1).strip()

                top_m = re.match(r"\s*topic:\s*(.+)", line)
                if top_m:
                    current_lesson_topic = top_m.group(1).strip()

                con_m = re.match(r"\s*consolidated_in:\s*(.+)", line)
                if con_m:
                    current_lesson_consolidated = con_m.group(1).strip()
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

        i += 1

    # Insert the newly pruned entries into the PRUNED LESSONS section
    if pruned_entries:
        if pruned_section_index != -1:
            # Find the end of the pruned section (the last # comment before the end of yaml)
            insert_idx = yaml_end_index
            new_lines.insert(insert_idx, "\n".join(pruned_entries))
        else:
            print("Warning: Pruned section not found, appending before end of yaml.")
            new_lines.insert(
                yaml_end_index,
                "  # ─── PRUNED LESSONS (already in SKILL.md — kept as index only) ─────────────",
            )
            new_lines.insert(yaml_end_index + 1, "\n".join(pruned_entries))

        # We need to flatten the list if we inserted strings with \n, but insert actually just shifts.
        # Better to insert them one by one.
        pass

    # Rebuilding correctly
    final_lines = []
    for line in new_lines:
        if "\n" in line:
            final_lines.extend(line.split("\n"))
        else:
            final_lines.append(line)

    if pruned_entries:
        LESSONS_FILE.write_text("\n".join(final_lines) + "\n", encoding="utf-8")
        print(f"Successfully pruned {len(pruned_entries)} lessons.")
    else:
        print("No lessons to prune.")


if __name__ == "__main__":
    prune_lessons()
