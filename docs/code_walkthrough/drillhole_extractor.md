---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - adapters
  - drillhole
aliases:
  - drillhole_extractor.py
  - DrillholeExtractor
cssclass: secinterp-note
---

# `gui/adapters/drillhole_extractor.py`

> [!abstract] Resumen en una línea
> Adapter **Extract** de sondajes: lee línea + collar/survey/interval + DEM y devuelve `DrillholeContext` desacoplado.

**Ruta**: `gui/adapters/drillhole_extractor.py` (369 líneas)
**Clase**: `DrillholeExtractor`
**Capa**: GUI · Adapters
**Tags**: #secinterp #gui #adapters #drillhole

---

## 🎯 ¿Por qué existe este archivo?

Sin adapter, el core tocaría `QgsVectorLayer`. Este archivo:

| Paso | Qué hace |
|------|----------|
| 1. Buffer de la línea | `QgsGeometry.buffer(buffer_width, segments=8)` |
| 2. Collars filtrados | Intersección + `layer_resolver` |
| 3. Pre-sample Z del DEM | `sample_elevation` por collar |
| 4. Surveys/Intervals | `DataFetcher` bulk por `hole_id` |

> Produce `DrillholeContext(line_points, section_azimuth, buffer_width, collar/survey/interval_data, pre_sampled_z)`.

---

## 🔗 Notas relacionadas

- [[drillhole_service]] — consume el contexto
- [[drillhole_page]] — formulario origen

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
