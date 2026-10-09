# Maintenance Session: 2026-10-08 - ai-context-core v4.1.1 Adoption

## Technical Summary

Adopted `ai-context-core` **v4.1.1** (`ai-ctx`) once published on PyPI. This patch
release ("Report Correctness Fixes") resolves **all five defects (F1–F5)** raised in
[improvement_report_v4.1.0.md](ai-context-core/improvement_report_v4.1.0.md) and
eliminates the manual `ai-ctx clean` workaround introduced during the 4.1.0 adoption.
The dependency was bumped, the cache was versioned automatically, and the analysis
artifacts were regenerated and verified. No public API changed.

## Changes Made

- **Dependency**: `ai-context-core>=4.1.0` → `>=4.1.1` in `pyproject.toml`
  (`project.dependencies` and `dependency-groups.dev`); `uv.lock` updated via
  `uv lock --upgrade-package ai-context-core --refresh` + `uv sync`.
- **Artifacts regenerated** with `ai-ctx full-scan`: `AI_CONTEXT.md`,
  `PROJECT_SUMMARY.md`, `project_context.json` (all git-ignored). No manual cache clean
  was required.
- **Metrics**: `agent_metrics.json` tool version `4.1.0` → `4.1.1`.
- **Documentation**: appended the **Verification in v4.1.1** section to
  `improvement_report_v4.1.0.md` and recorded this session.

## Verification Results

- **Previously reported defects (v4.1.0 report)**:
  - F1 cache versioning → `.ai_context_cache.json` now stores
    `_meta = {schema: 1, version: "4.1.1", config_fingerprint: "951b15ac6f51fda2"}`;
    the stale-cache incident cannot recur.
  - F2 security severity → `PROJECT_SUMMARY.md` reports `Max: LOW` (was hardcoded `HIGH`).
  - F3 intentional re-exports → no `UNUSED IMPORTS` false positives in `AI_CONTEXT.md`.
  - F4 churn scope → **Code Churn: 14,796** (197 files, +8,318 / −6,478), no longer
    dominated by `docs/`/`dist/` (was 512,693).
  - F5 Processing note → the generic "No Processing Algorithms found" advice is gone.
- **Project metrics** (ai-ctx 4.1.1):
  - ai-ctx Quality Score: **68.2/100** (unchanged from 4.1.0).
  - QGIS Compliance Score: **85.0/100**; i18n: **303/438 (69.2%)**.
  - Import graph: **Edges 60**, density **0.011** (stable after the versioned cache).
  - Qt6 readiness: no `PyQt5` imports detected.
- **Tooling**: `uv run ai-ctx --version` → `4.1.1`; `full-scan` completed.
- **Breaking surface**: none for this project — SecInterp has no `ai_context_core`
  imports in `core/`, `gui/`, or `exporters/` (CLI-only consumption).

## Impact

No change to the self-analysis score (68.2) or to plugin runtime. Reports are now
correct by default: accurate security severities, code-scoped churn, no re-export
false positives, and a self-invalidating cache. The operational `ai-ctx clean` step
documented for 4.1.0 is no longer necessary.
