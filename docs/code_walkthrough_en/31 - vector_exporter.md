---
tags:
  - secinterp
  - code-walkthrough
  - exporters
aliases:
  - vector_exporter.py
  - VectorExporter
cssclass: secinterp-note
---

# 31 — `exporters/vector_exporter.py`

> [!abstract] One-line summary
> The **generic vector exporter** for SHP, GPKG and DXF: prepares fields, creates the `QgsVectorFileWriter`, and writes `QgsFeature`s.

**Path**: `exporters/vector_exporter.py` (122 lines)
**Class**: `VectorExporter(BaseExporter)`
**Layer**: Exporters
**Tags**: #secinterp #exporters

---

## 🎯 Why does this file exist?

The 3 vector formats (SHP/GPKG/DXF) share the same QGIS **writer**. This exporter avoids duplicated code:

| Handled here | Detail |
|--------------|--------|
| Fields | `QgsFields` from the first feature's `attributes` |
| Geometry type | `settings["geometry_type"]` (default `LineString`) |
| CRS | `settings["crs"]` (default `EPSG:4326`) |
| Writer | `scu_io.create_vector_writer` |
| Features | `QgsFeature(fields)` + `writer.addFeature` |

> [!important] Inherits validation from `BaseExporter`
> Path security (`validate_export_path`) comes for free.

---

## 🧱 `export()` — flow

```python
class VectorExporter(BaseExporter):
    def get_supported_extensions(self) -> list[str]:
        return [".shp", ".gpkg", ".dxf"]

    def export(self, output_path: Path, features_data: list[dict[str, Any]], layer_name=None) -> bool:
        if not features_data:
            return False
        try:
            geometry_type = self.get_setting("geometry_type", QgsWkbTypes.Type.LineString)
            crs = self.get_setting("crs", QgsCoordinateReferenceSystem("EPSG:4326"))
            symb_mode = self.get_setting("symbology_export", QgsVectorFileWriter.SymbologyExport.NoSymbology)

            fields = self._prepare_fields(features_data)
            writer = scu_io.create_vector_writer(
                output_path, crs, fields, geometry_type,
                layer_name=layer_name, symbology_export=symb_mode,
            )
            if writer.hasError() != QgsVectorFileWriter.WriterError.NoError:
                logger.error(f"Failed to create writer: {writer.errorMessage()}")
                return False

            self._write_features(writer, features_data, fields)
            del writer
        except Exception:
            logger.exception(f"Vector export failed for {output_path}")
            return False
        else:
            return True
```

```mermaid
sequenceDiagram
    participant M as ExportService
    participant V as VectorExporter
    participant IO as scu_io
    participant W as QgsVectorFileWriter

    M->>V: export(path, features_data, layer_name)
    V->>V: _prepare_fields (QgsFields)
    V->>IO: create_vector_writer(path, crs, fields, geom_type, layer_name)
    IO-->>V: writer
    V->>V: _write_features(writer, features_data, fields)
    loop per feature
        V->>W: QgsFeature + addFeature
    end
    V-->>M: True/False
```

---

## 🧱 `_prepare_fields()`

```python
def _prepare_fields(self, features_data: list[dict[str, Any]]) -> QgsFields:
    fields = QgsFields()
    if features_data and "attributes" in features_data[0]:
        first_attrs = features_data[0]["attributes"]
        for key, value in first_attrs.items():
            if isinstance(value, int):
                fields.append(QgsField(key, QMetaType.Type.Int))
            elif isinstance(value, float):
                fields.append(QgsField(key, QMetaType.Type.Double))
            else:
                fields.append(QgsField(key, QMetaType.Type.QString))
    return fields
```

> [!warning] Schema from the first feature
> Fields are inferred from the **first** element. If other features have extra attributes, they are ignored. If the first feature is atypical, the schema is incomplete.

---

## 🧱 `_write_features()`

```python
def _write_features(self, writer, features_data, fields):
    for data in features_data:
        feature = QgsFeature(fields)
        if "geometry" in data:
            feature.setGeometry(data["geometry"])
        if "attributes" in data:
            attrs = data["attributes"]
            feature.setAttributes([attrs.get(field.name()) for field in fields])
        writer.addFeature(feature)
```

> [!tip] `layer_name` in `create_vector_writer`
> For GeoPackage, `layer_name` creates **sublayers** inside the container (`[SectionName]/`).

---

## 🏛️ Design patterns present

| Pattern | Where | Purpose |
|---------|-------|---------|
| **Template Method** | `BaseExporter` | Validate → prepare → write |
| **Type inference** | `_prepare_fields` | Infers `QgsField` by Python type |

---

## 🔗 Related notes

- [[00 - Index]] — vault index
- [[30 - base_exporter]] — base class and factory
- [[22 - dialog_export_manager]] — `export_preview` / `export_data` flows
- `sec_interp/core/utils/io.py` — `create_vector_writer`

---

*Note 31 of the SecInterp Code Walkthrough vault — v3.8.0*
