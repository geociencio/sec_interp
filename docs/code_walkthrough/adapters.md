---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - adapters
  - extract-phase
aliases:
  - gui/adapters
  - Adapters
cssclass: secinterp-note
---

# 25 — `gui/adapters/`

> [!abstract] Resumen en una línea
> Es la **fase Extract**: adapta QGIS → DTOs. Todos los adapters convierten capas/features a contextos desacoplados que el core consume.

**Ruta**: `gui/adapters/` (8 archivos, 1522 líneas)
**Claves**: `ProfileExtractor`, `GeologyExtractor`, `StructureExtractor`, `DrillholeExtractor`, `ValidationExtractor`, `DataFetcher`, `geometry`, `layer_resolver`
**Capa**: GUI · Adapters
**Tags**: #secinterp #gui #adapters #extract-phase

---

## 🎯 ¿Por qué existe este paquete?

Es la frontera **QGIS ↔ Core**. Todo adapter resuelve el mismo problema:

| Entrada | Salida |
|---------|--------|
| `QgsVectorLayer`, `QgsRasterLayer`, `QgsFeature` | `ProfileData`, `GeologyContext`, `DrillholeContext`, `LayerMetadata` |

> [!important] La única capa con `QgsProject`/`QgsGeometry`
> `core/` nunca importa `qgis.*`.

---

## 🧬 Mapa de adapters

| Adapter | Entrada QGIS | Salida (domain) | Consumidor core |
|---------|--------------|-----------------|-----------------|
| `profile_extractor` | `line + raster` | `ProfileData` | `controller._process_topography` |
| `geology_extractor` | `line + raster + outcrop` | `GeologyContext` | `GeologyService` |
| `structure_extractor` | `line + struct + raster` | `StructureContext` | `StructureService` |
| `drillhole_extractor` | `line + collar/survey/interval + raster` | `DrillholeContext` | `DrillholeService` |
| `validation_extractor` | `any layer` | `LayerMetadata` | `ProjectValidator` |
| `feature_fetcher` | `QgsVectorLayer` | `list[dict]` | Drillhole sub-sistema |
| `geometry` | `QgsGeometry/CRS/raster` | primitivas | todos los anteriores |
| `layer_resolver` | `id | name | object` | `QgsMapLayer` | controladores GUI |

---

## 🧱 Patrón — Extract

```python
# Ejemplo (GeologyExtractor)
def extract_context(self, line_lyr, raster_lyr, outcrop_lyr, field, band=1) -> GeologyContext:
    self._validate_inputs(...)         # → raises ValidationError
    line_geom, line_start = self._extract_line_info(line_lyr)
    da = geometry.create_distance_area(crs)
    master_profile, master_grid = self._generate_master_profile(line_geom, raster_lyr, band, da, line_start)
    outcrops = self._extract_outcrop_data(line_geom, outcrop_lyr, field)
    return GeologyContext(master_profile_data=..., master_grid_dists=..., outcrops=..., tolerance=0.001)
```

> [!tip] Validación temprana
> Cada adapter valida (capas válidas, campos existentes, banda en rango) y lanza `DataMissingError`/`ValidationError` antes de extraer.

---

## 🏛️ Patrones

| Patrón | Dónde |
|--------|-------|
| **Adapter / Bridge** | todo el paquete |
| **Fail-fast** | `_validate_inputs` |

---

## 🔗 Notas relacionadas

- [[controller]] — consume los contexts
- [[domain]] — `GeologyContext`, `DrillholeContext`, `LayerMetadata`
- [[profile_service]] — `ProfileExtractor` en detalle
- [[geology_service]] — `GeologyService`

---

*Nota 25 de la bóveda SecInterp Code Walkthrough — v3.8.0*
