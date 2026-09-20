---
tags:
  - secinterp
  - code-walkthrough
  - core
  - drillhole
aliases:
  - collar_processor.py
  - CollarProcessor
cssclass: secinterp-note
---

# `core/services/drillhole/collar_processor.py`

> [!abstract] One-line summary
> Projects **detached collars** onto the section line and filters by buffer.

**Path**: `core/services/drillhole/collar_processor.py` (100 lines)
**Class**: `CollarProcessor`
**Layer**: Core · Drillhole
**Tags**: #secinterp #core #drillhole

---

## 🧱 `extract_and_project_detached()` — flow

```python
def extract_and_project_detached(self, collar_data, line_points, buffer_width, collar_id_field, collar_z_field, collar_depth_field, pre_sampled_z=None) -> DrillholeProjection | None:
    point = collar_data.get("point")
    if not point: return None
    hole_id = collar_data.get("id") or attrs.get(collar_id_field)
    z = self._extract_z(attrs, collar_z_field, hole_id, pre_sampled_z)
    depth = self._extract_depth(attrs, collar_depth_field)
    dist_along, offset = ProjectionEngine.project_point_to_line(point, line_points)
    if offset <= buffer_width:
        return DrillholeProjection(hole_id=str(hole_id), distance=dist_along, elevation=z, offset=offset, total_depth=depth)
    return None
```

| Step | Role |
|------|------|
| `_extract_z / _extract_depth` | Reads `z`/`depth` from attributes or `pre_sampled_z` |
| `ProjectionEngine.project_point_to_line` | `(dist_along, offset)` |
| Filter | `offset ≤ buffer` → `DrillholeProjection` or `None` |

---

## 🔗 Related notes

- [[drillhole_service]] — calls it per collar
- [[projection_engine]] — projection math

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
