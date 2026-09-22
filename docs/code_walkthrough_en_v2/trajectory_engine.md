---
tags:
  - secinterp
  - code-walkthrough
  - core      # core | gui | exporters
  - processors     # services | managers | renderers | adapters | validation | etc.
aliases:
  - trajectory_engine.py  # e.g. path_resolver.py
  - trajectory_engine     # e.g. resolve_export_path
cssclass: secinterp-note
# note_lines: 700      # optional: ceiling > 500 for high-importance modules (max 700)
---

# `core/services/drillhole/trajectory_engine.py`

> [!abstract] One-line summary
> Engine for calculating and projecting drillhole trajectories (pure). — what this module does in one sentence, without touching QGIS if it is core.

**Path**: `core/services/drillhole/trajectory_engine.py` (111 lines)
**Main class/function**: `trajectory_engine`
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
    A["trajectory_engine"]
    A --> B["Dependency 1"]
    A --> C["Dependency 2"]
```

> [!tip] How to read
> Solid arrow = imports/delegates; dashed = callback/injected.

---

## 📦 Imports — architectural reading

```python
# trajectory_engine.py
from __future__ import annotations
from typing import Any
from sec_interp.core import utils as scu
from sec_interp.core.domain import DrillholeProjection, GeologySegment, SpatialMeta
from sec_interp.core.services.drillhole.interval_processor import IntervalProcessor
from sec_interp.core.services.drillhole.survey_processor import SurveyProcessor
```

| # | Observation |
|---|-------------|
| ① | (pending) |
| ② | (pending) |

---

## 🏗️ Structure inventory

**Clases:** `class TrajectoryEngine` — 3 métodos
**Funciones/Métodos:**
- `TrajectoryEngine.__init__(def __init__(self) -> None:)`
- `TrajectoryEngine.process_single_hole(def process_single_hole(self, hole_id: Any, collar_point: tuple[float, float], collar_z: float, given_depth: float, survey_data: list[tuple[float, float, float]], intervals: list[tuple[float, float, str]], line_points: list[tuple[float, float]], buffer_width: float, section_azimuth: float) -> tuple[list[GeologySegment], DrillholeProjection]:)`
- `TrajectoryEngine.create_drillhole_result(def create_drillhole_result(self, hole_id: Any, projected_traj: list[tuple], hole_geol_data: list[GeologySegment], collar_proj: Any=None) -> DrillholeProjection:)`

---

## 📁 Files in the package

- `trajectory_engine.py` — individual note for this file.

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
