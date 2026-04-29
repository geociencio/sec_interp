# Implementation Plan - Phase v3.5.0 (Operational Excellence & Agentic Autonomy)

## General Goal
Achieve 100% technical documentation coverage, implement the Generation 6 agentic system for autonomous maintenance, and ensure zero-regression architecture through automated gates.

---

## User Review Required

> [!IMPORTANT]
> **Critical Decisions**
>
> 1. **Automated Pruning**: The system will automatically move lessons older than 90 days to a pruned index in `AGENT_LESSONS.md`.
> 2. **Pre-push Gate**: Commits that introduce functions with Cyclomatic Complexity > 10 will be blocked at the `git push` level.
> 3. **Semantic Loading**: The agent will dynamically load only relevant skills based on the task to save tokens and improve focus.

---

## Proposed Changes

### Goal 1: Full Technical Documentation (100% Coverage)

#### Context
The current docstring coverage is 97.4%. To reach a perfect quality score and ensure long-term maintainability, all remaining modules must be documented.

#### Components to Implement
- [MODIFY] `core/services/` (Remaining modules)
- [MODIFY] `core/utils/` (Remaining modules)
- [MODIFY] `gui/` (Remaining modules)

### Goal 2: Gen 6 Agentic System (Autonomous Maintenance)

#### Context
Manual memory pruning and metric tracking are inconsistent and time-consuming. Gen 6 automates these "meta-tasks."

#### Components to Implement
- [NEW] `scripts/memory_prune.py`: Automates `AGENT_LESSONS.md` consolidation.
- [NEW] `scripts/context_selector.py`: Logic for semantic skill injection.
- [NEW] `scripts/metrics_report.py`: Generates Markdown trend reports.
- [MODIFY] `.agent/workflows/close-session.md`: Integrated with new scripts.
- [MODIFY] `.agent/workflows/start-session.md`: Integrated with semantic selector.

### Goal 3: Zero-Regression Architecture & Performance

#### Context
Prevent future complexity bloat and fix identified performance warnings.

#### Components to Implement
- [NEW] `.git/hooks/pre-push`: CC regression gate.
- [MODIFY] `gui/dialog_interpretation_manager.py`: Fix `SPATIAL_INDEX` warning at line 123.

---

## Verification Plan

### 1. Quality Audit
```bash
uv run qgis-analyzer analyze .
```
- Success: Docstring coverage = 100%, CC <= 10.

### 2. Regression Gate Test
- Success: Push is blocked if a high-complexity function is introduced.

### 3. Agentic Workflow Test
- Success: `/close-session` updates `agent_metrics.json` and prunes lessons without manual input.

---

## Total Effort Estimation

| Goal | Effort | Priority |
|------|--------|----------|
| Full Docstring Coverage | 2 days | High |
| Gen 6 Agentic Scripts | 3 days | High |
| Performance & Gates | 1 day | Medium |
