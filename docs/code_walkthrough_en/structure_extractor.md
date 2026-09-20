---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - adapters
aliases:
  - structure_extractor.py
  - StructureExtractor
cssclass: secinterp-note
---

# `gui/adapters/structure_extractor.py`

> [!abstract] One-line summary
> **Extract** adapter for structures: reads line + structures, filters by buffer and samples DEM → detached data.

**Path**: `gui/adapters/structure_extractor.py` (226 lines)
**Class**: `StructureExtractor` + `SectionContext`
**Layer**: GUI · Adapters
**Tags**: #secinterp #gui #adapters

---

## 🧱 `extract_section_and_structures()` — flow

```python
def extract_section_and_structures(self, line_lyr, struct_lyr, buffer_m) -> SectionContext | None:
    line_points, line_start, line_azimuth = _extract_line(line_lyr)
    structures = _filter_by_buffer(line_lyr, struct_lyr, buffer_m)
    return SectionContext(line_points=line_points, line_start=line_start, line_azimuth=line_azimuth, structures=[{"point": (x,y), "attributes": {...}}])
```

> `sample_elevation(raster_lyr, x, y, band)` is later injected as a closure into `StructureService`.

---

## 🔗 Related notes

- [[structure_service]] — consumes `SectionContext`
- [[structure_page]] — source form

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
