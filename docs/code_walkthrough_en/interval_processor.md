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

> [!abstract] One-line summary
> Interpolates **geological intervals** along the projected trajectory and returns `GeologySegment`s.

**Path**: `core/services/drillhole/interval_processor.py` (50 lines)
**Class**: `IntervalProcessor`
**Layer**: Core · Drillhole
**Tags**: #secinterp #core #drillhole

---

## 🧱 `interpolate_hole_intervals()` — flow

```python
def interpolate_hole_intervals(self, traj, intervals, buffer_width) -> list[GeologySegment]:
    if not intervals: return []
    rich_intervals = [(fd, td, {"unit": lith, "from": fd, "to": td}) for fd, td, lith in intervals]
    tuples = scu.interpolate_intervals_on_trajectory(traj, rich_intervals, buffer_width)
    for attr, points_2d, points_3d, points_3d_proj in tuples:
        segments.append(GeologySegment(unit_name=str(attr.get("unit", "Unknown")), geometry_wkt=None, attributes=attr, points=points_2d, points_3d=points_3d, points_3d_projected=points_3d_proj))
    return segments
```

> Delegates to `scu.interpolate_intervals_on_trajectory` (pure math) and wraps in `GeologySegment`.

---

## 🔗 Related notes

- [[trajectory_engine]] — calls it
- [[drillhole_service]] — orchestrator

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
