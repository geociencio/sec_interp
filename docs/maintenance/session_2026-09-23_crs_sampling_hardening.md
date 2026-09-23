# Maintenance Session: 2026-09-23 - CRS Sampling Hardening + Structure/Section UX Fixes

## Technical Summary

A manual QGIS 4 test with a geographic DEM (EPSG:4326, misleadingly named
`..._3857.tif`) and a projected section line (EPSG:32614, on-the-fly
reprojection) froze the machine on accept. Root cause: the profile sampling
path derived its densify interval from the raster pixel size in the raster's own
CRS and applied it as map units of the section line, exploding a ~50 km line
into hundreds of millions of vertices. The session fixed that class of bugs
end-to-end (freeze, wrong structural/collar elevations, geology precision),
added a best-effort mislabelled-CRS detector, fixed a signal-reconnection defect
that left structural field combos empty, and committed the pending UI-gating
work from the previous crashed session.

## Changes Made

### Freeze prevention and CRS-aware sampling
- `core/utils/geometry_utils/processing.py`: `MAX_DENSIFY_POINTS = 50_000`; the
  pure `densify_line_points` grows the interval when the requested vertex count
  would exceed the cap.
- `gui/adapters/geometry.py`: new `build_sampling_transform`,
  `raster_resolution_in_crs`, `resolve_sampling_interval`; `sample_elevation_along_line`
  resolves the interval in the section line CRS and reprojects each sample point
  into the raster CRS; `sample_point_elevation` accepts `source_crs`.
- `gui/adapters/geology_extractor.py`: master profile uses the CRS-aware
  interval and reprojects sample points.
- `gui/adapters/structure_extractor.py`: new `make_elevation_sampler` (resolves
  the line→raster transform once) used by the controller and preview service.
- `gui/adapters/drillhole_extractor.py`: collar Z fallback propagates the line
  CRS to the sampler.
- `plugin/render_pipeline.py`: dip-line length uses the CRS-aware resolution.
- `core/services/export/handlers/structures.py`: guards an invalid raster
  resolution.

### Mislabelled-CRS detection (blocking) and mismatch warning
- `core/validation/crs_plausibility.py` (new): conservative extent-based
  heuristic (`implausible_crs_reason`, `configured_layer_metadata`).
- `LayerMetadata`: `extent_*` + `pixel_size_x`; `ValidationExtractor` populates
  them.
- `CrsPlausibilityValidator` added to `validate_all` and
  `validate_preview_requirements` (hard error → blocks preview/export).
- `ProjectValidator.crs_plausibility_error`, `crs_compatibility_warning`;
  `InputManager.get_crs_plausibility_error` / `get_crs_warning`.
- `UIStatusManager`: DEM dot red on mislabel, amber on mismatch, one-time
  deduplicated message with remediation ("Assign Projection", not "Reproject").

### Structural measurement UX
- `gui/ui/pages/structure_page.py`: internal wiring moved into an idempotent
  `connect_signals()` (was in `_setup_ui`, lost after `SignalManager.connect_all`
  ran `disconnect_all` → field combos never populated).

### Pending UI gating (from previous crashed session)
- Committed the S0/S1/S2 gating, Mandatory labels, dependent-page blocking, and
  traffic-light status dots (`98758e92`).

## Verification Results

- Local suite: **666 tests OK** (`PYTHONPATH=.. uv run python3 -m unittest discover tests`).
- `ruff check` + `ruff format`: clean.
- New tests: `test_crs_plausibility.py`, `test_validation_extractor.py`,
  `test_structure_extractor.py`, `test_structure_page.py`; extended
  `test_project_validator.py`, `test_ui_gating.py`, `test_geometry_adapter.py`,
  `test_geometry_utils.py`.
- Manual smoke on QGIS 4 (`uv run qgis-manage deploy --no-compile --qgis-version 4`):
  freeze gone (preview/export in ms); topography 430 pts / 6109 m = 14.24 m per
  sample (exactly the pixel transformed to metres); structural ticks on the
  profile; collar Z correct; interpretations inherited (`chito`, `angie`) and
  persisted across QGIS restarts; GPKG/PNG export coherent.
- `gdalinfo` confirmed the DEM is EPSG:4326 despite the `_3857` filename.

## Impact

- Eliminates a machine-freezing failure mode and silent zero elevation for
  structures/collars under on-the-fly reprojection.
- Blocks mislabelled CRS before producing silently wrong output, with a clear
  remediation message.
- Restores structural field selection, unblocking structural workflows.

## Commits

- `baf11d8c` fix(dem): prevent sampling freeze when DEM and section line CRS differ
- `98758e92` feat(gui): gate dependent pages and buttons on mandatory inputs
- `02d9cd65` feat(validation): warn on CRS mismatch and make geology sampling CRS-aware
- `1e44c658` feat(validation): block on mislabelled CRS via extent plausibility
- `ef88acf7` fix(gui): repopulate structural field combos after signal reconnect
- `eb9ffa20` fix(gui): reproject structure and collar elevation sampling to DEM CRS

## Deferred

- Legend sizing/visibility (to be defined with the legend workstream).
- Bilinear resampling of the profile (nearest-neighbour accepted for now).
- Multi-line section selector (Fase 1.5 of the v3.9.0 plan).
- Data-origin fix: the geology CSV lost accented characters on import (UTF-8).
