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

> [!abstract] One-line summary
> Projects a **point onto the line** and returns `(dist_along, offset)` via `hypot`.

**Path**: `core/services/drillhole/projection_engine.py` (30 lines)
**Class**: `ProjectionEngine`
**Layer**: Core · Drillhole
**Tags**: #secinterp #core #drillhole

---

## 🧱 `project_point_to_line()` — math

```python
@staticmethod
def project_point_to_line(pt, line_points) -> tuple[float, float]:
    dist_along, nearest = project_point_onto_polyline(pt, line_points)
    offset = math.hypot(pt[0] - nearest[0], pt[1] - nearest[1])
    return dist_along, offset
```

> Delegates to `geometry_utils/measurement.project_point_onto_polyline` + `math.hypot`.

---

## 🔗 Related notes

- [[collar_processor]] — uses it
- [[trajectory_engine]] — trajectory projection

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
