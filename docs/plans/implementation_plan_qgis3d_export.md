# QGIS 3D Section Export — Implementation Plan

> **Date**: 2026-11-18
> **Status**: WP0–WP3 implemented (2026-11-18); WP4+ pending
> **Scope**: make SecInterp's 3D exports usable in QGIS's native 3D Map View.
> **Related**: [interop/stereonet plan](implementation_plan_interop_stereonet_3d.md) ·
> [BlenderGIS design](../research/blendergis_export_design.md)

---

## 1. Goal and non-goals

### Goal

Turn the current partial 3D export into a coherent **QGIS 3D section**:

- every section layer is georeferenced with Z and a consistent CRS;
- 3D styles make drillholes, interpretations, geology, structures and topography
  visible and semantically distinguishable;
- one action opens a 3D Map View with the project DEM, a sensible vertical scale and
  a camera perpendicular to the section;
- vertical exaggeration is consistent between terrain and vector layers.

### Non-goals

- Replacing QGIS 3D with BlenderGIS or embedding Blender.
- Forking BlenderGIS or adding a GeoPackage importer to it.
- Building a general 3D modelling engine.
- Exporting a `.qgz` scene template; the scene is built in the current project.
- Changing the existing 2D/PDF/SVG/CSV exports.

### Decisions already taken

| Decision | Choice |
| :--- | :--- |
| Primary 3D viewer | QGIS 3D Map View |
| BlenderGIS | Secondary; Shapefile only |
| QGIS 3D bundle format | GeoPackage with multiple layers |
| BlenderGIS bundle format | Shapefile bundle |
| Section transform | Shared `SectionFrame` |
| Scene delivery | GUI action in the current project, not a `.qgz` |
| Vertical exaggeration | Metadata; terrain and vectors scaled consistently |

---

## 2. Current baseline

| Layer | Current export | Gap |
| :--- | :--- | :--- |
| Interpretations | `PolygonZ` + `.qml` rule-based 3D renderer | No extrusion thickness |
| Drillhole traces | `LineStringZ` real/projected | No `.qml`; default lines are invisible |
| Drillhole intervals | `LineStringZ` real/projected | No `.qml`; no per-unit 3D color |
| Topography | 2D profile line `(dist, elev)` | No 3D layer; CRS mislabeled |
| Geology | 2D profile lines `(dist, elev)` | No 3D layer; CRS mislabeled |
| Structures | 2D profile lines `(dist, elev)` | No 3D layer; CRS mislabeled |
| Section line | Used internally | Not exported as geometry |
| Scene | None | No DEM terrain, vertical scale or section camera |

Code entry points:

- [interpretation_3d_exporter.py](../../exporters/interpretation_3d_exporter.py)
- [interpretation_3d/style.py](../../exporters/interpretation_3d/style.py) — no
  `setExtrusionHeight()`
- [drillhole_3d_exporter.py](../../exporters/drillhole_3d_exporter.py) — no style
  generation
- [handlers/interpretations.py](../../core/services/export/handlers/interpretations.py)
- [handlers/drillholes_3d.py](../../core/services/export/handlers/drillholes_3d.py)
- [handlers/topography.py](../../core/services/export/handlers/topography.py)
- [handlers/geology.py](../../core/services/export/handlers/geology.py)
- [handlers/structures.py](../../core/services/export/handlers/structures.py)
- [advanced_tab.py](../../gui/ui/pages/settings/advanced_tab.py)

---

## 3. Target architecture

```text
profile data (distance, elevation)
        │
        ▼
SectionFrame (pure core)
  origin, azimuth, CRS, length, VE
        │
        ├── 3D exporters ──► section_3d.gpkg (QGIS 3D)
        │                     section_*.shp (BlenderGIS)
        │
        └── QML/3D renderers ──► styles applied by the scene builder
                                      │
                                      ▼
                              QGIS 3D Map View
                       DEM + vertical scale + section camera
```

### 3.1 `SectionFrame` contract

New pure module: `core/domain/section_frame.py`.

