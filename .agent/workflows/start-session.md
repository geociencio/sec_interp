---
description: Standard and robust procedure for starting a "Local First" development session
agent: Senior Architect
skills: [qgis-core, qa-docker, agentic-memory]
runtimes: [antigravity, codewhale]
validation: |
  - Verify that all tests pass in Docker
  - Confirm that AI_CONTEXT.md is updated with recent metrics
  - Validate that there are no regressions in cyclomatic complexity
---

# Workflow: Start Session

This workflow optimizes the start of development by ensuring a synchronized, **contextualized**, and validated environment using Generation 6 semantic injection.

### 0. Semantic Skill Injection (Gen 6)
Optimize the current context by pre-loading only the necessary skills for the active tasks.
// turbo
```bash
uv run python scripts/context_selector.py --shell
```

🤖 **Agent Action**: Based on the output, prioritize the suggested skills and restrict loading of irrelevant modules to optimize token usage.

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
- Methods with high cyclomatic complexity (CC > 10)
- Architecture violations (UI in Core)

Review the following files in this order:
*   `.agent/next_steps.md`: **The Witness (Source of Truth)**. Defines the exact starting point and immediate goals.
*   `.agent/task.md`: **Active Board**. If it exists, it must align with `next_steps.md`. If not, create it based on `next_steps.md`.
*   `.agent/memory/AGENT_LESSONS.md`: **The Brain**. Error patterns to avoid and preferences.
*   `AI_CONTEXT.md`: Architectural context and long-term metrics.
*   `project_context.json`: Structured data on complexity and dependencies.
*   `docs/DEVELOPMENT_LOG.md`: See summary of the last session (reverse chronological order).

### 1.5 Metric Coherence Validation (CRITICAL)
Before starting work, verify that all .agent/ documentation files are consistent with ground-truth metrics. This catches stale references (test counts, quality scores, CC thresholds) that may have drifted between sessions.

// turbo
```bash
uv run python scripts/sync_metrics.py --quiet && uv run python scripts/validate_agent_metrics.py
```

🤖 **Agent Action**: If the validator reports inconsistencies, fix them before proceeding. Stale metrics in documentation lead to incorrect decisions.

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
🤖 **Agent Action**: Conclude the initialization with a YAML block showing current metrics AND the delta from the previous session:
```yaml
session_init: success
context_sync: complete
active_task: [task_name]
current_metrics:
  tests: 620
  quality_score: X
  cc_gate: PASS|FAIL
  i18n_gate: PASS|FAIL
delta_from_last:
  quality_score: +X.X
  tests: +N | -N | =
  issues: +N | -N | =
```

🤖 **Agent Action**: To compute the delta, compare `agent_metrics.json` → `last_session` values against the current `sync_metrics.py` output. If the delta shows a regression (negative quality, new CC failures), flag it immediately.

**Philosophy**: Start coding knowing *exactly* what happened yesterday and with specialized context loaded.
