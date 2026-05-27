#!/usr/bin/env python3
"""Runtime-Agnostic Workflow Executor (Gen 7).

Reads a .agent/workflows/*.md file and translates its steps into
runtime-appropriate instructions for antigravity or codewhale runtimes.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_DIR = PROJECT_ROOT / ".agent" / "workflows"

RUNTIME_TOOLS = {
    "codewhale": {
        "bash": "exec_shell",
        "read": "read_file",
        "write": "write_file",
        "agent_action": "AI reasoning step (no tool call needed)",
    },
    "antigravity": {
        "bash": "// turbo bash block",
        "read": "read_file",
        "write": "write_file",
        "agent_action": "AI reasoning step (Gemini-native)",
    },
}


def detect_runtime() -> str:
    """Auto-detect current runtime from environment markers."""
    # Check for CodeWhale-specific markers
    codewhale_markers = [
        PROJECT_ROOT / ".codewhale",
    ]
    for marker in codewhale_markers:
        if marker.exists():
            return "codewhale"
    return "antigravity"


def parse_yaml_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter."""
    result = {}
    if not content.startswith("---"):
        return result
    parts = content.split("---", 2)
    if len(parts) < 3:
        return result
    yaml_block = parts[1].strip()
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


def translate_workflow(workflow_name: str, runtime: str) -> str:
    """Read a workflow and translate it to runtime-specific instructions."""
    filepath = WORKFLOW_DIR / f"{workflow_name}.md"
    if not filepath.exists():
        return f"❌ Workflow not found: {workflow_name}"

    content = filepath.read_text(encoding="utf-8")
    yaml_data = parse_yaml_frontmatter(content)
    runtimes_supported = yaml_data.get("runtimes", ["antigravity"])
    tools = RUNTIME_TOOLS.get(runtime, RUNTIME_TOOLS["antigravity"])

    lines = []
    lines.append(f"# /{workflow_name} — {yaml_data.get('description', 'No description')}")
    lines.append(f"**Runtime**: {runtime}  |  **Agent**: {yaml_data.get('agent', 'N/A')}")
    lines.append(f"**Skills**: {', '.join(yaml_data.get('skills', [])) or 'N/A'}")

    if runtime not in runtimes_supported:
        lines.append(f"\n⚠️  This workflow has no explicit `runtimes:` field for `{runtime}`.")
        lines.append("   Execution may require manual adaptation.\n")

    lines.append("\n## Steps\n")

    # Parse body for steps
    body = content.split("---", 2)[-1] if "---" in content else content
    step_num = 0
    for line in body.splitlines():
        stripped = line.strip()

        # Detect section headers (###)
        if stripped.startswith("###"):
            step_num += 1
            title = stripped.lstrip("#").strip()
            lines.append(f"### Step {step_num}: {title}")

        # Detect turbo/bash blocks
        elif stripped.startswith("// turbo") and "```" not in stripped:
            lines.append(f"   [{tools['bash']}] (turbo)")

        elif stripped.startswith("```bash"):
            lines.append(f"   [{tools['bash']}]")

        elif stripped.startswith("```") and "bash" not in stripped:
            pass  # skip non-bash blocks

        elif stripped.startswith("🤖 **Agent Action"):
            action = stripped.replace("🤖", "").replace("**", "").strip()
            lines.append(f"   [{tools['agent_action']}] {action}")

        elif "🤖" in stripped:
            pass  # skip inline agent actions in step descriptions

    return "\n".join(lines)


def list_workflows():
    """List all workflows with their runtime support."""
    print("| Workflow | Runtimes | Agent | Skills |")
    print("| :--- | :--- | :--- | :--- |")
    for f in sorted(WORKFLOW_DIR.glob("*.md")):
        try:
            content = f.read_text(encoding="utf-8")
        except Exception:
            continue
        yaml_data = parse_yaml_frontmatter(content)
        name = f.stem
        runtimes = yaml_data.get("runtimes", ["antigravity"])
        agent = yaml_data.get("agent", "—")
        skills = ", ".join(yaml_data.get("skills", [])) or "—"
        runtime_str = ", ".join(runtimes)
        print(f"| `/{name}` | {runtime_str} | {agent} | {skills} |")


def main():
    if "--list" in sys.argv:
        list_workflows()
        return

    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("Usage: uv run python scripts/workflow_executor.py <workflow-name> [--runtime codewhale|antigravity]")
        print("       uv run python scripts/workflow_executor.py --list")
        sys.exit(0)

    workflow_name = sys.argv[1]

    runtime = "antigravity"
    for i, arg in enumerate(sys.argv):
        if arg == "--runtime" and i + 1 < len(sys.argv):
            runtime = sys.argv[i + 1]
            break
    if runtime not in ("antigravity", "codewhale"):
        runtime = detect_runtime()

    output = translate_workflow(workflow_name, runtime)
    print(output)


if __name__ == "__main__":
    main()
