---
tags:
  - secinterp
  - code-walkthrough
  - exporters
aliases:
  - dxf_exporter.py
  - DXFExporter
cssclass: secinterp-note
---

# `exporters/dxf_exporter.py`

> [!abstract] One-line summary
> Exports **vectors to DXF** with `QgsVectorFileWriter` (optional symbology).

**Path**: `exporters/dxf_exporter.py` (126 lines)
**Class**: `DXFExporter(BaseExporter)`
**Layer**: Exporters
**Tags**: #secinterp #exporters

---

## 🧱 `export()` — flow

```python
def export(self, output_path: Path, features_data: list[dict[str, Any]], layer_name=None) -> bool:
    geometry_type = self.get_setting("geometry_type", QgsWkbTypes.Type.LineString)
    crs = self.get_setting("crs", QgsCoordinateReferenceSystem("EPSG:4326"))
    fields = self._prepare_fields(features_data)
    writer = scu_io.create_vector_writer(output_path, crs, fields, geometry_type, layer_name=layer_name, symbology_export=symb_mode)
    for data in features_data:
        feature = QgsFeature(fields)
        feature.setGeometry(data["geometry"])
        feature.setAttributes([data["attributes"].get(f.name()) for f in fields])
        writer.addFeature(feature)
```

> Similar to `VectorExporter` but with `symbology_export` and `layer_name` for DXF (layers).

---

## 🔗 Related notes

- [[base_exporter]] — contract
- [[vector_exporter]] — generic counterpart

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
