---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - state-manager
aliases:
  - dialog_state_manager.py
  - StateManager
cssclass: secinterp-note
---

# 32 — `gui/dialog_state_manager.py`

> [!abstract] One-line summary
> Orchestrates **visual state + persistence**: delegates to `DialogSettingsPersistence` and `UIStatusManager`.

**Path**: `gui/dialog_state_manager.py` (117 lines)
**Class**: `StateManager`
**Layer**: GUI · Managers
**Tags**: #secinterp #gui #state-manager

---

## 🎯 Why does this file exist?

Without a manager, `main_dialog.py` would mix `QgsSettings` with status icons. This file **decouples** them:

| Delegate | Role |
|----------|------|
| `DialogSettingsPersistence` | `QgsSettings` → `PluginSettings` (load/save) |
| `UIStatusManager` | Icons, enable/disable of buttons/checkboxes |

---

## 🧱 API

```python
class StateManager:
    def __init__(self, dialog):
        self.persistence = DialogSettingsPersistence(dialog)
        self.status_manager = UIStatusManager(dialog)
    def setup_indicators(self): self.status_manager.setup_indicators()
    def update_all(self): self.status_manager.update_all()
    def save_settings(self): self.persistence.save_settings()
    def load_settings(self): self.persistence.load_settings()
```

---

## 🔗 Related notes

- [[main_dialog]] — creates it in `_init_managers`
- [[ui_pages]] — pages whose state it manages
- [[config]] — underlying `ConfigService`

---

*Note 32 of the SecInterp Code Walkthrough vault — v3.8.0*
