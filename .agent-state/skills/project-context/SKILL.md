---
name: project-context
description: Summary of the purpose, architecture, and structure of the SecInterp project. Use when starting new tasks, requesting summaries, or explaining the plugin architecture.
---

# SecInterp Project Context

Provides a comprehensive view of the QGIS plugin for geological section interpretation, facilitating consistent architectural decision-making.

## When to use this skill
- At the start of a session to refresh architectural knowledge.
- When proposing structural changes or new integrations.
- When the user requests the current project status.

## Degree of Freedom
- **Guided**: Use this information as a reference frame to propose solutions aligned with the project's vision.

## Workflow
1. **Reading**: Consult `AI_CONTEXT.md` and `PROJECT_SUMMARY.md`.
2. **Analysis**: Identify boundaries between `core`, `gui`, and `exporters`.
3. **Validation**: Ensure new proposals do not violate defined decoupling.

## Instructions and Rules

### Purpose
SecInterp is an advanced tool for geologists that allows for the interpolation of drillhole data into 2D/3D sections within QGIS, optimizing the modeling workflow.

### Core Architecture
- **Local First**: Prioritizes local performance and efficient memory management.
- **UI-Agnostic**: The processing core must function independently of Qt graphics elements.
- **3-Level Validation**: (Type, Schema, Business) in all domain services.

### Folder Structure
- `core/`: Plugin brain (servers, drillhole logic).
- `gui/`: Dynamic and responsive user interface.
- `exporters/`: Multi-format export logic.

## Quality Checklist
- [ ] Does the proposal respect Core/GUI separation?
- [ ] Does it align with the "Local First" vision?
- [ ] Is 3-level validation integrity maintained?

## Operational lessons (digest)

Distilled from the archived `AGENT_LESSONS.md` (full text in
`.agent-state/history/memory/AGENT_LESSONS_2026-10-19_full.md`):

- **CRS/raster**: always transform line→raster before sampling; deduplicate profile
  statistics by raster cell; cap densification (never use raw pixel size on a long line).
- **Qt lifecycle**: `QDialog.accept()` does not fire `closeEvent`; release resources in
  both paths. Page-internal signals belong in an idempotent `connect_signals()`, not
  `_setup_ui`.
- **Mocks**: mirror the real Qt API only; never invent a method to satisfy production
  code. Verify widget-specific mock fidelity before asserting state.
- **Data**: declare text encodings before parsing degrees (Latin-1 CSVs are real); dip
  direction is `strike ± 90` from the source label, not the cardinal azimuth.
- **Release/CI**: run the analyzer on the release branch, pin linters to the lock, build
  the offline help before packaging, and target versioned artifacts explicitly.
- **Agentic memory**: keep `AGENT_LESSONS.md` under 350 lines; archive older lessons and
  consolidate reusable rules into skills; refresh metrics from the analyzer artifact.
