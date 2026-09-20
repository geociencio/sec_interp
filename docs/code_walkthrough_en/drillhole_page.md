---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - ui-pages
aliases:
  - drillhole_page.py
  - DrillholePage
cssclass: secinterp-note
---

# `gui/ui/pages/drillhole_page.py`

> [!abstract] One-line summary
> **Drillhole** configuration page (Collar / Survey / Interval) with 3 tabs and validation.

> [!info] Refactor 2026-09-20
> This 451-line page was decomposed into tabs ([[drillhole_tabs]]); `DrillholePage` is now a **130-line coordinator**.

**Path**: `gui/ui/pages/drillhole_page.py` (130 lines; formerly 451)
**Class**: `DrillholePage(BasePage)`
**Layer**: GUI · UI Pages
**Tags**: #secinterp #gui #ui-pages

---

## 🧱 Structure

```python
class DrillholePage(BasePage):
    dataChanged = pyqtSignal()
    layer_keys = frozenset({"dh_collar_layer", ...})

    def _setup_ui(self):
        self.tab_widget = QTabWidget()
        # Tab Collar: QgsMapLayerComboBox + QgsFieldComboBox (id/x/y/z/depth)
        # Tab Survey: layer + fields (id/depth/azim/incl)
        # Tab Interval: layer + fields (id/from/to/lith)
```

> Validates with `ProjectValidator.is_drillhole_complete` via `resolve_layer_metadata`.

---

## 🔗 Related notes

- [[drillhole_service]] — consumes data from this page
- [[drillhole_extractor]] — Extract adapter

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
