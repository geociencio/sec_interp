# Next Steps - Post Phase v3.6.0 Closure (v3.7.0 Planning)

We have successfully closed the `v3.6.0` phase, which established 100% QGIS 4.x compatibility and high-performance spatial indexing via `QgsSpatialIndex`. The release package is verified and deployed. The next phase (v3.7.0) will focus on deep translation audit resolution and advanced 3D visual capabilities.

## 🎯 Preliminary Goals for Phase v3.7.0

### Goal 1: Technical Translation Audit (i18n Debt Reduction)
- **Objective**: Reduce the 596 static analysis warnings for `MISSING_I18N`.
- **Tasks**:
  - [ ] Audit untranslated strings flagged by `qgis-analyzer`.
  - [ ] Add `# no-i18n` or exclusion comments to technical string keys (e.g., datetime formats `%Y-%m-%d`, database query strings, schema names, logger patterns) to eliminate static analysis noise.
  - [ ] Implement a standardized script to verify that no user-facing strings are added without `self.tr()` wrapping.

### Goal 2: 3D Interpretation & Symbology Enhancements
- **Objective**: Extend custom rendering and styling features.
- **Tasks**:
  - [ ] Implement a live symbology/legend styling preview under the Settings sidebar.
  - [ ] Investigate adaptive vertical exaggeration settings for complex structural projections.
  - [ ] Expand Cartesian vertical projection integration tests for highly deviated drillhole surveys.

## 🛠️ Prioritized Technical Debt
- **🟡 Moderate**: Resolve false-positive `MISSING_I18N` linting warnings.
- **🟢 Minor**: Add a strict check in pre-commit hooks to validate `qt6_compat` import hygiene across all GUI pages.

## 🚀 How to Resume
Start the next development session using the standard workflow:
1. Run **`@[/start-session]`** to synchronize packages, execute the unit test suite, and audit the repository metrics.
2. Initialize the next task board.
