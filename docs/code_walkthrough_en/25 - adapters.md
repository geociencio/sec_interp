---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - adapters
aliases:
  - gui/adapters
cssclass: secinterp-note
---

# 25 — `gui/adapters/`

> [!abstract] One-line summary
> The **Extract phase**: adapters QGIS → DTOs. Every adapter converts layers/features into decoupled contexts the core consumes.

**Path**: `gui/adapters/` (8 files, 1522 lines)
**Key symbols**: `ProfileExtractor`, `GeologyExtractor`, `StructureExtractor`, `DrillholeExtractor`, `ValidationExtractor`, `DataFetcher`, `geometry`, `layer_resolver`
**Layer**: GUI · Adapters
**Tags**: #secinterp #gui #adapters

---

## 🎯 Why does this package exist?

It is the **QGIS ↔ Core** boundary. Every adapter solves the same problem:

| Input | Output |
|-------|--------|
| `QgsVectorLayer`, `QgsRasterLayer`, `QgsFeature` | `ProfileData`, `GeologyContext`, `DrillholeContext`, `LayerMetadata` |

> [!important] The only layer with `QgsProject`/`QgsGeometry`
> `core/` never imports `qgis.*`.

---

## 🧬 Adapter map

| Adapter | QGIS input | Output (domain) | Core consumer |
|---------|------------|-----------------|---------------|
| `profile_extractor` | `line + raster` | `ProfileData` | `controller._process_topography` |
| `geology_extractor` | `line + raster + outcrop` | `GeologyContext` | `GeologyService` |
| `structure_extractor` | `line + struct + raster` | `StructureContext` | `StructureService` |
| `drillhole_extractor` | `line + collar/survey/interval + raster` | `DrillholeContext` | `DrillholeService` |
| `validation_extractor` | `any layer` | `LayerMetadata` | `ProjectValidator` |
| `feature_fetcher` | `QgsVectorLayer` | `list[dict]` | Drillhole sub-system |
| `geometry` | `QgsGeometry/CRS/raster` | primitives | all of the above |
| `layer_resolver` | `id | name | object` | `QgsMapLayer` | GUI controllers |

---

## 🧱 Pattern — Extract

```python
def extract_context(self, line_lyr, raster_lyr, outcrop_lyr, field, band=1) -> GeologyContext:
    self._validate_inputs(...)         # → raises ValidationError
    line_geom, line_start = self._extract_line_info(line_lyr)
    da = geometry.create_distance_area(crs)
    master_profile, master_grid = self._generate_master_profile(...)
    outcrops = self._extract_outcrop_data(line_geom, outcrop_lyr, field)
    return GeologyContext(...)
```

> [!tip] Early validation
> Each adapter validates (valid layers, existing fields, band in range) and raises `DataMissingError`/`ValidationError` before extracting.

---

## 🏛️ Patterns

| Pattern | Where |
|---------|-------|
| **Adapter / Bridge** | whole package |
| **Fail-fast** | `_validate_inputs` |

---

## 🔗 Related notes

- [[10 - controller]] — consumes the contexts
- [[11 - domain]] — `GeologyContext`, `DrillholeContext`, `LayerMetadata`
- [[13 - profile_service]] — `ProfileExtractor` detail
- [[14 - geology_service]] — `GeologyService`

---

*Note 25 of the SecInterp Code Walkthrough vault — v3.8.0*
