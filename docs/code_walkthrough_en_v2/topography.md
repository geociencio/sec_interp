---
tags:
  - secinterp
  - code-walkthrough
  - core
  - export
  - handlers
aliases:
  - topography.py
  - export_topography
cssclass: secinterp-note
---

# `core/services/export/handlers/topography.py`

> [!abstract] One-line summary
> **Topography** export handler: dumps the topographic profile to CSV (dist, elev) and to a vector profile-line layer, as the first step of the export pipeline.

**Path**: `core/services/export/handlers/topography.py` (114 lines)
**Main function**: `export_topography`
**Layer**: Core (QGIS-agnostic)
**Tags**: #secinterp #core #export #handlers

---

## 🎯 Why does this file exist?

The topographic profile (`ProfileData`, a list of `(dist, elev)`) is the base dataset of
the whole section: it is the vertical reference on which geology, structures and
drillholes are drawn. Exporting it is, therefore, the first step and the one that
**must always** exist.

| Problem | Solution |
|---------|----------|
| Persist the topographic profile as CSV and vector | Two chained export blocks |
| It is the mandatory dataset of every export | The orchestrator validates its existence before calling |
| Report each generated file | `msg.append(...)` after each successful export |

> [!important] Architectural note
> QGIS-agnostic: `data` is `list[tuple]` (already-decoupled `(dist, elev)` pairs). It is
> the **only** handler without a `if not data` guard clause — because the orchestrator
> already raises `DataMissingError` if `profile_data` is empty (see Observations).

---

## 🧬 Relationship diagram

```mermaid
graph TD
    TOP["handlers/topography.py"]
    ORCH["orchestrator.py (ExportService)"]
    PR["path_resolver.py"]
    EXC["core/exceptions.py"]
    CSV["CSVExporter (injected)"]
    VEC["ProfileLineVectorExporter"]
    LOG["logger_config.get_logger"]

    ORCH -->|"export_topography(...)"| TOP
    ORCH -.->|"csv_exporter (parameter)"| TOP
    TOP -->|"get_profile_name / resolve_export_path"| PR
    TOP -->|"ExportError / DataMissingError"| EXC
    TOP -.->|"deferred import"| VEC
    TOP --> LOG
```

> [!tip] How to read
> `csv_exporter` is injected; `ProfileLineVectorExporter` is imported deferred. The
> handler trusts that the orchestrator already validated that `data` is not empty.

---

## 📦 Imports — architectural reading

```python
# core/services/export/handlers/topography.py
from __future__ import annotations

from pathlib import Path
from typing import Any

from sec_interp.core.exceptions import DataMissingError, ExportError
from sec_interp.core.services.export.path_resolver import get_profile_name, resolve_export_path
from sec_interp.core.utils.sampling import smooth_profile_by_distance
from sec_interp.logger_config import get_logger
```

```python
# deferred import (inside export_topography)
from sec_interp.exporters import ProfileLineVectorExporter
```

| # | Observation |
|---|-------------|
| ① | `DataMissingError`/`ExportError` from the project's own hierarchy; no `qgis.*` import. |
| ② | `data: list[tuple]` is the most "concrete" type in the package: `(dist, elev)` pairs. |
| ③ | `ProfileLineVectorExporter` deferred import, after the orchestrator's logical guard. |
| ④ | `csv_exporter` injected (shared across handlers by the orchestrator). |
| ⑤ | `smooth_profile_by_distance` is **pure core math** (distance-window moving average). |
| ⑥ | The module imports neither `QgsGeometry` nor `QgsCoordinateReferenceSystem`: `crs` is opaque. |

---

## 🏗️ Structure inventory

**Functions/Methods:**
- `export_topography(folder, data, crs, csv_exporter, msg, controller, settings, ext, options=None) -> None`
- `_export_profile_pair(folder, profile_name, pattern, stems, payloads, csv_exporter, vector_exporter, msg, ext) -> None`
- `_smoothed_topography(data, options) -> list[tuple] | None`
- `_record_written(msg, path, folder) -> None`

**Domain dependencies:**
- `ProfileData` (`list[tuple[float, float]]`) — distance/elevation pairs.
- `ProfileLineVectorExporter` (from `sec_interp.exporters`)
- `smooth_profile_by_distance` (from `sec_interp.core.utils.sampling`)

One public function + three private helpers. Since v3.9.1 the signature takes `options`
(`smooth` and `smooth_window`) to optionally emit the smoothed pair.

---

## 📖 Method-by-method walkthrough

### `export_topography`

```python
def export_topography(
    folder: Path,
    data: list[tuple],
    crs: Any,
    csv_exporter: Any,
    msg: list[str],
    controller: Any | None,
    settings: Any | None,
    ext: str,
    options: dict[str, Any] | None = None,
) -> None:
    """Export topographic data (CSV + vector)."""
    from sec_interp.exporters import ProfileLineVectorExporter

    logger.info("✓ Saving topographic profile...")
```

**No guard clause**: the first instruction is the deferred import (no `if not data`).
The guarantee that `data` is non-empty lives in the orchestrator, which raises
`DataMissingError` before invoking the handlers.

