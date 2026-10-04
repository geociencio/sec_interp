---
tags:
  - secinterp
  - code-walkthrough
  - core
  - export
  - orchestrator
aliases:
  - orchestrator.py
  - ExportService
cssclass: secinterp-note
note_lines: 700
---

# `core/services/export/orchestrator.py`

> [!abstract] One-line summary
> Core export facade: receives the already-computed profile data and **orchestrates** CSV/vector writing per entity, delegating to handlers based on options and resolving layers, CRS and format.

**Path**: `core/services/export/orchestrator.py` (207 lines)
**Main class**: `ExportService(ExportServiceCompatMixin)`
**Layer**: Core (gray zone: imports `QCoreApplication` for `tr()`)
**Tags**: #secinterp #core #export #orchestrator

---

## 🎯 Why does this file exist?

The GUI already holds the computed profile data (`profile_data`, `geol_data`, …).
Someone must decide **what** to export, **how** (format) and **where** (paths), without
every entity repeating that logic. `ExportService` centralizes that decision:

| Problem | Solution |
|---------|----------|
| Export 6 different entities with a single call | `export_data(...)` with an options dict |
| Choose format (SHP/GPKG/DXF) without scattered logic | `_orchestrate_exports` derives `format_ext` from settings |
| Decouple the core from the `exporters/` module | **Lazy** imports inside `_orchestrate_exports` |
| Validate minimum layers before writing | `_resolve_layers` raises `DataMissingError` |
| Translate messages without coupling to the GUI | `tr()` via `QCoreApplication.translate` |

> [!important] Architectural note — gray zone
> `orchestrator.py` **imports** `qgis.PyQt.QtCore.QCoreApplication` (for `tr()`). This is
> a controlled exception to the "QGIS-agnostic core" rule: the `qgis.PyQt` shim is used
> only for translation (see `tests/core/test_architecture_boundary.py`). The heavy
> `qgis.core` import is **isolated** in `map_settings_factory.py`.

---

## 🧬 Relationship diagram

```mermaid
graph TD
    GUI["GUI (dialog_export_manager)"]
    SHIM["core/services/export_service.py (shim)"]

    GUI -->|export_data(...)| EXP["ExportService"]
    SHIM -->|re-export| EXP

    EXP -->|inherits| COMPAT["ExportServiceCompatMixin"]
    EXP --> CTRL["ProfileController (Any)"]
    EXP --> AC["AccessControlService"]
    EXP --> MAPF["create_map_settings (factory)"]

    EXP -->|_orchestrate_exports| CSV["CSVExporter"]
    EXP --> TOPO["handlers/topography.py"]
    EXP --> AXES["handlers/axes.py"]
    EXP --> GEO["handlers/geology.py"]
    EXP --> STR["handlers/structures.py"]
    EXP --> DH["handlers/drillholes.py"]
    EXP --> DH3["handlers/drillholes_3d.py"]
    EXP --> INTERP["handlers/interpretations.py"]

    classDef core fill:#95e1d3,stroke:#38a169,stroke-width:2px,color:#000
    classDef gray fill:#ffe08a,stroke:#f4a261,stroke-width:2px,color:#000
    classDef gui fill:#4ecdc4,stroke:#0a9396,stroke-width:2px,color:#000
    class EXP,COMPAT,AC,CSV core
    class MAPF gray
    class GUI,SHIM gui
```

> [!tip] How to read
> `ExportService` is a **single entry point**: the GUI enters via `export_data`, and the
> service fans out to the handlers according to `options`. `COMPAT` (the mixin) provides
> the legacy API; `MAPF` (the factory) isolates the only `qgis.core` import.

---

## 📦 Imports — architectural reading

```python
"""Export orchestrator — thin facade delegating to handlers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qgis.PyQt.QtCore import QCoreApplication          # ①

from sec_interp.core.domain import PreviewParams       # ②
from sec_interp.core.exceptions import DataMissingError
from sec_interp.core.services.access_control_service import AccessControlService
from sec_interp.logger_config import get_logger

from .compat import ExportServiceCompatMixin           # ③
from .map_settings_factory import create_map_settings  # ④

logger = get_logger(__name__)
```

