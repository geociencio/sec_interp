# Active Tasks - Phase v3.7.0 (Technical i18n Audit & Symbology Preview)

Este tablero de tareas activas registra el progreso de la sesión actual de desarrollo, basado en `.agent/next_steps.md`.

## 🎯 Goal 1: Technical Translation Audit (i18n Debt Reduction)
- [x] Audit untranslated strings flagged by `qgis-analyzer` <!-- id: 1.1 -->
- [x] Add `# no-i18n` or exclusion comments to technical string keys (e.g., datetime formats, database queries, logger patterns) to eliminate noise <!-- id: 1.2 -->
- [x] Implement a standardized script to verify that no user-facing strings are added without `self.tr()` wrapping <!-- id: 1.3 -->
- [x] Triage 79 analyzer flags — 9 genuine gaps fixed, 70 false positives (dict keys, CSS, logging, HTML markup) <!-- id: 1.4 -->
- [x] Fix 9 genuine i18n gaps: wrapped dialog error titles with self.dialog.tr() in export_manager, preview_manager, and interpretation_manager <!-- id: 1.4b -->

## 🎯 Goal 2: 3D Interpretation & Symbology Enhancements
- [x] Make preview controls (buttons, LOD, checkboxes) collapsible via QgsCollapsibleGroupBox — separate from canvas <!-- id: 2.0 -->
- [ ] Implement a live symbology/legend styling preview under the Settings sidebar <!-- id: 2.1 -->
- [x] Implementation plan created for adaptive vertical exaggeration (docs/plans/implementation_plan_adaptive_ve_v3.7.0.md) <!-- id: 2.2 -->
- [ ] Execute Fase 1: Implement VerticalExaggerationService + unit tests <!-- id: 2.2a -->
- [ ] Expand Cartesian vertical projection integration tests for highly deviated drillhole surveys <!-- id: 2.3 -->

## 🛠️ Prioritized Technical Debt & Quality Gates
- [x] Resolve false-positive `MISSING_I18N` linting warnings <!-- id: 3.1 -->
- [ ] Add a strict check in pre-commit hooks to validate `qt6_compat` import hygiene across all GUI pages <!-- id: 3.2 -->

## 🧪 Operational Status
- **Active Task**: [collapsible_preview_controls] Separated preview canvas from collapsible controls/results. Next: Fase 1 — VerticalExaggerationService.
- **Current Metrics**:
  - Tests Passing: 620/620 (100%) (v3.7.0 Verified)
  - Quality Score: 52.3/100 (v3.7.0 Verified)
  - AST i18n Gate: PASS (0 violations)
  - qgis-analyzer MISSING_I18N: 70 remaining (all false positives)
