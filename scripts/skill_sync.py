#!/usr/bin/env python3
import os
import re
import yaml
from pathlib import Path


def sync_skills():
    base_path = Path(__file__).parent.parent
    skills_dir = base_path / ".agent" / "skills"
    agents_file = base_path / ".agent" / "AGENTS.md"

    if not agents_file.exists():
        print(f"Error: {agents_file} not found.")
        return

    skills = []
    print(f"Scanning skills in {skills_dir}...")

    for skill_path in skills_dir.glob("**/SKILL.md"):
        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Extract YAML frontmatter
            match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            if match:
                try:
                    metadata = yaml.safe_load(match.group(1))
                    metadata["path"] = str(skill_path.relative_to(base_path))
                    skills.append(metadata)
                except Exception as e:
                    print(f"Error parsing metadata for {skill_path}: {e}")

    if not skills:
        print("No skills found.")
        return

    # Sort skills by name
    skills.sort(key=lambda x: x.get("name", ""))

    # Prepare the Auto-invoke table
    table_lines = [
        "| Skill | Description | Trigger (Auto-invoke) |",
        "| :--- | :--- | :--- |",
    ]
    for s in skills:
        name = s.get("name", "N/A")
        desc = s.get("description", "N/A")
        trigger = s.get("trigger", "N/A")
        path = s.get("path", "")
        table_lines.append(
            f"| [{name}](file://{base_path}/{path}) | {desc} | {trigger} |"
        )

    table_content = "\n".join(table_lines)

    # Read AGENTS.md and replace the Auto-invoke section
    with open(agents_file, "r", encoding="utf-8") as f:
        agents_content = f.read()

    # Define the markers
    start_marker = "<!-- SKILLS_TABLE_START -->"
    end_marker = "<!-- SKILLS_TABLE_END -->"

    pattern = re.compile(
        f"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL
    )

    if pattern.search(agents_content):
        new_content = pattern.sub(
            f"{start_marker}\n{table_content}\n{end_marker}", agents_content
        )
    else:
        # If not found, append at the end of the Skills section or file
        new_content = (
            agents_content
            + f"\n\n## 🛠️ Auto-invoke Skills Matrix\n{start_marker}\n{table_content}\n{end_marker}\n"
        )

    with open(agents_file, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✅ Successfully synchronized {len(skills)} skills into AGENTS.md")


def sync_workflows():
    """Sync workflows metadata into AGENTS.md workflow table."""
    base_path = Path(__file__).parent.parent
    workflows_dir = base_path / ".agent" / "workflows"
    agents_file = base_path / ".agent" / "AGENTS.md"

    if not workflows_dir.exists():
        print(f"Error: {workflows_dir} not found.")
        return

    workflows = []
    print(f"Scanning workflows in {workflows_dir}...")

    for workflow_path in workflows_dir.glob("*.md"):
        with open(workflow_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Extract YAML frontmatter
            match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            if match:
                try:
                    metadata = yaml.safe_load(match.group(1))
                    metadata["name"] = workflow_path.stem
                    metadata["path"] = str(workflow_path.relative_to(base_path))

                    # Validate required fields
                    if "agent" in metadata and "skills" in metadata:
                        workflows.append(metadata)
                    else:
                        print(
                            f"⚠️  Skipping {workflow_path.name}: missing 'agent' or 'skills' metadata"
                        )
                except Exception as e:
                    print(f"Error parsing metadata for {workflow_path}: {e}")

    if not workflows:
        print("No workflows with metadata found.")
        return

    # Validate that all referenced skills exist
    skills_dir = base_path / ".agent" / "skills"
    existing_skills = {p.parent.name for p in skills_dir.glob("**/SKILL.md")}

    for wf in workflows:
        for skill in wf.get("skills", []):
            if skill not in existing_skills:
                print(
                    f"⚠️  Warning: Workflow '{wf['name']}' references non-existent skill '{skill}'"
                )

    print(f"✅ Validated {len(workflows)} workflows")
    print(f"   All referenced skills exist: {existing_skills}")


if __name__ == "__main__":
    print("🔄 Syncing Skills and Workflows...\n")
    sync_skills()
    print()
    sync_workflows()
    print("\n✨ Synchronization complete!")
