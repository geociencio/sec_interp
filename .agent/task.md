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
- [x] Migrate to scoped enums for Qt6/QGIS 4 (pyqgis4-checker) — 114 enum errors resolved <!-- id: 3.3 -->
- [x] Wire full security scan (Bandit) into release workflow <!-- id: 3.4 -->
- [x] Add Qt6 enum check gate (make qt6-check / CI job) <!-- id: 3.5 -->
- [ ] Retire core/utils/qt6_compat.py monkeypatch (harmless fallback, now unused) <!-- id: 3.6 -->

## 🧪 Operational Status
- **Active Task**: [qt6_scoped_enum_migration] Migrated 114 flat enums to scoped form. Next: Goal 2.1 (symbology) o Fase 1 adaptive VE.
- **Current Metrics**:
  - Tests Passing: 620/620 (100%)
  - Quality Score: 52.3/100
  - AST i18n Gate: PASS (0 violations)
  - qgis-analyzer MISSING_I18N: 72 (all false positives)
  - pyqgis4-checker: 0 enum incompatibilities
