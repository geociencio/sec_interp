# Implementation Plan: Live Symbology & Legend Styling Preview (Goal 1.1 / v3.11.0)

**Phase**: v3.11.0 — Goal 1.1 (3D Interpretation & Symbology Enhancements)
**Status**: 🚧 EN PROGRESO — Fase 0 (decisiones) y **Fase 1 ✅ implementada**
(pestaña Symbology con estilos por capa, modo de color topo movido desde Section, live
re-render, persistencia en proyecto). Pendiente: Fase 2 (editor por unidad completo),
Fase 3 (opciones de leyenda), Fase 4 (presets).
**Created**: 2026-09-23
**Referencias**: `gui/ui/pages/settings_page.py` (+ `settings/{default,advanced,info}_tab.py`),
`gui/preview_side_panel.py`, `gui/renderers/*` (`color_manager`, `topo_renderer`,
`structure_renderer`, `drillhole_renderer`, `geology_renderer`, `interpretation_renderer`),
`gui/preview_layer_factory.py`, `gui/dialog_settings_persistence.py`,
`gui/dialog_signal_manager.py`, `plugin/render_pipeline.py`,
`core/models/settings_model.py`, `exporters/{image,pdf,svg}_exporter.py`.

---

## 0. Resumen ejecutivo

Goal 1.1 pide un **editor de simbología con vista previa en vivo bajo el sidebar de
Settings**. v3.10.0 ya entregó el **núcleo por unidad** (panel lateral con ocultar/color
persistido, incluida litología de sondeos). Este plan cierra 1.1:

1. un **editor por capa** (topografía, estructuras, trazas de sondeo, interpretaciones)
   en una pestaña **Symbology** de Settings, con cambios **en vivo**;
