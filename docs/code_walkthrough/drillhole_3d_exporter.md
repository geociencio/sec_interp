---
tags:
  - secinterp
  - code-walkthrough
  - exporters
  - 3d
aliases:
  - drillhole_3d_exporter.py
  - DrillholeTrace3DExporter
cssclass: secinterp-note
---

# `exporters/drillhole_3d_exporter.py`

> [!abstract] Resumen en una línea
> Exporta **trazas e intervalos 3D** de sondajes a SHP/GPKG/DXF (LineStringZ / PolygonZ).

**Ruta**: `exporters/drillhole_3d_exporter.py` (243 líneas)
**Clases**: `DrillholeTrace3DExporter`, `DrillholeInterval3DExporter`
**Capa**: Exporters
**Tags**: #secinterp #exporters #3d

---

## 🧱 `DrillholeTrace3DExporter.export()` — flujo

```python
def export(self, output_path, data: dict[str, Any], layer_name=None) -> bool:
    drillhole_data = data.get("drillhole_data")
    crs = data.get("crs")
    use_projected = data.get("use_projected", False)
    if not drillhole_data or not crs: return False
    # fields: hole_id, depth, azimuth, inclination (QMetaType)
    # geometry: QgsLineStringZ desde trajectory (x,y,z)
    # writer: scu_io.create_vector_writer(path, crs, fields, QgsWkbTypes.LineStringZ, layer_name)
```

> `DrillholeInterval3DExporter` similar pero con `QgsWkbTypes.PolygonZ` para intervalos.

---

## 🔗 Notas relacionadas

- [[base_exporter]] — contrato
- [[drillhole_service]] — origen de datos

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
