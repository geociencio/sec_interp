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

> [!abstract] Resumen en una línea
> Página de configuración de **sondajes** (Collar / Survey / Interval) con 3 tabs y validación.

> [!info] Refactor 2026-09-20
> Esta página de 451 líneas se descompuso en tabs ([[drillhole_tabs]]); `DrillholePage` es ahora un **coordinador de 130 líneas**.

**Ruta**: `gui/ui/pages/drillhole_page.py` (130 líneas; antes 451)
**Clase**: `DrillholePage(BasePage)`
**Capa**: GUI · UI Pages
**Tags**: #secinterp #gui #ui-pages

---

## 🧱 Estructura

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

> Valida con `ProjectValidator.is_drillhole_complete` vía `resolve_layer_metadata`.

---

## 🔗 Notas relacionadas

- [[drillhole_service]] — consume datos de esta página
- [[drillhole_extractor]] — adapter Extract

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
