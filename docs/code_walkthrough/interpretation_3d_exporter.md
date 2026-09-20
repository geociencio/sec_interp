---
tags:
  - secinterp
  - code-walkthrough
  - exporters
  - 3d
aliases:
  - interpretation_3d_exporter.py
  - Interpretation3DExporter
cssclass: secinterp-note
---

# `exporters/interpretation_3d_exporter.py`

> [!abstract] Resumen en una línea
> Exporta **interpretaciones 3D** (polígonos con Z) a SHP/GPKG/DXF 2.5D.

**Ruta**: `exporters/interpretation_3d_exporter.py` (465 líneas)
**Clase**: `Interpretation3DExporter(BaseExporter)`
**Capa**: Exporters
**Tags**: #secinterp #exporters #3d

---

## 🧱 `export()` — flujo

```python
def export(self, output_path: str, data: dict[str, Any], layer_name=None) -> bool:
    interpretations = data.get("interpretations", [])
    section_line = data.get("section_line")
    if not self._validate_export_input(interpretations, section_line): return False
    fields, sorted_keys = self._prepare_fields(interpretations)
    origin_x, origin_y, azimuth = self._calculate_section_geometry(section_line)
    features = self._collect_projected_features(interpretations, fields, sorted_keys, origin_x, origin_y, azimuth)
    # writer: scu_io.create_vector_writer(path, crs, fields, QgsWkbTypes.PolygonZ, layer_name)
    # addFeature per interpretación proyectada (dist, elev → x,y,z)
```

> Convierte `(distance, elevation)` → `(x, y, z)` usando `origin` + `azimuth`.

---

## 🔗 Notas relacionadas

- [[base_exporter]] — contrato
- [[interpretation_manager]] — origen de datos

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
