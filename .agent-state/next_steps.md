# Next Steps (Updated 2026-10-19)

## ✅ Current state

- **Plugin**: v3.11.0 is published and merged into `main`; portal approval is still pending.
- **Reliability hardening closed**: export cache keys, Python 3.9 support, i18n refresh
  (0 `unfinished`, `.qm` recompiled), release quality gates, agentic metrics/memory/validator.
- **Agentic Forge v1.4.1** (`537f9fd`): framework updated; project adapters use
  `forge_metrics_checks`/`forge_metrics_report`, `memory prune --apply` and
  `workflow_graph`/`skill_conflicts`; active workflows use `testing-standards` instead of
  the deprecated `qa-docker` alias.
- **Tests**: 778 OK (827 static). `ruff`, `format`, `mypy`, `check_docs`, `forge validate`
  (17 skills / 18 workflows), `sync_metrics --validate`, `i18n-check` and release YAML pass.
- **Reference**: `docs/maintenance/session_2026-10-19_reliability_hardening.md`.

## 📌 Pending

1. **Portal QGIS** — confirm v3.11.0 approval (page still lists 3.10.0).
2. **`module_size_gate`** — 5 modules > 400 lines: `gui/adapters/geometry.py` (597),
   `gui/preview_layer_factory.py` (534), `exporters/interpretation_3d_exporter.py` (471),
   `gui/preview_renderer.py` (438), `core/controller.py` (427).
3. **`uv` 0.12.10 → 0.13.0** — blocked by pacman (Manjaro stable serves 0.12.10).
4. **Interop plan §9** — start with **B1** (drillhole 3D styles) → B3 → B2 → B4 → Phase A:
   `docs/plans/implementation_plan_interop_stereonet_3d.md`.
5. **Optional** — native review of the machine-assisted translations; refresh `help/html`
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
- **Docs i18n (optional)**: `USER_GUIDE` fr (28 %) / de (18 %).

## 🚀 How to resume

1. Run `/start-session` (refreshes `AI_CONTEXT.md` and reads this file).
2. Choose one:
   - `module_size_gate` refactor (before the next release), or
   - interop §9 **B1** (new feature), or
   - the `section_feature_id` multi-line fix.
3. Before closing: `/close-session` and confirm the release gate is green.
