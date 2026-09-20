---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - adapters
aliases:
  - drillhole_extractor.py
  - DrillholeExtractor
cssclass: secinterp-note
---

# `gui/adapters/drillhole_extractor.py`

> [!abstract] One-line summary
> **Extract** adapter for drillholes: reads line + collar/survey/interval + DEM and returns a detached `DrillholeContext`.

**Path**: `gui/adapters/drillhole_extractor.py` (369 lines)
**Class**: `DrillholeExtractor`
**Layer**: GUI · Adapters
**Tags**: #secinterp #gui #adapters

---

## 🎯 Why does this file exist?

Without an adapter, the core would touch `QgsVectorLayer`. This file:

| Step | What it does |
|------|--------------|
| 1. Line buffer | `QgsGeometry.buffer(buffer_width, segments=8)` |
| 2. Filtered collars | Intersection + `layer_resolver` |
| 3. Pre-sample Z from DEM | `sample_elevation` per collar |
| 4. Surveys/Intervals | `DataFetcher` bulk by `hole_id` |

> Produces `DrillholeContext(line_points, section_azimuth, buffer_width, collar/survey/interval_data, pre_sampled_z)`.

---

## 🔗 Related notes

- [[drillhole_service]] — consumes the context
- [[drillhole_page]] — source form

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
