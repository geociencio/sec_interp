---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - interpretation
aliases:
  - dialog_interpretation_manager.py
  - InterpretationManager
cssclass: secinterp-note
---

# 35 — `gui/dialog_interpretation_manager.py`

> [!abstract] One-line summary
> Manages **interpretation polygons**: digitization, geological attribute inheritance, and dual persistence (project JSON or vector layer).

**Path**: `gui/dialog_interpretation_manager.py` (444 lines)
**Class**: `InterpretationManager`
**Layer**: GUI · Managers
**Tags**: #secinterp #gui #interpretation

---

## 🎯 Why does this file exist?

Without a manager, `main_dialog` would accumulate drag, `QgsSpatialIndex`, JSON, and `QgsProject`. This file **centralizes**:

| Responsibility | How |
|----------------|-----|
| Digitization | `handle_interpretation_finished(polygon)` |
| Attribute inheritance | `QgsSpatialIndex` over outcrops to copy `unit`/`attrs` to the polygon |
| Dual persistence | `sync_from_layer` / `save_to_layer` vs `QgsProject` JSON (`save_interpretations`) |
| Preview sync | Callback `_on_preview_update` → `preview_manager.update_from_checkboxes` |

> [!important] Shared cache
> Uses `PreviewCache` (injected) for `geol` access without recomputation.

---

## 🧱 API

```python
class InterpretationManager:
    def __init__(self, dialog, cache: PreviewCache | None = None): ...
    def handle_interpretation_finished(self, polygon: InterpretationPolygon): ...
    def clear_interpretations(self): ...
    def load_interpretations(self): ...  # layer or project
    def save_interpretations(self): ...  # dual source
    def sync_from_layer(self, layer): ...
    def set_preview_update_handler(self, handler): ...
```

---

## 🔗 Related notes

- [[20 - main_dialog]] — creates and wires it
- [[11 - domain]] — `InterpretationPolygon`
- [[26 - ui_pages]] — `InterpretationPage` (form)

---

*Note 35 of the SecInterp Code Walkthrough vault — v3.8.0*
