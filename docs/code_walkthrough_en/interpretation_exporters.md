---
tags:
  - secinterp
  - code-walkthrough
  - exporters
aliases:
  - interpretation_exporters.py
  - Interpretation2DExporter
cssclass: secinterp-note
---

# `exporters/interpretation_exporters.py`

> [!abstract] One-line summary
> Exports **2D interpretations** (dist,elev) to vectors (SHP/GPKG/DXF) with `QgsGeometry.fromPolygonXY`.

**Path**: `exporters/interpretation_exporters.py` (146 lines)
**Class**: `Interpretation2DExporter(BaseExporter)`
**Layer**: Exporters
**Tags**: #secinterp #exporters

---

## 🧱 `export()` — flow

```python
def export(self, output_path: Path, data: dict[str, Any], layer_name=None) -> bool:
    interpretations = data.get("interpretations", [])
    fields = QgsFields()
    fields.append(QgsField("unit_name", QMetaType.Type.QString))
    writer = scu_io.create_vector_writer(output_path, crs, fields, QgsWkbTypes.Polygon, layer_name=layer_name)
    for interp in interpretations:
        geom = QgsGeometry.fromPolygonXY([[QgsPointXY(x, y) for x, y in interp.vertices_2d]])
        feature = QgsFeature(fields)
        feature.setGeometry(geom)
        feature.setAttributes([interp.unit_name])
        writer.addFeature(feature)
```

---

## 🔗 Related notes

- [[base_exporter]] — contract
- [[interpretation_manager]] — source

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
