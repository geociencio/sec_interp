---
tags:
  - secinterp
  - code-walkthrough
  - core
  - services
aliases:
  - trajectory_engine.py
  - TrajectoryEngine
cssclass: secinterp-note
---

# `core/services/drillhole/trajectory_engine.py`

> [!abstract] One-line summary
> A **pure** per-hole orchestrator: computes the 3D trajectory, projects it onto the section, interpolates lithological intervals and packages the result into a `DrillholeProjection` with `SpatialMeta` and `GeologySegment`.

**Path**: `core/services/drillhole/trajectory_engine.py` (111 lines)
**Main class/function**: `TrajectoryEngine`
**Layer**: Core (QGIS-agnostic)
**Tags**: #secinterp #core #services

---

## 🎯 Why does this file exist?

A drillhole requires **four coordinated transformations** (final depth, trajectory,
projection and interval interpolation). Doing them separately leaves the consumer
(`DrillholeService`) with a puzzle of calls; concentrating them here gives a single
entry point per hole:

| Problem | Solution |
|---------|----------|
| Coordinate survey → trajectory → projection → intervals | `process_single_hole` chains the 4 phases |
| Decide the hole's real depth | `SurveyProcessor.determine_final_depth` (delegated) |
| Build the final DTO with spatial metadata | `create_drillhole_result` assembles `SpatialMeta` + `segments` |

> [!important] Architectural note
> **QGIS-agnostic** and without global state (it only composes two injectable
> processors in `__init__`). It is the **heart of the drillhole domain**: it receives
> pure data (`collar_point`, `survey_data`, `intervals`, `line_points`) and returns pure
> DTOs (`GeologySegment`, `DrillholeProjection`). It never touches `qgis.core`.

---

## 🧬 Relationship diagram

```mermaid
graph TD
    TE["TrajectoryEngine"]
    SP["SurveyProcessor"]
    IP["IntervalProcessor"]
    SCU["core.utils.drillhole"]
    DP["DrillholeProjection"]
    SM["SpatialMeta"]
    GS["GeologySegment"]
    DS["DrillholeService.process_context"]

    TE --> SP
    TE --> IP
    TE --> SCU
    TE --> DP
    TE --> SM
    TE --> GS
    DS -->|process_single_hole| TE
    TE -.->|(hole_geol, hole_proj)| DS
```

> [!tip] How to read
> Solid arrow = imports/delegates; dashed = result returned to the orchestrator.
> `TrajectoryEngine` composes `SurveyProcessor` + `IntervalProcessor` (a light
> **mediator** pattern) and delegates trigonometry to `core.utils.drillhole`.

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
| ① | `utils as scu` — access to the three pure trajectory functions (`calculate_drillhole_trajectory`, `project_trajectory_to_section`). |
| ② | Imports **three** domain DTOs: `DrillholeProjection` (output), `GeologySegment` (segments) and `SpatialMeta` (3D points). |
| ③ | Composes two processors from the **same package** (`IntervalProcessor`, `SurveyProcessor`) — intra-service dependency, not crossed to QGIS. |
| ④ | `Any` only in `hole_id` and `collar_proj` (optional duck-typed parameter). |

> [!note] No local `math`
> Unlike `core/utils/drillhole.py`, there is no direct trigonometry here: all math is
> delegated. `TrajectoryEngine` is **pure orchestration**.

---

## 🏗️ Structure inventory

**Classes:** `class TrajectoryEngine` — 3 methods (2 public + `__init__`)

**Instance attributes:**
- `self.survey_processor: SurveyProcessor`
- `self.interval_processor: IntervalProcessor`

**Functions/Methods:**
- `__init__() -> None` — builds the two collaborating processors
- `process_single_hole(hole_id, collar_point, collar_z, given_depth, survey_data, intervals, line_points, buffer_width, section_azimuth) -> tuple[list[GeologySegment], DrillholeProjection]`
- `create_drillhole_result(hole_id, projected_traj, hole_geol_data, collar_proj=None) -> DrillholeProjection`

---

## 📁 Files in the package

| File | Note |
|------|------|
| `trajectory_engine.py` | this note |
| `survey_processor.py` | [[core_services_drillhole]] — `determine_final_depth` |
| `interval_processor.py` | [[interval_processor]] — interval interpolation |
| `collar_processor.py` | [[collar_processor]] — collar projection |
| `projection_engine.py` | [[core_services_drillhole]] — point-to-line projection |

---

## 📖 Method-by-method walkthrough

### `__init__`

```python
def __init__(self) -> None:
    self.survey_processor = SurveyProcessor()
    self.interval_processor = IntervalProcessor()
```

