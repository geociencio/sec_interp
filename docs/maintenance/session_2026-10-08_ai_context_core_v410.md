# Maintenance Session: 2026-10-08 - ai-context-core v4.1.0 Adoption

## Technical Summary

Adopted `ai-context-core` **v4.1.0** (`ai-ctx`) once published on PyPI. This minor
release ("Context Map & Debt Prioritization") adds a context-only mode
(`ai-ctx context`) that generates `AI_CONTEXT.md` + `project_context.json` without
emitting or auditing the score, configurable `[context].sections`, and anti-pattern
tuning (`allowlist`, `min_severity`). It also fixes the import graph (distribution
prefixes, relative imports, collision-free Mermaid IDs), makes churn realistic
(`--find-renames`, top-5 churned files), and stops flagging `__future__` imports as
unused. SecInterp consumes `ai-ctx` only through the CLI, so the internal
`ConfigLoader` deprecation facade does not affect this project.

## Changes Made

- **Dependency**: `ai-context-core>=4.0.0` → `>=4.1.0` in `pyproject.toml`
  (`project.dependencies` and `dependency-groups.dev`); `uv.lock` updated via
  `uv lock --upgrade-package ai-context-core` + `uv sync`.
- **Artifacts regenerated** with `ai-ctx full-scan`: `AI_CONTEXT.md`,
  `PROJECT_SUMMARY.md`, `project_context.json` (all git-ignored).
- **Metrics**: `agent_metrics.json` tool version `4.0.0` → `4.1.0`.
- **Documentation**: this session record; static audit of 4.1.0 with five verified
  defects + proposed fixes in
  [improvement_report_v4.1.0.md](ai-context-core/improvement_report_v4.1.0.md).

## Verification Results

- **Project metrics** (ai-ctx 4.1.0):
  - ai-ctx Quality Score: **68.2/100** (unchanged from 4.0.0).
  - QGIS Compliance Score: **85.0/100**; i18n: **303/438 (69.2%)**.
  - Qt6 readiness: no `PyQt5` imports detected.
- **New capabilities available** (not yet wired into project config):
  - `ai-ctx context` — lighter artifact regeneration without the score audit.
  - `ai-ctx roadmap` — technical-debt prioritization.
  - `[patterns.antipatterns]` — magic-number `allowlist` + `min_severity` cutoff.
- **Tooling**: `uv run ai-ctx --version` → `4.1.0`; `full-scan` completed.
- **Breaking surface**: none for this project — SecInterp has no `ai_context_core`
  imports in `core/`, `gui/`, or `exporters/` (CLI-only consumption).

## Impact

No change to the self-analysis score (68.2) or to plugin runtime. The improved import
graph and churn reporting yield a more accurate context map, and the new
anti-pattern tuning lets the project progressively whitelist justified magic numbers
in the `gui/adapters/` extraction layer.
