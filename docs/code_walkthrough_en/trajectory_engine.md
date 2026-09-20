---
tags:
  - secinterp
  - code-walkthrough
  - core
  - drillhole
aliases:
  - trajectory_engine.py
  - TrajectoryEngine
cssclass: secinterp-note
---

# `core/services/drillhole/trajectory_engine.py`

> [!abstract] One-line summary
> Orchestrates **3D trajectory → 2D projection → intervals** for a single drillhole.

**Path**: `core/services/drillhole/trajectory_engine.py` (111 lines)
**Class**: `TrajectoryEngine`
**Layer**: Core · Drillhole
**Tags**: #secinterp #core #drillhole

---

## 🧱 `process_single_hole()` — flow

```python
def process_single_hole(self, hole_id, collar_point, collar_z, given_depth, survey_data, intervals, line_points, buffer_width, section_azimuth):
    final_depth = self.survey_processor.determine_final_depth(given_depth, survey_data, intervals)
    trajectory = scu.calculate_drillhole_trajectory(collar_point, collar_z, survey_data, section_azimuth, total_depth=final_depth)
    projected_traj = [p for p in scu.project_trajectory_to_section(trajectory, line_points) if p[5] <= buffer_width]
    hole_geol_data = self.interval_processor.interpolate_hole_intervals(projected_traj, intervals, buffer_width)
    hole_proj = self.create_drillhole_result(hole_id, projected_traj, hole_geol_data)
    return hole_geol_data, hole_proj
```

| Step | Role |
|------|------|
| 1. `determine_final_depth` | Final depth from survey/intervals |
| 2. `calculate_drillhole_trajectory` + `project_trajectory_to_section` | 3D → 2D + buffer filter |
| 3. `interpolate_hole_intervals` | Geology along projected trajectory |
| 4. `create_drillhole_result` | `DrillholeProjection` with `SpatialMeta` |

---

## 🔗 Related notes

- [[drillhole_service]] — orchestrates per collar
- [[collar_processor]] / [[survey_processor]] / [[interval_processor]] — collaborators

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
