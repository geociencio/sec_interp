---
description: Standard and robust procedure for starting a "Local First" development session
agent: Senior Architect
skills: [qgis-core, qa-docker, agentic-memory]
validation: |
  - Verify that all tests pass in Docker
  - Confirm that AI_CONTEXT.md is updated with recent metrics
  - Validate that there are no regressions in cyclomatic complexity
---

# Workflow: Start Session

This workflow optimizes the start of development by ensuring a synchronized, **contextualized**, and validated environment.

### 1. Context Tuning (CRITICAL)
Updates and reads the context to understand "where we left off".
// turbo
```bash
uv run ai-ctx analyze --path . && cat .agent/next_steps.md && cat .agent/memory/AGENT_LESSONS.md
```

🤖 **Agent Action**: Validate Active Tasks.

*   **Task Management**:
    *   Verify if `.agent/task.md` exists.
    *   If it exists: Show the content ("Current Status").
    *   If it DOES NOT exist: Create it based on the active Implementation Plan or `next_steps.md`.

🤖 **Agent Action**: Review `AI_CONTEXT.md` and `project_context.json` using **qgis-core** skill to identify:
- Critical technical debt related to QGIS API
- Methods with high cyclomatic complexity (CC > 15)
- Architecture violations (UI in Core)

Review the following files in this order:
*   `.agent/next_steps.md`: **The Witness (Source of Truth)**. Defines the exact starting point and immediate goals.
*   `.agent/task.md`: **Active Board**. If it exists, it must align with `next_steps.md`. If not, create it based on `next_steps.md`.
*   `.agent/memory/AGENT_LESSONS.md`: **The Brain**. Error patterns to avoid and preferences.
*   `AI_CONTEXT.md`: Architectural context and long-term metrics.
*   `project_context.json`: Structured data on complexity and dependencies.
*   `docs/DEVELOPMENT_LOG.md`: See summary of the last session (reverse chronological order).

### 2. Quick Quality Scan
Perform a quick scan of the project status to identify critical technical debt.
```bash
uv run qgis-analyzer summary
```

### 3. Integrity Validation (Tests)
Ensure updated dependencies.
// turbo
```bash
uv sync
```

🤖 **Agent Action**: Verify that there are no dependency conflicts related to PyQGIS.

### 4. Status Verification (Sanity Check)
Confirm that the system is stable ("in green"). All tests must pass.

*Option A (Docker - Recommended):*
// turbo
```bash
make docker-test
```

🤖 **Agent Action**: Use **qa-docker** skill to interpret test failures and identify regressions.

*Option B (Local):*
```bash
env PYTHONPATH=.. uv run python3 -m unittest discover tests
```

## Expected Result
- Synchronized and validated environment (All tests OK).
- Clear mental map of pending tasks in `next_steps.md`.
- Agent operating with the correct profiles and skills loaded.

## Structured Session Status
🤖 **Agent Action**: Conclude the initialization with:
```yaml
session_init: success
context_sync: complete
active_task: [task_name]
current_metrics:
  tests: 535
  quality_score: X
```

**Philosophy**: Start coding knowing *exactly* what happened yesterday and with specialized context loaded.
