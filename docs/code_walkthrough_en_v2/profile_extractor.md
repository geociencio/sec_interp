---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - adapters
aliases:
  - profile_extractor.py
  - ProfileExtractor
cssclass: secinterp-note
---

# `gui/adapters/profile_extractor.py`

> [!abstract] One-line summary
> Topography **Extract** adapter (`ProfileExtractor`, 86 lines) sampling DEM elevations along the section line and returning `ProfileData` (rounded `list[(distance, elevation)]`), plus the LOD interval computation for preview.

**Path**: `gui/adapters/profile_extractor.py` (86 lines)
**Main class**: `ProfileExtractor`
**Layer**: GUI · Adapter (Extract side, depends on QGIS)
**Tags**: #secinterp #gui #adapters

---

## 🎯 Why does this file exist?

The topographic profile is the base of every section: geology, structures and
drillholes are drawn on top of it. Sampling the DEM requires a live
`QgsRasterLayer` and `QgsDistanceArea`, both forbidden in the core:

| Problem | Solution |
|---------|----------|
| The core cannot sample a raster or measure distances | `extract_profile` densifies + samples + accumulates here and returns tuples |
| Preview must degrade resolution to the canvas | `calculate_lod_interval` derives the sampling step from length/width |
| Raw DEM floats add sub-millimetre noise | 1-decimal rounding on output (`round(p.x(), 1)`) |
| Without a line no profile is possible | `DataMissingError` / `GeometryError` with `details={"layer": ...}` |

> [!important] Architectural note
> The thinnest adapter of the package: delegates almost everything to
> `geometry.py` (`create_distance_area`, `sample_elevation_along_line`) and only
> contributes orchestration, LOD and rounding. `ProfileController` calls it at
> two moments: `_process_topography` (`extract_profile`) and LOD preview
> (`calculate_lod_interval` → `extract_profile(interval=...)`).

---

## 🧬 Relationship diagram

```mermaid
graph TD
    PE["ProfileExtractor"]
    LOD["calculate_lod_interval()"]
    EXT["extract_profile()"]
    GEO["geometry<br/>create_distance_area<br/>sample_elevation_along_line"]
    PD["ProfileData<br/>(domain/entities.py)"]
    CTRL["ProfileController"]
    PREV["PreviewResult.topo"]

    CTRL -->|LOD + profile| PE
    LOD -->|interval| EXT
    PE --> GEO
    EXT -->|list[(dist, elev)]| PD
    PD --> PREV

    classDef gui fill:#ffe08a,stroke:#b8860b,stroke-width:2px,color:#000
    classDef core fill:#95e1d3,stroke:#38a169,stroke-width:2px,color:#000
    class PE,LOD,EXT,GEO gui
    class PD,PREV core
    classDef ctrl fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
    class CTRL ctrl
```

> [!tip] How to read
> `ProfileExtractor` is almost a facade over `geometry.py`: the added value is
> the LOD interval, the error guards and the tenth-rounding.

---

## 📦 Imports — architectural reading

```python
# gui/adapters/profile_extractor.py
from __future__ import annotations

from qgis.core import QgsRasterLayer, QgsVectorLayer
from qgis.PyQt.QtCore import QCoreApplication

from sec_interp.core.domain import ProfileData
from sec_interp.core.exceptions import DataMissingError, GeometryError
from sec_interp.gui.adapters import geometry
```

| # | Observation |
|---|-------------|
| ① | Only two `qgis.core` classes (the minimum for "line + raster"): the least QGIS-coupled adapter of the package. |
| ② | `qgis.PyQt.QtCore.QCoreApplication` for `self.tr()` with the `"ProfileExtractor"` context (Qt5/Qt6 agnostic). |
| ③ | Imports the domain `ProfileData` alias: output is typed (`list[tuple[float, float]]`) though built here. |
| ④ | Two domain exceptions with `details`: empty layer (`DataMissingError`) vs null geometry (`GeometryError`). |
| ⑤ | All heavy lifting (datum, densify, sampling) delegates to `geometry`. |

---

## 🏗️ Structure inventory

**Class:** `class ProfileExtractor` — 3 methods (`tr` + 2 public), no `__init__`, no state.

**Methods:**
- `tr(message)` — translation via `QCoreApplication.translate("ProfileExtractor", ...)`.
- `calculate_lod_interval(line_lyr, canvas_width)` — `line_len / max(200, canvas_width*2)` or `None` without a line.
- `extract_profile(line_lyr, raster_lyr, band_number=1, interval=None)` — 1-decimal rounded profile; `interval=None` → raster resolution.

---

## 📁 Files in the package

The extractor lives in the `gui/adapters/` package (the full Extract phase):

