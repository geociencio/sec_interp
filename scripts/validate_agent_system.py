#!/usr/bin/env python3
"""Agent System Structure Validator (Gen 7).

Validates the integrity of .agent/ files: YAML frontmatter, skill references,
script references, and structural completeness.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass as dc
from dataclasses import field as dc_field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENT_DIR = PROJECT_ROOT / ".agent"
SKILLS_DIR = AGENT_DIR / "skills"
WORKFLOW_DIR = AGENT_DIR / "workflows"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

REQUIRED_SKILL_FIELDS = ["name", "description", "trigger"]
REQUIRED_WORKFLOW_FIELDS = ["description", "agent", "skills"]


@dc
class ValidationIssue:
    """A single validation issue found in an .agent/ file."""

    file: str
    severity: str  # ERROR, WARNING
    message: str

    def __str__(self) -> str:
        """Format issue for display."""
        return f"  [{self.severity}] {self.file}: {self.message}"


@dc
class SystemReport:
    """Aggregate report of all validation issues found."""

    issues: list[ValidationIssue] = dc_field(default_factory=list)
    skills_checked: int = 0
    workflows_checked: int = 0

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "ERROR" for i in self.issues)


def parse_yaml_frontmatter(content: str) -> dict:
    result = {}
    if not content.startswith("---"):
        return result
    parts = content.split("---", 2)
    if len(parts) < 3:
        return result
    for line in parts[1].strip().splitlines():
        line = line.strip()
        if ":" in line:
            key, _, val = line.partition(":")
            key, val = key.strip(), val.strip()
            if val.startswith("[") and val.endswith("]"):
                result[key] = [v.strip().strip("'\"") for v in val[1:-1].split(",")]
            else:
                result[key] = val.strip("'\"")
    return result


def validate_skills() -> tuple[list[ValidationIssue], set[str]]:
    issues = []
    available_skills = set()

    if not SKILLS_DIR.exists():
        return issues, available_skills

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            issues.append(ValidationIssue(
                str(skill_dir.relative_to(AGENT_DIR)),
                "ERROR",
                f"Missing SKILL.md in {skill_dir.name}",
            ))
            continue

        content = skill_file.read_text(encoding="utf-8")
        yaml_data = parse_yaml_frontmatter(content)

        if not yaml_data:
            issues.append(ValidationIssue(
                str(skill_file.relative_to(AGENT_DIR)),
                "ERROR",
                "Missing YAML frontmatter",
            ))
            continue

        name = yaml_data.get("name", "")
        if not name:
            issues.append(ValidationIssue(
                str(skill_file.relative_to(AGENT_DIR)),
                "ERROR",
                "Missing 'name' field",
            ))
        else:
            available_skills.add(name)

        for field in REQUIRED_SKILL_FIELDS:
            if field not in yaml_data:
                issues.append(ValidationIssue(
                    str(skill_file.relative_to(AGENT_DIR)),
                    "WARNING" if field == "trigger" else "ERROR",
                    f"Missing '{field}' field",
                ))

        # Check minimum content
        if len(content) < 100:
            issues.append(ValidationIssue(
                str(skill_file.relative_to(AGENT_DIR)),
                "WARNING",
                f"Skill content is very short ({len(content)} chars)",
            ))

    return issues, available_skills


def validate_workflows(available_skills: set[str], available_scripts: set[str]) -> list[ValidationIssue]:
    issues = []

    if not WORKFLOW_DIR.exists():
        return issues

    for wf_file in sorted(WORKFLOW_DIR.glob("*.md")):
        if wf_file.name == "index.md":
            continue  # index.md is a reference doc, not a workflow
        content = wf_file.read_text(encoding="utf-8")
        yaml_data = parse_yaml_frontmatter(content)

        if not yaml_data:
            issues.append(ValidationIssue(
                str(wf_file.relative_to(AGENT_DIR)),
                "ERROR",
                "Missing YAML frontmatter",
            ))
            continue

        for field in REQUIRED_WORKFLOW_FIELDS:
            if field not in yaml_data:
                issues.append(ValidationIssue(
                    str(wf_file.relative_to(AGENT_DIR)),
                    "ERROR",
                    f"Missing '{field}' field",
                ))

        # Validate skill references
        skills = yaml_data.get("skills", [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",")]
        for skill in skills:
            if skill and skill not in available_skills:
                issues.append(ValidationIssue(
                    str(wf_file.relative_to(AGENT_DIR)),
                    "ERROR",
                    f"References unknown skill: '{skill}'",
                ))

        # Validate script references in bash blocks
        bash_blocks = re.findall(r"```bash\n(.*?)\n```", content, re.DOTALL)
        for block in bash_blocks:
            scripts = re.findall(r"scripts/([\w_]+\.py)", block)
            for script in scripts:
                if script not in available_scripts:
                    issues.append(ValidationIssue(
                        str(wf_file.relative_to(AGENT_DIR)),
                        "ERROR",
                        f"References unknown script: 'scripts/{script}'",
                    ))

    return issues


def main():
    quiet = "--quiet" in sys.argv

    available_scripts = {f.name for f in SCRIPTS_DIR.glob("*.py")} if SCRIPTS_DIR.exists() else set()

    skill_issues, available_skills = validate_skills()
    workflow_issues = validate_workflows(available_skills, available_scripts)

    all_issues = skill_issues + workflow_issues
    skills_count = len(list(SKILLS_DIR.iterdir())) if SKILLS_DIR.exists() else 0
    workflows_count = len(list(WORKFLOW_DIR.glob("*.md"))) if WORKFLOW_DIR.exists() else 0

    if not quiet:
        print(f"🔍 Validated {skills_count} skills, {workflows_count} workflows\n")

    if all_issues:
        errors = sum(1 for i in all_issues if i.severity == "ERROR")
        warnings = sum(1 for i in all_issues if i.severity == "WARNING")
        if not quiet:
            print(f"❌ {errors} error(s), {warnings} warning(s):\n")
            for issue in all_issues:
                print(str(issue))
        sys.exit(1)

    if not quiet:
        print("✅ All .agent/ files pass system validation")
    sys.exit(0)


if __name__ == "__main__":
    main()
