---
description: How to commit changes cleanly (handling hooks)
agent: QA Engineer
skills: [qa-standards, commit-standards, agentic-memory]
validation: |
  - Verify that ruff and black pass without errors
  - Confirm that ai-ctx analyze runs successfully
  - Validate that the commit message follows Conventional Commits
---

# Workflow: Create Commit

This workflow describes the process for committing changes, ensuring code quality standards are met without getting blocked by pre-commit hook conflicts.

### 1. Preparation and Cleanup (Automatic)
Ensures that the code complies with ruff and black standards to avoid hook failures.
// turbo
```bash
uv run ruff check --fix .
uv run ruff format .
uv run black .
```

### 2. Stage Changes
Add the files you wish to commit.
```bash
git add .
```

### 3. Quality Synchronization (Guardian)
Record the impact of changes in the Project Brain before saving.
// turbo
```bash
uv run ai-ctx analyze --path .
```

🤖 **Agent Action**: Analyze quality metrics and alert if:
- Cyclomatic complexity increased significantly
- Docstring coverage decreased
- New QGIS compliance violations were detected

### 4. Message Proposal (AI-Assisted)

🤖 **Agent Action**: Use **commit-standards** skill to:
- Analyze staged changes (`git diff --cached`)
- Generate 2-3 message options following Conventional Commits
- Validate format: correct type, appropriate scope, English, imperative
- Suggest scope based on modified files (core, gui, export, etc.)
- Alert if there are breaking changes requiring `!` or footer

### 4.5 Quality Reflection (Auditor Check) 🤖
- **Agent Reflection**: Activate the **@auditor** role.
- **Diff Analysis**: Contrast the generated commit message with `git diff --cached`.
- **Validation**: Ensure no "leakage" of temporary debug code (print, TODOs, commented-out logic).
- **Consolidation**: Verify that the commit represents a "clean unit of value."

### 5. Commit
Execute the commit with the approved message.
```bash
git commit -m "type(scope): description" -m "detailed body"
```

*If the pre-commit hook persists in failing:*
1. Review the detected error messages.
2. Run `git add` again if there were automatic changes.
3. Repeat the commit.

### 6. Structured Completion
🤖 **Agent Action**: Provide a final summary in the following YAML format:
```yaml
commit_status: success
files_changed: [list]
conventional_type: fix | feat | docs | style | etc
tests_verified: true/false
```

**Philosophy**: Each commit is a clean unit of value, documented and metrically validated.
