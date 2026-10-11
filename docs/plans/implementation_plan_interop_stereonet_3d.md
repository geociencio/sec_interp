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
- **Phase B — 3D model-input interop**: export GemPy/LoopStructural-ready inputs
  (orientations + surface points) from SecInterp's source geology/structures.

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
- A new **3D model-input export** (CSV) with GemPy/LoopStructural-style
  `orientations` and `surface_points`.
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
  (`:243-246`), where `dip_dir = (strike + 90) % 360` (RHR) — **verify the convention
  on real data before shipping** (§8-Q2).
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

## 4. Phase B — 3D model-input interop (GemPy / LoopStructural)

**Goal**: emit the inputs a 3D modelling tool needs, from SecInterp's **source** data
(not the section projection).

**Target formats**

| Tool | `orientations` (per measurement) | `surface_points` (per interface) |
|---|---|---|
| GemPy | `X, Y, Z, azimuth, dip, polarity` | `X, Y, Z, formation` |
| LoopStructural | orientations + geological surfaces | surfaces |

**Design decision (the crux)**: the source map coordinates are available in
`gui/adapters/` but are **dropped before `core/`**. Two options:

- **B1 (preferred)**: extend the core DTOs to carry `source_point` (and `source_z`
  from the sampled elevation) — as in Phase A — and put the exporter in `core/`
  (QGIS-agnostic, CSV only). Cleanest for architecture and tests; requires threading
  the point through the geology path too.
- **B2**: implement the 3D-input export in a **GUI-layer adapter** that reads the
  source layers directly (has `QgsProject`/geometry) and writes the files, keeping
  `core/` untouched. Faster, but adds a QGIS-dependent exporter outside the factory.

This plan recommends **B1** for the structures (already needed by Phase A) and a
**GUI adapter for the geology interfaces** (polygon vertices/centroids in the source
CRS), because geology sampling is inherently QGIS-side.

**Verification (deliberate)**
- The output is validated against a trivial GemPy model (two layers + one orientation)
  in a **manual smoke**, documented — we do **not** add GemPy as a test dependency.
- CRS/unit caveats documented (GemPy expects a single, consistent projected CRS).

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
2. **Strike convention**: is the incoming strike right-hand-rule? (→ `dip_dir = strike + 90`.)
3. **Source coords**: extend the core DTO with `source_point` (B1) vs a GUI-only
   exporter (B2)?
4. **Priority**: qgSurf/mplstereonet first, then GemPy/LoopStructural — confirm.
5. **Deliverable format**: CSV only, or CSV **and** a GeoPackage point layer?
6. **Version target**: v3.11.x, or fold into the next feature release?

> Per the @architect role, no code is written until these are answered and the plan is approved.