Initializes the two collaborators. They are **default instances** (not
constructor-injectable), unlike `DrillholeService`, which does allow injecting them.
If a test wants to substitute `IntervalProcessor`, it must monkeypatch the attribute.

> [!note] Composition over inheritance
> `TrajectoryEngine` inherits from nothing; it **uses** two processors. This is the
> package style: small, composable classes instead of deep hierarchies.

### `process_single_hole`

```python
def process_single_hole(
    self,
    hole_id: Any,
    collar_point: tuple[float, float],
    collar_z: float,
    given_depth: float,
    survey_data: list[tuple[float, float, float]],
    intervals: list[tuple[float, float, str]],
    line_points: list[tuple[float, float]],
    buffer_width: float,
    section_azimuth: float,
) -> tuple[list[GeologySegment], DrillholeProjection]:
```

Entry point. Chains four phases with explicit comments:

```python
# 1. Determine Final Depth
final_depth = self.survey_processor.determine_final_depth(
    given_depth, survey_data, intervals
)

# 2. Trajectory and Projection
trajectory = scu.calculate_drillhole_trajectory(
    collar_point,
    collar_z,
    survey_data,
    section_azimuth,
    total_depth=final_depth,
)
projected_traj = [
    p
    for p in scu.project_trajectory_to_section(trajectory, line_points)
    if p[5] <= buffer_width
]

# 3. Interpolate Intervals
hole_geol_data = self.interval_processor.interpolate_hole_intervals(
    projected_traj, intervals, buffer_width
)

# 4. Generate results
hole_proj = self.create_drillhole_result(hole_id, projected_traj, hole_geol_data)

return hole_geol_data, hole_proj
```

1. **Final depth**: `determine_final_depth` returns `max(given_depth, max_survey_depth,
   max_interval_depth)` — the hole reaches as deep as its deepest source says.
2. **Trajectory and projection**: `calculate_drillhole_trajectory` generates the 6-tuple
   `(depth, x, y, z, 0, 0)`; `project_trajectory_to_section` turns it into an 8-tuple
   and the list comprehension **filters** points with `p[5] > buffer_width`.
3. **Interval interpolation**: delegates to `IntervalProcessor`, which returns
   `list[GeologySegment]`.
4. **Result**: `create_drillhole_result` assembles the `DrillholeProjection`.

> [!warning] Two parameters are forwarded without being used here
> `section_azimuth` is forwarded to `calculate_drillhole_trajectory` (where today it is
> a **dead** parameter, see [[drillhole]]) and `densify_step` is **not passed**, so
> `calculate_drillhole_trajectory` uses its `1.0` default. The trajectory vertex density
> is fixed at 1 m and not exposed.

### `create_drillhole_result`

```python
def create_drillhole_result(
    self,
    hole_id: Any,
    projected_traj: list[tuple],
    hole_geol_data: list[GeologySegment],
    collar_proj: Any = None,
) -> DrillholeProjection:
```

Builds the final DTO. First it maps each projected point to a `SpatialMeta`:

```python
spatial_points = []
for p in projected_traj:
    spatial_points.append(
        SpatialMeta(
            hole_id=str(hole_id),
            dist_along=p[4],
            offset=p[5],
            z=p[3],
            x_3d=p[1],
            y_3d=p[2],
            x_proj=p[6],
            y_proj=p[7],
        )
    )
```

Then it resolves the `DrillholeProjection` header coordinates from three cascading
sources:

| Order | Source | Values |
|:---:|---|---|
| 1 | `collar_proj` (if injected) | `distance`, `elevation`, `offset`, `total_depth` |
| 2 | `spatial_points[0]` (first point) | `dist_along`, `z`, `offset`, `depth=0.0` |
| 3 | nothing | all `0.0` |

Finally:

```python
return DrillholeProjection(
    hole_id=str(hole_id),
    distance=dist,
    elevation=elev,
    offset=offset,
    total_depth=depth,
    points_3d=spatial_points,
    segments=hole_geol_data,
)
```

> [!important] `collar_proj` is optional and duck-typed
> The parameter `collar_proj: Any = None` allows injecting the collar projection (a
> light `DrillholeProjection` created by [[collar_processor]]) to copy its header fields.
> If absent, they are derived from the first trajectory point. In the real flow,
> `DrillholeService` does **not** pass it (it stays `None`), so the header comes from
> `spatial_points[0]` with `total_depth = 0.0`.

---

## 🔄 Data flow

