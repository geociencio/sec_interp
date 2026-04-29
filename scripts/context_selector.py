#!/usr/bin/env python3
"""
Context Selector Utility (Gen 6)
Analyzes task description and selects the most relevant skills to reduce token bloat.
"""

import sys
import re
from pathlib import Path

# Mapping of keywords to skill IDs
SKILL_MAP = {
    "memory": ["agentic-memory"],
    "prune": ["agentic-memory"],
    "lessons": ["agentic-memory"],
    "changelog": ["changelog-generator"],
    "release": ["release-management", "changelog-generator"],
    "commit": ["commit-standards"],
    "git": ["commit-standards"],
    "docstring": ["documentation-standards", "coding-standards"],
    "documentation": ["documentation-standards"],
    "type hint": ["coding-standards"],
    "pathlib": ["coding-standards"],
    "geology": ["geological-logic"],
    "drillhole": ["geological-logic"],
    "section": ["geological-logic"],
    "i18n": ["i18n-standards"],
    "translation": ["i18n-standards"],
    "docker": ["qa-docker"],
    "test": ["qa-docker"],
    "unittest": ["qa-docker"],
    "mock": ["qa-docker"],
    "qgis": ["qgis-core", "qgis-migration-4x"],
    "qt6": ["qgis-migration-4x"],
    "migration": ["qgis-migration-4x"],
    "pyqt": ["qgis-core"],
    "ui": ["ui-framework"],
    "dialog": ["ui-framework"],
    "widget": ["ui-framework"],
    "aesthetic": ["ui-framework"],
    "style": ["coding-standards", "ui-framework"],
}

# Priority skills that are almost always useful
DEFAULT_SKILLS = ["project-context", "coding-standards"]


def select_skills(text):
    """Select up to 3 relevant skills based on keyword matching."""
    matches = {}
    text = text.lower()

    for kw, skill_list in SKILL_MAP.items():
        # Use regex for word boundary matching
        if re.search(rf"\b{re.escape(kw)}\b", text):
            for skill in skill_list:
                matches[skill] = matches.get(skill, 0) + 1

    # Sort skills by match frequency
    sorted_skills = sorted(matches.items(), key=lambda x: x[1], reverse=True)
    selected = [s[0] for s in sorted_skills]

    # Fill with defaults if needed
    for d in DEFAULT_SKILLS:
        if d not in selected:
            selected.append(d)

    # Return top 3
    return selected[:3]


def main():
    # Source text can come from arguments or files
    source_text = " ".join(sys.argv[1:])

    if not source_text:
        # Try to read from task.md
        task_file = Path(".agent/task.md")
        if task_file.exists():
            # Only read the active (unchecked) tasks
            task_content = task_file.read_text()
            active_tasks = re.findall(r"- \[ \] (.*)", task_content)
            source_text = " ".join(active_tasks)

    if not source_text:
        # Fallback to AI_CONTEXT.md keywords
        context_file = Path("AI_CONTEXT.md")
        if context_file.exists():
            source_text = context_file.read_text()

    selected = select_skills(source_text)

    # Output for shell consumption
    if "--shell" in sys.argv:
        print(",".join(selected))
    else:
        print("Selected skills for current context:")
        for s in selected:
            print(f"- {s}")


if __name__ == "__main__":
    main()
