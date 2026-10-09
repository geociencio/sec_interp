# Maintenance Session: 2026-10-08 - ai-context-core v4.0.0 Adoption

## Technical Summary

Adopted `ai-context-core` **v4.0.0** (`ai-ctx`) once published on PyPI. This major
release ("Dead Code Removal & Metric Key Contract") removes the deprecated compatibility
facades and the dead `CheckerRegistry` chain, restores architectural purity in the
analyzer (`secrets_scanner` moved to `providers/`), and enforces the canonical metric-key
contract. No new runtime behavior was added beyond surfacing **anti-pattern detections**
(God Object, Spaghetti Code, Magic Numbers, Dead Code) that were previously computed but
never rendered. SecInterp consumes `ai-ctx` only through the CLI, so the breaking API-path
removals do not affect this project.

## Changes Made

- **Dependency**: `ai-context-core>=3.5.0` → `>=4.0.0` in `pyproject.toml`
  (`project.dependencies` and `dependency-groups.dev`); `uv.lock` updated via
  `uv lock --upgrade-package ai-context-core` + `uv sync`.
- **Artifacts regenerated** with `ai-ctx full-scan`: `AI_CONTEXT.md`,
  `PROJECT_SUMMARY.md`, `project_context.json` (all git-ignored).
- **Metrics**: `agent_metrics.json` tool version `3.3.0` → `4.0.0`.
- **Documentation**: this session record.

## Verification Results

- **New output**: `AI_CONTEXT.md` now carries a `⚠️ DETECTED ANTI-PATTERNS` section
  (Magic Number detections in `gui/adapters/drillhole_extractor.py`,
  `geology_extractor.py`, `geometry.py`, `profile_extractor.py`, `structure_extractor.py`)
  that was computed but never reported before v4.0.0.
- **Project metrics** (ai-ctx 4.0.0):
  - ai-ctx Quality Score: **68.2/100** (unchanged from 3.5.0).
  - QGIS Compliance Score: **85.0/100**; i18n: **303/438 (69.2%)**.
  - Qt6 readiness: no `PyQt5` imports detected.
- **Tooling**: `uv run ai-ctx --version` → `4.0.0`; `full-scan` completed.
- **Breaking surface**: none for this project — SecInterp has no `ai_context_core` imports
  in `core/`, `gui/`, or `exporters/` (CLI-only consumption).

## Impact

The self-analysis is unchanged in score (68.2) but now exposes the anti-pattern
detections that were previously hidden, giving the agent a fuller picture of magic-number
usage in the `gui/adapters/` extraction layer. The removal of deprecated facades has no
effect on SecInterp's plugin runtime.
