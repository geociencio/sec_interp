---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - input-manager
aliases:
  - dialog_input_manager.py
  - InputManager
cssclass: secinterp-note
---

# 33 — `gui/dialog_input_manager.py`

> [!abstract] One-line summary
> Aggregates **UI inputs**, builds `ValidationParams` via `ValidationExtractor`, and validates with `ProjectValidator`.

**Path**: `gui/dialog_input_manager.py` (200 lines)
**Class**: `InputManager`
**Layer**: GUI · Managers
**Tags**: #secinterp #gui #input-manager

---

## 🎯 Why does this file exist?

Without a manager, `main_dialog` would scatter `pages.dem.get_values()`. This file **centralizes**:

| Input | Source `Pages` |
|-------|----------------|
| DEM, Section, Geology, Structure, Drillhole | `pages.*` |
| Output path | `output_widget` |

> [!important] Validates with the core
> Builds `ValidationParams(LayerMetadata)` and delegates to `ProjectValidator.validate_all`.

---

## 🧱 API

```python
class InputManager:
    def get_validation_params(self) -> ValidationParams:
        # resolve_layer_metadata(line_lyr) → LayerMetadata
    def validate(self) -> tuple[bool, str]:
        try: ProjectValidator.validate_all(params)
        except ValidationError as e: return False, str(e)
        return True, ""
    def get_selected_values(self) -> dict: ...
```

---

## 🔗 Related notes

- [[20 - main_dialog]] — creates it in `_init_managers`
- [[16 - validation]] — `ProjectValidator`/`LayerMetadata`
- [[25 - adapters]] — `ValidationExtractor`

---

*Note 33 of the SecInterp Code Walkthrough vault — v3.8.0*
