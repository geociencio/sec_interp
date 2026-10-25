# Next Steps (Updated 2026-10-24)

## ✅ Current state

- **Plugin**: v3.11.0 is published, merged into `main`, and **approved in the QGIS plugin repository** (the public listing is no longer 3.10.0).
- **Reliability hardening closed**: export cache keys, Python 3.9 support, i18n refresh
  (0 `unfinished`, `.qm` recompiled), release quality gates, agentic metrics/memory/validator.
- **Agentic Forge v1.4.2** (`b264e35`): framework updated; project adapters use
  `forge_metrics_checks`/`forge_metrics_report`, `memory prune --apply` and
  `workflow_graph`/`skill_conflicts`; active workflows use `testing-standards` instead of
  the deprecated `qa-docker` alias.
- **Tests**: **839 OK** (888 static). `ruff`, `format`, `mypy`, `check_docs`,
  `forge validate` (17 skills / 18 workflows), `sync_metrics --validate`,
  `i18n-check` and release YAML pass.
- **Controller refactor**: `core/controller.py` is **295 lines** (was 465); cache keys
  and four processors live in `core/services/profile/`. Merged into `main` at `434421db`.
- **Geometry refactor**: `gui/adapters/geometry.py` is now a **69-line facade**; the
  implementation lives in `geometry_{crs,lines,sampling,stats,sections}.py` (69–174
  lines). Merged into `main` at `ee93def5`.
- **Preview layer factory**: `gui/preview_layer_factory.py` is now a **202-line facade**;
  builders live in `gui/preview_layers/{topography,geology,structures,drillholes,interpretations}.py`
  (25–157 lines). Merged into `main` at `bf3692a9`.
- **3D interpretation exporter**: `exporters/interpretation_3d_exporter.py` is now a
  **155-line facade**; helpers live in `exporters/interpretation_3d/{fields,geometry,style}.py`
  (67–178 lines). Merged into `main` at `91639cc3`.
- **Preview renderer**: `gui/preview_renderer.py` is now a **335-line façade**; layer
  collection and cleanup live in `preview_renderer_layers.py` (123) and
  `preview_renderer_cleanup.py` (68). Merged into `main` at `2e05e4f8`.
- **`module_size_gate`: PASS** — 0 modules >400 after all five refactors.
- **Interpretation settings tab (branch `refactor/interpretation-settings-tab`)**: moved
  `InterpretationPage` into `SettingsPage` as the **Interpretation Settings** tab;
  sidebar is now 6 entries. `MainWindow.page_interpretation` aliases
  `page_settings.interpretation_tab`, so persistence/consumers are unchanged. Merged into
  `main` at `1cc2c105`.
- **`section_feature_id` fix (branch `fix/section-feature-id`)**: `SectionPage` now has
  an `fid — label` selector that lists only 2-vertex lines, with a selectable label
  field (`Auto` or any attribute). The id is forwarded to topography/geology/
  structures/drillholes, `PreviewService` (LOD/topo/structures) and the async
  geology/drillhole tasks; cache keys already isolate features. **827 OK / 876 static**;
  merged into `main` at `83e86a2c`.
- **Core QGIS-agnostic**: `core/` no longer imports QGIS/PyQt. Translations, settings
  and map settings are injected via ports/adapters; `qgis_io.py` and `map_settings.py`
  live in `exporters/`; architecture allowlist is empty. Merged into `main` at
  `af0bfbbb`.
- **Code Walkthrough v2 consolidation**: v2 ES/EN is the only active vault; v1 is
  archived under `docs/archive/code_walkthrough_v1*`; 4 notes migrated and
  `section_feature_selector` / `interpretation_tab` added. Merged into `main` at
  `30b90605`.
- **QGIS 4 manual validation (2026-10-24)**: plugin deployed to
  `~/.local/share/QGIS/QGIS4/profiles/default/python/plugins/sec_interp` with
  `uv run qgis-manage deploy --no-compile --qgis-version 4`; backup
  `sec_interp.bak.20261024153917`; manual tests **confirmed OK** (2026-10-24).
  `secc1.shp`: 4 of 7 features listed by design; `a2`/`a3`/`a6` have 3/4/5 vertices.
- **Reference**: `docs/plans/implementation_plan_section_feature_id.md` ·
  `docs/maintenance/session_2026-10-24_section_feature_selection.md` ·
  `docs/plans/implementation_plan_module_size_controller.md` ·
  `docs/maintenance/session_2026-10-24_module_size_gate_completion.md`.

## 📌 Pending

1. **`uv` 0.12.10 → 0.13.0** — blocked by pacman (Manjaro stable serves 0.12.10).
2. **Interop plan §9** — start with **B1** (drillhole 3D styles) → B3 → B2 → B4 → Phase A:
   `docs/plans/implementation_plan_interop_stereonet_3d.md`.
3. **Optional** — native review of the machine-assisted translations; refresh `help/html`
   to v3.11.0 with `make deploy` (without `--no-compile`).

## ✅ Recently fixed

- `section_feature_id` is now passed end-to-end (branch `fix/section-feature-id`); the
  selector filters 2-vertex lines and exposes `fid — label` + label field. See
  `docs/plans/implementation_plan_section_feature_id.md`.

## 🧾 Remaining debt (documented, non-blocking)

- **Core QGIS allowlist** (7 files): `config.py`, `data_cache.py`,
  `access_control_service.py`, `export/map_settings_factory.py`, `export/orchestrator.py`,
  `utils/i18n.py`, `utils/io.py`.
- **Analyzer**: 36 known issues (19 `GOD_OBJECT`, 9 `MISSING_DOCSTRING`,
  4 `NON_PYTHONIC_LOOP`, 2 `POTENTIAL_MISSING_SLOT`, 1 `SPAGHETTI_CODE`,
  1 `UNPRECISE_LAYER`).
- **`ProfileController` GOD_OBJECT** (21 attributes, `core/controller.py:37`) —
  deferred after the module-size refactor; group lazy services into
  `ControllerServices` and keep compatibility properties.
- **Docs i18n (optional)**: `USER_GUIDE` fr (28 %) / de (18 %).
- **Framework pytest**: `test_workflow_graph_has_no_broken_refs` assumes only the three
  canonical agents; SecInterp's `qgis_driver` is valid via `opencode.json`. Deselect that
  one test when running `.agent/tests` (36 passed, 1 deselected).

## 🚀 How to resume

1. Run `/start-session` (refreshes `AI_CONTEXT.md` and reads this file).
2. Choose one:
   - interop §9 **B1** (new feature; recommended), or
   - the deferred `ProfileController` `GOD_OBJECT` refactor.
3. Before closing: `/close-session` and confirm the release gate is green.