```python
# lazy imports inside _orchestrate_exports (not at the top)
from sec_interp.exporters import CSVExporter
from .handlers import axes as axes_h
from .handlers import drillholes as dh_h
from .handlers import drillholes_3d as dh3_h
from .handlers import geology as geo_h
from .handlers import interpretations as interp_h
from .handlers import structures as struct_h
from .handlers import topography as topo_h
```

| # | Observation |
|---|-------------|
| ① | `QCoreApplication` = the only QGIS exception; used only for `tr()`. |
| ② | `PreviewParams` is the input DTO (QGIS types as `Any` inside it). |
| ③ | `ExportServiceCompatMixin` provides the legacy `_export_*` API (see [[compat]]). |
| ④ | `create_map_settings` isolates the `qgis.core` import in `map_settings_factory.py`. |
| ⑤ | Handlers and `CSVExporter` are imported **lazy** to avoid loading `exporters/` at package import. |

---

## 🏗️ Structure inventory

**Classes:** `class ExportService(ExportServiceCompatMixin)` — 6 own methods + 7 inherited from the mixin.

**Own functions/methods:**
- `__init__(controller: Any | None = None)` — stores `controller` and creates `AccessControlService`
- `tr(message: str) -> str` — translation via `QCoreApplication.translate`
- `export_data(output_folder, params, profile_data, geol_data, struct_data, drillhole_data, interp_data, export_options) -> list[str]` — main entry
- `_resolve_layers(params) -> tuple[Any, Any]` — validates and returns `(line_layer, raster_layer)`
- `_orchestrate_exports(folder, params, …) -> None` — handler table + dispatch
- `get_map_settings(layers, extent, size, background_color) -> Any` — delegates to `create_map_settings`

**Attributes:**
- `self.controller` — `ProfileController | None`
- `self.access_control` — `AccessControlService` (3D gate)

---

## 📁 Files in the package

| File | Lines | Role |
|---|--:|---|
| `__init__.py` | 9 | Re-exports `ExportService`, `create_map_settings`, `get_profile_name`, `resolve_export_path` |
| `orchestrator.py` | 207 | `ExportService` — export facade |
| `compat.py` | 129 | `ExportServiceCompatMixin` — legacy wrappers |
| `path_resolver.py` | 60 | Path and name resolution |
| `map_settings_factory.py` | 34 | `create_map_settings` — isolates `qgis.core` |
| `handlers/` | ~490 | Seven per-entity handlers |

> [!note] External shim
> `core/services/export_service.py` (outside the package) re-exports `ExportService` to
> keep `from sec_interp.core.services.export_service import ExportService` in tests.

---

## 📖 Method-by-method walkthrough

### `__init__`

```python
def __init__(self, controller: Any | None = None) -> None:
    self.controller = controller
    self.access_control = AccessControlService()
```

Minimal constructor. `controller` is optional and typed `Any` (really a
`ProfileController`); it is used to reload settings and derive the profile name.
`AccessControlService` decides whether the user may export 3D.

### `tr`

```python
def tr(self, message: str) -> str:
    return QCoreApplication.translate("ExportService", message)  # type: ignore[no-any-return]
```

Translates user-facing messages. The only point where the module touches QGIS. Every
message in `result_msg` goes through here (i18n).

### `export_data` — main entry

```python
def export_data(
    self, output_folder: Path, params: PreviewParams,
    profile_data: list[tuple], geol_data: list[Any] | None,
    struct_data: list[Any] | None, drillhole_data: list[Any] | None = None,
    interp_data: list[Any] | None = None,
    export_options: dict[str, bool] | None = None,
) -> list[str]:
    if export_options is None:
        export_options = {
            "exp_topo": True, "exp_geol": True, "exp_struct": True,
            "exp_drill": True, "exp_interp": True,
        }
    logger.info(f"Export options: {export_options}")

    if not any(export_options.values()):
        logger.warning("All export options are disabled. Nothing will be exported.")
        return [self.tr("⚠ No export options selected. Check Settings tab.")]

    if not profile_data:
        raise DataMissingError(self.tr("No profile data available for export"))

    line_layer = params.line_layer
    if not line_layer:
        raise DataMissingError(self.tr("Section line layer not found in parameters"))

    result_msg = [self.tr("✓ Saving files...")]
    self._orchestrate_exports(
        output_folder, params, profile_data, geol_data, struct_data,
        drillhole_data, interp_data, export_options, result_msg,
    )
    result_msg.append(self.tr("\n✓ All files saved to:\n{0}").format(output_folder))
    return result_msg
```

