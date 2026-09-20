---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - adapters
aliases:
  - geology_extractor.py
  - GeologyExtractor
cssclass: secinterp-note
---

# `gui/adapters/geology_extractor.py`

> [!abstract] One-line summary
> **Extract** adapter for geology: reads line + DEM + outcrops, densifies the master profile and intersects polygons → `GeologyContext`.

**Path**: `gui/adapters/geology_extractor.py` (235 lines)
**Class**: `GeologyExtractor`
**Layer**: GUI · Adapters
**Tags**: #secinterp #gui #adapters

---

## 🎯 Why does this file exist?

Without an adapter, the core would touch `QgsGeometry`. This file:

| Step | What it does |
|------|--------------|
| 1. Validate | `band`, `outcrop_name_field` |
| 2. Line | `QgsGeometry` + `QgsDistanceArea` |
| 3. Master profile | `_generate_master_profile` (densify + sample) |
| 4. Outcrops | Line↔polygon intersection → `OutcropSegments` |

> Produces `GeologyContext(master_profile_data, master_grid_dists, outcrops, tolerance)` for `GeologyService`.

---

## 🔗 Related notes

- [[geology_service]] — consumes the context
- [[geology_page]] — source form

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
