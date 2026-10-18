# Implementation Plan: Preview Side Panel — Legend + Interpretations + Per-Unit Interaction (v3.10.0)

**Phase**: v3.10.0
**Status**: ✅ IMPLEMENTADO 2026-09-23 — L-A (panel + interpretaciones; overlay retirado)
y L-B (ocultar/editar color por unidad, persistido; estructuras/sondeos intactos).
**Created**: 2026-09-23
**Referencias**: `gui/legend_widget.py`, `gui/preview_legend_renderer.py`,
`gui/ui/pages/preview_page.py`, `gui/preview_renderer.py`,
`gui/preview_layer_factory.py`, `gui/renderers/color_manager.py`,
`gui/renderers/base_renderer.py`, `gui/renderers/geology_renderer.py`,
`gui/renderers/drillhole_renderer.py`, `plugin/render_pipeline.py`,
`gui/dialog_interpretation_manager.py`, `gui/dialog_settings_persistence.py`,
`exporters/{image,pdf,svg}_exporter.py`.

---

## 0. Resumen ejecutivo

Hoy la leyenda es un **overlay translúcido** sobre el canvas (`LegendWidget`), con
layout fijo (Arial 8, esquina superior derecha, sin scroll ni elide) → con muchas
unidades tapa el perfil y trunca nombres. Se mueve a un **panel lateral colapsable**
(splitter) junto al canvas, se añade la **lista de interpretaciones** y, además, se
habilita **ocultar y editar el color por unidad geológica** (núcleo de Goal 1.1).
La leyenda del **export** (PNG/PDF/SVG) se mantiene como overlay en la imagen.

**Decisiones** (2026-09-23): panel = leyenda + interpretaciones (solo listadas);
comportamiento = splitter colapsable con ancho persistido; overlay retirado; export
sin cambios; interacción por unidad **solo geología**, persistida entre sesiones.

---

## 1. Contexto técnico verificado

| Hecho | Fuente |
|---|---|
| Leyenda = overlay translúcido sobre el canvas | `gui/legend_widget.py`, `main_dialog.py:82` |
| Render de leyenda con QPainter, layout fijo | `gui/preview_legend_renderer.py` |
| Se refresca tras cada preview | `plugin/render_pipeline.py:70` |
| Export dibuja leyenda sobre la imagen/página | `exporters/{image,pdf,svg}_exporter.py` |
| Colores por unidad cacheados y compartidos (geología + intervalos) | `gui/renderers/color_manager.py`, `drillhole_renderer.py` |
| `active_units` se limpia en cada cleanup | `gui/preview_renderer.py:293`, `preview_layer_factory.py:54` |
| Interpretaciones con `name/type/color` | `core/domain/entities.py` `InterpretationPolygon` |
| Preview = VBox (canvas+status, Controls, Results) dentro del splitter principal | `gui/ui/pages/preview_page.py`, `gui/ui/main_window.py` |

---

## 2. Fase L-A — Panel (sustituye al overlay)

### 2.1 Nuevo `gui/ui/widgets/preview_side_panel.py`
`PreviewSidePanel(QWidget)`:
- **Legend** (`QGroupBox`): `QListWidget` con `ElideRight` y tooltip por fila. Ítems:
  Topography (línea azul), Structures (rojo) y unidades geológicas (cuadradito de color).
- **Interpretations** (`QGroupBox`): lista de `dialog.interpretations` (color + `name` + `type`), solo lectura.
- API: `update_legend(renderer, visible)`, `update_interpretations(items)`,
  `set_legend_visible(bool)`; señales `unit_visibility_changed(str, bool)` y
  `unit_color_changed(str, QColor)` (usadas en L-B).

### 2.2 `gui/ui/pages/preview_page.py`
- Dentro del preview, `QSplitter(Qt.Horizontal)`: izquierda = frame del canvas
  (+barra de estado); derecha = `PreviewSidePanel`. Controls y Results debajo.
- `dump/load/reset`: `show_legend` (ya existe) + **tamaño/estado del splitter**.
- `self.side_panel` expuesto para el refresco.

