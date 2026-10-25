# Implementation Plan — Move Interpretation Settings into the Settings Page

**Status**: PROPUESTO — pendiente de aprobación
**Created**: 2026-10-24
**Scope**: mover `InterpretationPage` a `SettingsPage` como tab **“Interpretation”**
**Branch propuesta**: `refactor/interpretation-settings-tab`

---

## 1. Recomendación

**Sí, encaja mejor como tab de Settings.**

`InterpretationPage` no es una página de trabajo como DEM, Section, Geology o
Drillholes. Es configuración:

- almacenamiento de interpretaciones (JSON del proyecto vs capa vectorial);
- campos personalizados;
- herencia de atributos desde geología/sondajes.

No tiene `layer_keys`, no participa del preview y su título real ya es
**“Interpretation Settings”**. Ocupa una fila del sidebar que debería reservarse a
flujos de datos. Moverla reduce ruido y agrupa toda la configuración en un solo lugar.

**No es un cambio funcional**: los valores persistidos, las claves y el comportamiento
no cambian.

---

## 2. Estado actual

| Elemento | Tamaño / detalle |
|---|---|
| `gui/ui/pages/interpretation_page.py` | 230 líneas; `InterpretationPage(BasePage)` |
| `gui/ui/pages/settings_page.py` | 138 líneas; tabs Default, Advanced, Symbology, Plugin Information |
| `gui/ui/main_window.py` | 167 líneas; sidebar con 7 ítems y stacked con 7 páginas |
| Traducciones | contexto **`InterpretationPage`** en los 13 catálogos |

### Dependencias de `page_interpretation`

| Archivo | Uso |
|---|---|
| `gui/ui/main_window.py` | crea, apila y añade al sidebar |
| `gui/interpretation_persistence_mixin.py` | `page_interpretation.get_data()` (carga/guarda) |
| `gui/dialog_interpretation_manager.py` | `get_data()` para herencia/campos al terminar un polígono |
| `gui/dialog_settings_persistence.py` | incluye la página en `_data_pages()` |
| `gui/dialog_signal_manager.py` | la incluye en connect/disconnect |
| Tests | mocks de `page_interpretation`; sidebar por índice |
| Docs | `code_walkthrough*`, `DEVELOPER_ANALYSIS.md` |

### UI actual

Sidebar:

```text
0 DEM / Raster
1 Section Line
2 Geology
3 Structural
4 Drillholes
5 Interpretation   ← se elimina
6 Settings         ← pasa a 5
```

---

## 3. Diseño propuesto

### 3.1 Nueva `InterpretationTab`

Crear:

```text
gui/ui/pages/settings/interpretation_tab.py
```

```python
class InterpretationTab(QWidget):
    """Interpretation storage, custom fields and inheritance settings."""

    def __init__(self, parent=None): ...
    def get_data(self) -> dict[str, Any]: ...
    def dump(self) -> dict[str, Any]: ...
    def load(self, data: dict[str, Any]) -> None: ...
    def reset(self) -> None: ...
    def validate(self) -> tuple[bool, str]: ...
    def connect_signals(self) -> None: ...
    def disconnect_signals(self) -> None: ...
```

Mantener **exactamente** los mismos atributos que hoy usan tests/consumidores:

```text
cb_source, layer_combo, chk_auto_sync,
fields_table, btn_add_field, btn_remove_field,
chk_inherit_geol, chk_inherit_drill
```

y los mismos métodos/retornos de `get_data`, `dump`, `load`, `reset`, `validate`.

Cambios de forma:

- `QWidget` + `QVBoxLayout`, sin `BasePage` ni `QGroupBox` con título.
- Se eliminan el `group_box` y el stretch final de `BasePage`.
- Las secciones internas (`Interpretation Storage`, `Custom Attributes`,
  `Attribute Inheritance`) se conservan.
- `layer_keys = frozenset()` (compatibilidad con `_write_page/_read_page`).

### 3.2 Contexto de traducción

Para no regenerar los 13 catálogos, `InterpretationTab.tr()` debe seguir usando:

```python
QCoreApplication.translate("InterpretationPage", message)
```

