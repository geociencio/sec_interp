---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - adapters
  - validation
aliases:
  - validation_extractor.py
  - ValidationExtractor
cssclass: secinterp-note
---

# `gui/adapters/validation_extractor.py`

> [!abstract] Resumen en una línea
> Adapter **Extract** de validación: convierte `QgsLayer` → `LayerMetadata` desacoplado.

**Ruta**: `gui/adapters/validation_extractor.py` (176 líneas)
**Funciones**: `resolve_layer_metadata`, `extract_layer_metadata`, `extract_vector/raster_metadata`
**Capa**: GUI · Adapters
**Tags**: #secinterp #gui #adapters #validation

---

## 🎯 ¿Por qué existe este archivo?

Sin adapter, el core tocaría `QgsVectorLayer`. Este archivo:

| Función | Qué extrae |
|---------|------------|
| `_resolve_layer(layer_ref)` | `QgsProject.instance().mapLayer` |
| `extract_vector_metadata` | `name, is_valid, kind=vector, geometry_type, field_names/types, feature_count, crs_authid` |
| `extract_raster_metadata` | `band_count, crs_authid` |
| `resolve_layer_metadata` | Combo (resolve + extract) |

> `LayerMetadata` viaja a `ProjectValidator` sin QGIS.

---

## 🔗 Notas relacionadas

- [[validation]] — consume `LayerMetadata`
- [[layer_notification_manager]] — invalida caché al cambiar capa

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