### 2.3 Retirar overlay
- Eliminar `gui/legend_widget.py` y sus usos: `main_dialog` (creación),
  `dialog_lifecycle_mixin` (cleanup), `render_pipeline` (`legend_widget.update_legend`).
- `PreviewLegendRenderer` se mantiene (lo usan los exporters).

### 2.4 Refresco
- `plugin/render_pipeline.py`: tras render →
  `self.dlg.preview_widget.side_panel.update_legend(self.preview_renderer, show_legend)`.
- `InterpretationManager`/callbacks (add/finish/clear/delete) →
  `side_panel.update_interpretations(self.dialog.interpretations)`.

### 2.5 Tests
- Actualizar `test_main_dialog_signals_wiring.py` y `test_multi_session_persistence.py`
  (hoy parchean `LegendWidget`).
- Nuevos: población de leyenda, lista de interpretaciones, mostrar/ocultar, splitter.
- Mantener `test_preview_legend_renderer.py` y `test_renderer_draw_legend` (export).

---

## 3. Fase L-B — Interacción por unidad (Goal 1.1)

### 3.1 `gui/renderers/color_manager.py`
- Estado que **no se limpia** con `active_units`:
  - `_overrides: dict[str, QColor]`, `_hidden: set[str]`, `_known_units: set[str]`.
  - `register_units(names)`, `get_color` (override > cache > asignado),
    `set_color(name, QColor)`, `set_hidden(name, bool)`, `is_hidden(name)`,
    `hidden_units()`, `overrides()`.
  - `dump()/load()` (overrides hex + hidden).

### 3.2 `gui/renderers/base_renderer.py`
- `build_categorized_line_style(..., hidden: set[str] | None = None)`: omite las
  categorías ocultas. Por defecto `None` → **drillhole_renderer sin cambios**.

### 3.3 `gui/renderers/geology_renderer.py`
- Pasa `hidden=color_manager.hidden_units()` (ocultado acotado a geología).

### 3.4 `gui/preview_layer_factory.py`
- `create_geol_layer`: `color_manager.register_units({s.unit_name for s in geol_data})`
  (todas, incl. ocultas) y categorías solo visibles; `active_units` alimenta el panel.

### 3.5 Panel interactivo
- Fila: checkbox de visibilidad + `QToolButton` de color + etiqueta (elide).
- Toggle → `color_manager.set_hidden` + re-render desde caché
  (`preview_manager.update_from_checkboxes`), **sin invalidar S2**.
- Color → `QColorDialog.getColor` → `color_manager.set_color` + re-render.
- `PreviewSidePanel` recibe (callback/ref) al `layer_factory.color_manager`.

### 3.6 Persistencia
- `DialogSettingsPersistence`: guarda/carga `unit_overrides`/`unit_hidden` (proyecto,
  `SecInterp`) y las aplica a `color_manager` en `load_settings`. Persistir por nombre;
  unidad ausente → ignorada.

### 3.7 Tests
- `ColorManager`: override gana, hidden, register, los overrides/hidden **no** se
  limpian al resetear `active_units`, dump/load.
- `GeologyRenderer`: unidad oculta sin categoría; override aplicado; **drillhole intacto**.
- Panel: emite toggle/color; integración con `color_manager`.
- Persistencia: roundtrip.

---

## 4. Fuera de alcance
- Color/visibilidad editables por **interpretación** (solo listadas).
- Opciones de posición/tamaño de la leyenda en export.
- Remuestreo bilineal de la topografía.

## 5. Riesgos
- `ColorManager` compartido con intervalos de sondeo → ocultado acotado a geología
  mediante parámetro explícito.
- Re-render por toggle es cacheado (coste bajo); vigilar spam de señales.
- Nombres de unidad dinámicos en persistencia (tolerante a ausencias).
- Ensanchar el panel reduce el área del perfil → splitter colapsable + ancho persistido.

## 6. Commits previstos
1. `docs(plans): add preview side panel + unit interaction plan (v3.10.0)`
2. `feat(gui): move legend to a collapsible preview side panel with interpretations list` (L-A)
3. `feat(gui): per-unit visibility and color in the preview legend (Goal 1.1 core)` (L-B)
4. `chore(docs): close session side_panel_legend`
