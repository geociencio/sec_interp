# Active Tasks - Phase v3.8.0

Tablero de tareas activas basado en `.agent/next_steps.md`.

## 🚀 Release v3.8.0 — Core/GUI Decoupling & Reliability (COMPLETADO 2026-09-19)
- [x] Limpieza de árbol de trabajo + commits de higiene (`50a70ee`, `084ca3c8`) <!-- id: 13.1 -->
- [x] Phase 1-3: auditoría de calidad, versionado/docs, verificación (CC/security/tests) <!-- id: 13.2 -->
- [x] Phase 4: commit `4b7906cc` + tag `v3.8.0` + push a `origin/main` <!-- id: 13.3 -->
- [x] Phase 5: ZIP `sec_interp.3.8.0.zip` auditado + release GitHub publicado (latest) <!-- id: 13.4 -->
- [x] (Manual) Subir ZIP a plugins.qgis.org — PUBLICADO <!-- id: 13.5 -->

## 🔄 Core/GUI Decoupling Refactor (COMPLETADO 2026-09-19; mergeado a `main`)
- [x] Fase 0: baseline + `tests/core/test_architecture_boundary.py` (gate allowlist) + corregir comando de test <!-- id: 12.1 -->
- [x] Fase 1: limpieza de código muerto + consolidaciones (LOD, styling, memory-layer, ProfileSnapper) <!-- id: 12.2 -->
- [x] Fase 2: desacoplar God Object (PreviewCache, RenderState, protocolo de páginas, DI, event bus) <!-- id: 12.3 -->
- [x] Fase 3: consolidar pipeline de preview (render + filtrado únicos) <!-- id: 12.4 -->
- [x] Fase 4: LayerResolver/DataFetcher → gui/adapters; controller agnostic; geometría pura; gate 36 → 6 archivos <!-- id: 12.5 -->
- [x] Fase 4 (resto): migrar servicios QGIS-coupled (structure/geology/profile/drillhole/export) <!-- id: 12.6 -->
- [x] Fase 5: validación DTO (`LayerMetadata`); Fase 6: docs + release prep <!-- id: 12.7 -->

## 🧹 Root Directory Cleanup (COMPLETADO 2026-09-13)
- [x] Borrar ~90 MB de artefactos no rastreados (logs, caches, `analysis_results_*`) <!-- id: 9.1 -->
- [x] `git rm --cached` 26 artefactos generados + borrado de disco <!-- id: 9.2 -->
- [x] Untrack `.idea/`, `.vscode/`, `.continue/` + ampliar `.gitignore` <!-- id: 9.3 -->
- [x] Regenerar `.secrets.baseline` (eliminar entrada `.continue/` obsoleta) <!-- id: 9.4 -->

## 🚀 Release v3.7.2 — Qt6/QGIS 4 Compatibility Patch (COMPLETADO)
- [x] Diagnosticar 114 "Enum error" del portal (reporte pre-migración vs ZIP v3.7.1) <!-- id: 3.1 -->
- [x] Bump versión 3.7.1 → 3.7.2 (metadata, pyproject, uv.lock, README, CHANGELOG) <!-- id: 3.2 -->
- [x] Gates: qt6-check (0), CC PASS, security-scan PASS, docker-test 645/645 <!-- id: 3.3 -->
- [x] Commit `278058e` + tag `v3.7.2` + push + ZIP 3.9MB + draft release <!-- id: 3.4 -->
- [x] Publicar draft + subir ZIP a plugins.qgis.org (latest release en GitHub) <!-- id: 3.5 -->

## 🛠️ Agentic System Hardening (COMPLETADO)
- [x] Cierre de fase v3.7.0 (documento + logs + archivo de tasks) <!-- id: 0.1 -->
- [x] Reconciliación de métricas + validación interna (`validate_agent_metrics.py`) <!-- id: 0.2 -->
- [x] Poda de `history/next_steps/` + unificación de naming en `history/tasks/` <!-- id: 0.3 -->
- [x] Limpieza de scripts legacy + `scripts/README.md` <!-- id: 0.4 -->
- [x] `antigravity-framerepo/` marcado obsoleto <!-- id: 0.5 -->
- [x] Gen 7 tooling cableado + 25 tests en `tests/agentic/` <!-- id: 0.6 -->

