---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - adapters
  - structure
aliases:
  - structure_extractor.py
  - StructureExtractor
cssclass: secinterp-note
---

# `gui/adapters/structure_extractor.py`

> [!abstract] Resumen en una línea
> Adapter **Extract** de estructuras: lee línea + estructuras, filtra por buffer y muestrea DEM → datos desacoplados.

**Ruta**: `gui/adapters/structure_extractor.py` (226 líneas)
**Clase**: `StructureExtractor` + `SectionContext`
**Capa**: GUI · Adapters
**Tags**: #secinterp #gui #adapters #structure

---

## 🧱 `extract_section_and_structures()` — flujo

```python
def extract_section_and_structures(self, line_lyr, struct_lyr, buffer_m) -> SectionContext | None:
    line_points, line_start, line_azimuth = _extract_line(line_lyr)
    structures = _filter_by_buffer(line_lyr, struct_lyr, buffer_m)  # QgsFeatureRequest + QgsGeometry.buffer
    return SectionContext(line_points=line_points, line_start=line_start, line_azimuth=line_azimuth, structures=[{"point": (x,y), "attributes": {...}}])
```

> `sample_elevation(raster_lyr, x, y, band)` se inyecta luego como closure al `StructureService`.

---

## 🔗 Notas relacionadas

- [[structure_service]] — consume `SectionContext`
- [[structure_page]] — formulario origen

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
