# Next Steps - Qt6 Hotfix Applied + Spatial Optimization Pending

## Completed in Session: qt6_qdialog_hotfix
- [x] Fix `AttributeError: QDialog has no attribute 'Accepted'` in QGIS 4.0.1 (Qt6).
- [x] Replace `exec_()` → `exec()` and `QDialog.Accepted` → `1` across all call sites.
- [x] Update `MockQWidget` and test mocks for Qt6 API consistency.

## Pending - Post-Release Hotfix Tasks
- [ ] Push hotfix commit `0694e80` to `origin/main` (`git push origin main`).
- [ ] Consider tagging a `v3.6.1` patch release given that this is a runtime crash fix.
- [ ] Final check of `.qm` translation binaries in a live QGIS 4 environment (manual).
- [ ] Review remaining `MISSING_I18N` in `ProfileService` for completeness.

## Upcoming Tasks (Goal 2 - Phase v3.6.0)
- [ ] **Benchmark Spatial Performance**: Run current benchmarks in `tests/benchmarks/` to establish baseline for interpretation lookup.
- [ ] **Implement QgsSpatialIndex**: Integrate spatial index in `InterpretationManager` to speed up point-in-polygon lookups.
- [ ] **Verify Gains**: Re-run benchmarks to quantify performance improvement.

## How to Resume
1. Run `/start-session`.
2. Execute `make test` to ensure stability (571 tests expected).
3. Push hotfix: `git push origin main`.
4. Evaluate `v3.6.1` patch tag.
5. Continue with Goal 2: Spatial Performance Optimization.
