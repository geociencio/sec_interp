---
tags:
  - secinterp
  - code-walkthrough
  - exporters
  - interpretations
  - 3d
aliases:
  - interpretation_3d_exporter.py
  - Interpretation3DExporter
cssclass: secinterp-note
---

# `exporters/interpretation_3d_exporter.py`

> [!abstract] One-line summary
> Projects 2D interpretation polygons (`distance, elevation`) onto the section's vertical plane and exports them as `PolygonZ` with a categorised 2D QML style plus a rule-based 3D renderer.

**Path**: `exporters/interpretation_3d_exporter.py` (465 lines)
**Main class**: `Interpretation3DExporter(BaseExporter)`
**Layer**: Exporters (GUI · QGIS-dependent, with optional `qgis._3d` import)
**Tags**: #secinterp #exporters #interpretations #3d

---

## 🎯 Why does this file exist?

Interpretations are digitised over the 2D profile (`vertices_2d` in distance /
elevation, see [[interpretations]]). To show them in the QGIS 3D view they must be
**relocated to the real world**: each `(d, e)` point becomes `(easting, northing, elev)`
by shifting it from the section-line origin along its azimuth:

| Problem | Solution |
|---------|----------|
| The 2D polygon has no map coordinates | `_calculate_section_geometry` derives origin + azimuth from `section_line`; `_create_3d_rings` applies the rotation |
| Duplicate vertices or unclosed rings break `QgsPolygon` | `_get_unique_vertices` + `_ensure_closed_polygon` + `makeValid()` |
| Each unit needs its colour in 2D and 3D | `_setup_2d_renderer` (categorised) + `_configure_3d_renderer` (`qgis._3d` rules), saved as `.qml` |
| Custom attributes vary per polygon | `_prepare_fields` unions all keys (`sorted_keys`) into `QString(255)` columns |
| Missing `section_line` or degenerate geometry | `_validate_export_input` (returns `False` or raises `ExportError`) |

> [!important] Architectural note — 3D writer, not `IRenderer3D`
> Like the [[drillhole_3d_exporter]] exporters, this class **writes files**; it does not
> implement the `IRenderer3D.render_3d/clear` port (see [[core_interfaces]]). "3D
> rendering" here means: `PolygonZ` geometry + a `.qml` configuring QGIS's native 3D
> renderer when the layer loads.

---

## 🧬 Relationship diagram

```mermaid
graph TD
    EXP["Interpretation3DExporter"]
    BASE["BaseExporter"]
    IO["core/utils/io (create_vector_writer)"]
    ENT["InterpretationPolygon (core/domain)"]
    IH["handlers/interpretations.py"]
    ORCH["ExportService (orchestrator)"]
    AC["AccessControlService (3D gate)"]

    EXP -->|inherits| BASE
    EXP -->|create_vector_writer PolygonZ| IO
    EXP -->|reads vertices_2d/attributes| ENT
    EXP -->|QgsCategorizedSymbolRenderer| R2D["2D renderer"]
    EXP -->|qgis._3d (optional)| R3D["rule-based 3D renderer"]
    EXP -->|saves .qml| QML["QML style"]
    IH -->|uses| EXP
    AC -->|authorises| IH
    ORCH -->|exp_interp| IH
```

> [!tip] How to read
> The `interpretations` handler (see [[interpretations]]) chooses 2D vs 3D and passes
> `section_line` + `crs`. The `AccessControlService` gate lives in the handler, not
> here: this exporter assumes it is already authorised.

---

## 📦 Imports — architectural reading

```python
# exporters/interpretation_3d_exporter.py
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsLineString,
    QgsPoint,
    QgsPointXY,
    QgsPolygon,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QCoreApplication, QMetaType
from qgis.PyQt.QtGui import QColor

import sec_interp.core.utils.io as scu_io
from sec_interp.core.domain import InterpretationPolygon
from sec_interp.core.exceptions import ExportError
from sec_interp.exporters.base_exporter import BaseExporter
from sec_interp.logger_config import get_logger
```