```python
@dataclass(frozen=True)
class SectionFrame:
    origin_x: float
    origin_y: float
    azimuth_rad: float
    crs_authid: str
    length: float
    vertical_exaggeration: float = 1.0

    def to_map(self, distance: float, elevation: float) -> tuple[float, float, float]:
        x = self.origin_x + distance * math.cos(self.azimuth_rad)
        y = self.origin_y + distance * math.sin(self.azimuth_rad)
        return x, y, elevation
```

Rules:

- no QGIS imports in `core/`;
- origin = first vertex of the selected 2-vertex line;
- azimuth measured in the projected CRS;
- geographic source CRS is reprojected before the frame is built;
- true Z is exported; `vertical_exaggeration` is metadata, not baked by default;
- all 3D exporters consume the same frame object.

Tests:

- distance 0 and distance = length;
- azimuth 0°, 90°, 180°;
- Z passthrough;
- geographic input rejected or reprojected explicitly;
- frame equality/reproducibility.

### 3.2 3D layer contract

| Layer | Geometry | Fields |
| :--- | :--- | :--- |
| Topography | `LineStringZ` | `section_id`, `dist`, `elev` |
| Geology | `PolygonZ` per unit or `LineStringZ` contacts | `unit`, `unit_id`, `color`, `section_id` |
| Structures | `PointZ` or `LineStringZ` | `dip`, `strike`, `type`, `section_id` |
| Interpretations | `PolygonZ` | `id`, `name`, `type`, `color` |
| Drillhole traces | `LineStringZ` | `hole_id` |
| Drillhole intervals | `LineStringZ` | `hole_id`, `from_depth`, `to_depth`, `unit` |

Geology choice:

- **Preferred for colors**: one layer/file per unit, or a categorized 3D renderer by
  `unit`;
- **Alternative**: contacts as `LineStringZ` when polygon closure is ambiguous.

### 3.3 Output bundles

QGIS 3D:

```text
qgis3d/
  section_<id>.gpkg
    topography_3d
    geology_3d
    structures_3d
    interpretations_3d
    drillholes_3d
  section_<id>.json        # manifest
  styles/*.qml             # optional, applied by the scene builder
```

BlenderGIS (unchanged scope):

```text
blendergis/
  section_<id>_*.shp       # one SHP per layer/unit
  manifest.json
```

### 3.4 Manifest

```json
{
  "schema": 1,
  "section": {
    "id": "secc1",
    "crs": "EPSG:32614",
    "origin": [x0, y0],
    "azimuth_deg": 123.4,
    "length": 850.0,
    "units": {"horizontal": "m", "vertical": "m"}
  },
  "vertical_exaggeration": 1.0,
  "layers": [
    {"name": "topography_3d", "geometry": "LineStringZ"},
    {"name": "geology_3d", "geometry": "PolygonZ"},
    {"name": "structures_3d", "geometry": "PointZ"},
    {"name": "interpretations_3d", "geometry": "PolygonZ"},
    {"name": "drillholes_3d", "geometry": "LineStringZ"}
  ]
}
```

---

## 4. Work packages

### WP0 — `SectionFrame` and geometry helpers

**Deliverables**

- `core/domain/section_frame.py` (pure).
- Shared projection helper used by interpretation 3D and new exporters.
- Refactor `exporters/interpretation_3d/geometry.py` to consume the frame.
- Tests for transform and CRS policy.

**Entry points**: `core/domain/`, `exporters/interpretation_3d/`.

**Acceptance**: one transform implementation, no duplicated `cos/sin` formulas.

---

### WP1 — 3D topography, geology and structures

**Deliverables**

- `Topography3DExporter` (`LineStringZ`).
- `Geology3DExporter` (`PolygonZ` per unit or contacts).
- `Structure3DExporter` (`PointZ`/`LineStringZ` with dip/strike).
- Handler integration:
  - `handlers/topography.py`
  - `handlers/geology.py`
  - `handlers/structures.py`
- Multi-layer GeoPackage writer for QGIS 3D.

**Rules**

- Use `SectionFrame.to_map()` for every vertex.
- Preserve attributes and stable layer names.
- Geology units: one layer per unit or a categorized renderer.
- Structures: keep `dip`, `strike`, `type`; do not infer 3D planes in this phase.

