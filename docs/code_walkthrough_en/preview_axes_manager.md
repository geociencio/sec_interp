---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - preview
aliases:
  - preview_axes_manager.py
  - PreviewAxesManager
cssclass: secinterp-note
---

# `gui/preview_axes_manager.py`

> [!abstract] One-line summary
> Computes “nice” (1-2-5) intervals and draws grid + axes for the preview.

**Path**: `gui/preview_axes_manager.py` (204 lines)
**Class**: `PreviewAxesManager`
**Layer**: GUI · Preview
**Tags**: #secinterp #gui #preview

---

## 🎯 Why does this file exist?

The grid must be readable at any vertical exaggeration. This manager:

| Method | Role |
|--------|------|
| `get_nice_interval(target)` | 1-2-5-10 sequence with `log10` |
| `_compute_grid(extent, vert_exag)` | X/Y intervals and offsets |
| `create_axes_layer(...)` | `QgsVectorLayer` memory with `QgsLineSymbol` + `QgsPalLayerSettings` |

---

## 🔗 Related notes

- [[preview_renderer]] — uses it
- [[preview_layer_factory]] — profile layers

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
