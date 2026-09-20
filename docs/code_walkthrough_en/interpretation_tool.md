---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - tools
aliases:
  - interpretation_tool.py
  - ProfileInterpretationTool
cssclass: secinterp-note
---

# `gui/tools/interpretation_tool.py`

> [!abstract] One-line summary
> `QgsMapTool` for **digitizing interpretation polygons** in the preview (vertices, snap, finalization).

**Path**: `gui/tools/interpretation_tool.py` (269 lines)
**Class**: `ProfileInterpretationTool(QgsMapToolEmitPoint)`
**Layer**: GUI · Tools
**Tags**: #secinterp #gui #tools

---

## 🧱 API

```python
class ProfileInterpretationTool(QgsMapToolEmitPoint):
    polygonFinished = pyqtSignal(InterpretationPolygon)

    def __init__(self, canvas: QgsMapCanvas): ...
    def activate(self): ...   # cursor Cross
    def deactivate(self): ...
    def canvasPressEvent(self, event): ...   # Left: add vertex, Right: remove last
    def canvasMoveEvent(self, event): ...    # rubber band + snap
    def keyPressEvent(self, event): ...      # Enter: finalize, Escape: cancel
    def finalize_polygon(self): ...  # uuid, random color, timestamp → InterpretationPolygon
```

> Delegates to `ProfileSnapper` + `QgsRubberBand`/`QgsVertexMarker`.

---

## 🔗 Related notes

- [[tool_manager]] — manages it
- [[interpretation_manager]] — consumes `polygonFinished`

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