| # | Observation |
|---|-------------|
| ① | `QgsPolygon` + `QgsLineString(QgsPoint)` + `PolygonZ` → 3D rings with interior rings (holes supported). |
| ② | `QCoreApplication` only to translate the missing-`section_line` message (i18n, see [[interpretation_exporters]]). |
| ③ | `ExportError` (not `return False`) on structural failures: the only 2D/3D exporter that **raises**. |
| ④ | `QColor` to validate unit hex with `#FF0000` fallback (same rule in 2D and 3D). |
| ⑤ | `QgsVectorLayer` at top for the style memory layer; `qgis._3d` and `QgsVectorFileWriter` are **lazy** method-level imports. |
| ⑥ | `math` for `atan2/cos/sin` of the azimuthal projection (explicit trigonometry, no `QgsCoordinateTransform`). |

---

## 🏗️ Structure inventory

**Class:** `Interpretation3DExporter(BaseExporter)` — 2 public (`export`, `get_supported_extensions`) + 12 private.

**Constants:**

| Constant | Value | Use |
|----------|------:|-----|
| `MIN_VALID_POLYGON_VERTICES` | 4 | Minimum closed ring (3 unique + closure) in `_prepare_2d_geometry` |
| `MIN_REQUIRED_FOR_CLOSURE` | 2 | Only closes with more than 2 vertices |

**Export-pipeline methods:**
- `export(output_path, data, layer_name=None) -> bool`
- `_validate_export_input(interpretations, section_line) -> bool`
- `_prepare_fields(interpretations) -> tuple[list[QgsField], list[str]]`
- `_calculate_section_geometry(section_line) -> tuple[float, float, float]`
- `_collect_projected_features(interpretations, fields, sorted_keys, origin_x, origin_y, azimuth) -> list[QgsFeature]`
- `_prepare_2d_geometry(polygon) -> QgsGeometry | None`
- `_get_unique_vertices(vertices_2d)` / `_ensure_closed_polygon(vertices)` — ring sanitation
- `_project_to_3d_features(geom_2d, polygon, fields, origin_x, origin_y, azimuth, custom_keys, vert_exag=1.0)`
- `_create_3d_rings(poly_2d, origin_x, origin_y, azimuth, vert_exag) -> list[QgsLineString]`
- `_write_shapefile(path, features, fields, wkb_type, crs, layer_name=None) -> bool`
- `_make_fields_obj(fields_list)` / `_make_fields(fields_list)` — list → `QgsFields`

**Post-export style methods:**
- `_handle_post_export_styles(output_path, interpretations, fields, crs) -> None`
- `_generate_qml_style(shp_path, interpretations, fields, crs) -> None`
- `_setup_2d_renderer(layer, interpretations) -> None`
- `_configure_3d_renderer(layer, interpretations) -> None`

---

## 📁 Files in the package `exporters/`

| File | Role relative to this note |
|---|---|
| `interpretation_3d_exporter.py` | This note: `PolygonZ` + 2D/3D QML |
| [[interpretation_exporters]] | 2D twin: `Interpretation2DExporter` (`fromPolygonXY`, no QML) |
| [[drillhole_3d_exporter]] | The other 3D writer: `LineStringZ` traces and intervals |
| [[base_exporter]] | `BaseExporter`: shared contract |
| [[exporters]] | Package facade + `get_exporter()` by extension |

---

## 📖 Method-by-method walkthrough

### `export` — 5-phase pipeline

```python
def export(self, output_path: str, data: dict[str, Any], layer_name: str | None = None) -> bool:
    interpretations = data.get("interpretations", [])
    section_line = data.get("section_line")
    src_crs = data.get("crs", QgsCoordinateReferenceSystem())

    if not self._validate_export_input(interpretations, section_line):
        return False

    # Prepare fields
    fields, sorted_keys = self._prepare_fields(interpretations)

    # Calculate section azimuth and origin
    try:
        origin_x, origin_y, azimuth = self._calculate_section_geometry(section_line)
    except Exception as e:
        raise ExportError(f"Failed to calculate section geometry: {e}") from e

    # Transform and create features
    features = self._collect_projected_features(
        interpretations, fields, sorted_keys, origin_x, origin_y, azimuth
    )

    success = self._write_shapefile(
        output_path,
        features,
        fields,
        QgsWkbTypes.Type.PolygonZ,
        src_crs,
        layer_name=layer_name,
    )

    if success:
        self._handle_post_export_styles(output_path, interpretations, fields, src_crs)

    return success
```

