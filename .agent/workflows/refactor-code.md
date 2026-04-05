---
description: Guided workflow for code refactoring with complexity validation
agent: Senior Architect
skills: [domain-logic, domain-logic]
validation: |
  - Verify that cyclomatic complexity decreased (CC < 15)
  - Confirm that tests still pass after refactoring
  - Validate that no architecture violations were introduced
---

# Workflow: Refactor Code

This workflow guides code refactoring following project standards and using specialized knowledge from skills.

## When to Use This Workflow

- When `qgis-analyzer` detects methods with CC > 15.
- When `AI_CONTEXT.md` identifies critical technical debt.
- Before adding new features to complex modules.

## Refactoring Steps

1. **Identify Refactoring Target**:
   // turbo
   ```bash
   uv run ai-ctx analyze .
   ```

   🤖 **Agent Action**: Analyze `analysis_results/PROJECT_SUMMARY.md` to identify hotspots (CC > 15) and technical debt.

2. **Quick Auto-Correction** (Optional):
   // turbo
   ```bash
   uv run qgis-analyzer fix --dry-run .
   ```
   🤖 **Agent Action**: If safe auto-corrections are available, apply them using `fix --apply` before proceeding with manual refactoring.

3. **Load Specialized Context**:

   🤖 **Agent Action**: Depending on the module, load the appropriate skill (**domain-logic**, **domain-logic**, or **ui-framework**).

4. **Apply Refactoring**:

   🤖 **Agent Action**: Apply SOLID principles and reduce cyclomatic complexity.

5. **Validate with Tests**:
   // turbo
   ```bash
   make docker-test
   ```

   🤖 **Agent Action**: Use **qa-standards** skill to ensure no regressions.

6. **Verify Quality Metrics**:
   // turbo
   ```bash
   uv run ai-ctx analyze .
   ```

   🤖 **Agent Action**: Confirm improvement in Quality Score and reduction in Cyclomatic Complexity (CC).

6.5 Complexity Audit (Auditor Reflection) 🤖
- **Agent Reflection**: Activate the **@auditor** role.
- **Verification**: Ensure the refactor didn't introduce new architecture violations or hide complexity in "wrapper" functions.
- **Pattern Match**: Confirm adherence to the "Extract-then-Compute" standard.

7. **Refactoring Commit**:
   Use `/create-commit` workflow with a structured technical message.

## Expected Result
- More maintainable, testable code with reduced cyclomatic complexity.
- Zero functional regressions confirmed by tests.
- Technical documentation (docstrings) updated.
