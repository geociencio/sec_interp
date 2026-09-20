---
tags:
  - secinterp
  - code-walkthrough
  - exporters
  - drillhole
aliases:
  - drillhole_exporters.py
  - DrillholeTraceVectorExporter
cssclass: secinterp-note
---

# `exporters/drillhole_exporters.py`

> [!abstract] Resumen en una línea
> Exporta **trazas de sondajes 2D** a SHP/GPKG/DXF (LineString).

**Ruta**: `exporters/drillhole_exporters.py` (239 líneas)
**Clase**: `DrillholeTraceVectorExporter` (+ `DrillholeIntervalVectorExporter`)
**Capa**: Exporters
**Tags**: #secinterp #exporters #drillhole

---

## 🧱 `export()` — flujo

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

## 🔗 Notas relacionadas

- [[base_exporter]] — contrato
- [[drillhole_service]] — origen

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
