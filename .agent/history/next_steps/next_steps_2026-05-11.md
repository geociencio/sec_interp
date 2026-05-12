# Next Steps - Global i18n and Spatial Optimization

## Pending from Session: global_i18n_synchronization
- [ ] Final check of the translation binaries (`.qm`) in a live QGIS environment (manual).
- [ ] Review the few remaining "MISSING_I18N" in `ProfileService` to ensure no critical error message was missed.

## Upcoming Tasks (Goal 2)
- [ ] **Benchmark Spatial Performance**: Run current benchmarks in `tests/benchmarks/` to establish baseline for interpretation lookup.
- [ ] **Implement QgsSpatialIndex**: Integrate spatial index in `InterpretationManager` to speed up point-in-polygon lookups.
- [ ] **Verify Gains**: Re-run benchmarks to quantify performance improvement.

## How to Resume
1. Run `/start-session`.
2. Execute `make test` to ensure stability.
3. Start Goal 2: Spatial Performance Optimization.
