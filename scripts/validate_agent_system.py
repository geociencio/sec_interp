#!/usr/bin/env python3
"""Agent System Validator (Gen 8).

Validates the integrity of .agent/ files: YAML frontmatter, skill references,
script references, structural completeness, workflow dependency graph
(`--graph`), and skill-conflict detection (`--conflicts`).
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
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


def system_main():
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



# =====================================================================
# Workflow dependency graph  (was workflow_graph.py)
# =====================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENT_DIR = PROJECT_ROOT / ".agent"
WORKFLOW_DIR = AGENT_DIR / "workflows"
SKILLS_DIR = AGENT_DIR / "skills"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


@dataclass
class WorkflowNode:
    name: str
    file: str
    agent: str = ""
    skills: list[str] = field(default_factory=list)
    scripts: list[str] = field(default_factory=list)
    workflows: list[str] = field(default_factory=list)

@dataclass
class BrokenRef:
    source: str
    source_file: str
    ref_type: str
    ref_name: str

    def __str__(self):
        return f"  {self.source_file} [{self.ref_type}] → '{self.ref_name}' NOT FOUND"


def extract_scripts(content: str) -> list[str]:
    """Extract script references from bash code blocks."""
    scripts = []
    in_code_block = False
    for line in content.splitlines():
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            # Look for script paths
            for m in re.finditer(r"scripts/([\w_]+\.py)", line):
                scripts.append(m.group(1))
            # Look for uv run python scripts/ patterns
            for m in re.finditer(r"uv\s+run\s+python\s+scripts/([\w_]+\.py)", line):
                scripts.append(m.group(1))
    return list(set(scripts))


def extract_workflow_refs(content: str) -> list[str]:
    """Extract references to other workflows."""
    refs = []
    for m in re.finditer(r"/[\w-]+", content):
        ref = m.group(0)
        # Exclude common non-workflow patterns
        if ref in ("/app", "/tmp", "/usr", "/home"):
            continue
        refs.append(ref.lstrip("/"))
    return list(set(refs))


def get_workflow_name(filepath: Path) -> str:
    """Derive workflow name from filename."""
    return filepath.stem


def get_all_skills() -> set[str]:
    """List all available skill names."""
    skills = set()
    if SKILLS_DIR.exists():
        for d in SKILLS_DIR.iterdir():
            if d.is_dir() and (d / "SKILL.md").exists():
                skills.add(d.name)
    return skills


def get_all_scripts() -> set[str]:
    """List all available scripts."""
    scripts = set()
    if SCRIPTS_DIR.exists():
        for f in SCRIPTS_DIR.glob("*.py"):
            scripts.add(f.name)
    return scripts


def get_all_workflows() -> set[str]:
    """List all available workflow names."""
    workflows = set()
    if WORKFLOW_DIR.exists():
        for f in WORKFLOW_DIR.glob("*.md"):
            workflows.add(f.stem)
    return workflows


def scan_workflows() -> tuple[list[WorkflowNode], list[BrokenRef]]:
    """Scan all workflows and build dependency graph."""
    nodes: list[WorkflowNode] = []
    broken: list[BrokenRef] = []
    all_skills = get_all_skills()
    all_scripts = get_all_scripts()
    all_workflows = get_all_workflows()

    for filepath in sorted(WORKFLOW_DIR.glob("*.md")):
        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception:
            continue

        name = get_workflow_name(filepath)
        yaml_data = parse_yaml_frontmatter(content)

        agent = yaml_data.get("agent", "")
        skills = yaml_data.get("skills", [])

        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",")]

        scripts = extract_scripts(content)
        workflow_refs = extract_workflow_refs(content)
        workflow_refs = [w for w in workflow_refs if w != name and w in all_workflows]

        node = WorkflowNode(
            name=name,
            file=filepath.name,
            agent=agent,
            skills=skills,
            scripts=scripts,
            workflows=workflow_refs,
        )
        nodes.append(node)

        # Validate references
        for skill in skills:
            if skill not in all_skills:
                broken.append(BrokenRef(name, filepath.name, "skill", skill))

        for script in scripts:
            if script not in all_scripts:
                broken.append(BrokenRef(name, filepath.name, "script", script))

    return nodes, broken


def print_dependency_matrix(nodes: list[WorkflowNode]):
    """Print a tabular dependency matrix."""
    print("\n## Workflow → Script Dependencies\n")
    print("| Workflow | Scripts |")
    print("| :--- | :--- |")
    for node in nodes:
        scripts = ", ".join(f"`{s}`" for s in sorted(node.scripts)) if node.scripts else "—"
        print(f"| `/{node.name}` | {scripts} |")

    print("\n## Workflow → Skill Dependencies\n")
    print("| Workflow | Agent | Skills |")
    print("| :--- | :--- | :--- |")
    for node in nodes:
        agent = node.agent if node.agent else "—"
        skills = ", ".join(node.skills) if node.skills else "—"
        print(f"| `/{node.name}` | {agent} | {skills} |")

    print("\n## Workflow → Workflow Dependencies\n")
    print("| Workflow | References |")
    print("| :--- | :--- |")
    for node in nodes:
        refs = ", ".join(f"`/{w}`" for w in sorted(node.workflows)) if node.workflows else "—"
        print(f"| `/{node.name}` | {refs} |")

    print("\n## Skill Usage Frequency\n")
    skill_count: dict[str, int] = {}
    for node in nodes:
        for s in node.skills:
            skill_count[s] = skill_count.get(s, 0) + 1
    print("| Skill | Used by (workflows) |")
    print("| :--- | :--- |")
    for skill, count in sorted(skill_count.items(), key=lambda x: -x[1]):
        print(f"| `{skill}` | {count} |")


def print_summary(nodes: list[WorkflowNode], broken: list[BrokenRef]):
    """Print a compact summary."""
    all_skills = get_all_skills()
    all_scripts = get_all_scripts()

    # Find unused skills
    used_skills = set()
    for node in nodes:
        used_skills.update(node.skills)
    unused_skills = all_skills - used_skills

    # Find unused scripts (scripts not referenced by any workflow)
    used_scripts = set()
    for node in nodes:
        used_scripts.update(node.scripts)
    unused_scripts = all_scripts - used_scripts

    print(f"\n## Summary")
    print(f"- **Workflows**: {len(nodes)}")
    print(f"- **Skills**: {len(all_skills)} ({len(all_skills) - len(unused_skills)} referenced, "
          f"{len(unused_skills)} unreferenced)")
    if unused_skills:
        print(f"  - Unreferenced: {', '.join(sorted(unused_skills))}")
    print(f"- **Scripts**: {len(all_scripts)} ({len(all_scripts) - len(unused_scripts)} referenced, "
          f"{len(unused_scripts)} unreferenced)")
    if broken:
        print(f"- **Broken references**: {len(broken)}")


def graph_main():
    validate_only = "--validate" in sys.argv
    json_output = "--json" in sys.argv

    nodes, broken = scan_workflows()

    if json_output:
        output = {
            "workflows": [
                {
                    "name": n.name,
                    "file": n.file,
                    "agent": n.agent,
                    "skills": n.skills,
                    "scripts": n.scripts,
                    "references": n.workflows,
                }
                for n in nodes
            ],
            "broken_refs": [
                {"source": b.source, "source_file": b.source_file,
                 "ref_type": b.ref_type, "ref_name": b.ref_name}
                for b in broken
            ],
        }
        print(json.dumps(output, indent=2))
        sys.exit(1 if broken else 0)

    print("# Workflow Dependency Graph\n")

    if broken:
        print("## ❌ Broken References\n")
        for b in broken:
            print(str(b))

    print_dependency_matrix(nodes)
    print_summary(nodes, broken)

    if validate_only:
        if broken:
            print("\n❌ Validation FAILED: broken references found.")
            sys.exit(1)
        else:
            print("\n✅ Validation PASSED: all references valid.")
            sys.exit(0)




# =====================================================================
# Cross-skill conflict detector  (was check_skill_conflicts.py)
# =====================================================================

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


def conflicts_main() -> None:
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




def main() -> None:
    """Dispatch to the requested system-validation subcommand."""
    argv = sys.argv[1:]
    if "--graph" in argv:
        graph_main()
    elif "--conflicts" in argv:
        conflicts_main()
    else:
        system_main()


if __name__ == "__main__":
    main()