**Tests**

- Geometry type, Z range, CRS and fields for each layer.
- No QGIS import in `core/`.
- Empty data → no layer, no exception.

---

### WP2 — 3D styles

**Deliverables**

- Drillhole `.qml` with `QgsLine3DSymbol` (tube width).
- Drillhole intervals categorized by `unit`.
- Interpretation `QgsPolygon3DSymbol.setExtrusionHeight()`.
- 3D styles for topography, geology and structures.
- Materials per unit/color; no reliance on 2D symbology.

**Entry points**

- `exporters/drillhole_3d_exporter.py`
- `exporters/interpretation_3d/style.py`
- `exporters/section_3d/style.py` (new)

**Acceptance**

- Drillhole traces/intervals are visible in QGIS 3D.
- Interpretations have volume, not just a plane.
- Styles can be applied programmatically by the scene builder.

---

### WP3 — QGIS 3D bundle and manifest

**Deliverables**

- `section_3d.gpkg` multi-layer bundle.
- `section_3d.json` manifest.
- Export summary listing layers/files.
- Option “QGIS 3D (GPKG)” vs “BlenderGIS (SHP)”.

**Rules**

- QGIS 3D uses GPKG; BlenderGIS uses SHP.
- No GeoPackage in the BlenderGIS preset.
- Manifest is written even if only a subset of layers is exported.

**Tests**

- GPKG layers readable by QGIS; CRS/Z preserved.
- Manifest matches actual files.
- Missing layers are declared, not silently omitted.

---

### WP4 — 3D scene action

**Deliverables**

- `gui/3d/section_scene.py`.
- Action “Open 3D section” in the dialog/toolbar.
- Build/update `Qgs3DMapSettings` in the current project.
- Terrain from the project DEM or flat fallback.
- `setTerrainVerticalScale(ve)`.
- Extent/origin/background/lights.
- Camera:
  - QGIS 4: `QgsCrossSection(p1, p2, halfWidth)` +
    `setCrossSectionSideView()`;
  - QGIS 3.28: `QgsCameraController.setCameraPose()` fallback.
- Apply 3D renderers from WP2.

**Rules**

- Do not mutate the project permanently unless the user confirms.
- No `.qgz` template.
- Feature-detect QGIS 4 cross-section API.
- `Qgs3DMapCanvas` is a `QWindow` in QGIS 4; embed with
  `QWidget.createWindowContainer` and test the lifecycle.

**Tests**

- Mock `Qgs3DMapSettings` for extent/VE/origin.
- Camera pose math for a known line.
- Manual QGIS 3.28/4.x check.

---

### WP5 — Vertical exaggeration consistency

**Deliverables**

- `vertical_exaggeration` in the manifest and scene builder.
- Same factor applied to terrain and vector geometry, or explicit separation.
- Default heuristic:

```text
ve = clamp(length / (relief * 3), 1, 15)
```

- UI override (1×, 5×, 10×, 20×).

**Acceptance**

- A long, low-relief section looks readable without floating layers.
- Switching VE keeps geology, interpretations and drillholes aligned with terrain.
- No double application of the profile's display VE.

---

## 5. UI changes

In **Settings → Advanced**:

- keep existing interpretation/drillhole toggles;
- add “Export complete 3D section”;
- add format selector (QGIS 3D GPKG / BlenderGIS SHP);
- add vertical scale selector;
- show a warning when the section line CRS is geographic.

In the dialog:

- “Open 3D section” action after export (or independent of export);
- if a 3D view already exists, update it instead of creating duplicates;
- show a short status message with the layer count and VE.

---

## 6. Tests and QA

### Unit

- `SectionFrame` transform and CRS policy.
- Geometry fields/types for each 3D exporter.
- QML 3D renderer serialization (extrusion, line width, material).
- Manifest generation.

### Integration

- Export on `MURALLA.qgs`:
  - DEM `mdearea.tif`;
  - line `secc1.shp`;
  - geology, structures, drillholes.
