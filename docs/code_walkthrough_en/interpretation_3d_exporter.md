---
tags:
  - secinterp
  - code-walkthrough
  - exporters
aliases:
  - interpretation_3d_exporter.py
  - Interpretation3DExporter
cssclass: secinterp-note
---

# `exporters/interpretation_3d_exporter.py`

> [!abstract] One-line summary
> Exports **3D interpretations** (Z-aware polygons) to SHP/GPKG/DXF 2.5D.

**Path**: `exporters/interpretation_3d_exporter.py` (465 lines)
**Class**: `Interpretation3DExporter(BaseExporter)`
**Layer**: Exporters
**Tags**: #secinterp #exporters

---

## 🧱 `export()` — flow

```python
def export(self, output_path: str, data: dict[str, Any], layer_name=None) -> bool:
    interpretations = data.get("interpretations", [])
    section_line = data.get("section_line")
    if not self._validate_export_input(interpretations, section_line): return False
    fields, sorted_keys = self._prepare_fields(interpretations)
    origin_x, origin_y, azimuth = self._calculate_section_geometry(section_line)
    features = self._collect_projected_features(interpretations, fields, sorted_keys, origin_x, origin_y, azimuth)
    # writer: scu_io.create_vector_writer(path, crs, fields, QgsWkbTypes.PolygonZ, layer_name)
```

> Converts `(distance, elevation)` → `(x, y, z)` via `origin` + `azimuth`.

---

## 🔗 Related notes

- [[base_exporter]] — contract
- [[interpretation_manager]] — data source

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