| Phase | Input | Transformation | Output |
|-------|-------|----------------|--------|
| Final depth | `given_depth`, `survey_data`, `intervals` | `max(...)` in `SurveyProcessor` | `final_depth` |
| Trajectory | `collar_point`, `collar_z`, `survey_data` | `calculate_drillhole_trajectory` | 6-tuple `(depth,x,y,z,0,0)` |
| Projection + filter | 6-tuple + `line_points` | `project_trajectory_to_section` + `p[5] <= buffer_width` | filtered 8-tuple |
| Intervals | 8-tuple + `intervals` | `IntervalProcessor` | `list[GeologySegment]` |
| Result | 8-tuple + segments | `create_drillhole_result` | `DrillholeProjection` |

> [!tip] Canonical chain
> `DrillholeService.process_context` → `process_single_hole` → `create_drillhole_result`.
> The `(hole_geol_data, hole_proj)` return feeds the service's `geol_data_all` and
> `drillhole_data_all`, the two arrays that `PreviewResult` consolidates (see
> [[drillhole_service]] and [[dtos]]).

---

## 📐 The trajectory tuple schema

`create_drillhole_result` **does** reinterpret the indices of the projected 8-tuple
(produced by `scu.project_trajectory_to_section`):

| Index | Field | Mapped to |
|:---:|---|---|
| 1 | `x` | `SpatialMeta.x_3d` |
| 2 | `y` | `SpatialMeta.y_3d` |
| 3 | `z` | `SpatialMeta.z` |
| 4 | `dist_along` | `SpatialMeta.dist_along` |
| 5 | `offset` | `SpatialMeta.offset` |
| 6 | `proj_x` | `SpatialMeta.x_proj` |
| 7 | `proj_y` | `SpatialMeta.y_proj` |

> [!warning] Positional coupling
> This is the point where the positional schema of `core/utils/drillhole.py` gets
> "pinned" into a named DTO (`SpatialMeta`). A change of tuple order would silently
> break the correspondence. See "Open questions".

---

## 🔢 Numeric example — vertical hole

`hole_id="DH01"`, `collar_point=(100, 200)`, `collar_z=50`, `given_depth=0`,
`survey_data=[(10, 0, -90)]`, `intervals=[(0, 5, "LithA")]`,
`line_points=[(0,0),(300,0)]`, `buffer_width=50`, `section_azimuth=0`:

1. `final_depth = max(0, 10, 5) = 10`.
2. `trajectory = calculate_drillhole_trajectory((100,200), 50, [(10,0,-90)], 0, total_depth=10)`
   → points from `(0,100,200,50,0,0)` to `(10,100,200,40,0,0)` (vertical: only `z` decreases).
3. `project_trajectory_to_section` projects each `(x,y)` onto `[(0,0),(300,0)]` →
   increasing `dist_along`, `offset ≈ 0` for a collar on the line.
4. `interpolate_hole_intervals` returns a `GeologySegment` `"LithA"`.
5. `create_drillhole_result` assembles the `DrillholeProjection` with the `SpatialMeta`.

> [!note] The `p[5] <= buffer_width` filter is the key
> If the whole hole falls at `offset > buffer_width`, `projected_traj` becomes `[]` and
> the resulting `DrillholeProjection` has `points_3d=[]` and `segments=[]` (the case
> covered by `test_process_empty_traj`).

---

## 🏛️ Design patterns present

| Pattern | Where | Purpose |
|---------|-------|---------|
| **Pipeline** | `process_single_hole` (4 phases) | Chain independent transformations |
| **Composition root** | `__init__` | Build collaborators at a single point |
| **Facade** | the whole class | One simple API over a complex pipeline |
| **Mapper** | `create_drillhole_result` | 8-tuple → `SpatialMeta` → `DrillholeProjection` |
| **Cascading default** | `collar_proj`/`spatial_points[0]`/`0.0` selection | Resolve header with fallback |

---

## 🧾 API summary

| Symbol | Signature / Inherits | Typical use |
|--------|----------------------|-------------|
| `process_single_hole` | `(hole_id, collar_point, collar_z, given_depth, survey_data, intervals, line_points, buffer_width, section_azimuth) -> tuple[list[GeologySegment], DrillholeProjection]` | Process one full hole |
| `create_drillhole_result` | `(hole_id, projected_traj, hole_geol_data, collar_proj=None) -> DrillholeProjection` | Build the final DTO |
| `__init__` | `() -> None` | Instantiate `SurveyProcessor` + `IntervalProcessor` |

---

## 🛡️ Error handling

`TrajectoryEngine` does **not catch** exceptions: it lets them bubble up to
`DrillholeService`, which handles them:

