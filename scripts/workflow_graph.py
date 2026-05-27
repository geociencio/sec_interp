#!/usr/bin/env python3
"""
Workflow Dependency Graph & Broken Reference Detector (Gen 7)

Scans all .agent/workflows/*.md files and builds a directed graph of:
    workflow → script references (```bash blocks)
    workflow → skill references (YAML frontmatter + inline mentions)
    workflow → workflow references (/workflow-name patterns)

Validates that every referenced script and skill actually exists.
Useful for impact analysis when modifying scripts or skills.

Usage:
    uv run python scripts/workflow_graph.py [--json] [--validate]

Output:
    - Prints dependency matrix to stdout
    - With --validate: exits 1 if any broken references found
    - With --json: outputs structured JSON
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

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


def parse_yaml_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown."""
    result = {}
    if not content.startswith("---"):
        return result
    parts = content.split("---", 2)
    if len(parts) < 3:
        return result
    yaml_block = parts[1].strip()

    # Simple parser for flat key: value and key: [list]
    for line in yaml_block.splitlines():
        line = line.strip()
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                items = [v.strip().strip("'\"") for v in val[1:-1].split(",")]
                result[key] = items
            else:
                result[key] = val.strip("'\"")
    return result


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


def main():
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


if __name__ == "__main__":
    main()
