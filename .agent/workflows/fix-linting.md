---
description: Workflow to automatically correct linting and formatting issues
agent: QA Engineer
skills: [coding-standards, qa-standards]
validation: |
  - Verify that ruff and black pass without errors
  - Confirm that imports are sorted
---

# Workflow: Fix Linting

This workflow automates the correction of style and code quality issues reported by static tools.

### 1. Initial Diagnosis

🤖 **Agent Action**: Run analysis to identify issues.

```bash
uv run ruff check .
```

### 2. Automatic Correction (Auto-Fix)

🤖 **Agent Action**: Apply safe automatic corrections.

```bash
# 1. Sort imports
uv run ruff check --select I --fix .

# 2. Format code (Black style via Ruff)
uv run ruff format .

# 3. Apply general fixes (F401, E711, etc.)
uv run ruff check --fix .
```

### 3. QGIS-Specific Fixes

🤖 **Agent Action**: Use automatic fix for QGIS-specific issues (imports, signals, logging).

```bash
uv run qgis-analyzer fix . --apply --auto-approve
```

### 4. Assisted Manual Correction

For errors that CANNOT be corrected automatically (e.g., `F821 Undefined name`), the agent must:
1.  Identify the file and line.
2.  Apply a specific patch or manual edit.
3.  Verify that the correction does not break the logic.

### 5. Final Validation

```bash
uv run ruff check . && uv run ruff format --check .
```

### 6. Cleanup Commit

```bash
git add .
git commit -m "style: apply automated linting fixes"
```
