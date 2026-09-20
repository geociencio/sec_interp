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

> [!abstract] Resumen en una línea
> Calcula intervalos “nice” (1-2-5) y dibuja rejilla + ejes para el preview.

**Ruta**: `gui/preview_axes_manager.py` (204 líneas)
**Clase**: `PreviewAxesManager`
**Capa**: GUI · Preview
**Tags**: #secinterp #gui #preview

---

## 🎯 ¿Por qué existe este archivo?

La rejilla debe ser legible a cualquier exageración vertical. Este manager:

| Método | Rol |
|--------|-----|
| `get_nice_interval(target)` | Secuencia 1-2-5-10 con `log10` |
| `_compute_grid(extent, vert_exag)` | Intervalos X/Y y offsets |
| `create_axes_layer(...)` | `QgsVectorLayer` memoria con `QgsLineSymbol` + `QgsPalLayerSettings` |

---

## 🔗 Notas relacionadas

- [[preview_renderer]] — lo usa
- [[preview_layer_factory]] — capas del perfil

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