2. un **editor por unidad** más completo (color/ocultar/**renombrar/reordenar**),
   compartiendo la lógica con el panel lateral;
3. **opciones de leyenda** (posición/tamaño/columnas/qué incluir) para preview y export;
4. **persistencia** de todo el estilo (proyecto/settings) y, opcionalmente, **presets**.

**Principio**: todo es Present (estilos sobre memory layers); nunca se modifica la capa
origen ni el core de datos. Reutiliza `ColorManager` y el patrón de señales existente.

---

## 1. Contexto técnico verificado

| Hecho | Fuente |
|---|---|
| Settings = `QTabWidget` (Default, Advanced, Plugin Information) | `settings_page.py:45-55` |
| Pestañas son `QWidget` con `changed`/`get_data`/`reset`/`connect_signals` | `settings/default_tab.py` |
| Colores por unidad ya centralizados + overrides/hidden persistentes | `gui/renderers/color_manager.py` |
| Editor por unidad ya existe en el panel lateral (ocultar/color) | `gui/preview_side_panel.py` |
| Modo de color topo (gradiente/simple) vive en la página **Section** | `gui/ui/pages/section_page.py` |
| Colores de estructuras/trazas/interpretaciones están **hardcodeados** | `structure_renderer.py`, `drillhole_renderer.py`, `interpretation_renderer.py` |
| Leyenda del export = `PreviewLegendRenderer` (layout fijo) | `gui/preview_legend_renderer.py` |
| Re-render desde caché disponible | `preview_manager.update_from_checkboxes()` |
| Persistencia de estilo por unidad ya existe (`unit_style`) | `gui/dialog_settings_persistence.py` |

---

## 2. Fase 0 — Auditoría y consolidación (sin código)

Definir la **fuente única de verdad** del estilo y evitar controles duplicados:

- **Topografía**: el modo gradiente/simple ya está en la página *Section*. Decidir si se
  **mueve** a Settings → Symbology o se **refleja** (mismo estado, dos vistas).
- **Unidades geológicas / litologías de sondeo**: hoy en el panel lateral. Decidir si el
  editor completo vive en Settings y el panel lateral queda como vista rápida.
- Definir el objeto de estado: ampliar `ColorManager` + un nuevo `SymbologyState`
  (o sección en `PreviewSettings`) con: color/visibilidad de capas, overrides por unidad,
  orden y renombrado.

**Entregable**: mini-doc de decisión en este mismo archivo (tabla de "dónde vive cada control").

## 3. Fase 1 — Pestaña Symbology con vista previa viva

**Archivos**: `gui/ui/pages/settings/symbology_tab.py` (nuevo),
`gui/ui/pages/settings_page.py`, `gui/dialog_facade_mixin.py`, `gui/dialog_signal_manager.py`,
`gui/preview_layer_factory.py`, `gui/renderers/*`.

- Nueva pestaña **Symbology** (`SettingsPage.tab_widget`) con grupos:
  - **Topography**: modo (gradiente/simple), rampa/color, grosor de línea.
  - **Structures**: color y grosor de los ticks.
  - **Drillholes**: color/grosor de traza; etiquetas on/off.
  - **Interpretations**: color por defecto de nuevos polígonos.
- Cada control emite `changed` → **re-render inmediato** del preview con caché
  (`preview_manager.update_from_checkboxes()`), sin invalidar S2 (es presentación).
- Estilos aplicados en `PreviewLayerFactory`/renderers vía `apply_style(layer, **style)`
  (ya admite kwargs). Los colores dejan de ser constantes hardcodeadas y pasan a estado.
- i18n con `tr()`; desconexión simétrica.

## 4. Fase 2 — Editor por unidad completo (color/ocultar/renombrar/reordenar)

**Archivos**: `gui/renderers/color_manager.py`, `gui/preview_side_panel.py`,
`gui/ui/widgets/unit_style_editor.py` (nuevo, compartido), `gui/preview_layer_factory.py`.

- Extraer la fila de leyenda (`LegendRow`) a un **widget reutilizable**
  (`UnitStyleEditor`) usado por la pestaña Symbology y por el panel lateral.
- Ampliar `ColorManager` con:
  - `rename(old, new)` (mapa de etiquetas) y `order` (lista ordenada).
  - `set_color`, `set_hidden` (ya existen).
- Aplicar el **orden** y **etiquetas** al construir las categorías y al listar la leyenda.
- "Restablecer estilo por unidad" y "restablecer todo".

## 5. Fase 3 — Opciones de leyenda (preview + export)

**Archivos**: `gui/preview_side_panel.py`, `gui/preview_legend_renderer.py`,
`exporters/{image,pdf,svg}_exporter.py`, `gui/ui/pages/settings/symbology_tab.py`.

- Opciones: **posición** (arriba-derecha/izquierda/abajo), **tamaño** (fuente, alto),
  **columnas**/máximo de ítems con "+N más", **opacidad**, y **qué incluir**
  (topografía/estructuras/sondeos/unidades/interpretaciones).
- Reutilizar `PreviewLegendRenderer` para el export (respetando opciones) y el panel
  lateral para el preview. "Elide" ya aplicado en el panel.

## 6. Fase 4 — Persistencia y presets (opcional)

- Persistir todo el estilo en `PreviewSettings`/`ColorManager.dump()` +
  `DialogSettingsPersistence` (proyecto + QgsSettings), con migración tolerante.
- **Presets** de simbología (guardar/cargar) — puede quedar para una fase posterior.

---

## 7. Tests

- `SymbologyTab`: get_data/reset/changed, controles por capa.
- Renderers: color/grosor configurables (topo ya cubierto; añadir estructuras/sondeos/interp).
- `ColorManager`: rename/order/overrides/hidden; roundtrip de dump/load extendido.
- Panel/lado: filas reflejan rename/orden; reordenado en vivo.
- Export: `PreviewLegendRenderer` respeta posición/tamaño/columnas.
- Integración: cambiar un estilo re-renderiza desde caché (no invalida S2).
- Gates: `ruff`/format, suite, `qgis-analyzer --max-cc 10`, gates CC/Module Size/i18n,
  e **import real en QGIS 4** (lección: los mocks no detectan imports Qt incorrectos).

## 8. Riesgos

- **Duplicación de controles** (topo en Section vs Settings): resolver en Fase 0 con SSoT.
- **Regresión de rendimiento** al re-renderizar por cada cambio de estilo: caché ya lo
  hace barato; agrupar con debounce si hace falta.
- **Filtro hidden compartido** geología/sondeo (mismo ColorManager): decidir si se
  desacopla por capa o se mantiene por nombre de litología.
- **Persistencia de nombres dinámicos** de unidad (unidad ausente → ignorar).
- **Export vs panel**: dos rutas de leyenda pueden divergir; usar la misma fuente de datos.

## 9. Fuera de alcance

- Plantillas de estilo por proyecto (presets) → fase posterior.
- Editor de simbología de la capa origen en QGIS (solo memory layers del preview).
- Remuestreo bilineal / suavizado (ya cubierto en v3.9.1).

## 10. Decisiones (resueltas 2026-09-23)

1. **Modo de color topo** → **se MUEVE** de *Section* a *Settings → Symbology* (SSoT).
2. **Editor por unidad** → en *Settings → Symbology* la opción **más óptima**: editor
   completo como SSoT y el **panel lateral** como vista rápida reutilizando el mismo
   widget (`UnitStyleEditor`) y el mismo `ColorManager`.
3. **Renombrar/reordenar** → afecta **también a las etiquetas del canvas** (p. ej., traza
   de sondeo `hole_id` y etiquetas de leyenda).
4. **Persistencia** → en el **proyecto** (`SecInterp` entries), vía
   `DialogSettingsPersistence`.
5. **Presets** → **en esta versión** (guardar/cargar estilos).

## 11. Fases / entregables (resumen)

| Fase | Alcance | Estimación |
|---|---|---|
| 0 | Auditoría/SSoT (docs) | ~0.25 sesión |
| 1 | Pestaña Symbology + estilos por capa, live | ~0.75 sesión |
| 2 | Editor por unidad (rename/order) compartido | ~0.5 sesión |
| 3 | Opciones de leyenda (preview + export) | ~0.5 sesión |
| 4 | Persistencia avanzada / presets (opcional) | ~0.5 sesión |
