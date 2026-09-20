---
tags:
  - secinterp
  - code-walkthrough
  - exporters
aliases:
  - profile_exporters.py
  - ProfileLineVectorExporter
cssclass: secinterp-note
---

# `exporters/profile_exporters.py`

> [!abstract] One-line summary
> Exports **topographic profile, geology, structures, and axes** to vectors (SHP/GPKG/DXF).

**Path**: `exporters/profile_exporters.py` (362 lines)
**Classes**: `ProfileLineVectorExporter`, `GeologyVectorExporter`, `StructureVectorExporter`, `AxesVectorExporter`
**Layer**: Exporters
**Tags**: #secinterp #exporters

---

## 🧱 Exporters

| Class | Geometry | Fields |
|-------|----------|--------|
| `ProfileLineVectorExporter` | `LineString` (dist,elev) | `distance`, `elevation` |
| `GeologyVectorExporter` | `Polygon` (segments) | `unit_name` |
| `StructureVectorExporter` | `LineString` (dips) | `strike`, `dip` |
| `AxesVectorExporter` | `LineString` (axes) | `label` |

> All use `scu_io.create_vector_writer` + `BaseExporter.validate_export_path`.

---

## 🔗 Related notes

- [[base_exporter]] — contract
- [[profile_service]] — topo source

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
