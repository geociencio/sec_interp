---
description: Audits the consistency of the agentic system (Skills and Workflows) against the master standard.
agent: Senior Architect
skills: [domain-logic, commit-standards, documentation-standards]
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

## 3. Automatic Synchronization

Run synchronization to ensure `AGENTS.md` is up to date.
// turbo
```bash
python3 scripts/skill_sync.py
```

## Expected Result
- Detailed report of deviations from the standard.
- Immediate correction proposal for obsolete components.
- Guaranteed synchronization of the skills matrix.