| Step | Behavior |
|------|----------|
| 1. Options | If `export_options` is `None`, enables all 5 entities by default |
| 2. Guard | If **no** option is enabled, returns a warning message (does not export) |
| 3. Validation | Raises `DataMissingError` if `profile_data` is empty or `line_layer` missing |
| 4. Orchestration | Delegates to `_orchestrate_exports`, accumulating messages in `result_msg` |
| 5. Close | Appends the final summary with the destination folder |

> [!important] `export_data` is a two-level facade
> It does the validation/guards and then delegates ALL the work to `_orchestrate_exports`.
> The `list[str]` return is the feedback channel to the GUI (no Qt signals).

### `_resolve_layers`

```python
def _resolve_layers(self, params: PreviewParams) -> tuple[Any, Any]:
    line_layer = params.line_layer
    if not line_layer or not line_layer.isValid():
        raise DataMissingError(self.tr("Section line layer not found or invalid"))
    raster_layer = params.raster_layer
    return line_layer, raster_layer
```

Validates that `line_layer` exists and is valid (calls `isValid()`, a QGIS method that
crosses typed as `Any`). Returns `(line_layer, raster_layer)`; `raster_layer` may be
`None` (not validated here because only structures use it).

### `_orchestrate_exports` — orchestration core

```python
def _orchestrate_exports(
    self, folder: Path, params: PreviewParams, profile_data: list[tuple],
    geol_data: list[Any] | None, struct_data: list[Any] | None,
    drillhole_data: list[Any] | None, interp_data: list[Any] | None,
    options: dict[str, Any], msg: list[str],
) -> None:
    from sec_interp.exporters import CSVExporter
    from .handlers import axes as axes_h
    from .handlers import drillholes as dh_h
    from .handlers import drillholes_3d as dh3_h
    from .handlers import geology as geo_h
    from .handlers import interpretations as interp_h
    from .handlers import structures as struct_h
    from .handlers import topography as topo_h

    line_layer, raster_layer = self._resolve_layers(params)
    line_crs = line_layer.crs()

    export_settings = None
    if self.controller is not None:
        reload_func = getattr(self.controller, "reload_settings", None)
        if reload_func:
            reload_func()
        settings_obj = getattr(self.controller, "settings", None)
        if settings_obj:
            export_settings = getattr(settings_obj, "export", None)

    format_ext = ".shp"
    if export_settings:
        if export_settings.default_format == "GeoPackage":
            format_ext = ".gpkg"
        elif export_settings.default_format == "DXF":
            format_ext = ".dxf"

    csv_exporter = CSVExporter({})

    def topo_handler(settings=export_settings, ext=format_ext) -> None:
        topo_h.export_topography(
            folder, profile_data, line_crs, csv_exporter, msg,
            self.controller, settings, ext,
        )
        axes_h.export_axes(
            folder, profile_data, line_crs, msg, self.controller, settings, ext,
        )

    handlers = {
        "exp_topo": topo_handler,
        "exp_geol": lambda: geo_h.export_geology(
            folder, geol_data, line_crs, csv_exporter, msg,
            self.controller, export_settings, format_ext,
        ),
        "exp_struct": lambda: struct_h.export_structures(
            folder, struct_data, raster_layer, line_crs, csv_exporter, msg,
            options, self.controller, export_settings, format_ext,
        ),
        "exp_drill": lambda: dh_h.export_drillholes(
            folder, drillhole_data, line_crs, msg, self.controller, export_settings, format_ext,
        ),
        "exp_drill_3d": lambda: dh3_h.export_drillholes_3d(
            folder, drillhole_data, line_crs, msg, options,
            self.controller, export_settings, format_ext,
        ),
        "exp_interp": lambda: interp_h.export_interpretations(
            folder, interp_data, line_layer, line_crs, msg,
            self.controller, export_settings, format_ext, self.access_control,
        ),
    }
    for opt, handler in handlers.items():
        if options.get(opt, True):
            handler()
```

