# Session: Qt6 QDialog Hotfix
**Date**: 2026-05-12
**Topic**: qt6_qdialog_hotfix
**Phase**: v3.6.0 Post-Release

## Context
After the v3.6.0 release, a runtime crash was discovered in QGIS 4.0.1 (Qt6):

```
AttributeError: type object 'QDialog' has no attribute 'Accepted'.
  File "gui/dialog_interpretation_manager.py", line 227, in handle_interpretation_finished
    if dlg.exec_() != QDialog.Accepted:
```

## Root Cause Analysis
In Qt6, the `QDialog.Accepted` / `QDialog.Rejected` enum constants were moved from the class
namespace into the `QDialog.DialogCode` enum. Flat access (`QDialog.Accepted`) no longer works.
Additionally, `exec_()` was deprecated in Qt5 and removed in Qt6 — the replacement is `exec()`.

The Python binding for QGIS 4.0.1 uses PyQt6 under the hood, where this API removal takes effect.

## Fix Applied

| File | Change |
|---|---|
| `gui/dialog_interpretation_manager.py` | `exec_() != QDialog.Accepted` → `exec() != 1` |
| `sec_interp_plugin.py` | `self.dlg.exec_()` → `self.dlg.exec()` |
| `tests/mocks/qt_mocks.py` | `MockQWidget.exec_()` → `MockQWidget.exec()` |
| `tests/gui/test_dialog_interpretation_manager.py` | `QDialog.Accepted` → `1`, `QDialog.Rejected` → `0` |

## Decision: Use integer `1` instead of `QDialog.DialogCode.Accepted`
Using `1` (the underlying integer value) instead of `QDialog.DialogCode.Accepted` keeps the
code Qt-version agnostic without requiring version detection. This is the recommended pattern
for QGIS PyQt wrappers where the exact enum path varies between Qt5 and Qt6.

## Metrics
- Commit: `0694e80`
- Tests: 571/571 (100%)
- Files changed: 4

## Pending Actions
- Push to `origin/main`.
- Evaluate `v3.6.1` patch tag.