| Phase | What it does |
|-------|--------------|
| 1. Extract | `interpretations` (default `[]`), `section_line`, `crs` (default empty CRS) |
| 2. Validate | No interpretations → `False`; no `section_line` → **`ExportError`** |
| 3. Section geometry | Origin + azimuth; any failure → `ExportError` with cause (`from e`) |
| 4. Project | One 3D `QgsFeature` per part of each polygon (Multi counts as N) |
| 5. Style | Only on write success; QML failures are `warning`, never abort |

### `_validate_export_input` — dual regime

Empty list = warning + `False` (benign case); missing `section_line` = translated
`ExportError` via `QCoreApplication.translate` (no line means no 3D frame possible).

### `_prepare_fields` — custom-attribute union

Fixed schema (`id`/`name`/`type`/`color`/`created_at` with SHP lengths 50/100/50/10/30)
plus one `QString(255)` column per custom key found in **any** polygon (`sorted_keys`
sorted = deterministic columns). Same schema as the 2D exporter; returns
`(fields, sorted_keys)`.

### `_calculate_section_geometry` — origin and azimuth

```python
line_points = section_line.asMultiPolyline()[0] if section_line.isMultipart() else section_line.asPolyline()
p1, p2 = line_points[0], line_points[-1]
azimuth = math.atan2(p2.y() - p1.y(), p2.x() - p1.x())
return p1.x(), p1.y(), azimuth
```

Only the **first and last vertices** matter: the section is modelled as a straight
vertical plane even if the line has kinks (multipart uses the first part). The radian
azimuth feeds `cos/sin` in `_create_3d_rings`; origin and azimuth are logged in degrees.

### `_collect_projected_features` — loop with filter

Per polygon: `_prepare_2d_geometry` (degenerate ones yield `None` and are skipped) and
`extend` with `_project_to_3d_features(..., vert_exag=1.0)`. Vertical exaggeration is
visual (canvas) and is not baked into the SHP.

### `_prepare_2d_geometry` — ring sanitation

```python
def _prepare_2d_geometry(self, polygon: Any) -> QgsGeometry | None:
    vertices = self._get_unique_vertices(polygon.vertices_2d)
    if not vertices:
        return None

    vertices = self._ensure_closed_polygon(vertices)

    if len(vertices) < MIN_VALID_POLYGON_VERTICES:
        logger.warning(f"Polygon {polygon.id} has insufficient unique vertices. Skipping.")
        return None

    qgs_points_3d = [QgsPoint(x, y, 0.0) for x, y in vertices]
    polygon_2d = QgsPolygon()
    polygon_2d.setExteriorRing(QgsLineString(qgs_points_3d))
    geom_2d = QgsGeometry(polygon_2d)

    if not geom_2d.isGeosValid():
        logger.info(f"Correcting 2D geometry for polygon {polygon.id}")
        geom_2d = geom_2d.makeValid()

    return geom_2d
```

Chain: dedup → closure → minimum count (4 = closed triangle) → build with `z=0.0` →
`isGeosValid()` and `makeValid()` if needed. Point `x` is distance, `y` is elevation;
real georeferencing happens later in `_create_3d_rings`.

### Ring sanitation — `_get_unique_vertices` / `_ensure_closed_polygon`

`_get_unique_vertices` drops only **consecutive** duplicates (`v != dedup[-1]`, cheap,
no tolerance); `_ensure_closed_polygon` appends the first vertex (`[*vertices,
vertices[0]]`, no mutation of the original) when there are more than 2 vertices
(`MIN_REQUIRED_FOR_CLOSURE`) and the ring is open.

### `_project_to_3d_features` — Multi as N features

```python
polygons_2d = geom_2d.asMultiPolygon() if geom_2d.isMultipart() else [geom_2d.asPolygon()]

for poly_2d in polygons_2d:
    rings_3d = self._create_3d_rings(poly_2d, origin_x, origin_y, azimuth, vert_exag)
    ...
    polygon_3d = QgsPolygon()
    polygon_3d.setExteriorRing(rings_3d[0])
    for i in range(1, len(rings_3d)):
        polygon_3d.addInteriorRing(rings_3d[i])
    ...
    feat.setAttribute("id", polygon.id)
    feat.setAttribute("name", polygon.name)
    for key in custom_keys:
        feat.setAttribute(key, str(polygon.attributes.get(key, "")))
```

