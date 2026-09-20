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

> [!abstract] Resumen en una línea
> Página de **configuración** (Default/Advanced/Info) con `QgsSettings` y toggles de exportación 3D/LOD.

**Ruta**: `gui/ui/pages/settings_page.py` (416 líneas)
**Clase**: `SettingsPage(BasePage)`
**Capa**: GUI · UI Pages
**Tags**: #secinterp #gui #ui-pages

---

## 🧱 Estructura

```python
class SettingsPage(BasePage):
    def _setup_ui(self):
        self.tab_widget = QTabWidget()
        # Tab Default: QgsMapLayerComboBox + QgsFieldComboBox
        # Tab Advanced: QCheckBox enable_3d, max_points, vert_exag
        # Tab Info: read_plugin_metadata() + QLabel
```

> Usa `ConfigService` + `QgsSettings("SecInterp/enable_3d")` para feature gate 3D.

---

## 🔗 Notas relacionadas

- [[config]] — `ConfigService`
- [[access_control_service]] — gate 3D

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