Así se reutilizan las traducciones existentes. El texto “Interpretation Settings” ya
está traducido en ese contexto.

El label del tab puede usar `self.tr("Interpretation")` desde `SettingsPage`; si se
añade una cadena nueva, actualizar los 13 `.ts` en la misma fase.

### 3.3 `SettingsPage`

- Crear `self.interpretation_tab = InterpretationTab()`.
- Añadirlo al `QTabWidget` en este orden:

```text
Default | Advanced | Symbology | Interpretation | Plugin Information
```

- `connect_signals()`: conectar `interpretation_tab.changed` (si se añade) o llamar a
  `interpretation_tab.connect_signals()`.
- `disconnect_signals()`: desconectar el tab.
- No fusionar `interpretation_tab.get_data()` en `SettingsPage.get_data()` salvo que se
  necesite; los consumidores seguirán usando `page_interpretation.get_data()` a través
  del alias.

### 3.4 `MainWindow`

- Eliminar `from .pages.interpretation_page import InterpretationPage`.
- Crear primero `self.page_settings = SettingsPage()`.
- Exponer el alias de compatibilidad:

```python
self.page_interpretation = self.page_settings.interpretation_tab
```

- Eliminar `self.stacked_widget.addWidget(self.page_interpretation)`.
- Eliminar el ítem **Interpretation** del sidebar.
- Ajustar el orden: Settings pasa a índice 5.
- Mantener `nav_geology`, `nav_struct`, `nav_drillhole` sin cambios.

### 3.5 Persistencia

No se toca el esquema de datos:

```text
source_type, target_layer_id, auto_sync, custom_fields,
interp_inherit_geol, interp_inherit_drill
```

`DialogSettingsPersistence._data_pages()` puede seguir incluyendo
`self.dialog.page_interpretation` porque el alias apunta al tab y este conserva
`dump()/load()/reset()`. No hay migración de proyectos existentes.

Alternativa (si se quiere limpiar el alias): quitar `page_interpretation` de
`_data_pages()` y persistir el tab desde `SettingsPage`. Es más cambio y no aporta
beneficio inmediato; **no se recomienda en esta fase**.

### 3.6 Señales

Para evitar conexiones duplicadas:

- `DialogSignalManager` deja de listar `page_interpretation` en sus dos listas de pages.
- `SettingsPage` es el único responsable de `interpretation_tab.connect_signals()` /
  `disconnect_signals()`.
- `DialogSettingsPersistence` conserva el alias solo para `dump/load/reset` (no señales).

Si se añade `changed` al tab, `SettingsPage` lo conecta a su manejador; no se persiste
inmediatamente, se mantiene el guardado actual al aceptar/cerrar el diálogo.

### 3.7 Compatibilidad

Mantener un shim de una release:

```python
# gui/ui/pages/interpretation_page.py
from .settings.interpretation_tab import InterpretationTab

InterpretationPage = InterpretationTab
```

Así cualquier import/documentación antigua sigue funcionando. El shim se puede eliminar
cuando no queden referencias.

---

## 4. Archivos a modificar

| Archivo | Acción |
|---|---|
| `gui/ui/pages/settings/interpretation_tab.py` | **nuevo**: mover la UI/lógica |
| `gui/ui/pages/interpretation_page.py` | shim de compatibilidad |
| `gui/ui/pages/settings_page.py` | crear tab y añadirlo |
| `gui/ui/main_window.py` | quitar página/sidebar; alias |
| `gui/dialog_signal_manager.py` | quitar `page_interpretation` de las listas |
| `gui/dialog_settings_persistence.py` | sin cambios (alias) |
| `gui/interpretation_persistence_mixin.py` | sin cambios (alias) |
| `gui/dialog_interpretation_manager.py` | sin cambios (alias) |
| `tests/gui/test_ui_gating.py` | ajustar índices del sidebar |
| `tests/gui/test_settings_page.py` | tab presente y orden |
| `tests/gui/test_dialog_settings_persistence.py` | alias sigue funcionando |
| `tests/gui/test_main_dialog_settings.py` | alias/mocks |
| `docs/code_walkthrough*`, `docs/maintainer/DEVELOPER_ANALYSIS.md` | actualizar referencias |
| `docs/CHANGELOG.md`, `docs/DEVELOPMENT_LOG.md` | entrada del refactor |

