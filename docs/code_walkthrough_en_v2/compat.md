---
tags:
  - secinterp
  - code-walkthrough
  - core      # core | gui | exporters
  - general     # services | managers | renderers | adapters | validation | etc.
aliases:
  - compat.py  # e.g. path_resolver.py
  - compat     # e.g. resolve_export_path
cssclass: secinterp-note
# note_lines: 700      # optional: ceiling > 500 for high-importance modules (max 700)
---

# `core/services/export/compat.py`

> [!abstract] One-line summary
> Backward compatibility wrappers for ExportService private API. — what this module does in one sentence, without touching QGIS if it is core.

**Path**: `core/services/export/compat.py` (129 lines)
**Main class/function**: `compat`
**Layer**: core (QGIS-agnostic / GUI · Type)
**Tags**: #secinterp #core #general

---

## 🎯 Why does this file exist?

| Problem | Solution |
|---------|----------|
| (pending) | (pending) |
| (pending) | (pending) |

> [!important] Architectural note
> QGIS-agnóstico (e.g. "QGIS-agnostic", "Extract Adapter", "Factory").

---

## 🧬 Relationship diagram

```mermaid
graph TD
    A["compat"]
    A --> B["Dependency 1"]
    A --> C["Dependency 2"]
```

> [!tip] How to read
> Solid arrow = imports/delegates; dashed = callback/injected.

---

## 📦 Imports — architectural reading

```python
# compat.py
from __future__ import annotations
from pathlib import Path
from typing import Any
```

| # | Observation |
|---|-------------|
| ① | (pending) |
| ② | (pending) |

---

## 🏗️ Structure inventory

**Clases:** `class ExportServiceCompatMixin` — 7 métodos
**Funciones/Métodos:**
- `ExportServiceCompatMixin._export_topography(def _export_topography(self, folder: Path, data: list[tuple], crs: Any, csv_exporter: Any, msg: list[str], settings: Any | None=None, ext: str='.shp') -> None:)`
- `ExportServiceCompatMixin._export_geology(def _export_geology(self, folder: Path, data: list[Any] | None, crs: Any, csv_exporter: Any, msg: list[str], settings: Any | None=None, ext: str='.shp') -> None:)`
- `ExportServiceCompatMixin._export_structures(def _export_structures(self, folder: Path, data: list[Any] | None, raster_layer: Any | None, crs: Any, csv_exporter: Any, msg: list[str], options: dict[str, Any] | None=None, settings: Any | None=None, ext: str='.shp') -> None:)`
- `ExportServiceCompatMixin._export_drillholes(def _export_drillholes(self, folder: Path, data: list[Any] | None, crs: Any, msg: list[str], settings: Any | None=None, ext: str='.shp') -> None:)`
- `ExportServiceCompatMixin._export_axes(def _export_axes(self, folder: Path, data: list[tuple], crs: Any, msg: list[str], settings: Any | None=None, ext: str='.shp') -> None:)`
- `ExportServiceCompatMixin._export_interpretations(def _export_interpretations(self, folder: Path, data: list[Any] | None, line_layer: Any, crs: Any, msg: list[str], settings: Any | None=None, ext: str='.shp') -> None:)`
- `ExportServiceCompatMixin._get_export_path(def _get_export_path(self, folder: Path, base_name: str, settings: Any | None, ext: str) -> tuple[Path, str]:)`

---

## 📁 Files in the package

- `compat.py` — individual note for this file.

---

## 📖 Method-by-method walkthrough

### `method_1`

```python
# (enriquecer)
```

_(enriquecer leyendo el fuente)_

### `method_2`

```python
# (enriquecer)
```

_(enriquecer leyendo el fuente)_

<!-- Add one subsection per public method of the module -->

---

## 🔄 Data flow

| Phase | Input | Transformation | Output |
|-------|-------|----------------|--------|
| - | - | - | - |
| - | - | - | - |

---

## 🏛️ Design patterns present

| Pattern | Where | Purpose |
|---------|-------|---------|
| - | - | - |

---

## 🧾 API summary

| Symbol | Signature / Inherits | Typical use |
|--------|----------------------|-------------|
| (no symbols) | `-` | - |

---

## 🛡️ Error handling

_(pending)_

---

## 🧪 Associated tests

_(pending)_

---

## 👀 Observations and notes

> [!success] Strengths
> - (skeleton)

> [!warning] Points of attention
> - (skeleton)

> [!question] Open questions
> - (skeleton)

---

## 🔗 Related notes

- [[Index]] — vault index
- [[Index]] — index
- [[controller]] — orchestrator

---

*Note of the SecInterp Code Walkthrough v2 vault — v3.8.0*
