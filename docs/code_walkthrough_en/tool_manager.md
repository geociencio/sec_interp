---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - map-tools
aliases:
  - dialog_tool_manager.py
  - ToolManager
cssclass: secinterp-note
---

# 36 — `gui/dialog_tool_manager.py`

> [!abstract] One-line summary
> Manages **map tools** for the preview canvas: pan, measure, and interpretation — creation, signals, and toggling.

**Path**: `gui/dialog_tool_manager.py` (203 lines)
**Class**: `ToolManager`
**Layer**: GUI · Managers
**Tags**: #secinterp #gui #map-tools

---

## 🎯 Why does this file exist?

Without a manager, `main_dialog` would inline `QgsMapToolPan`, `ProfileMeasureTool`, `ProfileInterpretationTool`. This file **centralizes**:

| Tool | Role |
|------|------|
| `QgsMapToolPan` | Navigation |
| `ProfileMeasureTool` | Multi-point measurement with snap |
| `ProfileInterpretationTool` | Polygon digitization |

> [!important] Callback injection
> `on_interpretation_finished` → `InterpretationManager`; `update_measurement_display` → `MainDialog`.

---

## 🧱 API

```python
class ToolManager:
    def __init__(self, canvas, preview_widget, translate, on_interpretation_finished, update_measurement_display, pan_tool=None, ...): ...
    def initialize_tools(self): ...  # creates if not injected + connect_signals + setMapTool(pan)
    def connect_signals(self): ...   # idempotent
    def disconnect_signals(self): ...
    def toggle_measure_tool(self, checked): ...
    def toggle_interpretation_tool(self, checked): ...
```

---

## 🔗 Related notes

- [[main_dialog]] — creates it
- [[interpretation_manager]] — target of `on_interpretation_finished`

---

*Note 36 of the SecInterp Code Walkthrough vault — v3.8.0*
