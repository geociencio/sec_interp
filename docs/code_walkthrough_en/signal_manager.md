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

> [!abstract] One-line summary
> Centralizes **all signal/slot wiring** for the dialog — idempotent and grouped by domain.

**Path**: `gui/dialog_signal_manager.py` (354 lines)
**Class**: `SignalManager`
**Layer**: GUI · Managers
**Tags**: #secinterp #gui #signals

---

## 🎯 Why does this file exist?

Without a manager, `main_dialog` would scatter 50+ `button.clicked.connect(...)`. This file:

| Group | Signals |
|-------|---------|
| Preview | `generate_btn → preview_manager.generate_preview`, checkboxes → `update_from_checkboxes` |
| Export | `export_btn → export_manager.export_*` |
| Tools | `measure/interpret toggles → tool_manager` |
| State | `layer combos → state_manager.update_all` |
| Navigation | `sidebar → stacked_widget` |

> [!important] Idempotent
> `connect_all()` first calls `disconnect_all()` → safe to call on every `run()` without duplication.

---

## 🧱 API

```python
class SignalManager:
    def __init__(self, dialog, preview_manager, export_manager, tool_manager, state_manager): ...
    def connect_all(self): ...   # disconnect + connect by groups
    def disconnect_all(self): ... # contextlib.suppress(TypeError, RuntimeError)
```

---

## 🔗 Related notes

- [[main_dialog]] — creates it and calls it on every `run()`
- [[dialog_preview_manager]] — preview signal destination
- [[state_manager]] — state signal destination

---

*Note 34 of the SecInterp Code Walkthrough vault — v3.8.0*
