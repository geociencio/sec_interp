# Active Task Board (Updated 2026-09-21)

## 🎯 Current Focus: Goal 1 — 3D Interpretation & Symbology Enhancements

**Status**: PENDING (post v3.8.0)
**Reference plan**: `docs/plans/implementation_plan_adaptive_ve_v3.7.0.md` (5-phase plan)

### Pending Tasks

- [ ] **1.1** Implement a live symbology/legend styling preview under the Settings sidebar
- [x] **1.2** Fase 1: Implement `core/services/vertical_exaggeration_service.py` + unit tests ✅ 2026-09-21 (9/9 tests, gates PASS)
- [x] **1.3** Fase 2: Add Auto/Manual toggle to `dem_page.py` (`auto_vert_exag` default True) ✅ 2026-09-21 (7/7 tests, gates PASS)
- [ ] **1.4** Fase 3: Integrate into `dialog_preview_manager`/`render_pipeline` (§5.1: topo+struct only — decidido)
- [ ] **1.5** Expand Cartesian vertical projection integration tests (highly deviated drillhole surveys)

### Resume Point

Per `next_steps.md` → "How to Resume": continue with **Goal 1.1** (symbology preview)
or **Fase 1 adaptive VE** (1.2).

### Non-blocking Documented Debt

- 6 gray areas (genuine QGIS integration): `i18n.py`, `config.py`, `data_cache.py`,
  `access_control_service.py`, `export/map_settings_factory.py`, `export/orchestrator.py`, `io.py`.
- Optional docs: translate `USER_GUIDE` fr (28%) / de (18%); run `make docs` to publish.

### Closed

- Goal 2 (tech debt): analyzer 0 issues, module_size PASS, CC PASS, i18n PASS ✅
