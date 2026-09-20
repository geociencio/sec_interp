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

> [!info] Refactor 2026-09-20
> Esta página de 416 líneas se descompuso en tabs ([[settings_tabs]]); `SettingsPage` es ahora un **coordinador de 124 líneas**.

**Ruta**: `gui/ui/pages/settings_page.py` (124 líneas; antes 416)
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