---

## 5. Tests

### Unitarios

- `InterpretationTab` conserva:
  - `get_data()` con `source_type`, `target_layer_id`, `auto_sync`, `custom_fields`,
    `inherit_geology`, `inherit_drillholes`;
  - `dump()/load()` de herencia y campos;
  - `validate()` de nombres vacíos/duplicados;
  - `reset()`.
- `SettingsPage`:
  - tiene 5 tabs y “Interpretation” en el índice 3;
  - `interpretation_tab` es el mismo objeto que `MainWindow.page_interpretation`;
  - `connect_signals`/`disconnect_signals` no duplican conexiones.
- `MainWindow`:
  - sidebar tiene 6 ítems, sin “Interpretation”;
  - Settings es el índice 5;
  - `page_interpretation` sigue existiendo y apunta al tab.
- Persistencia:
  - `DialogSettingsPersistence` sigue llamando `dump/load` una vez;
  - no cambian las claves `interp_*`.

### Integración

- Abrir el diálogo, ir a Settings > Interpretation, cambiar herencia/campos, aceptar,
  reabrir y verificar que se restauran.
- Con una interpretación dibujada, el manager sigue leyendo
  `page_interpretation.get_data()` sin cambios.
- `test_qgis_smoke` sigue abriendo el diálogo y encontrando Settings.

### Gates

- Suite completa (≥827).
- `ruff`, `format`, `mypy`, `check_docs`, `forge validate`.
- `i18n-check` (si se añade el label “Interpretation” como cadena nueva).
- Analyzer: CC/module-size PASS.

---

## 6. Fases

1. **Fase 0 — Caracterización**: tests del comportamiento actual de
   `InterpretationPage` (get_data/dump/load/validate) y del sidebar. Deben pasar antes
   del movimiento.
2. **Fase 1 — Extracción del tab**: crear `InterpretationTab` y el shim; sin tocar
   `MainWindow` todavía. Tests del tab.
3. **Fase 2 — Integración**: añadir tab a `SettingsPage`, crear alias, quitar página del
   stacked/sidebar, ajustar `DialogSignalManager` y tests de índices.
4. **Fase 3 — Docs/cierre**: actualizar walkthroughs, changelog, devlog; suite y gates;
   commit y merge.

Cada fase es un commit atómico. No se mezcla con el fix de `section_feature_id` ya
mergeado.

---

## 7. Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| Romper `page_interpretation.get_data()` | alias al tab; tests de consumidores |
| Duplicar conexiones de señales | quitar la página de `DialogSignalManager`; solo `SettingsPage` conecta |
| Cambiar el contexto i18n | `tr` sigue usando `"InterpretationPage"` |
| Perder persistencia | mismas claves y protocolo `dump/load`; test de round-trip |
| Índices del sidebar | actualizar `test_ui_gating` y smoke |
| Tab demasiado alto | layout con scroll/stretch como Symbology; verificar en QGIS 3.28 y 4 |
| Acceso menos directo | opcional: botón “Interpretation settings…” en el panel de interpretación que abra `tab_widget.setCurrentWidget(interpretation_tab)` |

---

## 8. Criterios de aceptación

- Sidebar: DEM, Section, Geology, Structural, Drillholes, Settings (6 ítems).
- Settings tiene tabs Default, Advanced, Symbology, **Interpretation**, Plugin Information.
- `MainWindow.page_interpretation` sigue existiendo y apunta al tab.
- Las interpretaciones se cargan/guardan exactamente igual; claves sin cambios.
- `get_data()`, `dump()`, `load()`, `reset()` y `validate()` conservan contrato.
- Tests/gates verdes; sin regresión en QGIS 3.28 ni QGIS 4.
- `Invert line` y el fix de `section_feature_id` no se tocan.

---

**Aprobación requerida**: confirmar el movimiento y el alias de compatibilidad antes de
crear la rama `refactor/interpretation-settings-tab`.
