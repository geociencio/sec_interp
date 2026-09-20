---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - signals
aliases:
  - dialog_signal_manager.py
  - SignalManager
cssclass: secinterp-note
---

# 34 — `gui/dialog_signal_manager.py`

> [!abstract] Resumen en una línea
> Centraliza **todas las conexiones signal/slot** del diálogo — idempotente y agrupado por dominio.

**Ruta**: `gui/dialog_signal_manager.py` (354 líneas)
**Clase**: `SignalManager`
**Capa**: GUI · Managers
**Tags**: #secinterp #gui #signals

---

## 🎯 ¿Por qué existe este archivo?

Sin manager, `main_dialog` tendría 50+ `button.clicked.connect(...)` dispersos. Este archivo:

| Grupo | Señales |
|-------|---------|
| Preview | `generate_btn → preview_manager.generate_preview`, checkboxes → `update_from_checkboxes` |
| Export | `export_btn → export_manager.export_*` |
| Tools | `measure/interpret toggles → tool_manager` |
| State | `layer combos → state_manager.update_all` |
| Navigation | `sidebar → stacked_widget` |

> [!important] Idempotente
> `connect_all()` primero hace `disconnect_all()` → puede llamarse en cada `run()` sin duplicar.

---

## 🧱 API

```python
class SignalManager:
    def __init__(self, dialog, preview_manager, export_manager, tool_manager, state_manager): ...
    def connect_all(self): ...   # disconnect + connect por grupos
    def disconnect_all(self): ... # contextlib.suppress(TypeError, RuntimeError)
```

---

## 🔗 Notas relacionadas

- [[20 - main_dialog]] — lo crea y lo llama en cada `run()`
- [[21 - dialog_preview_manager]] — destino de señales de preview
- [[32 - state_manager]] — destino de señales de estado

---

*Nota 34 de la bóveda SecInterp Code Walkthrough — v3.8.0*
