---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - ui
  - main-window
aliases:
  - gui/ui/main_window.py
  - SecInterpMainWindow
  - UI Pages
cssclass: secinterp-note
---

# 26 — `gui/ui/main_window.py` + `pages/`

> [!abstract] Resumen en una línea
> Es la **UI programática** del plugin: `SecInterpMainWindow` ensambla `Sidebar` + `QStackedWidget` (7 páginas) + `PreviewWidget` y expone los pages al diálogo.

**Ruta**: `gui/ui/main_window.py` (158 l.) + `gui/ui/pages/` (9 archivos, ~2254 l. total)
**Clase**: `SecInterpMainWindow(QDialog)`
**Capa**: GUI · UI
**Tags**: #secinterp #gui #ui #main-window

---

## 🎯 ¿Por qué existe este paquete?

No hay `.ui` de Qt Designer. La UI se construye **en código** (skill `ui-framework`):

| Componente | Rol |
|------------|-----|
| `SecInterpMainWindow` | `QDialog` con `QSplitter` [Sidebar | Stack | Preview] |
| `Sidebar` | Lista de navegación (`QListWidget` con iconos) |
| `pages/*Page` | Cada wizard step (DEM, Section, Geology, Structure, Drillhole, Interpretation, Settings, Preview) |
| `PreviewWidget` | Canvas + status + results |

> [!important] La UI no tiene lógica de negocio
> Los pages son **formularios**: exponen `get_values()`/`set_values()` y emiten señales. La lógica vive en los managers.

---

## 🧱 `SecInterpMainWindow` — ensamblado

```python
class SecInterpMainWindow(QDialog):
    def __init__(self, iface=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Sec Interp"))
        self.resize(1200, 700)

        self.sidebar = Sidebar()
        self.stacked_widget = QStackedWidget()
        self.preview_widget = PreviewWidget()
        self.output_widget = QgsFileWidget()
        self.button_box = QDialogButtonBox(Ok | Cancel | Save | Help)

        self.page_dem = DemPage(iface)
        self.page_section = SectionPage()
        self.page_geology = GeologyPage()
        self.page_struct = StructurePage()
        self.page_drillhole = DrillholePage()
        self.page_interpretation = InterpretationPage()
        self.page_settings = SettingsPage()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)  # [Sidebar | Pages | Preview]
        splitter.setChildrenCollapsible(True)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.stacked_widget)  # contiene las páginas
        splitter.addWidget(self.preview_widget)
        main_layout.addWidget(splitter)
        main_layout.addWidget(self.button_box)
```

| Elemento | Widget |
|----------|--------|
| `sidebar` | `QListWidget` con iconos QGIS |
| `stacked_widget` | Contiene `page_*` (una visible a la vez) |
| `preview_widget` | `QgsMapCanvas` + leyenda + resultados |
| `output_widget` | `QgsFileWidget` para carpeta de salida |
| `button_box` | Ok/Cancel/Save/Help |

> [!tip] Navegación
> `sidebar.currentRowChanged → stacked_widget.setCurrentIndex` (conectado en `_connect_signals`).

---

## 🧱 `pages/` — cada página

| Page | Archivo | Campos clave |
|------|---------|--------------|
| `DemPage` | `dem_page.py` (222 l.) | `QgsMapLayerComboBox` DEM, `raster_band_combo`, `vertexag_spin` |
| `SectionPage` | `section_page.py` (117 l.) | `QgsMapLayerComboBox` línea, `buffer_spin` |
| `GeologyPage` | `geology_page.py` (120 l.) | `QgsMapLayerComboBox` outcrops + `field_combo` |
| `StructurePage` | `structure_page.py` (166 l.) | `QgsMapLayerComboBox` + `dip/strike field`, `scale_spin` |
| `DrillholePage` | `drillhole_page.py` (451 l.) | 3 sub-formularios: collar/survey/interval + `buffer_spin` |
| `InterpretationPage` | `interpretation_page.py` (230 l.) | Lista de polígonos + color/type |
| `SettingsPage` | `settings_page.py` (416 l.) | Toggles de exportación, 3D, LOD, `max_points` |
| `PreviewWidget` | `preview_page.py` (262 l.) | `QgsMapCanvas`, `results_text`, controles LOD, checkboxes de visibilidad |
| `BasePage` | `base_page.py` (105 l.) | Contrato común (`get_values`, `set_values`, `reset_defaults`) |

> [!note] `PreviewWidget` es especial
> No es una página del stack; es el visor a la derecha del `QSplitter`, siempre visible.

---

## 🏛️ Patrones de diseño presentes

| Patrón | Dónde | Propósito |
|--------|-------|-----------|
| **Programmatic UI** | `main_window.py` | Sin `.ui` files, control total |
| **Stacked Navigation** | `Sidebar` + `QStackedWidget` | Wizard por pasos |
| **Page Object** | cada `*Page` | Encapsula formulario de un dominio |
| **Composition** | `SecInterpMainWindow` | Agrega pages + preview |

---

## 🔗 Notas relacionadas

- [[00 - Index]] — índice de la bóveda
- [[20 - main_dialog]] — orquesta esta ventana
- [[21 - dialog_preview_manager]] — usa `preview_widget.canvas`

---

*Nota 26 de la bóveda SecInterp Code Walkthrough — v3.8.0*