| File | Lines | Role |
|---|--:|---|
| `__init__.py` | 7 | Package docstring: Extract-then-Compute contract |
| `drillhole_extractor.py` | 369 | `DrillholeExtractor` → `DrillholeContext` |
| `geology_extractor.py` | 235 | `GeologyExtractor` → `GeologyContext` |
| `geometry.py` | 226 | QGIS geometry helpers and DEM sampling (used by this note) |
| `layer_resolver.py` | 113 | `LayerResolver` + `resolve_layer` (layer cache) |
| `structure_extractor.py` | 226 | `SectionContext` + `StructureExtractor` |
| `validation_extractor.py` | 176 | `resolve_layer_metadata`, `build_validation_params` |
| `feature_fetcher.py` | 84 | `DataFetcher` (bulk child reads) |
| `profile_extractor.py` | 86 | `ProfileExtractor` → `ProfileData` (this note) |

---

## 📖 Method-by-method walkthrough

### `tr` — adapter i18n

```python
def tr(self, message: str) -> str:
    return QCoreApplication.translate("ProfileExtractor", message)
```

Same pattern as drillholes and geology. Only used in the two `extract_profile`
`raise`s (`calculate_lod_interval` generates no messages: it returns `None`).

### `calculate_lod_interval` — canvas-based sampling step

```python
def calculate_lod_interval(self, line_lyr: QgsVectorLayer, canvas_width: int) -> float | None:
    line_feat = next(line_lyr.getFeatures(), None)
    if not line_feat:
        return None
    line_geom = line_feat.geometry()
    if not line_geom or line_geom.isNull():
        return None
    line_len = line_geom.length()
    max_pts = max(200, int(canvas_width * 2))
    return line_len / max_pts if max_pts > 0 else None
```

| Step | Detail |
|------|--------|
| **Guards** | No features or null geometry → `None` (no exception: without LOD the native resolution is used). |
| **Budget** | `max(200, canvas_width*2)`: minimum 200 points (legibility) and 2 points per pixel on large canvases (profile anti-aliasing). |
| **Step** | `line_len / max_pts` in CRS units; `max_pts > 0` always holds via `max`, but the guard protects against extreme negative `canvas_width`. |

> [!note] LOD = Level of Detail
> An 800 px canvas asks ~1600 points; a 3200 m section samples every 2 m. Preview
> stays fluid without losing visible fidelity.

### `extract_profile` — sampling and rounding

```python
def extract_profile(
    self,
    line_lyr: QgsVectorLayer,
    raster_lyr: QgsRasterLayer,
    band_number: int = 1,
    interval: float | None = None,
) -> ProfileData:
    line_feat = next(line_lyr.getFeatures(), None)
    if not line_feat:
        raise DataMissingError(
            self.tr("Line layer has no features"), {"layer": line_lyr.name()}
        )
    geom = line_feat.geometry()
    if not geom or geom.isNull():
        raise GeometryError(self.tr("Line geometry is not valid"), {"layer": line_lyr.name()})
    da = geometry.create_distance_area(line_lyr.crs())
    points = geometry.sample_elevation_along_line(
        geom, raster_lyr, band_number, da, interval=interval
    )
    return [(round(p.x(), 1), round(p.y(), 1)) for p in points]
```

| Step | Detail |
|------|--------|
| **Strict guards** | Exceptions here (unlike LOD): without a line there is no profile to degrade. |
| **Datum** | `create_distance_area` with the line CRS (ellipsoidal distances). |
| **Sampling** | `sample_elevation_along_line` with the LOD `interval` or `None` (→ raster resolution). |
| **Rounding** | `round(..., 1)` on distance and elevation: profile-space `QgsPointXY(dist, elev)` becomes domain `ProfileData`. |

> [!tip] Double line read
> `calculate_lod_interval` and `extract_profile` read the first feature
> separately (two iterators). When LOD precedes the profile, the line is read
> twice; acceptable (first feature, no scan), but unify if project contention is
> ever measured.

---

## 🔄 Data flow

| Phase | Input | Transformation | Output |
|-------|-------|----------------|--------|
| LOD | `line_lyr` + `canvas_width` | `length / max(200, w*2)` | `interval` or `None` |
| Guards | 1st feature | empty → `DataMissingError`; null → `GeometryError` | valid geometry |
| Datum | line CRS | `create_distance_area` | `QgsDistanceArea` |
| Sampling | line + DEM + `da` | densify → accumulate → `sample` | `list[QgsPointXY(dist, elev)]` |
| Domain | profile points | `round(1 decimal)` | `ProfileData` |
| Delivery | `ProfileData` | (via `controller`) | `PreviewResult.topo` |

---

## 🏛️ Design patterns present

| Pattern | Where | Purpose |
|---------|-------|---------|
| **Thin facade** | `extract_profile` | Orchestrates `geometry.*` after validating |
| **LOD (Level of Detail)** | `calculate_lod_interval` | Canvas-proportional resolution |
| **Validated fail-fast** | `raise` with `details` | No line, no profile |
| **Domain rounding** | `round(..., 1)` | Agreed precision with rendering |