| Stage | Detail |
|-------|--------|
| **Resolution** | `_resolve_layers` + `line_crs = line_layer.crs()` (real CRS of the line) |
| **Settings** | If `controller` present, reload settings and read `settings.export.default_format` |
| **Format** | `default_format`: `GeoPackage → .gpkg`, `DXF → .dxf`, otherwise `→ .shp` |
| **Dispatch** | `handlers` is a **dict of callables** indexed by the option |
| **Special topo** | `topo_handler` is a closure that exports topography **and** axes together |

> [!important] Dispatch table (`handlers`)
> This is the heart of the **Registry/Command** pattern: each option key maps to a
> callable. The final loop `for opt, handler in handlers.items()` runs only the enabled
> ones. Note: `exp_drill_3d` is **not** in `export_data`'s default dict, but the dispatch
> supports it if `options` injects it.

> [!tip] `exp_topo` uses a closure, the rest use `lambda`
> `topo_handler` needs two calls (topography + axes), hence the `def`; the rest are
> single-call `lambda`s. Both capture `format_ext`/`export_settings`.

### `get_map_settings`

```python
def get_map_settings(
    self, layers: list[Any], extent: Any, size: Any | None, background_color: Any,
) -> Any:
    return create_map_settings(layers, extent, size, background_color)
```

Delegates to `create_map_settings` (the factory isolating `qgis.core`). Used for canvas/
image rendering. Return `Any` (= `QgsMapSettings`) to avoid importing QGIS here.

---

## 🔄 Data flow

| Phase | Input | Transformation | Output |
|-------|-------|----------------|--------|
| Entry | `(output_folder, params, profile_data, …)` | validation of options and data | `list[str]` messages |
| Resolution | `params.line_layer` | `isValid()` + `crs()` | `(line_layer, raster_layer)`, `line_crs` |
| Format | `settings.export.default_format` | `.shp/.gpkg/.dxf` mapping | `format_ext` |
| Dispatch | `options` (flags dict) | `handlers` loop | call to each enabled handler |
| Writing | `data` + `crs` + `csv_exporter` | `exporter.export(...)` | CSV + vector files |

---

## 🏛️ Design patterns present

| Pattern | Where | Purpose |
|---------|-------|---------|
| **Facade** | `ExportService` / `export_data` | Single entry for the whole export subsystem |
| **Registry / Dispatch table** | `handlers` dict | Map options → callables, run only active ones |
| **Command (callables)** | `topo_handler` and `lambda`s | Encapsulate each export as an invokable |
| **Strategy (format)** | `format_ext` | Switch SHP/GPKG/DXF based on settings |
| **Factory** | `CSVExporter({})` / `create_map_settings` | Create collaborators without coupling constructors |
| **Mixin** | `ExportServiceCompatMixin` | Add legacy API without deep inheritance |
| **Lazy import** | imports inside `_orchestrate_exports` | Avoid loading `exporters/` at import time |

---

## 🧾 API summary

| Symbol | Signature / Inherits | Typical use |
|--------|----------------------|-------------|
| `ExportService` | `(ExportServiceCompatMixin)` | Export facade |
| `__init__` | `(controller: Any | None = None) -> None` | Store controller + access_control |
| `tr` | `(message: str) -> str` | Message translation |
| `export_data` | `(output_folder, params, profile_data, geol_data, struct_data, drillhole_data=None, interp_data=None, export_options=None) -> list[str]` | Full export |
| `_resolve_layers` | `(params) -> tuple[Any, Any]` | Validate section layer |
| `_orchestrate_exports` | `(folder, params, …, options, msg) -> None` | Dispatch to handlers |
| `get_map_settings` | `(layers, extent, size, background_color) -> Any` | Create `QgsMapSettings` |

