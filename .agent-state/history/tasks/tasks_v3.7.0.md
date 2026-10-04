# Tasks - Phase v3.7.0

## 🎯 Goal 1: Technical Translation Audit (i18n Debt Reduction)
- [x] Audit untranslated strings flagged by `qgis-analyzer` <!-- id: 1.1 -->
- [x] Add `# no-i18n` or exclusion comments to technical string keys <!-- id: 1.2 -->
- [x] Implement a standardized script to verify no user-facing strings without `self.tr()` <!-- id: 1.3 -->
- [x] Triage 79 analyzer flags — 9 genuine gaps fixed, 70 false positives <!-- id: 1.4 -->
- [x] Fix 9 genuine i18n gaps in export_manager, preview_manager, interpretation_manager <!-- id: 1.4b -->

## 🎯 Goal 2: 3D Interpretation & Symbology Enhancements
- [x] Make preview controls collapsible via QgsCollapsibleGroupBox <!-- id: 2.0 -->
- [ ] Implement a live symbology/legend styling preview under the Settings sidebar <!-- id: 2.1 -->
- [x] Implementation plan created for adaptive vertical exaggeration <!-- id: 2.2 -->
- [ ] Execute Fase 1: Implement VerticalExaggerationService + unit tests <!-- id: 2.2a -->
- [ ] Expand Cartesian vertical projection integration tests for deviated surveys <!-- id: 2.3 -->

## 🛠️ Prioritized Technical Debt & Quality Gates
- [x] Resolve false-positive `MISSING_I18N` linting warnings <!-- id: 3.1 -->
- [x] Migrate to scoped enums for Qt6/QGIS 4 (pyqgis4-checker) — 114 enum errors resolved <!-- id: 3.3 -->
- [x] Wire full security scan (Bandit) into release workflow <!-- id: 3.4 -->
- [x] Add Qt6 enum check gate (make qt6-check / CI job) <!-- id: 3.5 -->
- [ ] Retire core/utils/qt6_compat.py monkeypatch <!-- id: 3.6 -->

## 🧪 Operational Status (at closure)
- **Active Task**: [qt6_scoped_enum_migration] — completed. Next: Goal 2.1 (symbology) or Fase 1 adaptive VE.
- **Metrics**: 620/620 tests, Quality 52.3/100, Maintainability 99.9/100, Security 100/100, CC PASS, i18n AST PASS.
