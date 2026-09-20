---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - preview
aliases:
  - preview_renderer.py
  - PreviewRenderer
cssclass: secinterp-note
---

# `gui/preview_renderer.py`

> [!abstract] One-line summary
> Preview render orchestrator: delegates to `PreviewLayerFactory`, `PreviewAxesManager`, and `PreviewLegendRenderer`.

**Path**: `gui/preview_renderer.py` (306 lines)
**Class**: `PreviewRenderer`
**Layer**: GUI · Preview
**Tags**: #secinterp #gui #preview

---

## 🎯 Why does this file exist?

Rendering the preview mixes layers, axes, and legend. This file **orchestrates**:

| Component | Role |
|-----------|------|
| `PreviewLayerFactory` | Creates memory layers + styles |
| `PreviewAxesManager` | Grid and axis labels |
| `PreviewLegendRenderer` | Legend |
| `PreviewOptimizer` | LOD simplification |

---

## 🧱 API

```python
class PreviewRenderer:
    def __init__(self, canvas: QgsMapCanvas | None = None): ...
    def render(self, topo_data, geol_data, struct_data, vert_exag, dip_line_length, max_points, preserve_extent, drillhole_data, interp_data): ...
    @property
    def active_units(self): ...
```

---

## 🔗 Related notes

- [[renderers]] — layer renderers
- [[preview_layer_factory]] — factory it uses
- [[preview_state]] — output

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
