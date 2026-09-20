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

> [!abstract] Resumen en una línea
> `QgsMapTool` para **digitizar polígonos** de interpretación en el preview (vértices, snap, finalización).

**Ruta**: `gui/tools/interpretation_tool.py` (269 líneas)
**Clase**: `ProfileInterpretationTool(QgsMapToolEmitPoint)`
**Capa**: GUI · Tools
**Tags**: #secinterp #gui #tools

---

## 🧱 API

```python
class ProfileInterpretationTool(QgsMapToolEmitPoint):
    polygonFinished = pyqtSignal(InterpretationPolygon)

    def __init__(self, canvas: QgsMapCanvas): ...
    def activate(self): ...   # cursor Cross, log_critical_operation
    def deactivate(self): ...
    def canvasPressEvent(self, event): ...   # Left: add vertex, Right: remove last
    def canvasMoveEvent(self, event): ...    # rubber band + snap
    def keyPressEvent(self, event): ...      # Enter: finalize, Escape: cancel
    def finalize_polygon(self): ...  # uuid, color random, timestamp → InterpretationPolygon
```

> Delegado en `ProfileSnapper` + `QgsRubberBand`/`QgsVertexMarker`.

---

## 🔗 Notas relacionadas

- [[tool_manager]] — lo gestiona
- [[interpretation_manager]] — consume `polygonFinished`

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
