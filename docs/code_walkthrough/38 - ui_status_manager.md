---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - status
aliases:
  - ui_status_manager.py
  - UIStatusManager
cssclass: secinterp-note
---

# 38 — `gui/ui_status_manager.py`

> [!abstract] Resumen en una línea
> Gestiona **indicadores visuales y enable/disable** de la UI según validez de entradas.

**Ruta**: `gui/ui_status_manager.py` (85 líneas)
**Clase**: `UIStatusManager`
**Capa**: GUI
**Tags**: #secinterp #gui #status

---

## 🎯 ¿Por qué existe este archivo?

Sin manager, `main_dialog` tendría lógica de `setEnabled` dispersa. Este archivo **centraliza**:

| Método | Qué habilita/deshabilita |
|--------|--------------------------|
| `setup_indicators` | Iconos warning/success |
| `update_preview_checkbox_states` | `chk_topo/geol/struct/drillholes` |
| `update_button_state` | `btn_preview`, `Ok`, `btn_save` |

---

## 🔗 Notas relacionadas

- [[32 - state_manager]] — delega aquí
- [[33 - input_manager]] — `is_section_valid` / `can_preview` / `can_export`

---

*Nota 38 de la bóveda SecInterp Code Walkthrough — v3.8.0*
