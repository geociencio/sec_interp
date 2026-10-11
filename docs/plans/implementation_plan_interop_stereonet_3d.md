# Implementation Plan: External Interop — Stereonet Analysis & 3D Modelling

**Phase**: post-v3.10.0 backlog (candidate v3.11.x)
**Status**: 📝 PLAN — pending architect/user approval (no code written)
**Created**: 2026-10-11
**Origin**: ecosystem deep scan — `.agent-state/history/ecosystem_comparison_2026-10-11.md`
**References (verified)**: `core/domain/entities.py:46-66` (`StructureMeasurement`),
`core/services/structure_service.py:121,139` (source `point` dropped here),
`gui/adapters/structure_extractor.py:30-131` (`SectionContext`/`detach_structures`),
`exporters/profile_exporters.py:171-278` (`StructureVectorExporter`),
`core/services/export/handlers/structures.py:32-90` (`export_structures`),
`exporters/__init__.py:54-81` (`get_exporter`), `core/utils/parsing.py:32` (`parse_strike`),
`core/utils/spatial.py` (`calculate_apparent_dip`, `calculate_line_azimuth`).

---

## 0. Executive summary

The 2026 ecosystem scan shows **stereonet analysis** (qgSurf ~83k, Stereonet ~19.6k,
GeoStereonet, Stereoplot, GeoTrace…) and **3D geological modelling** (LoopStructural,
GemPy) are **crowded and mature** markets, while SecInterp's defensible moat is its
**integrated 2D section workflow**. Chasing either feature head-on is expensive and
low-differentiation. This plan therefore adds **interoperation exports** — SecInterp
keeps producing its section data and hands it to the specialist tools — rather than
reimplementing a stereonet or a 3D modelling engine.

Two deliverables:

- **Phase A — Stereonet interop**: export the structural measurements (true dip +
  strike/dip-direction) in a form `mplstereonet` and qgSurf consume directly.
- **Phase B — QGIS 3D Map View hand-off**: make the Z-aware exports render correctly in QGIS's native **3D Map View** (the workflow actually in use) — 3D styling + scene setup — with external modelling (GemPy/LoopStructural) kept as an optional extra.

**Out of scope**: an in-plugin stereonet viewer and any 3D modelling engine.

---

## 1. Verified technical context

| Fact | Source |
|---|---|
| `StructureMeasurement` carries `distance, elevation, apparent_dip, original_dip, original_strike, attributes` — **no source (x,y), no rake** | `core/domain/entities.py:46-66` |
| The source measurement `point` (map `(x,y)`) is available at extraction and **discarded** when the DTO is built | `structure_service.py:121` (in) vs `:139` (out) |
| The extractor already produces `{"point": (x,y), "attributes": {...}}` + `line_azimuth` | `structure_extractor.py:38-46,110-131` |
| `StructureVectorExporter` writes only `app_dip`, `dist`, `elev` (+ original attrs) — **dip/strike are not exported** | `profile_exporters.py:243-246` |
| `export_structures` writes `structural_profile.csv` (`dist, apparent_dip`) + a vector file | `handlers/structures.py:53-81` |
| `get_exporter` dispatches by **file extension** (`.csv`, `.gpkg`, `.shp`, `.dxf`…) | `exporters/__init__.py:54-81` |
| Strike is parsed to an **azimuth 0–360** (RHR/quadrant supported) | `core/utils/parsing.py:9-40` |

**Consequence**: Phase A needs only a small, non-breaking DTO/field extension.
Phase B needs source map coordinates, which currently do **not** reach `core/` —
a design decision (see §4 and §8-Q3).

---

## 2. Scope

**In scope**
- A new **structural attitude export** (CSV and/or GeoPackage) with true dip,
  strike and dip-direction, ready for `mplstereonet`/qgSurf.
- **QGIS 3D Map View hand-off**: 3D styling (QML) and scene setup for the existing
  Z-aware exports; optional GemPy/LoopStructural model inputs.
- Documentation of the interoperability formats + tests.

**Out of scope**
- An in-plugin stereonet renderer; fold-axis / kinematic analysis.
- Any 3D modelling engine or 3D scene view inside the plugin.
- Fault rake / slickenline kinematics (not in the current data model — see §7).

---

## 3. Phase A — Stereonet interop export

**Goal**: one click produces the attitudes the specialist tools read.

**Design**
- Extend `StructureMeasurement` with an **optional** `source_point: tuple[float, float] | None = None`
  (backward-compatible; existing constructors keep working).
