---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - ui
aliases:
  - gui/ui/main_window.py
  - SecInterpMainWindow
cssclass: secinterp-note
---

# 26 — `gui/ui/main_window.py` + `pages/`

> [!abstract] One-line summary
> The **programmatic UI** of the plugin: `SecInterpMainWindow` assembles `Sidebar` + `QStackedWidget` (7 pages) + `PreviewWidget` and exposes the pages to the dialog.

**Path**: `gui/ui/main_window.py` (158 l.) + `gui/ui/pages/` (9 files, ~2254 l. total)
**Class**: `SecInterpMainWindow(QDialog)`
**Layer**: GUI · UI
**Tags**: #secinterp #gui #ui

---

## 🎯 Why does this package exist?

There is no Qt Designer `.ui`. The UI is built **in code** (skill `ui-framework`):

| Component | Role |
|-----------|------|
| `SecInterpMainWindow` | `QDialog` with `QSplitter` [Sidebar | Stack | Preview] |
| `Sidebar` | Navigation list (`QListWidget` with icons) |
| `pages/*Page` | Each wizard step (DEM, Section, Geology, Structure, Drillhole, Interpretation, Settings, Preview) |
| `PreviewWidget` | Canvas + status + results |

> [!important] The UI has no business logic
> Pages are **forms**: they expose `get_values()`/`set_values()` and emit signals. Logic lives in managers.

---

## 🧱 `SecInterpMainWindow` — assembly

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
        splitter.addWidget(self.stacked_widget)  # holds the pages
        splitter.addWidget(self.preview_widget)
        main_layout.addWidget(splitter)
        main_layout.addWidget(self.button_box)
```

| Element | Widget |
|---------|--------|
| `sidebar` | `QListWidget` with QGIS icons |
| `stacked_widget` | Holds `page_*` (one visible at a time) |
| `preview_widget` | `QgsMapCanvas` + legend + results |
| `output_widget` | `QgsFileWidget` for output folder |
| `button_box` | Ok/Cancel/Save/Help |

> [!tip] Navigation
> `sidebar.currentRowChanged → stacked_widget.setCurrentIndex` (wired in `_connect_signals`).

---

## 🧱 `pages/` — each page

| Page | File | Key fields |
|------|------|------------|
| `DemPage` | `dem_page.py` (222 l.) | `QgsMapLayerComboBox` DEM, `raster_band_combo`, `vertexag_spin` |
| `SectionPage` | `section_page.py` (117 l.) | `QgsMapLayerComboBox` line, `buffer_spin` |
| `GeologyPage` | `geology_page.py` (120 l.) | `QgsMapLayerComboBox` outcrops + `field_combo` |
| `StructurePage` | `structure_page.py` (166 l.) | `QgsMapLayerComboBox` + `dip/strike field`, `scale_spin` |
| `DrillholePage` | `drillhole_page.py` (451 l.) | 3 sub-forms: collar/survey/interval + `buffer_spin` |
| `InterpretationPage` | `interpretation_page.py` (230 l.) | Polygon list + color/type |
| `SettingsPage` | `settings_page.py` (416 l.) | Export toggles, 3D, LOD, `max_points` |
| `PreviewWidget` | `preview_page.py` (262 l.) | `QgsMapCanvas`, `results_text`, LOD controls, visibility checkboxes |
| `BasePage` | `base_page.py` (105 l.) | Common contract (`get_values`, `set_values`, `reset_defaults`) |

> [!note] `PreviewWidget` is special
> It is not a stack page; it is the viewer to the right of the `QSplitter`, always visible.

---

## 🏛️ Design patterns present

| Pattern | Where | Purpose |
|---------|-------|---------|
| **Programmatic UI** | `main_window.py` | No `.ui` files, full control |
| **Stacked Navigation** | `Sidebar` + `QStackedWidget` | Wizard steps |
| **Page Object** | each `*Page` | Encapsulates one domain form |
| **Composition** | `SecInterpMainWindow` | Adds pages + preview |

---

## 🔗 Related notes

- [[Index]] — vault index
- [[main_dialog]] — orchestrates this window
- [[dialog_preview_manager]] — uses `preview_widget.canvas`

---

*Note 26 of the SecInterp Code Walkthrough vault — v3.8.0*
