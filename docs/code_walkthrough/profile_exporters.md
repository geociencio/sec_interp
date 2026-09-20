---
tags:
  - secinterp
  - code-walkthrough
  - exporters
  - profile
aliases:
  - profile_exporters.py
  - ProfileLineVectorExporter
cssclass: secinterp-note
---

# `exporters/profile_exporters.py`

> [!abstract] Resumen en una línea
> Exporta **perfil topográfico, geología, estructuras y ejes** a vectores (SHP/GPKG/DXF).

**Ruta**: `exporters/profile_exporters.py` (362 líneas)
**Clases**: `ProfileLineVectorExporter`, `GeologyVectorExporter`, `StructureVectorExporter`, `AxesVectorExporter`
**Capa**: Exporters
**Tags**: #secinterp #exporters #profile

---

## 🧱 Exporters

| Clase | Geometría | Campos |
|-------|-----------|--------|
| `ProfileLineVectorExporter` | `LineString` (dist,elev) | `distance`, `elevation` |
| `GeologyVectorExporter` | `Polygon` (segmentos) | `unit_name` |
| `StructureVectorExporter` | `LineString` (dips) | `strike`, `dip` |
| `AxesVectorExporter` | `LineString` (ejes) | `label` |

> Todos usan `scu_io.create_vector_writer` + `BaseExporter.validate_export_path`.

---

## 🔗 Notas relacionadas

- [[base_exporter]] — contrato
- [[profile_service]] — origen topo

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
