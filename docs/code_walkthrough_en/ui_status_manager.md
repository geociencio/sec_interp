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

> [!abstract] One-line summary
> Manages **visual indicators and enable/disable** of the UI based on input validity.

**Path**: `gui/ui_status_manager.py` (85 lines)
**Class**: `UIStatusManager`
**Layer**: GUI
**Tags**: #secinterp #gui #status

---

## 🎯 Why does this file exist?

Without a manager, `main_dialog` would scatter `setEnabled` logic. This file **centralizes**:

| Method | What it enables/disables |
|--------|--------------------------|
| `setup_indicators` | Warning/success icons |
| `update_preview_checkbox_states` | `chk_topo/geol/struct/drillholes` |
| `update_button_state` | `btn_preview`, `Ok`, `btn_save` |

---

## 🔗 Related notes

- [[state_manager]] — delegates here
- [[input_manager]] — `is_section_valid` / `can_preview` / `can_export`

---

*Note 38 of the SecInterp Code Walkthrough vault — v3.8.0*
