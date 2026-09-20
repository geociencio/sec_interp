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

> [!abstract] Resumen en una línea
> Orquesta **trayectoria 3D → proyección 2D → intervalos** para un sondaje individual.

**Ruta**: `core/services/drillhole/trajectory_engine.py` (111 líneas)
**Clase**: `TrajectoryEngine`
**Capa**: Core · Drillhole
**Tags**: #secinterp #core #drillhole

---

## 🧱 `process_single_hole()` — flujo

```python
def process_single_hole(self, hole_id, collar_point, collar_z, given_depth, survey_data, intervals, line_points, buffer_width, section_azimuth):
    final_depth = self.survey_processor.determine_final_depth(given_depth, survey_data, intervals)
    trajectory = scu.calculate_drillhole_trajectory(collar_point, collar_z, survey_data, section_azimuth, total_depth=final_depth)
    projected_traj = [p for p in scu.project_trajectory_to_section(trajectory, line_points) if p[5] <= buffer_width]
    hole_geol_data = self.interval_processor.interpolate_hole_intervals(projected_traj, intervals, buffer_width)
    hole_proj = self.create_drillhole_result(hole_id, projected_traj, hole_geol_data)
    return hole_geol_data, hole_proj
```

| Paso | Rol |
|------|-----|
| 1. `determine_final_depth` | Profundidad final desde survey/intervalos |
| 2. `calculate_drillhole_trajectory` + `project_trajectory_to_section` | 3D → 2D + filtro por buffer |
| 3. `interpolate_hole_intervals` | Geología a lo largo de la trayectoria proyectada |
| 4. `create_drillhole_result` | `DrillholeProjection` con `SpatialMeta` |

---

## 🔗 Notas relacionadas

- [[drillhole_service]] — lo orquesta por collar
- [[collar_processor]] / [[survey_processor]] / [[interval_processor]] — colaboradores

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
