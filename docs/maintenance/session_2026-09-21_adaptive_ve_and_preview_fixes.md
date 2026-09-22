# Maintenance Session: 2026-09-21 - Adaptive Vertical Exaggeration + Preview Fixes

## Technical Summary

Implemented the **adaptive vertical exaggeration (VE)** feature end-to-end (Goal 1.2 of the
v3.8.0 phase), replacing the static manual `vertexag_spin` with a geometry-driven Auto/Manual
system, and fixed two user-facing defects: the applied VE was invisible in the UI, and the plugin
leaked temporary memory layers that triggered QGIS's "temporary scratch layers" warning on exit.

## Changes Made

### Adaptive Vertical Exaggeration (4 phases)

- **Core** — `core/services/vertical_exaggeration_service.py` (new, stdlib-only, thread-safe).
  `VerticalExaggerationService.calculate(topo, struct)` derives VE from the profile aspect ratio
  (`elevation_range / distance_range` → base 1/2/5/10) modulated by structural density
  (×0.7/×1.0/×1.3), clamped to `[0.5, 20.0]` and rounded to 1 decimal. `calculate_from_result`
  consumes a `PreviewResult` using **topo+struct only** (decision §5.1: excludes async
  geol/drillhole to avoid re-render flicker). All thresholds as class constants (ruff PLR2004).
- **GUI** — `gui/ui/pages/dem_page.py`: `Auto` checkbox (default on) disabling the manual spin;
  `set_auto_ve()` read-only label next to the toggle. `DialogDefaults.AUTO_VERTICAL_EXAGGERATION`,
  `DemSettings.auto_vert_exag`, and `ConfigService` load/static-defaults/reset.
- **Integration** — `gui/preview_render_mixin.py::_resolve_vertical_exaggeration()` resolves
  auto=service vs manual=spin; `plugin/render_pipeline.py::draw_preview` accepts `vert_exag` (no
  longer reads the spin); `VerticalExaggerationService` injected into `PreviewManager` via DI.
  VE excluded from `PreviewParams`/`PreviewParamHasher` (avoids cache-miss loop).
- **Persistence + docs** — persistence tests (`config`, `settings_model`, `config_integration`);
  `ARCHITECTURE_EN.md` service entry + mermaid node; new code-walkthrough vault note + Index;
  mirrors re-synced. Plan `implementation_plan_adaptive_ve_v3.8.0.md` marked COMPLETED.

### VE visibility

- `gui/preview_reporter.py`: `format_results_message` gained `vert_exag`/`auto_vert_exag` and a
  new `format_vertical_exaggeration` (shows `Vertical exaggeration: 2.6× (auto)` / `(manual)`) plus
  a conditional footer.
- Both result-message call sites (`dialog_preview_manager.py`, `preview_callbacks_mixin.py`) pass
  the resolved VE and update `page_dem.set_auto_ve(...)`.
- `_resolve_vertical_exaggeration` logs the resolved VE at INFO.

### Temporary scratch-layer fix

- Root cause: preview memory layers are registered in `QgsProject` for stable QGIS 4 rendering but
  were only removed at the start of the next render. The OK/Save button routes through
  `accept_handler` → `self.accept()`, which does **not** fire `closeEvent`, so cleanup never ran on
  that path.
- Fix: public `PreviewRenderer.cleanup()`; called from `DialogLifecycleMixin._cleanup_preview_renderer()`
  (closeEvent), `PluginLifecycleMixin.unload()`, and `DialogFacadeMixin.accept_handler()`.

## Verification Results

- **Tests**: 643 static (594 local discovery OK; Docker 5/5 shards OK).
- **Analyzer**: `qgis-analyzer analyze . --max-cc 10` → 0 issues; maintainability 100.0; security 100.0.
- **Quality**: Module Stability 53.8/100 · CC gate PASS · i18n gate PASS · module_size PASS.
- **Lint**: `ruff check` + `ruff format` PASS.

## Impact

Adaptive VE is now the default behavior (Auto on), with the manual mode preserved as an override.
Temporary layers no longer leak across dialog close paths, eliminating the misleading
"temporary scratch layers" warning. No data-persistence behavior changed (interpretations remain
JSON-in-project or external layer).

## Commits

`38c1c651`, `8ded9ccd`, `c443b49f`, `26bdd8fd`, `6236e93e`, `f069c830`, `8f50994a`.
