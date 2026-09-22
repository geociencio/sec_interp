# Active Task Board (Updated 2026-09-21)

## 🎯 Current Focus: Goal 1 — 3D Interpretation & Symbology Enhancements

**Status**: IN PROGRESS — Adaptive VE (Goal 1.2 umbrella) COMPLETE ✅
**Reference plan**: `docs/plans/implementation_plan_adaptive_ve_v3.8.0.md` (COMPLETADO)

### Pending Tasks

- [ ] **1.1** Implement a live symbology/legend styling preview under the Settings sidebar
- [x] **1.2** Adaptive VE — Fases 1-4 COMPLETE ✅ 2026-09-21 (service + toggle + integration + persistence; 24 tests; VE visible en Results + etiqueta junto al checkbox)
- [ ] **1.5** Expand Cartesian vertical projection integration tests (highly deviated drillhole surveys)

### Also completed this session (beyond the plan)

- [x] VE visible en el panel Results (`2.6× (auto)` / `3.5× (manual)`) + etiqueta de solo lectura junto al checkbox Auto
- [x] Fix: layers temporales de preview ya no persisten al cerrar (OK/Save, Cancel/X y unload)
- [~] **Code Walkthrough Vault v2** (docs-only, 2026-09-22): nueva bóveda bilingüe completa en progreso (`code_walkthrough_v2` ES/EN). Tooling (`generate_vault_v2.py`, `check_notes.py`), `project_structure_table.md`, 56 esqueletos Core + 7 notas enriquecidas. Ver `.agent/next_steps.md`.

### Resume Point

Continuar con **Goal 1.1** (symbology preview) o **1.5** (tests proyección cartesiana).

### Non-blocking Documented Debt

- 6 gray areas (genuine QGIS integration): `i18n.py`, `config.py`, `data_cache.py`,
  `access_control_service.py`, `export/map_settings_factory.py`, `export/orchestrator.py`, `io.py`.
- Optional docs: translate `USER_GUIDE` fr (28%) / de (18%); run `make docs` to publish.

### Closed

- Goal 2 (tech debt): analyzer 0 issues, module_size PASS, CC PASS, i18n PASS ✅
- Adaptive VE (Goal 1.2): full end-to-end ✅
