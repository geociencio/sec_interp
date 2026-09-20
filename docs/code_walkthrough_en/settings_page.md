---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - ui-pages
aliases:
  - settings_page.py
  - SettingsPage
cssclass: secinterp-note
---

# `gui/ui/pages/settings_page.py`

> [!abstract] One-line summary
> **Settings** page (Default/Advanced/Info) with `QgsSettings` and 3D/LOD toggles.

> [!info] Refactor 2026-09-20
> This 416-line page was decomposed into tabs ([[settings_tabs]]); `SettingsPage` is now a **124-line coordinator**.

**Path**: `gui/ui/pages/settings_page.py` (124 lines; formerly 416)
**Class**: `SettingsPage(BasePage)`
**Layer**: GUI · UI Pages
**Tags**: #secinterp #gui #ui-pages

---

## 🧱 Structure

```python
class SettingsPage(BasePage):
    def _setup_ui(self):
        self.tab_widget = QTabWidget()
        # Tab Default: QgsMapLayerComboBox + QgsFieldComboBox
        # Tab Advanced: QCheckBox enable_3d, max_points, vert_exag
        # Tab Info: read_plugin_metadata() + QLabel
```

> Uses `ConfigService` + `QgsSettings("SecInterp/enable_3d")` for 3D feature gate.

---

## 🔗 Related notes

- [[config]] — `ConfigService`
- [[access_control_service]] — 3D gate

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
