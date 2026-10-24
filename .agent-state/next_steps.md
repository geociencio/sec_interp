# Next Steps (Updated 2026-10-24)

## ✅ Current state

- **Plugin**: v3.11.0 is published, merged into `main`, and **approved in the QGIS plugin repository** (the public listing is no longer 3.10.0).
- **Reliability hardening closed**: export cache keys, Python 3.9 support, i18n refresh
  (0 `unfinished`, `.qm` recompiled), release quality gates, agentic metrics/memory/validator.
- **Agentic Forge v1.4.2** (`b264e35`): framework updated; project adapters use
  `forge_metrics_checks`/`forge_metrics_report`, `memory prune --apply` and
  `workflow_graph`/`skill_conflicts`; active workflows use `testing-standards` instead of
  the deprecated `qa-docker` alias.
- **Tests**: **808 OK** (857 static). `ruff`, `format`, `mypy`, `check_docs`,
  `forge validate` (17 skills / 18 workflows), `sync_metrics --validate`,
  `i18n-check` and release YAML pass.
- **Controller refactor**: `core/controller.py` is **295 lines** (was 465); cache keys
  and four processors live in `core/services/profile/`. Merged into `main` at `434421db`.
- **Geometry refactor**: `gui/adapters/geometry.py` is now a **69-line facade**; the
  implementation lives in `geometry_{crs,lines,sampling,stats,sections}.py` (69–174
  lines). Merged into `main` at `ee93def5`.
- **Preview layer factory**: `gui/preview_layer_factory.py` is now a **202-line facade**;
  builders live in `gui/preview_layers/{topography,geology,structures,drillholes,interpretations}.py`
  (25–157 lines). Branch `refactor/module-size-preview-layer-factory` (local, not merged yet).
- **Reference**: `docs/plans/implementation_plan_module_size_controller.md`.

## 📌 Pending

1. **`module_size_gate`** — 2 modules > 400 lines: `exporters/interpretation_3d_exporter.py`
   (472), `gui/preview_renderer.py` (439).
2. **`uv` 0.12.10 → 0.13.0** — blocked by pacman (Manjaro stable serves 0.12.10).
3. **Interop plan §9** — start with **B1** (drillhole 3D styles) → B3 → B2 → B4 → Phase A:
   `docs/plans/implementation_plan_interop_stereonet_3d.md`.
4. **Optional** — native review of the machine-assisted translations; refresh `help/html`
   to v3.11.0 with `make deploy` (without `--no-compile`).

## ⚠️ Known separate bug

`section_feature_id` is part of the component cache key but is still **not passed** to
`extract_profile` / `calculate_lod_interval`; the multi-line selector does not change the
sampled section yet. Fix it before claiming multi-line support.

## 🧾 Remaining debt (documented, non-blocking)

- **Core QGIS allowlist** (7 files): `config.py`, `data_cache.py`,
  `access_control_service.py`, `export/map_settings_factory.py`, `export/orchestrator.py`,
  `utils/i18n.py`, `utils/io.py`.
- **Analyzer**: 37 known issues (20 `GOD_OBJECT`, 9 `MISSING_DOCSTRING`,
  4 `NON_PYTHONIC_LOOP`, 2 `POTENTIAL_MISSING_SLOT`, 1 `SPAGHETTI_CODE`,
  1 `UNPRECISE_LAYER`).
- **`ProfileController` GOD_OBJECT** (22 attributes, `core/controller.py:30`) —
  deferred after the module-size refactor; group lazy services into
  `ControllerServices` and keep compatibility properties.
- **Docs i18n (optional)**: `USER_GUIDE` fr (28 %) / de (18 %).
- **Framework pytest**: `test_workflow_graph_has_no_broken_refs` assumes only the three
  canonical agents; SecInterp's `qgis_driver` is valid via `opencode.json`. Deselect that
  one test when running `.agent/tests` (36 passed, 1 deselected).

## 🚀 How to resume

1. Run `/start-session` (refreshes `AI_CONTEXT.md` and reads this file).
2. Choose one:
   - `module_size_gate` refactor (before the next release), or
   - interop §9 **B1** (new feature), or
   - the `section_feature_id` multi-line fix.
3. Before closing: `/close-session` and confirm the release gate is green.
