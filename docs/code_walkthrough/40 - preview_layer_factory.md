---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - preview
  - factory
aliases:
  - preview_layer_factory.py
  - PreviewLayerFactory
cssclass: secinterp-note
---

# 40 — `gui/preview_layer_factory.py`

> [!abstract] Resumen en una línea
> Factory que crea **capas de memoria** para el preview (topo, geología, sondajes, estructuras, interpretaciones) y les aplica los renderers.

**Ruta**: `gui/preview_layer_factory.py` (471 líneas)
**Clase**: `PreviewLayerFactory`
**Capa**: GUI · Preview
**Tags**: #secinterp #gui #preview #factory

---

## 🎯 ¿Por qué existe este archivo?

El preview no usa capas del proyecto; genera **memory layers** temporales, les asigna geometría y los viste.

| Capa creada | Método | Renderer |
|-------------|--------|----------|
| Topo | `create_topo_layer(ProfileData)` | `TopoRenderer` |
| Geología | `create_geology_layer(GeologyData)` | `GeologyRenderer` |
| Sondajes | `create_drillhole_layers(...)` | `DrillholeRenderer` |
| Estructuras | `create_structure_layer(...)` | `StructureRenderer` |
| Interpretaciones | `create_interpretation_layer(...)` | `InterpretationRenderer` |

> Usa `gui/utils.create_memory_layer` y `core/utils/geometry_utils/optimization.PreviewOptimizer` para simplificación LOD.

---

## 🔗 Notas relacionadas

- [[23 - renderers]] — renderers que aplica
- [[39 - preview_state]] — output `RenderState`

---

*Nota 40 de la bóveda SecInterp Code Walkthrough — v3.8.0*
