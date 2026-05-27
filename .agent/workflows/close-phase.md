---
description: Formal procedure for closing a major development phase
agent: Senior Architect
skills: [qgis-core, qa-docker, changelog-generator]
validation: |
  - Verify that 620 tests pass in Docker
  - Confirm that closure document is complete
  - Validate that metrics are documented
  - Verify that technical debt is classified
---

# Workflow: Phase Closure

This workflow documents the complete process for formally closing a major development phase (e.g., v3.2.0 → v3.3.0).

## 1. Comprehensive Accomplishments Review

🤖 **Agent Action**: Use **qgis-core** skill to validate compliance with QGIS standards.

Analyze and document all goals completed during the phase:

- **Infrastructure**: New tools, Docker, CI/CD, etc.
- **Functionalities**: Features implemented and validated.
- **Quality**: Improvements in tests, code metrics, refactorings.
- **Documentation**: Guides, architecture, ADRs created or updated.

## 2. Technical Debt Identification

Classify accumulated technical debt into three levels:

- **🔴 Critical**: Blocks functionality or affects stability (must be resolved before release).
- **🟡 Moderate**: Important but not blocking (priority for the next phase).
- **🟢 Minor**: Cosmetic or maintainability improvements (backlog).

## 3. Metrics and Final Verification

🤖 **Agent Action**: Analyze metrics and compare with the previous phase.

Run the full project analysis and document:

// turbo
```bash
uv run ai-ctx analyze --path .
```

Verify that all tests pass:

// turbo
```bash
make docker-test
```

🤖 **Agent Action**: Use **qa-docker** skill to validate that 620 tests pass.

Document key metrics:
- Total tests and status (620 tests)
- Pylint/Ruff score
- Maximum cyclomatic complexity
- Type hint coverage
- Docstring coverage

## 4. Closure Document Creation

Create the formal document in `docs/maintenance/phase_closure_vX.Y.Z.md` with:

```markdown
# Phase Closure - SecInterp vX.Y.Z
## Formal Development Phase Closure Document

**Closure Date:** YYYY-MM-DD
**Current Version:** X.Y.Z
**Phase:** [Descriptive Phase Name]
**Responsible:** [Name]

---

## 1. Executive Summary
[Description of main goals and key achievements]

## 2. Main Achievements
[Detailed breakdown by category]

## 3. Challenges Faced and Solutions
[Significant problems and how they were resolved]

## 4. Accumulated Technical Debt
[Classification by priority]

## 5. Project Metrics
[Table with key metrics]

## 6. Conclusion and Recommendations
[Next steps and priorities for the next phase]
```

## 5. Master Log Update

Update the following files:

- **`docs/source/MAINTENANCE_LOG.md`**: Consolidate all phase changes into a single entry.
- **`docs/CHANGELOG.md`**: Use **changelog-generator** to move all changes from `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD`.
- **`docs/DEVELOPMENT_LOG.md`**: Add phase closure entry at the top.

## 6. Version Control Synchronization

### 6.1 Phase Task Archiving
Move the active task file to the history for traceability:

```bash
mv .agent/task.md .agent/history/tasks/tasks_vX.Y.Z.md
```

### 6.2 Git Sync
Verify repository status:

```bash
git status
git log --oneline -10
```

If there are pending commits to push:

```bash
git push origin main
```

Create a phase closure tag (optional, if not an official release):

```bash
git tag phase-vX.Y.Z -m "Phase X.Y.Z closure: [brief description]"
git push origin phase-vX.Y.Z
```

## 7. Stakeholder Communication

Prepare a closure message for stakeholders (if applicable):

- Summary of main achievements
- Quality metrics
- Next steps
- Estimated timeline for the next phase

## 8. Preparation for Next Phase

Create the `.agent/next_steps.md` file with:

- Prioritized technical debt
- Preliminary goals for the next phase
- Command to resume: `/start-session`

---

**Philosophy**: A phase doesn't end when the code works, but when the knowledge is documented and the vision is clear for the next cycle.