---

## 🧾 API summary

| Symbol | Signature | Typical use |
|--------|-----------|-------------|
| `ProfileExtractor` | stateless GUI class | `ProfileExtractor()` (injected into the controller) |
| `calculate_lod_interval` | `(line_lyr, canvas_width: int) -> float \| None` | pre-preview step |
| `extract_profile` | `(line_lyr, raster_lyr, band_number=1, interval=None) -> ProfileData` | topographic profile |
| `tr` | `(message: str) -> str` | i18n of the two errors |

---

## 🛡️ Error handling

| Situation | Behaviour |
|-----------|-----------|
| LOD without features / null geometry | `None` (native resolution used) |
| Profile without features | `DataMissingError` + `details={"layer": ...}` |
| Null profile geometry | `GeometryError` + `details={"layer": ...}` |
| `sample` with `ok=False` (inside `geometry`) | `0.0` elevation per point |

> [!tip] Tolerant LOD, strict profile
> The asymmetry is intentional: LOD is an optimization (may be missing) and the
> profile is a requirement (no section without it). Each fails at its own level.

---

## 🧪 Associated tests

No dedicated tests (there is no `test_profile_extractor.py`); indirect coverage:

- `tests/gui/tasks/test_geology_task.py` — tasks consuming extracted `topo`.
- `tests/integration/test_geology_structure_workflow.py` — end-to-end integrated profile.
- `tests/integration/test_async_orchestrators.py` — orchestration with injected `ProfileExtractor`.
- `tests/core/test_preview_service.py` — the core `ProfileData` consumer.
- `tests/core/test_geometry_utils.py` — mirror math of the sampling.

> [!warning] Coverage gap
> `calculate_lod_interval` (zero width, huge canvas, feature-less line) and the
> 1-decimal rounding are trivial mock-first cases with no test. A ~50-line
> `test_profile_extractor.py` would close them.

---

## 🧵 Thread-safety and i18n

| Aspect | Detail |
|--------|--------|
| **Thread** | `getFeatures`, `create_distance_area` (uses `QgsProject.transformContext`) and `dataProvider().sample` → main thread. Only `ProfileData` (tuples) travels to the `QgsTask`. |
| **Rounding** | `round()` over pure floats: safe on any thread; could run in the worker, but here it keeps the agreed output. |
| **i18n** | `self.tr()` with the `"ProfileExtractor"` context via `qgis.PyQt`; distances and elevations are not translated (data). |

---

## 📐 `ProfileData` and its rounding

| Aspect | Detail |
|--------|--------|
| **Type** | `ProfileData = list[tuple[float, float]]` (`(distance, elevation)`, see domain) |
| **Precision** | 1 decimal (~10 cm): below typical DEM noise and stable for the cache hash |
| **Typical LOD** | 800 px canvas → ~1600 points; `interval = line_len / 1600` |
| **No LOD** | `interval=None` → `rasterUnitsPerPixelX` (one vertex per pixel) |

> [!note] Rounding stabilizes the cache
> `PreviewParams` is hashed for `DataCache`: two samplings of the same DEM with
> different float noise would give different keys without `round`. See
> [[preview_param_hasher]] and [[data_cache]].

---

## 👀 Observations and notes

> [!success] Strengths
> - Near-total delegation to `geometry.py`: the adapter duplicates no math.
> - LOD with a 200-point floor: legible even on tiny canvases.
> - Layer-`details` errors for precise GUI messages.
> - Rounding stabilizing render and cache at once.

> [!warning] Points of attention
> - Double read of the first feature (LOD + profile) without sharing the iterator.
> - `extract_profile` does not validate the raster (delegated to `geometry`, returning `0.0` per point): an invalid DEM silently yields a flat profile.
> - Unreachable `max_pts > 0` via `max(200, ...)`: defensive but dead guard.
> - `band_number` not validated against `bandCount()` (geology does validate).

> [!question] Open questions
> - Validate `raster_lyr.isValid()` and `band_number` here as `GeologyExtractor` does?
> - Share the read geometry between `calculate_lod_interval` and `extract_profile`?
> - Make the `round` decimals configurable (e.g. by CRS units)?

---

## 🔗 Related notes

- [[Index]] — vault index
- [[gui_adapters]] — Extract adapters package note
- [[geometry]] — `create_distance_area` and `sample_elevation_along_line` (the real work)
- [[controller]] — `ProfileController` (calls LOD + profile)
- [[dtos]] — `PreviewParams` (`band_num`, `canvas_width`, `auto_lod`) and `PreviewResult.topo`
- [[domain]] — `ProfileData` alias
- [[data_cache]] — hashed cache stabilized by rounding
- [[drillhole_extractor]] — `pre_sampled_z` from the same DEM sampled here

---

*Note of the SecInterp Code Walkthrough v2 vault — v3.8.0*
