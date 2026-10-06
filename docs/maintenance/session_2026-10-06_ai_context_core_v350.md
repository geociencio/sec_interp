# Maintenance Session: 2026-10-06 - ai-context-core v3.5.0 Adoption

## Technical Summary

Adopted `ai-context-core` **v3.5.0** (`ai-ctx`) once published on PyPI. This release
("Explainable Scoring & Context Enrichment") resolves all active correctness findings
(A1–A5) raised in `improvement_report_v3.4.0.md`, adds an explainable **Score Breakdown**,
externalizes scoring thresholds, and introduces an i18n UI allowlist. The dependency was
bumped, the analysis artifacts were regenerated, and a local `.analyzerignore` adjustment
was made so entry points are detected.

## Changes Made

- **Dependency**: `ai-context-core>=3.4.0` → `>=3.5.0` in `pyproject.toml`
  (`project.dependencies` and `dependency-groups.dev`); `uv.lock` updated via
  `uv lock --upgrade-package ai-context-core` + `uv sync`.
- **Configuration**: removed the global `__init__.py` pattern from `.analyzerignore`
  (it also excluded the plugin entry point `classFactory`); analyzed modules 66 → 76.
- **Artifacts regenerated** with `ai-ctx full-scan`: `AI_CONTEXT.md`,
  `PROJECT_SUMMARY.md`, `project_context.json`.
- **Documentation**: appended the **Verification in v3.5.0** section to
  `docs/maintenance/ai-context-core/improvement_report_v3.4.0.md` and recorded this session.

## Verification Results

- **Correctness findings (v3.4.0 report)**:
  - A1 `entry_points` persisted → `ENTRY POINTS` renders `__init__.py (qgis_plugin)`.
  - A2 test counting decoupled → **Test Files: 137** (was "0"), `Tests: +10.0` (no `-20`).
  - A3 legacy i18n wrapper removed; A4 unused param removed; A5 silent `except` removed.
  - B `Score Breakdown` present and `max_complexity` penalizes outliers.
  - C i18n UI allowlist (`DEFAULT_UI_FUNCTIONS`, configurable via `patterns.i18n`).
  - D `--include-md` / `context_docs`; E2 deprecation policy; E4 aggregator split.
  - E1 (dead `context_builders/`, `patterns_detectors/`, `commands/`) still pending.
- **Project metrics** (ai-ctx 3.5.0):
  - ai-ctx Quality Score: **68.2/100** (was 36.2).
  - Test Files: **137**; Maintainability: **43.8**; Avg CC: **13.2**.
  - QGIS Compliance Score: **85.0/100**; i18n: **303/438 (69.2%)**.
- **Tooling**: `uv run ai-ctx --version` → `3.5.0`; `full-scan` completed.

## Impact

The project's self-analysis is now accurate and explainable: the spurious `-20` test
penalty is gone, entry points are visible, and the score can be justified item by item.
Remaining non-blocking debt is confined to the tool internals (E1) and a future CI smoke
test (`ai-ctx` output vs. fixtures).
