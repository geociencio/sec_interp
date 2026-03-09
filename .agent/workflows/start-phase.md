---
description: Formal procedure for starting a new major development phase
agent: Senior Architect
skills: [qgis-core, geological-logic, qa-docker]
validation: |
  - Verify that implementation_plan is created and complete
  - Confirm that tests pass before starting
  - Validate that goals are clear and prioritized
  - Verify that next_steps.md is updated
---

# Workflow: Start Phase

This workflow documents the complete process for formally starting a new major development phase (e.g., v3.2.0 → v3.3.0).

## 1. Review of Previous Phase Closure

🤖 **Agent Action**: Analyze the closure document and extract prioritized technical debt.

Read the closure document of the previous phase:

```bash
cat docs/maintenance/phase_closure_v[PREVIOUS].md
```

Identify:
- Inherited technical debt (prioritized)
- Recommendations for the new phase
- Baseline metrics for comparison

## 2. Goals Definition for the New Phase

Create a planning document in `docs/plans/implementation_plan_vX.Y.Z.md`:

```markdown
# Implementation Plan - Phase vX.Y.Z ([Phase Name])

## General Goal
[Clear description of this phase's purpose]

---

## User Review Required

> [!IMPORTANT]
> **Critical Decisions**
>
> [List of architectural or design decisions requiring approval]

---

## Proposed Changes

### Goal 1: [Goal Name]

#### Context
[Why this goal is necessary]

#### Components to Implement

##### [NEW/MODIFY] [file](file:///absolute/path)
[Description of changes]

#### Detailed Estimation

| Component | Effort | Phase |
|-----------|--------|-------|
| ... | X hours | Sprint Y |

---

## Verification Plan

### 1. [Verification Type]
[Commands and success criteria]

---

## Total Effort Estimation

| Goal | Effort | Priority |
|------|--------|----------|
| ... | X days | High/Medium/Low |
```

## 3. Current State Analysis

Run the full project analysis:

// turbo
```bash
uv run ai-ctx analyze --path .
```

Document the baseline state:
- Number of Python files
- Total tests
- Quality metrics (Ruff, Type Hints, Docstrings)
- Average cyclomatic complexity

## 4. Stability Verification

🤖 **Agent Action**: Use **qa-docker** skill to validate baseline stability.

Ensure the project is in a stable state before starting:

// turbo
```bash
make docker-test
```

**Success Criteria**: All unit tests passing (100% success rate).

## 5. Environment Synchronization

Update dependencies and tools:

// turbo
```bash
uv sync
```

Verify that the local environment is clean:

```bash
git status
```

If there are uncommitted changes, evaluate if they should be part of the previous phase or discarded.

## 6. Tracking Structure Creation

Create the task file in `.agent/task.md` (if using AI artifacts):

```markdown
# Tasks - Phase vX.Y.Z

## Goal 1: [Name]
- [ ] Sub-task 1 <!-- id: 1 -->
- [ ] Sub-task 2 <!-- id: 2 -->

## Goal 2: [Name]
- [ ] Sub-task 1 <!-- id: 3 -->
```

## 7. CHANGELOG Update

Prepare the `[Unreleased]` section in `docs/CHANGELOG.md`:

```markdown
## [Unreleased]

### Added
- [To be documented during the phase]

### Changed
- [To be documented during the phase]

### Fixed
- [To be documented during the phase]
```

## 8. Start Communication

Document the phase start in `docs/DEVELOPMENT_LOG.md`:

```markdown
## [YYYY-MM-DD] Start of Phase vX.Y.Z
- **Goal**: [Brief description]
- **Estimated Duration**: X weeks
- **Priorities**: [List of main goals]
```

## 9. AI Workflow Configuration (if applicable)

Update `.agent/next_steps.md` with the new phase's context:

```markdown
# Next Steps - SecInterp vX.Y.Z

**Phase vX.Y.Z ([Name])** has started. The main goals are:

1. [Goal 1]
2. [Goal 2]
3. [Goal 3]

## How to Resume
To start a development session:
```bash
/start-session
```

**Current Status**: Stable. Implementation plan approved.
```

## 10. First Phase Commit

Create an initial commit marking the phase start:

```bash
git add docs/plans/implementation_plan_vX.Y.Z.md docs/DEVELOPMENT_LOG.md .agent/next_steps.md
git commit -m "chore: initialize phase vX.Y.Z - [Phase Name]

- Created implementation plan with [N] goals
- Updated development log with phase start
- Prepared tracking structure"
```

---

**Philosophy**: A phase well started is a phase half completed. Clarity in goals and baseline documentation are fundamental for success.