## 🧠 Gen 8 Agentic System Evolution (COMPLETED 2026-09-13)
- [x] Phase A: root `AGENTS.md` SSoT; retired `skill_sync.py` + `context_selector.py` <!-- id: 8.1 -->
- [x] Phase B: fold 5 scripts into `sync_metrics.py` / `validate_agent_system.py`; fuse test-runners; retire CodeWhale bridge <!-- id: 8.2 -->
- [x] Phase C: externalize thresholds (`check_cc.py --threshold`) <!-- id: 8.3 -->
- [x] Phase D: native subagents in `opencode.json`; remove `runtimes:` <!-- id: 8.4 -->
- [x] Phase E: standard `SKILL.md` format + `skills.paths` discovery <!-- id: 8.5 -->
- [ ] Phase F: session-as-durable-object (proposal only — not scheduled) <!-- id: 8.6 -->

## 🎯 Goal 1: 3D Interpretation & Symbology Enhancements
- [ ] Implement live symbology/legend styling preview under Settings sidebar <!-- id: 1.1 -->
- [ ] Fase 1: `core/services/vertical_exaggeration_service.py` + unit tests <!-- id: 1.2 -->
- [ ] Fase 2: Auto/Manual toggle en `dem_page.py` <!-- id: 1.3 -->
- [ ] Fase 3: Integración en render pipeline de `sec_interp_plugin.py` <!-- id: 1.4 -->
- [ ] Expandir tests de integración de proyección vertical cartesiana <!-- id: 1.5 -->

## 🎯 Goal 2: Technical Debt Reduction
- [x] Retirar `core/utils/qt6_compat.py` — ya no existe (retirado en refactor Core/GUI) <!-- id: 2.1 -->
- [x] Fix 2 `NON_PYTHONIC_LOOP` — `enumerate` sobre generador (`interpretation_inheritance_mixin.py`) <!-- id: 2.2 -->
- [x] Fix 1 `SPATIAL_INDEX` — `QgsFeatureRequest().setFilterRect()` (`interpretation_persistence_mixin.py`) <!-- id: 2.3 -->
- [x] Resolver `module_size_gate` FAIL — 7 módulos descompuestos a <300 (PASS) <!-- id: 2.4 -->

## 🔧 qgis-plugin-analyzer 1.14.0 Upgrade (COMPLETADO 2026-09-14)
- [x] Bump `qgis-plugin-analyzer` 1.13.2 → 1.14.0 (`pyproject.toml` + `uv.lock`) <!-- id: 10.1 -->
- [x] Re-run `qgis-analyzer analyze .`; refresh `agent_metrics.json` (i18n 72 → 2, issues 75 → 5) <!-- id: 10.2 -->
- [x] `sync_metrics --validate` PASS <!-- id: 10.3 -->

## 🔄 Upstreaming Migration: SecInterp scripts → qgis-plugin-analyzer (COMPLETADO 2026-09-17)
- [x] Confirmar upstreaming implementado en analyzer 1.14.0 (regla `MISSING_I18N` AST + `--max-cc`) <!-- id: 11.1 -->
- [x] Retirar `scripts/check_cc.py` y `scripts/verify_i18n_hygiene.py` <!-- id: 11.2 -->
- [x] Refactor `sync_metrics.py` (CC gate vía `--max-cc`, i18n gate vía `MISSING_I18N == 0`) <!-- id: 11.3 -->
- [x] Suprimir 2 FP de `PerformanceTimer` vía `pyproject.toml` (`MISSING_I18N` 2 → 0) <!-- id: 11.4 -->
- [x] Arreglar pre-push hook (`--output json` → `--max-cc 10`) <!-- id: 11.5 -->
- [x] Reescribir `docs/plans/upstreaming_qgis_analyzer.md` + actualizar refs (workflows/skills/metrics) <!-- id: 11.6 -->

## 🧪 Operational Status
- **Active Task**: Module Size Gate Remediation COMPLETADO y mergeado a `main` (`99138c05`). Next: Goal 1.1 (symbology), Fase 1 adaptive VE (1.2), or tech debt 2.2/2.3.
- **Metrics**: 616 tests (Docker 5/5 suites OK), Quality 54.0/100, Maintainability 100.0/100, Security 100/100, CC PASS, i18n gate PASS, module_size gate PASS. Analyzer 1.14.0: **0 issues**. Goal 2 (tech debt) cerrado.
