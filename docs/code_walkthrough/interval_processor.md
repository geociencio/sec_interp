---
tags:
  - secinterp
  - code-walkthrough
  - core
  - drillhole
aliases:
  - interval_processor.py
  - IntervalProcessor
cssclass: secinterp-note
---

# `core/services/drillhole/interval_processor.py`

> [!abstract] Resumen en una línea
> Interpola **intervalos geológicos** a lo largo de la trayectoria proyectada y devuelve `GeologySegment`s.

**Ruta**: `core/services/drillhole/interval_processor.py` (50 líneas)
**Clase**: `IntervalProcessor`
**Capa**: Core · Drillhole
**Tags**: #secinterp #core #drillhole

---

## 🧱 `interpolate_hole_intervals()` — flujo

```python
def interpolate_hole_intervals(self, traj, intervals, buffer_width) -> list[GeologySegment]:
    if not intervals: return []
    rich_intervals = [(fd, td, {"unit": lith, "from": fd, "to": td}) for fd, td, lith in intervals]
    tuples = scu.interpolate_intervals_on_trajectory(traj, rich_intervals, buffer_width)
    for attr, points_2d, points_3d, points_3d_proj in tuples:
        segments.append(GeologySegment(unit_name=str(attr.get("unit", "Unknown")), geometry_wkt=None, attributes=attr, points=points_2d, points_3d=points_3d, points_3d_projected=points_3d_proj))
    return segments
```

> Delega en `scu.interpolate_intervals_on_trajectory` (matemática pura) y envuelve en `GeologySegment`.

---

## 🔗 Notas relacionadas

- [[trajectory_engine]] — lo llama
- [[drillhole_service]] — orquestador

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