| Case | Behavior |
|------|----------|
| `projected_traj` empty | `create_drillhole_result` returns a DTO with `points_3d=[]` and `0.0` header (no `IndexError`) |
| Unordered survey | `calculate_drillhole_trajectory` ignores it (guard in `_process_survey_segment`) |
| `ValueError`/`TypeError`/`KeyError`/`SecInterpError` | caught in `DrillholeService.process_context` and logged with `logger.exception` |

> [!note] Why it does not catch here
> The engine knows neither the `feedback` nor the logging context; its contract is
> "either return a valid DTO, or propagate the exception". The upper layer decides
> whether a single hole's failure aborts everything or is skipped (today: skipped).

---

## 🧪 Associated tests

Mapping to the real tests under `tests/core/`:

- `tests/core/services/test_drillhole_engine_crash.py::test_create_result_with_empty_traj` —
  `create_drillhole_result` with `projected_traj=[]` does not raise `IndexError`.
- `tests/core/services/test_drillhole_engine_crash.py::test_process_empty_traj` —
  far hole (`offset > buffer`) → empty `points_3d`.
- `tests/core/services/drillhole/test_processors.py::TestSurveyProcessor` — covers
  `determine_final_depth` (phase 1 delegate).
- `tests/core/services/drillhole/test_processors.py::TestIntervalProcessor` — covers
  interpolation (phase 3 delegate).
- `tests/core/test_drillhole_service.py::test_process_context_projects_collar` —
  full-pipeline integration.

> [!tip] The crash test is a documented regression
> `test_drillhole_engine_crash.py` exists precisely because an empty trajectory once
> raised `IndexError`. The `collar_proj → spatial_points[0] → 0.0` cascade in
> `create_drillhole_result` is the defense.

---

## ⚡ Performance and complexity

| Aspect | Analysis |
|--------|----------|
| **Complexity** | dominated by `calculate_drillhole_trajectory` `O(n)` (densification) and `project_trajectory_to_section` `O(n·m)` |
| **Densification** | `densify_step` stays at its `1.0` default (not exposed) → up to ~1 vertex per metre |
| **Early filter** | `p[5] <= buffer_width` discards points before interpolation, saving work |
| **Instances** | `SurveyProcessor`/`IntervalProcessor` are created **once** per engine; `TrajectoryEngine` is shared across holes |

> [!tip] One engine, many holes
> `DrillholeService.__init__` creates a single `TrajectoryEngine` and reuses it in the
> `for collar in collar_data` loop. Since methods do not mutate instance state (beyond
> the collaborators), it is safe inside a `QgsTask`.

---

## 🌐 i18n and migration notes

- **No user-facing strings**: the module does not inherit `TranslatableMixin`; it emits
  no messages. Any error text is produced above, in `DrillholeService`.
- **Thread-safety**: no per-call mutable state ⇒ reentrant and `QgsTask`-safe.
- **v3.x migration**: forwarding `section_azimuth` to `calculate_drillhole_trajectory`
  is currently a no-op (dead parameter); and `densify_step` is not propagated. Both are
  candidates for a refactor.

---

## 👀 Observations and notes

> [!success] Strengths
> - Clear orchestration with phase comments (`# 1. … # 4.`) that make the flow legible.
> - Clean composition of two specialized collaborators.
> - Defense against empty trajectory (no `IndexError`) in `create_drillhole_result`.

> [!warning] Points of attention
> - `section_azimuth` is propagated to a dead parameter (see [[drillhole]]).
> - `densify_step` is not exposed: density is fixed at 1 m.
> - The positional 8-tuple → `SpatialMeta` mapping is fragile to reordering.

> [!question] Open questions
> - Expose `densify_step` as an engine/service parameter?
> - Inject `SurveyProcessor`/`IntervalProcessor` via constructor (like `DrillholeService`)?
> - Migrate tuples to `NamedTuple` to remove positional coupling?

---

## 🔗 Related notes

- [[Index]] — vault index
- [[drillhole_service]] — main consumer of `process_single_hole`
- [[collar_processor]] — produces the `collar_proj` that feeds the header
- [[interval_processor]] — collaborator of the interpolation phase
- [[core_services_drillhole]] — `SurveyProcessor` and `ProjectionEngine` (delegates)
- [[drillhole]] — `calculate_drillhole_trajectory` / `project_trajectory_to_section`
- [[dtos]] — `DrillholeProjection`, `SpatialMeta`, `GeologySegment`

---

*Note of the SecInterp Code Walkthrough v2 vault — v3.9.0*
