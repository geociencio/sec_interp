# Maintenance Session: 2026-10-11 - Ecosystem Scan & Stereonet/3D Interop Plan

## Technical Summary

Two related pieces of work: (1) a **deep scan of the QGIS plugin ecosystem** relevant
to SecInterp, refreshing the public comparison report, and (2) an **interoperability
plan** for stereo net analysis and 3D modelling that follows directly from it —
**no code was written**, the plan is saved for a future session.

Part of a larger 2026-10-11 working day; the QGIS-MCP integration
(`session_2026-10-11_qgis_mcp_integration.md`) and the release-train unblock
(`session_2026-10-11_release_train_v3.10.0.md`) have their own notes.

## 1. Ecosystem scan

- Widened the competitive study from 7 to **~30 relevant plugins** across five clusters:
  geological sections, drillholes, structural/stereonet, 3D modelling, geological
  mapping (source: `plugins.qgis.org` tags + GitHub; download counts are the portal's
  cumulative figures, an adoption proxy).
- **New findings / corrections** vs the published report:
  - **OpenLog** (Apeiron/Oslandia, ~21k) — new, active direct competitor (drillhole 3D +
    section + log) and the declared successor to Geoscience's drill tools.
  - **Geoscience 2.0 is now QGIS 4-ready** → the "QGIS 4 ahead" claim was outdated.
  - **Stereonet space is crowded/mature** (qgSurf ~83k, Stereonet ~19.6k, GeoStereonet,
    Stereoplot, GeolAttitude…).
  - **3D modelling** is owned by LoopStructural (QGIS plugin) + GemPy.
  - **Adoption reality**: SecInterp ~4,640 downloads vs qProf ~212k, Geoscience ~124k,
    qgSurf ~83k → best engineering/breadth, not market leader.
- **Artifacts**: internal note `.agent-state/history/ecosystem_comparison_2026-10-11.md`
  (not published) and `docs/PLUGIN_REPORT_AND_COMPARISON_EN.md` refreshed to
  v3.10.0 / 2026-10-11 (new §6.9–§6.11, §7.5 adoption snapshot, updated SWOT/roadmap).

## 2. Stereonet / 3D interop plan

- **Premise**: do not chase the crowded stereonet space or build a 3D engine — **hand
  SecInterp's data to the specialist tools**.
- `docs/plans/implementation_plan_interop_stereonet_3d.md` — scope confirmed with the
  user and **deferred** (§9 resume checklist):
  - **Phase A (stereonet)**: export `dip` + `dip_dir` (primary) and `strike` (auxiliary)
    as **CSV + GeoPackage**; add `source_point` to the core DTO. `dip_dir` comes from the
    source dip field (`ECHADO "22 SW" → 225`) with an RHR fallback.
  - **Phase B (QGIS 3D Map View)**: B1 drillhole 3D `.qml` (tube symbols), B3
    interpretation extrusion thickness, B2 a **GUI action** building the 3D scene
    (DEM terrain + vertical scale), B4 vertical-exaggeration consistency.

### Verified technical context (grounding the plan)

| Fact | Source |
|---|---|
| `StructureMeasurement` has `distance, elevation, apparent_dip, original_dip, original_strike, attributes` — no source `(x,y)`, no dip direction | `core/domain/entities.py:46-66` |
| Source `point` present at extraction, **dropped** when the DTO is built | `structure_service.py:121`→`:139` |
| Interpretations export already ships a 3D `.qml`; drillhole 3D exports have **no style** | `interpretation_3d_exporter.py:431-471`, `drillhole_3d_exporter.py` |
| `STRIKE` is a plain azimuth (`N15W→345`); `ECHADO` carries `dip + direction` (`22 SW→225`) | `basedatosestruct_clean.csv`, `core/utils/parsing.py:97-163` |

## Verification Results

- `check_docs` PASS (36 active docs) · `sync_vault_mirrors --check` clean.
- `validate_agent_system.py` PASS (14 skills / 14 workflows).
- `ruff check` clean; `ruff format --check` no changes; `unittest discover tests` green.

## Impact

- The comparison report no longer overstates SecInterp's market position and scores the
  new competitive landscape; the roadmap prefers **interoperation** over reimplementation.
- A concrete, sample-data-validated plan is ready to implement (starting with B1) without
  re-deriving the extension points.
