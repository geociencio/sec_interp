---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - preview
aliases:
  - preview_state.py
  - PreviewCache
  - RenderState
cssclass: secinterp-note
---

# 39 — `gui/preview_state.py`

> [!abstract] Resumen en una línea
> Dos contenedores **compartidos** por managers: `PreviewCache` (datos `topo/geol/struct/drillhole`) y `RenderState` (canvas + layers).

**Ruta**: `gui/preview_state.py` (57 líneas)
**Clases**: `PreviewCache`, `RenderState`
**Capa**: GUI
**Tags**: #secinterp #gui #preview

---

## 🧱 `PreviewCache`

```python
_CACHE_KEYS = ("topo", "geol", "struct", "drillhole")

class PreviewCache:
    def __init__(self): self._data = dict.fromkeys(_CACHE_KEYS)
    def get(self, key, default=None): ...
    def update(self, other=None, **kwargs): ...
    def __getitem__(self, key): ...
    def __setitem__(self, key, value): ...
```

> [!tip] Compartido por inyección
> Creado en `main_dialog._init_managers` y pasado a `PreviewManager` e `InterpretationManager`.

---

## 🧱 `RenderState`

```python
class RenderState:
    def __init__(self): self.canvas = None; self.layers = []
    def update(self, canvas, layers): ...
```

> Fuente de verdad para `ExportManager` (antes `current_canvas/current_layers` sueltos).

---

## 🔗 Notas relacionadas

- [[20 - main_dialog]] — lo crea
- [[21 - dialog_preview_manager]] — escribe `cached_data`
- [[22 - dialog_export_manager]] — lee `render_state`

---

*Nota 39 de la bóveda SecInterp Code Walkthrough — v3.8.0*
