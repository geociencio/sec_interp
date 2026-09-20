---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - preview
aliases:
  - preview_layer_factory.py
  - PreviewLayerFactory
cssclass: secinterp-note
---

# 40 — `gui/preview_layer_factory.py`

> [!abstract] One-line summary
> Factory that creates **memory layers** for the preview (topo, geology, drillholes, structures, interpretations) and styles them with renderers.

**Path**: `gui/preview_layer_factory.py` (471 lines)
**Class**: `PreviewLayerFactory`
**Layer**: GUI · Preview
**Tags**: #secinterp #gui #preview

---

## 🎯 Why does this file exist?

The preview doesn't use project layers; it generates **memory layers** on the fly, assigns geometry, and styles them.

| Layer created | Method | Renderer |
|---------------|--------|----------|
| Topo | `create_topo_layer(ProfileData)` | `TopoRenderer` |
| Geology | `create_geology_layer(GeologyData)` | `GeologyRenderer` |
| Drillholes | `create_drillhole_layers(...)` | `DrillholeRenderer` |
| Structures | `create_structure_layer(...)` | `StructureRenderer` |
| Interpretations | `create_interpretation_layer(...)` | `InterpretationRenderer` |

> Uses `gui/utils.create_memory_layer` and `core/utils/geometry_utils/optimization.PreviewOptimizer` for LOD simplification.

---

## 🔗 Related notes

- [[23 - renderers]] — renderers it applies
- [[39 - preview_state]] — output `RenderState`

---

*Note 40 of the SecInterp Code Walkthrough vault — v3.8.0*
