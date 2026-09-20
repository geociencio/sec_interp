---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - tools
aliases:
  - measure_tool.py
  - ProfileMeasureTool
cssclass: secinterp-note
---

# `gui/tools/measure_tool.py`

> [!abstract] Resumen en una línea
> `QgsMapTool` para medición **multi-punto** en el preview con snap y métricas de polilínea.

**Ruta**: `gui/tools/measure_tool.py` (330 líneas)
**Clase**: `ProfileMeasureTool(QgsMapToolEmitPoint)`
**Capa**: GUI · Tools
**Tags**: #secinterp #gui #tools

---

## 🧱 API

```python
class ProfileMeasureTool(QgsMapToolEmitPoint):
    measurementChanged = pyqtSignal(dict)
    measurementCleared = pyqtSignal()
    measurementFinished = pyqtSignal()

    def __init__(self, canvas: QgsMapCanvas): ...
    def canvasPressEvent(self, event): ...   # añade punto + snap
    def canvasMoveEvent(self, event): ...    # rubber band
    def keyPressEvent(self, event): ...      # Escape → reset
```

> Delegado en `ProfileSnapper` (snap) + `calculate_polyline_metrics` (core, math pura).

---

## 🔗 Notas relacionadas

- [[tool_manager]] — lo gestiona
- [[preview_renderer]] — canvas donde mide

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
