---
tags:
  - secinterp
  - code-walkthrough
  - core      # core | gui | exporters
  - processors     # services | managers | renderers | adapters | validation | etc.
aliases:
  - collar_processor.py  # e.g. path_resolver.py
  - collar_processor     # e.g. resolve_export_path
cssclass: secinterp-note
# note_lines: 700      # optional: ceiling > 500 for high-importance modules (max 700)
---

# `core/services/drillhole/collar_processor.py`

> [!abstract] One-line summary
> Processing logic for Drillhole Collars (pure computation). — what this module does in one sentence, without touching QGIS if it is core.

**Path**: `core/services/drillhole/collar_processor.py` (100 lines)
**Main class/function**: `collar_processor`
**Layer**: core (QGIS-agnostic / GUI · Type)
**Tags**: #secinterp #core #processors

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
    A["collar_processor"]
    A --> B["Dependency 1"]
    A --> C["Dependency 2"]
```

> [!tip] How to read
> Solid arrow = imports/delegates; dashed = callback/injected.

---

## 📦 Imports — architectural reading

```python
# collar_processor.py
from __future__ import annotations
import contextlib
from typing import Any
from sec_interp.core.domain import DrillholeProjection
from sec_interp.core.services.drillhole.projection_engine import ProjectionEngine
```

| # | Observation |
|---|-------------|
| ① | (pending) |
| ② | (pending) |

---

## 🏗️ Structure inventory

**Clases:** `class CollarProcessor` — 4 métodos
**Funciones/Métodos:**
- `CollarProcessor.extract_and_project_detached(def extract_and_project_detached(self, collar_data: dict[str, Any], line_points: list[tuple[float, float]], buffer_width: float, collar_id_field: str, collar_z_field: str, collar_depth_field: str, pre_sampled_z: dict[Any, float] | None=None) -> DrillholeProjection | None:)`
- `CollarProcessor.build_coordinate_map(def build_coordinate_map(self, collar_data: list[dict[str, Any]]) -> dict[Any, tuple[float, float]]:)`
- `CollarProcessor._extract_z(def _extract_z(self, attrs: dict[str, Any], z_field: str, hole_id: Any, pre_sampled: dict[Any, float] | None) -> float:)`
- `CollarProcessor._extract_depth(def _extract_depth(self, attrs: dict[str, Any], depth_field: str) -> float:)`

---

## 📁 Files in the package

- `collar_processor.py` — individual note for this file.

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