---

## 🛡️ Error handling

| Situation | Behavior |
|-----------|----------|
| `export_options` all `False` | Does not export; returns warning `⚠ No export options selected` |
| `profile_data` empty | Raises `DataMissingError` |
| `params.line_layer` missing | Raises `DataMissingError` |
| `line_layer` invalid (`_resolve_layers`) | Raises `DataMissingError` |
| Error in a handler | The handler wraps it in `ExportError` and **propagates** (not caught here) |
| `controller` is `None` | Skips settings reload and defaults to `.shp` |

> [!note] No `try/except` in the orchestrator
> The orchestrator relies on the `SecInterpError` hierarchy (see [[exceptions]]) to type
> failures. Each handler decides whether to abort (`raise ExportError`) or continue
> (early-return when `data` is empty). The orchestrator only **validates preconditions**
> with `DataMissingError`.

---

## 🧪 Associated tests

**Unit (mock-first)** in `tests/core/test_export_service.py`:

- `test_export_data_minimal` — topography + axes with exporter mocks.
- `test_export_data_all_types` — geology, structures, drillholes, interpretations.
- `test_export_data_3d_restricted` — 3D gate via `AccessControlService`.
- `test_export_data_missing_profile` — `DataMissingError` without `profile_data`.
- `test_export_data_no_line_layer` — `DataMissingError` without `line_layer`.
- `test_export_*_error` (geology/structures/drillholes/axes/interpretation/topography) — `ExportError` propagation.
- `test_get_map_settings` — delegation to `create_map_settings`.

**Integration** in `tests/integration/test_export_service_e2e.py` (with real QGIS):

- `test_export_topography_creates_csv` / `_creates_shp` — real file writing.
- `test_export_nothing_when_all_options_disabled` — options guard.
- `test_export_raises_when_no_profile_data` — validation.
- `test_export_geology_creates_csv_and_shp`, `test_export_interpretations_creates_2d_shp`, etc.

**Full flow** in `tests/integration/test_export_workflow.py` (3D projection logic).

---

## 👀 Observations and notes

> [!success] Strengths
> - Clean facade: one entry, `list[str]` return with no Qt signals.
> - Declarative dispatch table (`handlers`) that is easy to extend.
> - Lazy imports isolate the heavy `exporters/` module.
> - `qgis.core` stays isolated in `map_settings_factory.py`; the rest uses `Any`.

> [!warning] Points of attention
> - **Gray zone**: imports `QCoreApplication` in a "core" module (documented exception).
> - `exp_drill_3d` is absent from `export_data`'s default dict: it depends on `options` injecting it.
> - `_resolve_layers` validates `line_layer` but not `raster_layer` (subtle asymmetry).
> - UI messages (`✓ Saving files...`) are built in the core; formatting should belong to the GUI.
> - Signature duplication: `_orchestrate_exports` repeats almost all of `export_data`'s parameters.

> [!question] Open questions
> - Add `exp_drill_3d` to the default dict for symmetry with `exp_drill`?
> - Move message formatting (`✓ …`, emojis) to the GUI layer?
> - Unify layer validation (`line` and `raster`) in `_resolve_layers`?
> - Extract the `handlers` table into a declarative `Mapping` in its own module?

---

## 🔗 Related notes

- [[Index]] — vault index
- [[compat]] — `ExportServiceCompatMixin`, mixin inherited by this class
- [[path_resolver]] — `get_profile_name` / `resolve_export_path`
- [[core_services_export_handlers]] — the seven handlers it delegates to
- [[core_services_export]] — the `export/` package (re-exports)
- [[controller]] — `self.controller` (source of settings and data)
- [[dtos]] — `PreviewParams`, the input DTO
- [[exceptions]] — `DataMissingError` / `ExportError`
- [[topography]] / [[geology]] / [[structures]] / [[drillholes]] / [[drillholes_3d]] / [[interpretations]] — individual handlers

---

*Note of the SecInterp Code Walkthrough v2 vault — v3.9.1*
