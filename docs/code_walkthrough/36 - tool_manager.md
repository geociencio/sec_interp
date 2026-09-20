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

> [!abstract] Resumen en una línea
> Gestiona **map tools** del preview canvas: pan, measure e interpretation — creación, signals y toggling.

**Ruta**: `gui/dialog_tool_manager.py` (203 líneas)
**Clase**: `ToolManager`
**Capa**: GUI · Managers
**Tags**: #secinterp #gui #map-tools

---

## 🎯 ¿Por qué existe este archivo?

Sin manager, `main_dialog` crearía `QgsMapToolPan`, `ProfileMeasureTool`, `ProfileInterpretationTool` inline. Este archivo **centraliza**:

| Tool | Rol |
|------|-----|
| `QgsMapToolPan` | Navegación |
| `ProfileMeasureTool` | Medición multi-punto con snap |
| `ProfileInterpretationTool` | Digitización de polígonos |

> [!important] Inyección de callbacks
> `on_interpretation_finished` → `InterpretationManager`; `update_measurement_display` → `MainDialog`.

---

## 🧱 API

```python
class ToolManager:
    def __init__(self, canvas, preview_widget, translate, on_interpretation_finished, update_measurement_display, pan_tool=None, ...): ...
    def initialize_tools(self): ...  # crea si no inyectadas + connect_signals + setMapTool(pan)
    def connect_signals(self): ...   # idempotente
    def disconnect_signals(self): ...
    def toggle_measure_tool(self, checked): ...
    def toggle_interpretation_tool(self, checked): ...
```

---

## 🔗 Notas relacionadas

- [[20 - main_dialog]] — lo crea
- [[35 - interpretation_manager]] — destino de `on_interpretation_finished`

---

*Nota 36 de la bóveda SecInterp Code Walkthrough — v3.8.0*
