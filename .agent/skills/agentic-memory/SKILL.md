---
name: agentic-memory
description: This skill allows the agent to manage its own semantic memory, extracting lessons, patterns, and user preferences to improve long-term effectiveness.
trigger: at the end of each significant session, when detecting repetitive error patterns or user preferences.
---

# Skill: Agentic Memory (Brain)

This skill enables the agent to manage its own semantic memory by extracting lessons, patterns, and user preferences to enhance long-term effectiveness.

## Extraction Guidelines

The agent must actively look for the following elements during interaction:

1.  **Error Patterns**: Solutions to bugs that took more than 3 attempts or required deep investigation.
2.  **Implicit Preferences**: Style or architectural decisions that the user repeatedly approves.
3.  **Technical Hotspots**: Areas of code that are difficult to test or refactor.
4.  **Design Decisions**: Justifications for why one implementation was chosen over another.

## Update Protocol (`AGENT_LESSONS.md`)

At the end of each significant session, the agent must:

1.  **Verify Path**: Ensure you are NOT in `antigravity-framerepo/` or `scaffold/`. All persistence must happen in the project root's `.agent/` directory.
2.  **Target Metrics**: Update `.agent/memory/agent_metrics.json` (NEVER a scaffold file).
3.  **Synthesize**: Summarize findings in entries of at most 3 lines in `AGENT_LESSONS.md`.
4.  **Categorize**: Use tags such as `[TECHNICAL]`, `[USER_PREFERENCE]`, `[ARCHITECTURE]`.
5.  **Structure**: Maintain a YAML-friendly format for future RAG integrations.

## Structured Entry Example

```yaml
- date: 2026-02-05
  category: TECHNICAL
  topic: QgsGeometry Mocking
  lesson: "The 'is3D' method fails in simple mocks; requires QGIS context injection."
  action: "Use QgsGeometry.fromWkt() whenever possible to avoid manual mocks."
```

## Pre-flight Self-Audit

Before concluding any task or workflow, the agent must perform a self-audit:
1. **Lessons Check**: "Have I applied relevant lessons from `AGENT_LESSONS.md`?"
2. **Context Integrity**: "Does my solution follow the project's architectural standards (e.g., Core/GUI separation)?"
3. **Structured Output**: "Does my final response provide a clear, structured summary of what was done and tested?"

---
*Skill generated for the evolution of the SecInterp Agent Architecture.*
