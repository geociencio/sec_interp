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

> [!abstract] Resumen en una línea
> Agrega **entradas de la UI**, construye `ValidationParams` vía `ValidationExtractor` y valida con `ProjectValidator`.

**Ruta**: `gui/dialog_input_manager.py` (200 líneas)
**Clase**: `InputManager`
**Capa**: GUI · Managers
**Tags**: #secinterp #gui #input-manager

---

## 🎯 ¿Por qué existe este archivo?

Sin manager, `main_dialog` haría `pages.dem.get_values()` disperso. Este archivo **centraliza**:

| Entrada | Origen `Pages` |
|---------|----------------|
| DEM, Section, Geology, Structure, Drillhole | `pages.*` |
| Output path | `output_widget` |

> [!important] Valida con el core
> Construye `ValidationParams(LayerMetadata)` y delega en `ProjectValidator.validate_all`.

---

## 🧱 API

```python
class InputManager:
    def __init__(self, pages: Pages, output_widget, translate): ...
    def get_validation_params(self) -> ValidationParams:
        # resolve_layer_metadata(line_lyr) → LayerMetadata
        # retorna ValidationParams para ProjectValidator
    def validate(self) -> tuple[bool, str]:
        try: ProjectValidator.validate_all(params)
        except ValidationError as e: return False, str(e)
        return True, ""
    def get_selected_values(self) -> dict: ...
```

---

## 🔗 Notas relacionadas

- [[20 - main_dialog]] — lo crea en `_init_managers`
- [[16 - validation]] — `ProjectValidator`/`LayerMetadata`
- [[25 - adapters]] — `ValidationExtractor`

---

*Nota 33 de la bóveda SecInterp Code Walkthrough — v3.8.0*
