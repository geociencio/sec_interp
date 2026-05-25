# Next Steps - Post Phase v3.6.0 Closure (v3.7.0 Progress)

We have successfully completed Goal 1 of the `v3.7.0` phase, achieving a clean internationalization sweep. The quality gate AST-based script `verify_i18n_hygiene.py` is established, and all untranslated strings in the GUI layer have been wrapped in `self.tr()` or marked with `# no-i18n` tags. The next session will focus on the remaining goals of Phase v3.7.0.

## 🎯 Preliminary Goals for Phase v3.7.0

### Goal 1: Technical Translation Audit (i18n Debt Reduction)
- **Objective**: Reduce static analysis warnings for `MISSING_I18N` to 0.
- **Tasks**:
  - [x] Audit untranslated strings flagged by `qgis-analyzer`. <!-- id: 1.1 -->
  - [x] Add `# no-i18n` or exclusion comments to technical string keys to eliminate static analysis noise. <!-- id: 1.2 -->
  - [x] Implement a standardized script to verify that no user-facing strings are added without `self.tr()` wrapping. <!-- id: 1.3 -->

### Goal 2: 3D Interpretation & Symbology Enhancements
- **Objective**: Extend custom rendering and styling features.
- **Tasks**:
  - [ ] Implement a live symbology/legend styling preview under the Settings sidebar. <!-- id: 2.1 -->
  - [ ] Investigate adaptive vertical exaggeration settings for complex structural projections. <!-- id: 2.2 -->
  - [ ] Expand Cartesian vertical projection integration tests for highly deviated drillhole surveys. <!-- id: 2.3 -->

## 🛠️ Prioritized Technical Debt
- [x] Resolve false-positive `MISSING_I18N` linting warnings. <!-- id: 3.1 -->
- [ ] Add a strict check in pre-commit hooks to validate `qt6_compat` import hygiene across all GUI pages. <!-- id: 3.2 -->

## 🚀 How to Resume
Start the next development session using the standard workflow:
1. Run **`@[/start-session]`** to synchronize packages, execute the unit test suite, and audit the repository metrics.
2. Initialize the next task board.
