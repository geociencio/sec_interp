#!/usr/bin/env python3
"""Cross-Skill Conflict Detector (Gen 7).

Scans `.agent/skills/*/SKILL.md` frontmatter and reports potential conflicts
or overlaps that could confuse the agent when multiple skills claim the same
trigger. Complements `validate_agent_system.py` (structure) with semantic
overlap detection.

Usage:
    uv run python scripts/check_skill_conflicts.py [--quiet]

Exit code: 0 if no conflicts, 1 if any potential conflict is detected.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / ".agent" / "skills"

# A workflow referenced by more than this many skill triggers is a potential
# overlap (too many skills competing for the same trigger).
TRIGGER_OVERLAP_THRESHOLD = 3

WORKFLOW_REF = re.compile(r"/([a-z][a-z0-9-]+)")


def _parse_frontmatter(content: str) -> dict:
    """Extract frontmatter fields from a SKILL.md file."""
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    fields = {}
    for line in parts[1].splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fields[key.strip()] = val.strip().strip("'\"")
    return fields


def load_skills(skills_dir: Path) -> list[dict]:
    """Load all skills with their frontmatter metadata."""
    skills = []
    for path in sorted(skills_dir.glob("*/SKILL.md")):
        content = path.read_text(encoding="utf-8")
        meta = _parse_frontmatter(content)
        meta["path"] = str(path.relative_to(PROJECT_ROOT))
        meta["dir"] = path.parent.name
        skills.append(meta)
    return skills


def check_completeness(skills: list[dict]) -> list[str]:
    """Report skills missing required frontmatter fields."""
    issues = []
    required = ("name", "description", "trigger")
    for skill in skills:
        for field in required:
            if not skill.get(field):
                issues.append(
                    f"{skill.get('dir', '?')}: missing '{field}' field in SKILL.md"
                )
    return issues


def check_duplicates(skills: list[dict]) -> list[str]:
    """Report duplicate skill names or copy-pasted descriptions."""
    issues = []
    names = Counter(s.get("name") for s in skills if s.get("name"))
    for name, count in names.items():
        if count > 1:
            issues.append(f"duplicate skill name '{name}' ({count} times)")

    descriptions = Counter(s.get("description") for s in skills if s.get("description"))
    for desc, count in descriptions.items():
        if count > 1:
            issues.append(f"duplicate description shared by {count} skills: {desc[:60]}...")
    return issues


def check_trigger_overlap(skills: list[dict]) -> list[str]:
    """Report workflows referenced by an excessive number of skill triggers."""
    issues = []
    workflow_skills: dict[str, list[str]] = {}
    for skill in skills:
        trigger = skill.get("trigger", "") or ""
        for match in WORKFLOW_REF.findall(trigger):
            workflow_skills.setdefault(match, []).append(skill.get("name", "?"))
    for workflow, names in sorted(workflow_skills.items()):
        if len(names) > TRIGGER_OVERLAP_THRESHOLD:
            issues.append(
                f"workflow '/{workflow}' triggers {len(names)} skills "
                f"({', '.join(names)}) — potential overlap"
            )
    return issues


def find_conflicts(skills: list[dict]) -> list[str]:
    """Aggregate all conflict detections into a single issue list."""
    issues = []
    issues.extend(check_completeness(skills))
    issues.extend(check_duplicates(skills))
    issues.extend(check_trigger_overlap(skills))
    return issues


def main() -> None:
    quiet = "--quiet" in sys.argv

    if not SKILLS_DIR.exists():
        print(f"❌ {SKILLS_DIR} not found", file=sys.stderr)
        sys.exit(1)

    skills = load_skills(SKILLS_DIR)
    if not quiet:
        print(f"🔍 Scanned {len(skills)} skills for conflicts")

    issues = find_conflicts(skills)

    if not issues:
        if not quiet:
            print("✅ No skill conflicts or overlaps detected.")
        sys.exit(0)

    print(f"⚠️  Found {len(issues)} potential skill conflict(s):")
    for issue in issues:
        print(f"  - {issue}")
    sys.exit(1)


if __name__ == "__main__":
    main()
