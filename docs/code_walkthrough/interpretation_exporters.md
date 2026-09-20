---
tags:
  - secinterp
  - code-walkthrough
  - exporters
  - interpretation
aliases:
  - interpretation_exporters.py
  - Interpretation2DExporter
cssclass: secinterp-note
---

# `exporters/interpretation_exporters.py`

> [!abstract] Resumen en una línea
> Exporta **interpretaciones 2D** (dist,elev) a vectores (SHP/GPKG/DXF) con `QgsGeometry.fromPolygonXY`.

**Ruta**: `exporters/interpretation_exporters.py` (146 líneas)
**Clase**: `Interpretation2DExporter(BaseExporter)`
**Capa**: Exporters
**Tags**: #secinterp #exporters #interpretation

---

## 🧱 `export()` — flujo

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

## 🔗 Notas relacionadas

- [[base_exporter]] — contrato
- [[interpretation_manager]] — origen

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
