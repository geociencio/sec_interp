---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - preview
aliases:
  - preview_state.py
  - PreviewCache
cssclass: secinterp-note
---

# 39 — `gui/preview_state.py`

> [!abstract] One-line summary
> Two **shared** containers for managers: `PreviewCache` (`topo/geol/struct/drillhole`) and `RenderState` (canvas + layers).

**Path**: `gui/preview_state.py` (57 lines)
**Classes**: `PreviewCache`, `RenderState`
**Layer**: GUI
**Tags**: #secinterp #gui #preview

---

## 🧱 `PreviewCache`

```python
_CACHE_KEYS = ("topo", "geol", "struct", "drillhole")
class PreviewCache:
    def __init__(self): self._data = dict.fromkeys(_CACHE_KEYS)
    def get(self, key, default=None): ...
    def update(self, other=None, **kwargs): ...
```

> [!tip] Shared by injection
> Created in `main_dialog._init_managers` and passed to `PreviewManager` and `InterpretationManager`.

---

## 🧱 `RenderState`

```python
class RenderState:
    def __init__(self): self.canvas = None; self.layers = []
    def update(self, canvas, layers): ...
```

> Source of truth for `ExportManager` (previously loose `current_canvas/current_layers`).

---

## 🔗 Related notes

- [[20 - main_dialog]] — creates it
- [[21 - dialog_preview_manager]] — writes `cached_data`
- [[22 - dialog_export_manager]] — reads `render_state`

---

*Note 39 of the SecInterp Code Walkthrough vault — v3.8.0*
