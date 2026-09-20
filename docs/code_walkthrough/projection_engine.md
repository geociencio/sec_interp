---
tags:
  - secinterp
  - code-walkthrough
  - core
  - drillhole
aliases:
  - projection_engine.py
  - ProjectionEngine
cssclass: secinterp-note
---

# `core/services/drillhole/projection_engine.py`

> [!abstract] Resumen en una línea
> Proyecta un **punto a la línea** y devuelve `(dist_along, offset)` con `hypot`.

**Ruta**: `core/services/drillhole/projection_engine.py` (30 líneas)
**Clase**: `ProjectionEngine`
**Capa**: Core · Drillhole
**Tags**: #secinterp #core #drillhole

---

## 🧱 `project_point_to_line()` — matemática

```python
@staticmethod
def project_point_to_line(pt, line_points) -> tuple[float, float]:
    dist_along, nearest = project_point_onto_polyline(pt, line_points)
    offset = math.hypot(pt[0] - nearest[0], pt[1] - nearest[1])
    return dist_along, offset
```

> Delega en `geometry_utils/measurement.project_point_onto_polyline` + `math.hypot`.

---

## 🔗 Notas relacionadas

- [[collar_processor]] — lo usa
- [[trajectory_engine]] — proyección de trayectoria

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
