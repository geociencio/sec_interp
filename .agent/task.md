# Active Task Board (Updated 2026-09-27)

### Completed this session (2026-09-27 — release train + CI + vault)

- [x] **v3.9.0 released** (tag `v3.9.0`, GitHub release live; portal skipped by decision).
  Fixed a release-blocking mock-isolation bug in `tests/gui`; gates green (696 local /
  681 Docker, analyzer 0, security PASS); ZIP audited. Commits `e00604e`, `664d775`.
- [x] **Release train v3.9.1 / v3.10.0 / v3.11.0** prepared on cumulative branches and
  **scheduled** (Sundays Oct 4 / 11 / 18) via `.github/workflows/scheduled-release.yml`;
  validated with a `dry_run`.
- [x] **CI repaired on `main`** (ruff pin, Qt6 detection, Docker test job, docs token guard,
  legacy `release.yml` removed) — `main` all green, no more failed-run notifications.
- [x] **Qt6 / QGIS 4 fixes**: `QgsRasterBandStats` scope + `Qgis.RasterBandStatistic` fallback.
- [x] **Code Walkthrough v2 vault refreshed to v3.9.0**: 308 notes, `check_notes --strict` PASS.

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
- [x] **Code Walkthrough Vault v2** (docs-only, 2026-09-22): bóveda bilingüe **COMPLETA** —
  Core 56/56 + GUI 73/73 + Fase 3 22/22 + Fase 4 (23 hubs `layer_*` + Index final)
  (302 notas, `check_notes.py --strict` PASS, 0 enlaces rotos). Tooling + `project_structure_table.md`.
  Ver `.agent/next_steps.md`.

### Also completed this session (2026-09-23, beyond the plan)

- [x] **CRS Sampling Hardening + Structure/Section fixes** (6 commits
  `baf11d8c..eb9ffa20`): anti-cuelgue DEM/CRS, detección bloqueante de CRS mal
  etiquetado, sampler CRS-aware (geología/estructuras/collares), fix de combos
  estructurales. Suite verde (unittest 666), smoke QGIS 4 OK. Ver `.agent/next_steps.md`.

### Also completed this session (2026-09-23, DEM/Section v3.9.0)

- [x] **Fases 1.5 + 1.6 + 2 + 3** completadas (`2a14767b..6d342189`): resolver
  central de la sección, stats de banda del DEM, modo de color topo, stats
  perfil-vs-DEM. Suite verde, analyzer 0 issues, smoke QGIS 4 OK. Ver
  `.agent/next_steps.md`.

### Resume Point

Tren de releases en marcha (v3.9.0 publicado; v3.9.1 / v3.10.0 / v3.11.0 programados para el
4 / 11 / 18 oct desde sus ramas). `main` queda en v3.9.0 hasta sincronizar el tren. Siguiente:
**subir el ZIP al portal** en cada release, **refresco completo de la bóveda a v3.11.0** tras el
tren, y deuda funcional (**Goal 1.1 Fase 4** presets, **selector multi-línea**, **Goal 1.5**).

### Non-blocking Documented Debt

- 6 gray areas (genuine QGIS integration): `i18n.py`, `config.py`, `data_cache.py`,
  `access_control_service.py`, `export/map_settings_factory.py`, `export/orchestrator.py`, `io.py`.
- Optional docs: translate `USER_GUIDE` fr (28%) / de (18%); run `make docs` to publish.

### Closed

- Goal 2 (tech debt): analyzer 0 issues, module_size PASS, CC PASS, i18n PASS ✅
- Adaptive VE (Goal 1.2): full end-to-end ✅
