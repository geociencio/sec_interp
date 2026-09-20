---
tags:
  - secinterp
  - code-walkthrough
  - exporters
aliases:
  - drillhole_3d_exporter.py
  - DrillholeTrace3DExporter
cssclass: secinterp-note
---

# `exporters/drillhole_3d_exporter.py`

> [!abstract] One-line summary
> Exports **3D drillhole traces and intervals** to SHP/GPKG/DXF (LineStringZ / PolygonZ).

**Path**: `exporters/drillhole_3d_exporter.py` (243 lines)
**Classes**: `DrillholeTrace3DExporter`, `DrillholeInterval3DExporter`
**Layer**: Exporters
**Tags**: #secinterp #exporters

---

## 🧱 `DrillholeTrace3DExporter.export()` — flow

```python
def export(self, output_path, data: dict[str, Any], layer_name=None) -> bool:
    drillhole_data = data.get("drillhole_data")
    crs = data.get("crs")
    use_projected = data.get("use_projected", False)
    if not drillhole_data or not crs: return False
    # fields: hole_id, depth, azimuth, inclination
    # geometry: QgsLineStringZ from trajectory (x,y,z)
    # writer: scu_io.create_vector_writer(path, crs, fields, QgsWkbTypes.LineStringZ, layer_name)
```

> `DrillholeInterval3DExporter` similar with `QgsWkbTypes.PolygonZ` for intervals.

---

## 🔗 Related notes

- [[base_exporter]] — contract
- [[drillhole_service]] — data source

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
