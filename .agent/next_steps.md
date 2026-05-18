# Next Steps - Qt6 Hotfix Applied + Spatial Optimization Pending

## Completed in Session: qt6_qdialog_hotfix
- [x] Fix `AttributeError: QDialog has no attribute 'Accepted'` in QGIS 4.0.1 (Qt6).
- [x] Replace `exec_()` → `exec()` and `QDialog.Accepted` → `1` across all call sites.
- [x] Update `MockQWidget` and test mocks for Qt6 API consistency.

## Pending - Pre-Release Tasks for v3.6.0
- [x] Push hotfix commit `0694e80` to `origin/main` (`git push origin main`).
- [x] Applied Qt6 QImage and QPainter global color fixes and pushed.
- [x] Review remaining `MISSING_I18N` in `ProfileService` for completeness (No missing strings found in codebase).
- [ ] Final check of `.qm` translation binaries in a live QGIS 4 environment (manual).
- [ ] **Release v3.6.0**: Prepare Changelog, metadata, and generate release artifact.

## Upcoming Tasks (Goal 2 - Phase v3.6.0)
- [x] **Benchmark Spatial Performance**: Run current benchmarks in `tests/benchmarks/` to establish baseline for interpretation lookup.
- [x] **Implement QgsSpatialIndex**: Integrate spatial index in `InterpretationManager` to speed up point-in-polygon lookups.
- [x] **Verify Gains**: Re-run benchmarks to quantify performance improvement.

## How to Resume
1. Perform the Final Release Workflow for `v3.6.0` using `/release-plugin`.
2. Close the session using `/close-session`.