- Populate it in `structure_service._process_single_structure` (`:139`) from the
  `point` already in hand (`:121`).
- Add `dip`, `strike`, `dip_dir` columns to `StructureVectorExporter._create_structure_fields`
  (`:243-246`). **Semantics confirmed by the user (from `basedatosestruct_clean.csv`)**:
  `RUMBO`/`STRIKE` = **strike azimuth** (`N 15° W → 345`); `ECHADO` = **dip + dip direction**
  (`22° SW → dip 22, dip_dir 225`). So the orientation a stereonet consumes comes from the
  dip field, and `parse_dip` already extracts `(dip, dip_dir)` — but `StructureMeasurement`
  keeps only the angle and drops the direction. Phase A must therefore **carry the dip
  direction from the source** (primary); RHR `dip_dir = (strike + 90) % 360` is a fallback
  only.
- Output a `dip_dir` + `dip` pair as the **primary** orientation (what qgSurf/mplstereonet
  plot), with `strike` kept as an auxiliary column.
- Output **both** a CSV and a GeoPackage point layer (confirmed), with the same columns.

> ⚠️ **Open technical point**: for a plane, strike ⟂ dip-direction. Here `RUMBO 345` and
> `ECHADO → 225` differ by ~120°, not 90° (a stereonet tool plots from **one** pair, so they
> cannot both be fed). Need to confirm which is authoritative for this dataset — the dip
> direction from `ECHADO` (recommended), or `RUMBO`.
- Add a `structural_attitudes.csv` writer alongside `structural_profile.csv`
  (`handlers/structures.py`), with a header the tools map without renaming:

  | Column | For | Meaning |
  |---|---|---|
  | `dip_dir` | qgSurf (point layer) | Dip direction (azimuth, 0–360) |
  | `dip` | both | True dip (0–90) |
  | `strike` | mplstereonet | RHR strike (0–360) |
  | `app_dip` | cross-check | Apparent dip on the section |
  | `dist`, `elev` | traceability | Section space |
  | `x`, `y` | traceability | Source coordinates (CRS = source layer) |
  | *(original attrs)* | provenance | Hole/feature id, unit, etc. |

**Files**
- `core/domain/entities.py` — `source_point` field.
- `core/services/structure_service.py` — populate `source_point`.
- `exporters/profile_exporters.py` — attitude columns.
- `core/services/export/handlers/structures.py` — `structural_attitudes.csv`.
- `docs/` — a short "Interoperability" note (path TBD, §8-Q5).

**Tests**
- `tests/core/` — `StructureMeasurement` keeps `initializer` compatibility;
  `dip_dir` conversion.
- `tests/exporters/` — the CSV/GeoPackage carries `dip_dir/dip/strike/x/y`.
- A round-trip assertion: the emitted header matches the documented qgSurf/mplstereonet
  contract.

---

## 4. Phase B — QGIS 3D Map View hand-off

**Context**: the 3D workflow actually in use is SecInterp's Z-aware export loaded in
QGIS's native **3D Map View**, not an external modeller. What exists today:

| Export | Geometry | Style | 3D Map View state |
|---|---|---|---|
| Interpretations (`Interpretation3DExporter`) | `PolygonZ` projected onto the section plane | `.qml` with a **rule-based 3D renderer** per unit | renders per-unit in 3D |
| Drillhole traces / intervals (`Drillhole*3DExporter`) | `LineStringZ` (traces and intervals) | **no `.qml`** | thin default lines, no 3D symbol |

**Goal**: make "SecInterp export → open 3D Map View" a one-step, coherent result.

**Confirmed scope** (from the user, 2026-10-11: *both* layer types; missing = **styles,
terrain, vertical scale**; extrusion **yes**):

- **B1 — 3D styles.** Interpretations already ship a 3D `.qml`; give the **drillhole**
  traces/intervals the same treatment — a `.qml` with `QgsLine3DSymbol` (tube width),
  intervals coloured by `unit`. (`Drillhole*3DExporter` currently emit **no style**.)
- **B2 — 3D scene setup.** Terrain from the project DEM + a defined **vertical scale**,
  so the exported layers open in the 3D Map View without hand-configuring the canvas.
  Design to confirm: a GUI action that builds/updates a `Qgs3DMapSettings` scene in the
  current project (vs. shipping a `.qgz`/scene template).
- **B3 — Extrusion thickness.** Give interpretation "slabs" a width so they read as 3D
  bodies instead of co-planar section polygons.