```python
    try:
        profile_name = get_profile_name(controller)
        pattern = getattr(settings, "naming_pattern", None) if settings else None
        vector_exporter = ProfileLineVectorExporter({})

        _export_profile_pair(
            folder, profile_name, pattern,
            ("topo_profile", "profile_line"),
            ({"headers": ["dist", "elev"], "rows": data},
             {"profile_data": data, "crs": crs}),
            csv_exporter, vector_exporter, msg, ext,
        )

        smoothed = _smoothed_topography(data, options or {})
        if smoothed:
            _export_profile_pair(
                folder, profile_name, pattern,
                ("topo_profile_smoothed", "profile_line_smoothed"),
                ({"headers": ["dist", "elev"], "rows": smoothed},
                 {"profile_data": smoothed, "crs": crs}),
                csv_exporter, vector_exporter, msg, ext,
            )
```

The public body was reduced to **two calls to the same helper**: one with the raw data and
one (optional) with the smoothed profile. That removed the duplicated
"resolve path → export → record message" logic that used to be written twice.

### `_export_profile_pair` — one CSV + one vector

```python
csv_path, csv_layer = resolve_export_path(folder, csv_stem, profile_name, pattern, ".csv")
if csv_exporter.export(csv_path, csv_payload, layer_name=csv_layer):
    _record_written(msg, csv_path, folder)
else:
    logger.warning(f"Failed to write CSV topography to {csv_path}")

vec_path, vec_layer = resolve_export_path(folder, vec_stem, profile_name, pattern, ext)
if vector_exporter.export(vec_path, vec_payload, layer_name=vec_layer):
    _record_written(msg, vec_path, folder)
else:
    logger.warning(f"Failed to write vector topography to {vec_path}")
```

It takes `stems` and `payloads` as two-element tuples: the order is always
`(CSV, vector)`. A write failure does **not** raise: it logs a `warning` and continues with
the other file (per-file best effort; a hard error only comes from a broken overall flow).

### `_smoothed_topography` — deciding the second pass

```python
window = float(options.get("smooth_window", 0) or 0)
if options.get("smooth") and window > 0 and data:
    return smooth_profile_by_distance(data, window)
return None
```

| `smooth` | `smooth_window` | `data` | Result |
|---|---|---|---|
| `False` | any | any | `None` (no second pass) |
| `True` | `0` | non-empty | `None` (invalid window) |
| `True` | `> 0` | empty | `None` |
| `True` | `> 0` | non-empty | smoothed list |

The function is pure: it touches neither disk nor QGIS. `smooth_profile_by_distance` applies
a distance-window moving average (not an index window), so an irregular sampling does not
bias the result.

### `_record_written` — one line per file

```python
msg.append(f"  - {path.relative_to(folder)}")
```

The summary shown to the user lists paths **relative** to the output folder, so the message
does not depend on where the export ran.

### Files written

| Condition | CSV | Vector |
|---|---|---|
| Always | `topo_profile.csv` | `profile_line.<ext>` |
| `smooth` + window > 0 | `topo_profile_smoothed.csv` | `profile_line_smoothed.<ext>` |

The suffix and naming pattern are resolved by `resolve_export_path` from
`get_profile_name(controller)` and `settings.naming_pattern`.

**Normalization**: the standard double `except` → `ExportError` with cause: first the
expected failures (`OSError`, `ValueError`, `TypeError`, `DataMissingError`), then any
`Exception` as "Critical error".

---

## 🔄 Data flow

| Phase | Input | Transformation | Output |
|-------|-------|----------------|--------|
| Raw CSV | `data` (dist/elev pairs) | passthrough as `rows` | `topo_profile.csv` + `msg` |
| Raw vector | `data`, `crs` | `ProfileLineVectorExporter.export` | `profile_line.<ext>` + `msg` |
| Smoothed (optional) | `data` + `options` | `smooth_profile_by_distance` | `topo_profile_smoothed.csv` / `profile_line_smoothed.<ext>` |
| Errors | raw exception | `except → ExportError` | domain exception |

---

## 🏛️ Design patterns present

| Pattern | Where | Purpose |
|---------|-------|---------|
| **Lazy import (deferred)** | `ProfileLineVectorExporter` | save loading when unnecessary |
| **Dependency injection** | `csv_exporter` as parameter | share the exporter |
| **Facade** | `export_topography` | hide 2–4 files behind one signature |
| **Extract helper** | `_export_profile_pair` | a single copy of the CSV+vector pair |
| **Pure function** | `_smoothed_topography` / `smooth_profile_by_distance` | test smoothing without I/O |
| **Exception translation** | `except → ExportError` | normalize failures |

---

## 🧾 API summary

| Symbol | Signature / Inherits | Typical use |
|--------|----------------------|-------------|
| `export_topography` | `(folder, data, crs, csv_exporter, msg, controller, settings, ext, options=None) -> None` | Export the topographic profile (raw and optionally smoothed) |
| `_export_profile_pair` | `(folder, profile_name, pattern, stems, payloads, csv_exporter, vector_exporter, msg, ext) -> None` | Write one CSV+vector pair |
| `_smoothed_topography` | `(data, options) -> list[tuple] \| None` | Decide and compute the smoothed profile |
| `_record_written` | `(msg, path, folder) -> None` | Append a line to the summary |
| `ProfileLineVectorExporter` | `BaseExporter` (deferred import) | Write the profile line |

