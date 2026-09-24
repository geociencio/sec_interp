# Active Task Board (Updated 2026-09-23)

## 🎯 Current Focus: Goal 1 — 3D Interpretation & Symbology Enhancements

**Status**: IN PROGRESS — Adaptive VE (Goal 1.2 umbrella) COMPLETE ✅
**Reference plan**: `docs/plans/implementation_plan_adaptive_ve_v3.8.0.md` (COMPLETADO)

### Pending Tasks

- [~] **1.1** Live symbology/legend styling preview under Settings — Fases 1–3 COMPLETE ✅
  (v3.11.0: pestaña Symbology con estilos por capa, editor por unidad rename/order,
  opciones de leyenda posición/fuente/máximo) + fixes de layout del diálogo.
  **Pendiente: Fase 4 (presets)**. Plan:
  `docs/plans/implementation_plan_symbology_preview_v3.11.0.md`.
- [x] **1.2** Adaptive VE — Fases 1-4 COMPLETE ✅ 2026-09-21 (service + toggle + integration + persistence; 24 tests; VE visible en Results + etiqueta junto al checkbox)
- [ ] **1.5** Expand Cartesian vertical projection integration tests (highly deviated drillhole surveys)

### Also completed this session (beyond the plan)

- [x] VE visible en el panel Results (`2.6× (auto)` / `3.5× (manual)`) + etiqueta de solo lectura junto al checkbox Auto
- [x] Fix: layers temporales de preview ya no persisten al cerrar (OK/Save, Cancel/X y unload)
- [x] **Code Walkthrough Vault v2** (docs-only, 2026-09-22): bóveda bilingüe **COMPLETA** —
  Core 56/56 + GUI 73/73 + Fase 3 22/22 + Fase 4 (23 hubs `layer_*` + Index final)
  (302 notas, `check_notes.py --strict` PASS, 0 enlaces rotos). Tooling + `project_structure_table.md`.
  Ver `.agent/next_steps.md`.

### Also completed this session (2026-09-23, beyond the plan)

- [x] **CRS Sampling Hardening + Structure/Section fixes** (6 commits
  `baf11d8c..eb9ffa20`): anti-cuelgue DEM/CRS, detección bloqueante de CRS mal
  etiquetado, sampler CRS-aware (geología/estructuras/collares), fix de combos
  estructurales. Suite verde (unittest 666), smoke QGIS 4 OK. Ver `.agent/next_steps.md`.

### Also completed this session (2026-09-23, v3.9.1 + v3.10.0)

- [x] **Smoothed geology (v3.9.1)** + **Preview side panel (v3.10.0)**: geology follows
  the smoothed profile; collapsible legend panel with interpretations list and per-unit
  hide/color (incl. drillhole lithologies), persisted. 729 tests, analyzer 0 issues.
  Ver `.agent/next_steps.md`.

### Also completed this session (2026-09-23, smoothed profile)

- [x] **Optional smoothed topography profile** (`3094a1f1`, `76fc6206`):
  Smooth control + window in Controls, soft-red overlay, extra smoothed export
  files. Suite green, analyzer 0 issues. Ver `.agent/next_steps.md`.

### Also completed this session (2026-09-23, DEM/Section v3.9.0)

- [x] **Fases 1.5 + 1.6 + 2 + 3** completadas (`2a14767b..6d342189`): resolver
  central de la sección, stats de banda del DEM, modo de color topo, stats
  perfil-vs-DEM. Suite verde, analyzer 0 issues, smoke QGIS 4 OK. Ver
  `.agent/next_steps.md`.

### Also completed this session (2026-09-23, v3.11.0 — Goal 1.1 Fases 1–3)

- [x] **Live Symbology & Legend Styling (v3.11.0)**: pestaña Settings → Symbology con
  estilos por capa en vivo (`layer_styles`), editor por unidad compartido
  (ocultar/color/rename/reorder → alias+orden en leyenda), opciones de leyenda
  (posición/fuente/máximo "+N more"), leyenda con simbología real separando Geología vs
  Litologías de sondeo e interpretaciones editables, y fixes de layout (Symbology en
  scroll + secciones colapsables; diálogo acotado a pantalla). 11 commits
  (`ba62083a..63b47c99`), 743 tests, analyzer 0 issues. Ver `.agent/next_steps.md`.

### Resume Point

Bóveda v2 completa ✅. Plan **DEM/Section v3.9.0 completo** ✅.
**Goal 1.1 / v3.11.0 Fases 1–3 ✅** (symbology preview + leyenda). Siguiente:
**Fase 4 — presets de simbología**, **selector multi-línea** (infra lista),
**Goal 1.5** (tests proyección) o preparar **release v3.9.x/v3.11.0**.

### Non-blocking Documented Debt

- 6 gray areas (genuine QGIS integration): `i18n.py`, `config.py`, `data_cache.py`,
  `access_control_service.py`, `export/map_settings_factory.py`, `export/orchestrator.py`, `io.py`.
- Optional docs: translate `USER_GUIDE` fr (28%) / de (18%); run `make docs` to publish.

### Closed

- Goal 2 (tech debt): analyzer 0 issues, module_size PASS, CC PASS, i18n PASS ✅
- Adaptive VE (Goal 1.2): full end-to-end ✅
