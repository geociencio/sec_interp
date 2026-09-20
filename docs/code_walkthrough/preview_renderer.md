---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - preview
  - renderer
aliases:
  - preview_renderer.py
  - PreviewRenderer
cssclass: secinterp-note
---

# `gui/preview_renderer.py`

> [!abstract] Resumen en una línea
> Orquestador de render del preview: delega en `PreviewLayerFactory`, `PreviewAxesManager` y `PreviewLegendRenderer`.

**Ruta**: `gui/preview_renderer.py` (306 líneas)
**Clase**: `PreviewRenderer`
**Capa**: GUI · Preview
**Tags**: #secinterp #gui #preview #renderer

---

## 🎯 ¿Por qué existe este archivo?

Renderizar el preview mezcla capas, ejes y leyenda. Este archivo **orquesta**:

| Componente | Rol |
|------------|-----|
| `PreviewLayerFactory` | Crea capas de memoria + estilos |
| `PreviewAxesManager` | Rejilla y etiquetas de ejes |
| `PreviewLegendRenderer` | Leyenda |
| `PreviewOptimizer` | Simplificación LOD |

---

## 🧱 API

```python
class PreviewRenderer:
    def __init__(self, canvas: QgsMapCanvas | None = None): ...
    def render(self, topo_data, geol_data, struct_data, vert_exag, dip_line_length, max_points, preserve_extent, drillhole_data, interp_data): ...  # crea capas → aplica ejes → leyenda → canvas.setLayers
    @property
    def active_units(self): ...  # proxy a layer_factory
```

---

## 🔗 Notas relacionadas

- [[renderers]] — renderers de capa
- [[preview_layer_factory]] — factory que usa
- [[preview_state]] — output

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
