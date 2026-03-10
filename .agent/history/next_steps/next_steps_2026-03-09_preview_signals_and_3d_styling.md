# Next Steps - Preview Signals & 3D Styling (Session 2026-03-09)

## Handover Context
- **Current Status**: Fixed two critical UX/Export issues.
    1. **Signal Restoration**: The preview status bar (coords/scale) now survives signal disconnections during page switches. Centralized in `connect_signals()`/`disconnect_signals()`.
    2. **3D Style Application**: Exported 3D polygons now use `QgsRuleBased3DRenderer` to ensure proper color differentiation in QGIS, bypassing unstable data-defined property keys.
- **Pending Tasks**: None from this session. Verification is complete and confirmed by the user.
- **Errors/Warnings**: Mypy warns about missing QGIS stubs/types, which is expected in this environment.

## Priority for Next Session
1. **Drillhole Logic expansion**: Resume planned Phase 3.3.0 tasks regarding drillhole data handling and validation.
2. **Standardization**: Continue with return type hint coverage expansion (target >= 70%).

## Quick Resume
```bash
# Verify signal restoration tests
make docker-test
```
