# Next Steps - 2026-03-01

## Current Context
Phase 3.2.0 (Testing Expansion) and Phase 3.2.1 (Documentation Automation) have been completed. The project now has **450 unit and integration tests** passing successfully in Docker. A regression in the trajectory engine was fixed.

## Immediate Pending Tasks
- [ ] **QGIS 4.x Migration**: Start the API compatibility audit (Skill `qgis-migration-4x`).
- [ ] **UI Refactoring**: Reduce complexity in dialog managers that still exceed Ruff thresholds.
- [ ] **3D Coverage**: Expand integration tests for edge cases in complex Cartesian projections.

## Command to Resume
```bash
/inicia-sesion
```

## Quality Items
- [ ] Fix 4 "skipped" tests in the current suite (verify why they are skipped in Docker).
- [ ] Remove `DEPRECATED` warnings in the Docker build (switch to BuildKit if possible in the environment).