- Verify:
  - every layer has Z and the same CRS;
  - interpretations have extrusion;
  - drillholes have 3D style;
  - GPKG has all expected layers.
- QGIS 3D smoke:
  - scene opens with terrain;
  - camera is perpendicular;
  - VE alignment;
  - no crashes on close/reopen.

### Gates

- `make flake8`, `make qgis-validate`, `make portal-check` unaffected.
- `ruff`/`mypy`/`unittest` green.
- `core/` remains QGIS-free.
- i18n for new UI strings.

---

## 7. Acceptance checklist

- [ ] Topography, geology, structures, interpretations and drillholes export in 3D.
- [ ] Every layer uses the same `SectionFrame`, CRS and Z convention.
- [ ] Drillholes are visible with 3D line symbols.
- [ ] Interpretations have extrusion thickness.
- [ ] GPKG bundle opens in QGIS 3D with all layers.
- [ ] Manifest records CRS, origin, azimuth, length, units and VE.
- [ ] The scene action sets DEM, VE, extent and a perpendicular camera.
- [ ] Terrain and vectors remain aligned when VE changes.
- [ ] QGIS 3.28 and 4.x paths are tested.
- [ ] 2D exports and BlenderGIS SHP behavior are unchanged.

---

## 8. Risks and mitigations

| Risk | Mitigation |
| :--- | :--- |
| `Qgs3DMapCanvas` is `QWindow` in QGIS 4 | Prototype early; `createWindowContainer`; test lifecycle |
| `terrainVerticalScale` may not scale vectors identically | B4 alignment test; apply VE explicitly if needed |
| GPKG styles are not auto-loaded | Apply QML/renderers from the scene builder |
| Geographic CRS / float32 precision | Reproject to metric CRS; reject degrees |
| PolygonZ vertical faces render oddly | Extrusion + material test; fallback to line contacts |
| Large sections / many units | Layer per unit, LOD option, avoid thousands of objects |
| QGIS 3.28 lacks `QgsCrossSection` | Feature detection + camera-pose fallback |
| User project mutation | Build/update scene in memory; ask before saving |

---

## 9. Implementation order

1. **WP0** — `SectionFrame` + tests.
2. **WP1** — topography and geology 3D; then structures.
3. **WP2** — drillhole styles + interpretation extrusion.
4. **WP3** — GPKG bundle + manifest.
5. **WP4** — scene action + camera.
6. **WP5** — VE consistency and polish.

WP0–WP3 are testable without a live 3D view; WP4 is the highest-risk UI work and
should follow once the data contract is stable.

---

## 10. Progress

- [x] **WP0 — `SectionFrame`**: pure domain frame, validation, endpoint
  factory and tests; interpretation 3D now consumes the shared frame.
- [x] **WP1 — 3D topography/geology/structures**: `Topography3DExporter`
  (`LineStringZ`), `Geology3DExporter` (`PolygonZ` bands) and
  `Structure3DExporter` (`PointZ`), with a shared GeoPackage bundle and
  per-layer Shapefile fallback. Activation is gated by `exp_section_3d`,
  exposed in WP3.
- [x] **WP2 — 3D styles and extrusion**: drillhole traces/intervals receive
  `QgsLine3DSymbol` QML, interpretation 3D symbols use `setExtrusionHeight()`,
  and topography/geology/structures get 3D QML sidecars.
- [x] **WP3 — GeoPackage bundle + manifest**: `exp_section_3d` is exposed in
  Settings → Advanced and wired into the export dialog; successful 3D exports
  write `section_3d.json` with CRS, origin, azimuth, length, VE and layer
  geometry.
- [ ] WP4 — 3D scene action/camera.
- [ ] WP5 — vertical-exaggeration consistency.

## 11. Open questions

1. Geology: one layer per unit vs a single categorized layer? (Recommendation: one
   layer per unit for reliable 3D material assignment.)
2. Default VE: automatic heuristic or fixed 5× until validated?
3. Should the 3D scene be ephemeral or persisted in the project?
4. Is “Open 3D section” always available, or only after a successful 3D export?
5. Which QGIS versions are the minimum test matrix: 3.28, 3.40, 4.x?
