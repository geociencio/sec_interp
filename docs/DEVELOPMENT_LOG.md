# SecInterp - Development Log

Chronological record of development activities, significant fixes, and technical decisions.

---

## [2026-01-03] - Global Ruff Activation & Cleanup (10:20)

### Activities
- **Ruff Rule Enablement**: Activated `F401` (unused imports), `F841` (unused variables), and `I001` (isort) project-wide.
- **Automated Fixes**: Executed `ruff check --fix` and `ruff format`. 253 fixes applied, 102 files reformatted.
- **Mock System Refactor**: Enhanced `tests/base_test.py` to fix regressions in `MockQWidget`, `MockQgsProject`, and `MockQApplication`.
- **Regression Fixes**:
    - Restored missing `logger` in `gui/main_dialog_settings.py`.
    - Fixed 3D component discovery in `exporters/interpretation_3d_exporter.py`.
    - Modernized `isinstance` checks in `gui/services/parallel_geology_service.py` (Rule `UP038`).

### Verification
- Full test suite passed: **316 tests** (312 passed, 4 skipped).
- Detailed report saved in: [ruff_cleanup_2026-01-03_10-20.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/maintenance/ruff_cleanup_2026-01-03_10-20.md)

---

## [2026-01-03] - Bug Fix: Preview Render TypeError (10:45)

### Problem
- **TypeError**: `cannot unpack non-iterable GeologySegment object` in `gui/preview_renderer.py`.
- **Cause**: After refactoring `GeologyData` to use `GeologySegment` objects, a legacy list comprehension in `render()` was still trying to unpack them as 3-tuples.

### Fix
- Updated `gui/preview_renderer.py` to extract points from `GeologySegment.points` when calculating `reference_data`.
- Added a regression test case in `tests/gui/test_preview_components.py`.

### Verification
- Full test suite passed: **316 tests**.
- Regression confirmed manually via test case.

---
