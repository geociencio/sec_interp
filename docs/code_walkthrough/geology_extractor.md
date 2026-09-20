---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - adapters
  - geology
aliases:
  - geology_extractor.py
  - GeologyExtractor
cssclass: secinterp-note
---

# `gui/adapters/geology_extractor.py`

> [!abstract] Resumen en una línea
> Adapter **Extract** de geología: lee línea + DEM + outcrops, densifica el perfil maestro e intersecta polígonos → `GeologyContext`.

**Ruta**: `gui/adapters/geology_extractor.py` (235 líneas)
**Clase**: `GeologyExtractor`
**Capa**: GUI · Adapters
**Tags**: #secinterp #gui #adapters #geology

---

## 🎯 ¿Por qué existe este archivo?

Sin adapter, el core tocaría `QgsGeometry`. Este archivo:

| Paso | Qué hace |
|------|----------|
| 1. Valida | `band`, `outcrop_name_field` |
| 2. Línea | `QgsGeometry` + `QgsDistanceArea` |
| 3. Perfil maestro | `_generate_master_profile` (densifica + muestrea) |
| 4. Outcrops | Intersección línea↔polígono → `OutcropSegments` |

> Produce `GeologyContext(master_profile_data, master_grid_dists, outcrops, tolerance)` para `GeologyService`.

---

## 🔗 Notas relacionadas

- [[geology_service]] — consume el contexto
- [[geology_page]] — formulario origen

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