Ring 0 is exterior, the rest interior (holes). Fixed attributes go by name and custom
ones with `str(val)` (symmetric with the 2D exporter). Note the empty `QgsFeature()` +
`setFields`: unlike 2D, it is not built as `QgsFeature(fields)`.

### `_create_3d_rings` — the azimuthal projection

```python
rings_3d = []
cos_a = math.cos(azimuth)
sin_a = math.sin(azimuth)

for ring_2d in poly_2d:
    points_3d = []
    for p_2d in ring_2d:
        east = origin_x + (p_2d.x() * cos_a)
        north = origin_y + (p_2d.x() * sin_a)
        elev = p_2d.y() / vert_exag
        points_3d.append(QgsPoint(east, north, elev))

    rings_3d.append(QgsLineString(points_3d))
return rings_3d
```

`cos_a`/`sin_a` are precomputed once per polygon (not per vertex). Distance `p_2d.x()`
advances along the azimuth; elevation `p_2d.y()` is preserved (divided by `vert_exag`,
today always 1.0). It is a rigid transform: profile distances and angles survive.

### `_write_shapefile` — write with writer check

The writer comes from `scu_io.create_vector_writer(...)`; if
`writer.hasError() != QgsVectorFileWriter.WriterError.NoError` it **raises**
`ExportError(writer.errorMessage())` instead of returning `False`. `_make_fields_obj`
converts the `QgsField` list into the `QgsFields` container the writer requires.

### Post-export QML — 2D + 3D style that never aborts

`_generate_qml_style` builds a `Polygon?crs=...&z=yes` memory layer, applies
`name`-categorised 2D symbology (`_setup_2d_renderer`: 180-alpha fill, `darker(150)`
outline) and, if `import qgis._3d` works (`HAS_3D`), a rule-based 3D renderer with one
rule per unit (`"name" = '...'`, `QgsPhongMaterialSettings` with diffuse + `lighter(120)`
ambient). The `.qml` is saved next to the SHP via `saveNamedStyle`; any failure is a
`warning` in `_handle_post_export_styles` and the export stays `True`.

---

## 🔄 Data flow

| Phase | Input | Transformation | Output |
|-------|-------|----------------|--------|
| Validate | `interpretations`, `section_line` | empty → `False`; no line → `ExportError` | Guards |
| Fields | `attributes` of all polygons | sorted key union | `fields` + `sorted_keys` |
| Section | `section_line` (single/multi) | first/last vertex → `atan2` | `(origin_x, origin_y, azimuth)` |
| 2D sanitation | `vertices_2d` | dedup → closure → `makeValid` | Valid `QgsGeometry` or `None` |
| Projection | `(d, e)` + origin/azimuth | `east/north/elev` per vertex | `PolygonZ` per part |
| Write | features + `PolygonZ` | writer + `hasError` check | SHP/GPKG/DXF |
| Style | memory layer + units | categorised 2D + 3D rules | `.qml` next to the SHP |

---

## 🏛️ Design patterns present

| Pattern | Where | Purpose |
|---------|-------|---------|
| **Template Method** | `BaseExporter` → `export` | Shared export contract |
| **Pipeline** | `export` in 5 phases | Each phase testable separately |
| **Null Object (skip)** | `_collect_projected_features` | Degenerate polygons skipped |
| **Fail fast** | `ExportError` on validation/geometry | No 3D frame means no partial output |
| **Graceful degradation** | `HAS_3D`, `_handle_post_export_styles` | Without `qgis._3d` only 2D style; without QML the SHP still stands |
| **Lazy import** | `qgis._3d`, `QgsVectorFileWriter`, renderers | Heavy modules only when used |

---

## 🧾 API summary

