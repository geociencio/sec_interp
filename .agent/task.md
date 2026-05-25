# Active Tasks - Phase v3.7.0 (Technical i18n Audit & Symbology Preview)

Este tablero de tareas activas registra el progreso de la sesión actual de desarrollo, basado en `.agent/next_steps.md`.

## 🎯 Goal 1: Technical Translation Audit (i18n Debt Reduction)
- [x] Audit untranslated strings flagged by `qgis-analyzer` <!-- id: 1.1 -->
- [x] Add `# no-i18n` or exclusion comments to technical string keys (e.g., datetime formats, database queries, logger patterns) to eliminate noise <!-- id: 1.2 -->
- [x] Implement a standardized script to verify that no user-facing strings are added without `self.tr()` wrapping <!-- id: 1.3 -->

## 🎯 Goal 2: 3D Interpretation & Symbology Enhancements
- [ ] Implement a live symbology/legend styling preview under the Settings sidebar <!-- id: 2.1 -->
- [ ] Investigate adaptive vertical exaggeration settings for complex structural projections <!-- id: 2.2 -->
- [ ] Expand Cartesian vertical projection integration tests for highly deviated drillhole surveys <!-- id: 2.3 -->

## 🛠️ Prioritized Technical Debt & Quality Gates
- [x] Resolve false-positive `MISSING_I18N` linting warnings <!-- id: 3.1 -->
- [ ] Add a strict check in pre-commit hooks to validate `qt6_compat` import hygiene across all GUI pages <!-- id: 3.2 -->

## 🧪 Operational Status
- **Active Task**: [verify_i18n] Verificación del impacto de la auditoría de i18n y ejecución del script de higiene
- **Current Metrics**:
  - Tests Passing: 572/572 (100%) (v3.6.0 Baseline)
  - Quality Score: 40.8/100 (v3.6.0 Baseline)
