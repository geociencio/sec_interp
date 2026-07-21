# Session 2026-07-20 — i18n Genuine Gaps Fix

**Date**: 2026-07-20
**Topic**: `i18n_gaps_fix`
**Phase**: v3.7.0 — Goal 1 (i18n Debt Reduction)
**Commit**: `641453b`

---

## Executive Summary

Completed the triage of all 79 MISSING_I18N flags from qgis-analyzer. Identified 9 genuine gaps (untranslated dialog error titles and an HTML label) and 70 false positives (dict keys, CSS/QSS, hex colors, unicode symbols, logging strings, HTML markup). Fixed all 9 gaps by wrapping bare strings with `self.dialog.tr()`.

---

## Analysis Results

### 79 MISSING_I18N Classification

| Category | Count | Action |
|---|---|---|
| Dict keys / perf keys | 20 | False positive — `# no-i18n` annotated |
| Logging strings | 16 | False positive — developer-facing |
| Internal logic flags | 7 | False positive — log level comparisons |
| CSS/QSS stylesheets | 5 | False positive — technical styling |
| Color hex codes | 4 | False positive — visual constants |
| Unicode symbols | 4 | False positive — universal indicators |
| HTML markup | 4 | False positive — interleaved with tr()-wrapped text |
| File format / domain strings | 3 | False positive — QFileDialog filter, geological values |
| Developer error messages | 3 | False positive — exception messages |
| Attribute names | 1 | False positive — `hasattr()` check |
| **Genuine gaps** | **9** | **Fixed** |

### 9 Genuine Gaps Fixed

| File | String | Fix |
|---|---|---|
| `gui/dialog_export_manager.py:78` | `"Export Error"` | → `self.dialog.tr("Export Error")` |
| `gui/dialog_export_manager.py:210` | `"Data Export Error"` | → `self.dialog.tr("Data Export Error")` |
| `gui/dialog_export_manager.py:213` | `"Unexpected Data Export Error"` | → `self.dialog.tr("Unexpected Data Export Error")` |
| `gui/dialog_preview_manager.py:118` | `"Preview Error"` | → `self.dialog.tr("Preview Error")` |
| `gui/dialog_preview_manager.py:122` | `"Unexpected Preview Error"` | → `self.dialog.tr("Unexpected Preview Error")` |
| `gui/dialog_preview_manager.py:126` | `"Critical Error"` | → `self.dialog.tr("Critical Error")` |
| `gui/dialog_preview_manager.py:420` | `"Geology Error"` | → `self.dialog.tr("Geology Error")` |
| `gui/dialog_preview_manager.py:432` | `"Drillhole Error"` | → `self.dialog.tr("Drillhole Error")` |
| `gui/dialog_interpretation_manager.py:244` | `"ID:"` | → `self.dialog.tr("ID")` |

---

## Quality Gates

| Gate | Result |
|---|---|
| AST i18n Gate | PASS (0 violations in 53 files) |
| ruff check | PASS (0 errors) |
| CC gate (check_cc.py) | PASS (all CC <= 10) |
| Conventional Commit | PASS |
| Pre-commit hooks | All passed |

---

## Files Modified

| File | Changes |
|---|---|
| `gui/dialog_export_manager.py` | 3 lines |
| `gui/dialog_preview_manager.py` | 5 lines |
| `gui/dialog_interpretation_manager.py` | 1 line |

---

## Remaining Work

- **Goal 2.1**: Implement live symbology/legend styling preview under Settings sidebar
- **Goal 2.2**: Investigate adaptive vertical exaggeration settings
- **Goal 2.3**: Expand Cartesian vertical projection integration tests
- **Tech Debt 4.1**: qt6_compat import hygiene pre-commit check
- **Tech Debt 4.2**: Fix 2 NON_PYTHONIC_LOOP issues
- **Tech Debt 4.3**: Investigate 1 SPATIAL_INDEX warning
