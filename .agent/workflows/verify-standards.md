---
description: Audits the consistency of the agentic system (Skills and Workflows) against the master standard.
agent: Senior Architect
skills: [coding-standards, commit-standards, documentation-standards]
runtimes: [antigravity, codewhale]
validation:
  - Do all Skills have a Quality Checklist?
  - Is all Skill and Workflow documentation in English?
  - Do Workflows have Expected Result sections?
---

# Workflow: Verify Agentic Standards

This flow ensures that the AI "brain" stays organized, readable, and under the quality standards defined in technical research.

## 1. Skills Audit

Review each file in `.agent/skills/` looking for:
1.  **YAML**: Presence of `name` and `description`.
2.  **Language**: Main content and descriptions in English.
3.  **Structure**: Sections: When to use, Degree of Freedom, Workflow, and Instructions.

## 2. Workflow Audit

Review each file in `.agent/workflows/` looking for:
1.  **YAML**: Clear description of the objective.
2.  **Structure**: Numbered steps and use of `// turbo` where applicable.
3.  **Expected Result**: Presence of success metrics at the end of the document.

## 3. Structural Validation (Gen 7)

Verify the integrity of the `.agent/` system: YAML frontmatter, skill/script references, and workflow dependency graph.

// turbo
```bash
uv run python scripts/validate_agent_system.py
uv run python scripts/workflow_graph.py --validate
uv run python scripts/check_skill_conflicts.py
```

🤖 **Agent Action**: `workflow_graph.py --validate` exits with code 1 if any workflow references a missing skill or script. `check_skill_conflicts.py` reports skills that share the same trigger (potential contradictory guidance). Fix any broken reference or conflict before proceeding.

## Expected Result
- Detailed report of deviations from the standard.
- Immediate correction proposal for obsolete components.
- Validated `.agent/` structure (frontmatter + references) with no broken dependencies.
- Agent configuration maintained in a single source of truth (root `AGENTS.md`).