| Symbol | Signature / Inherits | Typical use |
|--------|----------------------|-------------|
| `Interpretation3DExporter` | `(BaseExporter)` | Section polygons → `PolygonZ` + `.qml` |
| `export` | `(output_path, data, layer_name=None) -> bool` | `data = {"interpretations": [...], "section_line": geom, "crs": ...}` |
| `_validate_export_input` | `(interpretations, section_line) -> bool` | `False` if empty; `ExportError` without line |
| `_prepare_fields` | `(interpretations) -> tuple[list[QgsField], list[str]]` | 5 fixed + sorted custom |
| `_calculate_section_geometry` | `(section_line) -> tuple[float, float, float]` | `(origin_x, origin_y, azimuth)` |
| `_collect_projected_features` | `(interpretations, fields, sorted_keys, ox, oy, az) -> list[QgsFeature]` | Loop with `vert_exag=1.0` |
| `_prepare_2d_geometry` | `(polygon) -> QgsGeometry \| None` | Sanitation + `makeValid` |
| `_project_to_3d_features` | `(geom_2d, polygon, fields, ox, oy, az, keys, vert_exag=1.0)` | Multi → N features |
| `_create_3d_rings` | `(poly_2d, ox, oy, azimuth, vert_exag) -> list[QgsLineString]` | Per-vertex azimuthal rotation |
| `_write_shapefile` | `(path, features, fields, wkb_type, crs, layer_name=None) -> bool` | Writer + `ExportError` on failure |
| `_generate_qml_style` | `(shp_path, interpretations, fields, crs) -> None` | Memory layer → `.qml` |
| `_setup_2d_renderer` / `_configure_3d_renderer` | `(layer, interpretations) -> None` | 2D categorised / 3D rules |

---

## 🛡️ Error handling

| Situation | Behaviour |
|-----------|-----------|
| Empty `interpretations` | `warning` + `return False` |
| Missing `section_line` | `ExportError` translated with `QCoreApplication.translate` |
| `_calculate_section_geometry` fails | `ExportError(...) from e` (cause preserved) |
| Polygon with < 4 vertices after sanitation | `warning` with `polygon.id`; skipped |
| Invalid geometry | `makeValid()` + `info`; QGIS writes it anyway if still off |
| Writer error | `ExportError(writer.errorMessage())` |
| QML style failure | `warning`; export still `True` |
| `qgis._3d` missing | `HAS_3D=False`; 2D style only |

> [!note] Only exporter mixing `bool` and exceptions
> `False` = "nothing to export" (benign); `ExportError` = "3D frame impossible or
> broken write" (structural). See [[exceptions]] for the full hierarchy.

---

## 🧪 Associated tests

**Unit** in `tests/exporters/test_interpretation_3d_exporter.py`:

- `test_azimuth_calculation_east` — azimuth of an east line.
- `test_geometric_transformation_north` — projection with a north line.
- `test_overturned_fold_geometry` — overturned-fold geometry (complex rings).

**Integration** (projection and workflow):

- `tests/integration/test_export_workflow.py::test_3d_projection_logic` and `test_3d_projection_north` — projection onto the section plane.
- `tests/integration/test_3d_projections.py` — end-to-end 3D projections.
- `tests/integration/test_export_service_e2e.py::test_export_interpretations_creates_2d_shp` — 2D twin e2e.
- `tests/integration/test_interpretation_workflow.py` — interpretation workflow.

---

## 👀 Observations and notes

> [!success] Strengths
> - Readable 5-phase pipeline with separated concerns (validate → fields → section → project → style).
> - Full 2D sanitation (dedup, closure, minimum count, `makeValid`) before touching Z.
> - `ExportError` with chained cause (`from e`) instead of a mute `False`.
> - Graceful degradation: without `qgis._3d` or QML, the SHP is still valid.
> - `cos/sin` precomputed per polygon, not per vertex.

> [!warning] Points of attention
> - The section collapses to first/last vertex: kinked lines flatten to one straight plane.
> - `vert_exag` hardwired to `1.0`: the parameter exists but the caller never varies it.
> - No vertex simplification: dense polygons project point by point.

> [!question] Open questions
> - Support multi-leg sections (one plane per leg) instead of a single azimuth?
> - Expose `vert_exag` from `data` to bake exaggeration into the SHP?

---

## 🔗 Related notes

- [[Index]] — vault index
- [[exporters]] — `exporters/` package facade
- [[base_exporter]] — `BaseExporter`, base class
- [[interpretation_exporters]] — 2D twin (`fromPolygonXY`, same field schema)
- [[drillhole_3d_exporter]] — the other 3D writer (`LineStringZ`)
- [[interpretations]] — `exp_interp` handler (2D/3D dispatch + access gate)
- [[orchestrator]] — `ExportService`, general orchestration
- [[domain]] — `InterpretationPolygon` (`vertices_2d`, `attributes`, `color`)

---

*Note of the SecInterp Code Walkthrough v2 vault — v3.9.0*
