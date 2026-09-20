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

> [!abstract] One-line summary
> `QgsMapTool` for **multi-point** measurement in the preview with snap and polyline metrics.

**Path**: `gui/tools/measure_tool.py` (330 lines)
**Class**: `ProfileMeasureTool(QgsMapToolEmitPoint)`
**Layer**: GUI · Tools
**Tags**: #secinterp #gui #tools

---

## 🧱 API

```python
class ProfileMeasureTool(QgsMapToolEmitPoint):
    measurementChanged = pyqtSignal(dict)
    measurementCleared = pyqtSignal()
    measurementFinished = pyqtSignal()

    def __init__(self, canvas: QgsMapCanvas): ...
    def canvasPressEvent(self, event): ...   # adds point + snap
    def canvasMoveEvent(self, event): ...    # rubber band
    def keyPressEvent(self, event): ...      # Escape → reset
```

> Delegates to `ProfileSnapper` (snap) + `calculate_polyline_metrics` (core, pure math).

---

## 🔗 Related notes

- [[tool_manager]] — manages it
- [[preview_renderer]] — canvas where it measures

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
