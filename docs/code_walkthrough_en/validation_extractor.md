---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - adapters
aliases:
  - validation_extractor.py
  - ValidationExtractor
cssclass: secinterp-note
---

# `gui/adapters/validation_extractor.py`

> [!abstract] One-line summary
> **Extract** adapter for validation: converts `QgsLayer` → detached `LayerMetadata`.

**Path**: `gui/adapters/validation_extractor.py` (176 lines)
**Functions**: `resolve_layer_metadata`, `extract_layer_metadata`, `extract_vector/raster_metadata`
**Layer**: GUI · Adapters
**Tags**: #secinterp #gui #adapters

---

## 🎯 Why does this file exist?

Without an adapter, the core would touch `QgsVectorLayer`. This file:

| Function | What it extracts |
|----------|------------------|
| `_resolve_layer(layer_ref)` | `QgsProject.instance().mapLayer` |
| `extract_vector_metadata` | `name, is_valid, kind=vector, geometry_type, field_names/types, feature_count, crs_authid` |
| `extract_raster_metadata` | `band_count, crs_authid` |
| `resolve_layer_metadata` | Combo (resolve + extract) |

> `LayerMetadata` travels to `ProjectValidator` without QGIS.

---

## 🔗 Related notes

- [[validation]] — consumes `LayerMetadata`
- [[layer_notification_manager]] — invalidates cache on layer change

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
