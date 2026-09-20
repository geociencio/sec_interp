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

> [!abstract] Resumen en una línea
> Proyecta **collares desacoplados** a la línea de sección y filtra por buffer.

**Ruta**: `core/services/drillhole/collar_processor.py` (100 líneas)
**Clase**: `CollarProcessor`
**Capa**: Core · Drillhole
**Tags**: #secinterp #core #drillhole

---

## 🧱 `extract_and_project_detached()` — flujo

```python
def extract_and_project_detached(self, collar_data, line_points, buffer_width, collar_id_field, collar_z_field, collar_depth_field, pre_sampled_z=None) -> DrillholeProjection | None:
    point = collar_data.get("point")
    if not point: return None
    hole_id = collar_data.get("id") or attrs.get(collar_id_field)
    if not hole_id: return None
    z = self._extract_z(attrs, collar_z_field, hole_id, pre_sampled_z)
    depth = self._extract_depth(attrs, collar_depth_field)
    dist_along, offset = ProjectionEngine.project_point_to_line(point, line_points)
    if offset <= buffer_width:
        return DrillholeProjection(hole_id=str(hole_id), distance=dist_along, elevation=z, offset=offset, total_depth=depth)
    return None
```

| Paso | Rol |
|------|-----|
| `_extract_z / _extract_depth` | Lee `z`/`depth` de atributos o `pre_sampled_z` |
| `ProjectionEngine.project_point_to_line` | `(dist_along, offset)` |
| Filtro | `offset ≤ buffer` → `DrillholeProjection` o `None` |

---

## 🔗 Notas relacionadas

- [[drillhole_service]] — lo llama por collar
- [[projection_engine]] — matemática de proyección

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
