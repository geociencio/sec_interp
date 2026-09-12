# Active Tasks - Phase v3.8.0

Tablero de tareas activas basado en `.agent/next_steps.md`.

## 🛠️ Agentic System Hardening (COMPLETADO)
- [x] Cierre de fase v3.7.0 (documento + logs + archivo de tasks) <!-- id: 0.1 -->
- [x] Reconciliación de métricas + validación interna (`validate_agent_metrics.py`) <!-- id: 0.2 -->
- [x] Poda de `history/next_steps/` + unificación de naming en `history/tasks/` <!-- id: 0.3 -->
- [x] Limpieza de scripts legacy + `scripts/README.md` <!-- id: 0.4 -->
- [x] `antigravity-framerepo/` marcado obsoleto <!-- id: 0.5 -->
- [x] Gen 7 tooling cableado + 25 tests en `tests/agentic/` <!-- id: 0.6 -->

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
- **Active Task**: [agentic_system_hardening] completado. Next: Goal 1.1 (symbology) o Fase 1 adaptive VE.
- **Metrics**: 645/645 tests, Quality 52.3/100, Maintainability 99.9/100, Security 100/100, CC PASS, i18n AST PASS.
