# Active Tasks - Phase v3.8.0

Tablero de tareas activas basado en `.agent/next_steps.md`.

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
- [ ] Retirar `core/utils/qt6_compat.py` <!-- id: 2.1 -->
- [ ] Fix 2 `NON_PYTHONIC_LOOP` <!-- id: 2.2 -->
- [ ] Investigar 1 `SPATIAL_INDEX` en `dialog_interpretation_manager.py` <!-- id: 2.3 -->
- [ ] Resolver `module_size_gate` FAIL (7 módulos > 400 líneas) <!-- id: 2.4 -->

## 🧪 Operational Status
- **Active Task**: [Gen 8 agentic system evolution] COMPLETED (Phases A–E). Next: Goal 1.1 (symbology) or Fase 1 adaptive VE.
- **Metrics**: 640/640 tests, Quality 52.3/100, Maintainability 99.9/100, Security 100/100, CC PASS, i18n AST PASS, qt6-check PASS.
