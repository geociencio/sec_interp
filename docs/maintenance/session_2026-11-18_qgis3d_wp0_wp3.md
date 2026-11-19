# Session 2026-11-18 — QGIS 3D WP0–WP3 & Drillhole Z Audit

## Objective

Implement the first four work packages of the QGIS 3D section export plan and
verify the exported drillhole interval geometries.

## Result

- **WP0–WP3** implemented and merged into `main` through PRs #5, #6 and #7.
- **857 tests OK**, mypy 107 files, Ruff/Flake8/docs/forge/metrics green.
- Drillhole interval audit: geometry and attributes are complete; absolute Z is
  DEM-based and does not match the source collar elevation field.
- **WP4 (3D scene) and WP5 (VE consistency)** remain.

## Changes

### WP0 — SectionFrame

- `core/domain/section_frame.py`: pure frame with origin, azimuth, CRS, length
  and VE metadata; `from_endpoints()` and `to_map()`.
- Interpretation 3D geometry now consumes the shared frame.
- 7 unit tests.

### WP1 — 3D section layers

- `Topography3DExporter` (`LineStringZ`), `Geology3DExporter` (`PolygonZ` bands)
  and `Structure3DExporter` (`PointZ`).
- `handlers/section_3d.py`: shared GeoPackage bundle or separate Shapefiles.
- Gated by `exp_section_3d`.

### WP2 — 3D styles

- Drillhole trace/interval QML with `QgsLine3DSymbol`; intervals categorized by
  `unit`.
- Interpretation extrusion (`setExtrusionHeight`, 5 m default).
- Topography, geology and structures 3D QML sidecars.
- QGIS 4.2 offscreen smoke generated all five QML files.

### WP3 — Activation and manifest

- Settings → Advanced → “Export complete 3D section” (`exp_section_3d`).
- Persistence and dialog/export wiring.
- `section_3d.json` with CRS, origin, azimuth, length, units, VE and layer
  geometry.

### Drillhole interval audit

Exported `secc1.gpkg` layer `drillhole_intervals_3d_real_secc1`:

- 195 intervals, 5 holes, `LineStringZ`, EPSG:32614.
- 195/195 match `DillLith.csv`; from/to/unit exact, no gaps, continuous XYZ,
  monotonic Z, no zero-length intervals.
- Real vs projected: 195/195, identical Z, XY offset up to 7.1 m.
- **Z mismatch with collar table**: traces start at DEM elevations (329–564 m)
  instead of source `Elevation (m)` (2110–2225 m); difference -1581 to -1822 m.
  The collar Z field was likely empty, so the DEM fallback was used.
- QGIS 3D display issue: the layer has no applied 3D renderer and the QML width
  is only 2 m over a 6.1 km section; set a 3D line renderer width of 20–30 m.

## Verification

- `PYTHONPATH=.. uv run python3 -m unittest discover tests`: 857 OK (2 skipped).
- `make mypy`: 107 files, clean.
- `make flake8`, Ruff, docs, forge and metrics: clean.
- PR CI: five checks green on #5, #6 and #7.
- QGIS 4.2 offscreen 3D QML smoke: 5/5 styles generated.

## Pending

1. **WP4** — scene action with DEM, vertical scale and cross-section camera.
2. **WP5** — coherent vertical exaggeration between terrain and vectors.
3. **Drillhole Z** — decide whether collar elevation or DEM is authoritative and
   configure the Z field accordingly.
4. Apply the 3D renderer directly and increase the line width for display.
5. P1 signal paths, analyzer issue #1, translations, BlenderGIS P0.

## Notes

- `examples/sample_data/MURALLA.qgs` remains modified by QGIS; `.qgs~`,
  `.bak-20261110-204854` and `mdearea_bgis.tif/.wld` are local artifacts and were
  not committed.
