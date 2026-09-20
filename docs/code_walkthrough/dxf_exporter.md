---
tags:
  - secinterp
  - code-walkthrough
  - exporters
  - dxf
aliases:
  - dxf_exporter.py
  - DXFExporter
cssclass: secinterp-note
---

# `exporters/dxf_exporter.py`

> [!abstract] Resumen en una línea
> Exporta **vectores a DXF** con `QgsVectorFileWriter` (simbología opcional).

**Ruta**: `exporters/dxf_exporter.py` (126 líneas)
**Clase**: `DXFExporter(BaseExporter)`
**Capa**: Exporters
**Tags**: #secinterp #exporters #dxf

---

## 🧱 `export()` — flujo

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

> Similar a `VectorExporter` pero con `symbology_export` y `layer_name` para DXF (capas).

---

## 🔗 Notas relacionadas

- [[base_exporter]] — contrato
- [[vector_exporter]] — homólogo genérico

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