- **B4 — VE consistency.** `Interpretation3DExporter` hardcodes `vert_exag=1.0`
  (`_collect_projected_features`, `:385`); align/document the interaction with B2's
  vertical scale.

**Acceptance criteria (validated on `examples/sample_data/`)**

Project `MURALLA.qgs` (DEM `mdearea.tif`, line `secc1.shp`, geology `geologia.shp`,
structures `pts.shp`, drillhole CSVs `DrillCollar/DrillsurveySummary/DillLith/…`):

1. Drillhole 3D exports (traces + intervals, real and projected) come with a `.qml`
   whose 3D symbol is a visible tube; intervals differ per `unit`.
2. One action opens/shows a 3D Map View with `mdearea.tif` as terrain and the exported
   layers, at the configured vertical scale.
3. Interpretation 3D polygons render per-unit and (when enabled) carry the extrusion
   thickness.
4. `ruff`/`mypy`/`unittest` green; no `qgis` import added to `core/`.

> Cleanup while here: `Interpretation3DExporter._write_shapefile` builds an unused
> `SaveVectorOptions(driverName="ESRI Shapefile")` and then delegates to
> `create_vector_writer` (driver by extension) — dead code.

### 4.1 Optional — External 3D modelling (GemPy / LoopStructural)

If **building** models (not just viewing) is wanted later, emit GemPy/LoopStructural
inputs (`orientations` `X, Y, Z, azimuth, dip, polarity`; `surface_points`
`X, Y, Z, formation`) from the source data. That needs source map coordinates, which
are dropped before `core/` (`structure_service.py:121`→`:139`) — the same `source_point`
extension as Phase A, plus a GUI adapter for the geology interfaces.
**Demoted to optional** because the workflow in use is the QGIS 3D View.

---

## 5. Phase C — optional (only if approved)

- A **qgSurf field-mapping preset** and a short "export → open in tool X" checklist in
  the UI/Help.
- A **docs page** "Interoperability" listing the supported hand-offs (qgSurf,
  mplstereonet, GemPy, LoopStructural) and their exact columns.
- Round-trip note: what SecInterp can **import back** (nothing, for now).

---

## 6. QA & gates

- Core stays QGIS-free; no new `qgis` import in `core/` (test `tests/core` runs without QGIS).
- `ruff check`/`format` clean; `make mypy` (core + exporters) stays green; CC ≤ 10.
- `unittest discover tests` green; new unit tests for the conversion + export fields.
- i18n: any new user-facing string wrapped/translated (14 languages).
- Documentation gate: `check_docs` + vault mirrors (`sync_vault_mirrors.sh`).

---

## 7. Risks

| Risk | Mitigation |
|---|---|
| Strike convention ambiguity (RHR vs dip-direction) | Verify on real data; expose both `strike` and `dip_dir`; document |
| No rake/fault kinematics in the model | State the limitation; qgSurf fault plotting not covered in v1 |
| GemPy/LoopStructural input drift across versions | Pin the documented columns; keep the CSV, not a bespoke binary format |
| Scope creep into a real stereonet/3D engine | Explicit non-goals (§2); interop only |
| Source-CRS/units mismatch for 3D | Document; emit in the source CRS; no silent reprojection |

---

## 8. Open questions (need approval before Phase A code)

1. **Scope**: confirm **exports only** (interop), not a native stereonet preview.
2. **Orientation semantics** — *confirmed by the user 2026-10-11*: `RUMBO N15W` → strike
   345; `ECHADO 22 SW` → dip 22, **dip_dir 225**. The export uses **dip + dip_dir** as the
   primary pair (strike kept as auxiliary). **Still open**: strike 345 and dip_dir 225 are
   ~120° apart, not perpendicular (a plane needs 90°) → confirm which pair is
   authoritative before plotting.
3. **Source coords** — *answered 2026-10-11*: **extend the core DTO** with `source_point`.
4. **Priority**: qgSurf/mplstereonet (stereonet) first — confirm. And within 3D, which
   of §4's candidate items matter most (3D QML for drillholes, scene setup, VE
   consistency, extrusion)?
5. **Deliverable format** — *answered 2026-10-11*: **both** CSV and GeoPackage.
6. **Version target**: v3.11.x, or fold into the next feature release?
7. **3D scope** — *answered 2026-10-11*: both layer types; missing = **styles, terrain,
   vertical scale**; **extrusion wanted**. Remaining design choice: B2 as a **GUI action
   that builds/updates the live 3D scene** vs. shipping a `.qgz`/scene template — which?

> Per the @architect role, no code is written until these are answered and the plan is approved.
