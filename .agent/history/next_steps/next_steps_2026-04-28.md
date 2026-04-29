# Next Steps: QGIS 4 Stabilization & Feature Expansion

## 🎯 Immediate Objectives
1.  **Docstring Coverage campaign**:
    - [ ] `core/services/` (Target: 100% coverage).
    - [ ] `core/utils/` (Target: 100% coverage).
2.  **Fix Pending Issues**:
    - [ ] `gui/dialog_interpretation_manager.py:123`: Fix `SPATIAL_INDEX` warning.
    - [ ] Perform a full audit with `qgis-analyzer analyze` to catch any new regressions after merge.
3.  **Functional Features (v3.5.0-dev)**:
    - [ ] Implement `scripts/context_selector.py` for semantic skill injection.
    - [ ] Review functional roadmap for Phase 3.5.0.

## 🛠️ Maintenance Tasks
- [ ] Run `make test` regularly to ensure stability in `main`.
- [ ] Monitor performance metrics (LOD and RAM).

## 🚀 Resume Command
```bash
/start-session
```

---
*Last update: 2026-04-28 — Session [qgis4_readiness_and_cc_merge] closed.*
