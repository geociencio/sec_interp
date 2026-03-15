---
description: Procedure to end a work session, update logs, and archive results
agent: QA Engineer
skills: [qa-docker, commit-standards, agentic-memory, documentation-standards, changelog-generator]
validation: |
  - Verify that all logs are updated
  - Confirm that tests pass before closing
  - Validate that .agent/next_steps.md exists and has clear content
---

# Workflow: Close Session

This workflow closes the development cycle, converting technical work into historical memory for the next session.

### 1. Memory Update (Logs & Roadmap)

🤖 **Agent Action**: Validate that all critical files are updated.

*   **Session Topic**: Define a short name for the session (e.g., `stabilization_mocks`).
*   **Active Implementation Plan**: Update task status in the current plan.
*   **Task Persistence**:
    *   Ensure `.agent/task.md` reflects actual progress.
    *   If a major phase was completed, archive it in `.agent/history/tasks/`.
    *   **DO NOT DELETE** this file if the phase continues.
*   **`.agent/next_steps.md`**: **[CRITICAL]** Create or update this file with the "handover": what's missing, what errors are pending, and what command to resume.
*   **Next Steps Archiving**: Copy `.agent/next_steps.md` to `.agent/history/next_steps/next_steps_YYYY-MM-DD.md` to maintain a historical record.
*   **`docs/maintenance/session_YYYY-MM-DD_[TOPIC].md`**: **[MANDATORY]** Create this file with the session's technical summary.
*   **`docs/DEVELOPMENT_LOG.md`**: **[CRITICAL]** Add entry following the `documentation-standards` format.
*   **`docs/CHANGELOG.md`**: Record user-visible changes in `[Unreleased]` using the **changelog-generator** skill based on session commits. **(NOTA: La habilidad `changelog-generator` es interpretativa [prompt-based]. NO intentes ejecutar ningún script de Python. En su lugar, usa `git log` para leer los commits recientes de la sesión, analízalos mentalmente y usa la herramienta de edición de archivos para escribir directamente en CHANGELOG.md)**.

### 2. Final Verification (Safety Net)

🤖 **Agent Action**: Use **qa-docker** skill to validate stability before closing.

Run formatter, linter, and tests to ensure quality.
```bash
uv run ruff check --fix . && uv run ruff format . && uv run black .
```

*Option A (Docker - Recommended):*
// turbo
```bash
make docker-test
```

🤖 **Agent Action**: Verify that tests pass. Alert if there are failures.

*Option B (Local):*
```bash
PYTHONPATH=.. uv run python3 -m unittest discover tests
```

🤖 **Agent Action**: Validate Active Tasks.
Verify that `.agent/task.md` exists and is updated before committing.

### 3. Final Memory Synchronization (AI)

🤖 **Agent Action (Skill Sync)**: Run skill synchronization and update AGENTS.md.
// turbo
```bash
python3 scripts/skill_sync.py
```

🤖 **Agent Action (Learning)**: Explicitly identify the 3 most important technical lessons learned this session.
*   Update YAML entries in `AGENT_LESSONS.md`.
*   Update `agent_metrics.json` with the session summary.

🤖 **Agent Action**: Update AI_CONTEXT.md and validate that next_steps.md is clear.
Ensure the AI "Brain" is up to date with the final changes.
// turbo
```bash
uv run ai-ctx analyze --path . && cat .agent/next_steps.md
```

### 4. Local Commit

🤖 **Agent Action**: Use **commit-standards** skill to generate an appropriate message.

Save your progress.
```bash
git add .
git commit -m "chore(docs): close session [TOPIC]"
```

**Recommended Format**: `chore(docs): close session [descriptive_topic]`

*If the pre-commit hook persists in failing:*
1. Review the detected error messages.
2. Run `git add` again if there were automatic changes.
3. Repeat the commit.

### 5. Summary for the User

🤖 **Agent Action**: Generate a structured session summary.

Generate a final message listing:
*   Updated log files.
*   Test status (e.g., 535 tests OK).
*   Content of `.agent/next_steps.md`.
*   Suggestion for the next session (command `/start-session`).

## Expected Result
- Session memory persisted in Logs and `next_steps.md`.
- Repository clean and technically validated.
- Clear instructions for the assistant to resume the task without context loss.

**Philosophy**: A session doesn't end when the code works, but when the story is told.
