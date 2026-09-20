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

> [!abstract] Resumen en una línea
> Orquesta **estado visual + persistencia**: delega en `DialogSettingsPersistence` y `UIStatusManager`.

**Ruta**: `gui/dialog_state_manager.py` (117 líneas)
**Clase**: `StateManager`
**Capa**: GUI · Managers
**Tags**: #secinterp #gui #state-manager

---

## 🎯 ¿Por qué existe este archivo?

Sin manager, `main_dialog.py` mezclaría `QgsSettings` con iconos de estado. Este archivo **desacopla**:

| Delegado | Rol |
|----------|-----|
| `DialogSettingsPersistence` | `QgsSettings` → `PluginSettings` (load/save) |
| `UIStatusManager` | Iconos, enable/disable de botones/checkboxes |

---

## 🧱 API

```python
class StateManager:
    def __init__(self, dialog):
        self.persistence = DialogSettingsPersistence(dialog)
        self.status_manager = UIStatusManager(dialog)

    # delegación visual
    def setup_indicators(self): self.status_manager.setup_indicators()
    def update_all(self): self.status_manager.update_all()

    # persistencia
    def save_settings(self): self.persistence.save_settings()
    def load_settings(self): self.persistence.load_settings()
```

---

## 🔗 Notas relacionadas

- [[main_dialog]] — lo crea en `_init_managers`
- [[ui_pages]] — pages cuyos estados gestiona
- [[config]] — `ConfigService` subyacente

---

*Nota 32 de la bóveda SecInterp Code Walkthrough — v3.8.0*
