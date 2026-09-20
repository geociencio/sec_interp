---
tags:
  - secinterp
  - code-walkthrough
  - exporters
aliases:
  - drillhole_exporters.py
  - DrillholeTraceVectorExporter
cssclass: secinterp-note
---

# `exporters/drillhole_exporters.py`

> [!abstract] One-line summary
> Exports **2D drillhole traces** to SHP/GPKG/DXF (LineString).

**Path**: `exporters/drillhole_exporters.py` (239 lines)
**Class**: `DrillholeTraceVectorExporter` (+ `DrillholeIntervalVectorExporter`)
**Layer**: Exporters
**Tags**: #secinterp #exporters

---

## 🧱 `export()` — flow

```python
def export(self, output_path, data: dict[str, Any], layer_name=None) -> bool:
    drillhole_data = data.get("drillhole_data")
    crs = data.get("crs")
    if not drillhole_data or not crs: return False
    # fields: hole_id, depth, azimuth
    # geometry: QgsGeometry.fromPolylineXY([QgsPointXY(dist, elev) for p in hole.points_3d_projected])
    # writer: scu_io.create_vector_writer(path, crs, fields, QgsWkbTypes.LineString, layer_name)
```

---

## 🔗 Related notes

- [[base_exporter]] — contract
- [[drillhole_service]] — source

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
