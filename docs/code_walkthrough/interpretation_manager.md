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

> [!abstract] Resumen en una línea
> Gestiona **polígonos de interpretación**: digitización, herencia de atributos geológicos, y persistencia (JSON de proyecto o capa vectorial).

> [!info] Refactor 2026-09-20
> Este manager de 444 líneas se descompuso en mixins ([[interpretation_mixins]]); `InterpretationManager` es ahora una clase de **107 líneas**.

**Ruta**: `gui/dialog_interpretation_manager.py` (107 líneas; antes 444)
**Clase**: `InterpretationManager`
**Capa**: GUI · Managers
**Tags**: #secinterp #gui #interpretation

---

## 🎯 ¿Por qué existe este archivo?

Sin manager, `main_dialog` acumularía drag, `QgsSpatialIndex`, JSON y `QgsProject`. Este archivo **centraliza**:

| Responsabilidad | Cómo |
|-----------------|------|
| Digitización | `handle_interpretation_finished(polygon)` |
| Herencia de atributos | `QgsSpatialIndex` sobre outcrops para copiar `unit`/`attrs` al polígono |
| Persistencia dual | `sync_from_layer` / `save_to_layer` vs `QgsProject` JSON (`save_interpretations`) |
| Sincronización con preview | Callback `_on_preview_update` → `preview_manager.update_from_checkboxes` |

> [!important] Cache compartida
> Usa `PreviewCache` (inyectada) para acceso a `geol` sin recalcular.

---

## 🧱 API

```python
class InterpretationManager:
    def __init__(self, dialog, cache: PreviewCache | None = None): ...
    def handle_interpretation_finished(self, polygon: InterpretationPolygon): ...
    def clear_interpretations(self): ...
    def load_interpretations(self): ...  # layer o proyecto
    def save_interpretations(self): ...  # dual source
    def sync_from_layer(self, layer): ...
    def set_preview_update_handler(self, handler): ...
```

---

## 🔗 Notas relacionadas

- [[main_dialog]] — lo crea y lo cablea
- [[domain]] — `InterpretationPolygon`
- [[ui_pages]] — `InterpretationPage` (formulario)

---

*Nota 35 de la bóveda SecInterp Code Walkthrough — v3.8.0*
