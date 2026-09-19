# Maintenance Session: 2026-09-19 - Core/GUI Decoupling Refactor

## Technical Summary

Executed the first four phases of the architecture refactor plan
(`docs/plans/implementation_plan_architecture_refactor_v3.8.0.md`) to enforce the
Extract-then-Compute boundary between `core/` and `gui/`. The work lives on the
feature branch `refactor/core-gui-decoupling` and is guarded by a new architecture
allowlist gate.

## Changes Made

### Fase 0 — Baseline + guardrails
- Added `tests/core/test_architecture_boundary.py`: scans `core/` for forbidden QGIS
  coupling (`qgis.core`, `qgis.gui`, `qgis.PyQt`, `QgsProject.instance()`) and enforces
  a shrinking allowlist (starts at 36 files, now 31).
- Fixed the canonical test command in `AGENTS.md`
  (`PYTHONPATH=.. uv run python3 -m unittest discover tests`; `pytest` is broken by `pytest-qt`).

### Fase 1 — Dead code + consolidation
- Removed `gui/lod_calculator.py`, `PreviewRenderer.export_to_image`,
  `PreviewLayerFactory.interpolate_elevation`, the synchronous drillhole pipeline in
  `PreviewService`, and 15 unused `DialogConfig` constants.
- Consolidated categorized styling (`build_categorized_line_style`), memory-layer creation
  (`gui/utils.create_memory_layer`), and `ProfileSnapper` (`gui/tools/snapper.py`).

### Fase 2 — God Object decoupling (5 steps)
- Shared `PreviewCache` + callbacks to break the `PreviewManager ↔ InterpretationManager` cycle.
- `RenderState` contract for the export path.
- Page `dump()/load()/reset()` persistence protocol.
- Narrow dependency injection into `InputManager`, `NavigationManager`, `ToolManager`.
- `SignalManager` turned into a manager-wired event bus.

### Fase 3 — Preview consolidation
- Single render path (`_render_cached_data`) and single visibility filtering.

### Fase 4 — Core QGIS-agnostic migration (10 increments)
- Moved Qt signal wiring (`LayerNotificationManager`) and `DataFetcher` (`gui/adapters/feature_fetcher.py`) to GUI.
- Delegated `QgsDistanceArea` creation to `spatial.create_distance_area`; `controller.py` is now QGIS-agnostic at the import level.
- Reimplemented pure-math geometry in stdlib: Douglas-Peucker decimation, polyline metrics,
  line azimuth, and densify.
- Removed dead modules/helpers (`resource_manager.py`, `calculate_step_size`, core `create_memory_layer`, `run_geometry_operation`).

## Verification Results

- **Tests**: 576/576 OK (`PYTHONPATH=.. uv run python3 -m unittest discover tests`).
- **Architecture gate**: 3/3 OK; allowlist shrank 36 → 31 files.
- **Lint/format**: `ruff check .` and `ruff format` PASS.
- Manual QGIS 4 validation of preview, measurement, interpretation, and settings
  persistence confirmed no regressions after each phase.

## Impact

- `core/` is ~56% QGIS-agnostic (31 of 72 modules still coupled, down from 36 flagged).
- The `gui/adapters/` Extract layer is established; remaining coupled services
  (`structure_service`, `geology_service`, `profile_service`, `drillhole_service`,
  `export_service`) and `LayerResolver` are the next migration targets.
- Net negative line count across the branch (dead code + consolidation).