---

## 📐 Handler signature contract

Nine parameters (the last one optional), with an injected `csv_exporter`:

| Parameter | Type | Role |
|-----------|------|------|
| `folder` | `Path` | Base output directory |
| `data` | `list[tuple]` | Decoupled `ProfileData` (`(dist, elev)` pairs) |
| `crs` | `Any` | Section CRS |
| `csv_exporter` | `Any` | `CSVExporter` injected by the orchestrator |
| `msg` | `list[str]` | Message accumulator |
| `controller` | `Any \| None` | Profile-name source |
| `settings` | `Any \| None` | Settings (`naming_pattern`) |
| `ext` | `str` | Output extension |
| `options` | `dict \| None` | `smooth` and `smooth_window` (optional second pass) |

> [!note] `data` is not transformed
> Unlike `geology.py` (flattening) or `structures.py` (field extraction), topography
> already arrives in the exact shape the CSV needs: `rows = data` with no mapping.

## 🔁 Invocation from the orchestrator

The orchestrator groups topography and axes into one composite handler:

```python
def topo_handler(settings=export_settings, ext=format_ext) -> None:
    topo_h.export_topography(
        folder, profile_data, line_crs, csv_exporter, msg,
        self.controller, settings, ext, options,
    )
    axes_h.export_axes(
        folder, profile_data, line_crs, msg,
        self.controller, settings, ext,
    )

handlers = {"exp_topo": topo_handler, ...}
```

The `profile_data` comes from the direct parameter of `export_data` (not from a DTO),
and is the same `ProfileData` that `export_axes` consumes.

---

## 🛡️ Error handling

| Caught type | Action | Result |
|-------------|--------|--------|
| `OSError`, `ValueError`, `TypeError`, `DataMissingError` | `logger.exception` + `raise ExportError(...) from e` | domain error |
| `Exception` (rest) | `logger.exception` + `raise ExportError(...) from e` | critical error |

> [!note] Empty-data validation lives in the orchestrator
> `ExportService.export_data` raises `DataMissingError` if `profile_data` is empty
> **before** delegating. Hence this handler omits the `if not data: return`.

---

## 🧪 Associated tests

- `tests/core/test_export_service.py::test_export_data_minimal` — topography as the
  minimal export case (topo + axes only).
- `tests/core/test_export_service.py::test_export_topography_error` — exporter failure
  → `ExportError`.
- `tests/core/test_export_service.py::test_export_data_missing_profile` — the
  orchestrator raises `DataMissingError` without a profile.
- `tests/core/test_profile_exporters.py::test_profile_line_exporter_success` — real
  logic of `ProfileLineVectorExporter`.
- `tests/integration/test_export_service_e2e.py::test_export_topography_creates_csv` —
  real CSV export.

---

## 👀 Observations and notes

> [!success] Strengths
> - Clear, stable signature: one mandatory dataset + presentation options.
> - `data` passes through to the CSV unchanged, zero friction.
> - Smoothing is a pure, reusable, testable function.
> - Uniform error contract with `ExportError`.

> [!warning] Points of attention
> - The missing guard clause couples the handler to the orchestrator's contract (fragile
>   if called directly).
> - `data: list[tuple]` does not specify the pair shape (should be `list[tuple[float, float]]`).
> - A failed write only logs a `warning`: the summary can list an incomplete pair without
>   flagging the error.

> [!question] Open questions
> - Add a defensive `if not data: return` in case the handler is reused outside the
>   orchestrator?
> - Type `data` as `ProfileData` (alias already defined in `entities.py`)?

---

## 🧭 Export summary example

With `smooth=True` and `smooth_window=25`, the accumulated `msg` looks like this:

```text
  - topo_profile.csv
  - profile_line.gpkg
  - topo_profile_smoothed.csv
  - profile_line_smoothed.gpkg
```

Without smoothing only the first two lines appear. The order mirrors the calls: the raw
pair first and the smoothed one after, which is also the order the user sees in the dialog
summary.

| Situation | `msg` |
|---|---|
| Full export | 2 lines (or 4 with smoothing) |
| CSV fails, vector OK | 1 line (or 3) + `warning` in the log |
| Vector fails, CSV OK | 1 line (or 3) + `warning` in the log |
| Flow exception | `ExportError` (no partial summary returned) |

---

## 🔗 Related notes

- [[Index]] — vault index
- [[core_services_export_handlers]] — `handlers/` package it belongs to
- [[orchestrator]] — delegates to `export_topography` and `export_axes` under `exp_topo`
- [[path_resolver]] — `get_profile_name` / `resolve_export_path`
- [[compat]] — `_export_topography` compatibility wrapper
- [[preview_service]] — produces the exported topographic profile (`ProfileData`)
- [[entities]] — `ProfileData` (`list[tuple[float, float]]`)

---

*Note of the SecInterp Code Walkthrough v2 vault — v3.11.0*
