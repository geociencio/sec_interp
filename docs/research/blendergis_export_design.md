# BlenderGIS Export Design

> **Date**: 2026-11-01
> **Status**: design proposal (analysis + implementation plan)
> **Goal**: export SecInterp section data so it can be imported into Blender through
> [BlenderGIS](https://github.com/domlysz/blendergis) as georeferenced 3D layers.
> **Scope**: exporter architecture and file contract; not the Blender-side art direction.

---

## 1. Executive summary

SecInterp already has the right foundation: interpretation polygons and drillhole
traces/intervals are exported as `PolygonZ`/`LineStringZ` with a CRS and a
section-derived origin/azimuth. BlenderGIS can import those Shapefile geometries.

The current flow is not yet a complete BlenderGIS pipeline because:

1. the **2D profile exports** (topography, geology, structures, interpretations) use
   `(distance, elevation)` coordinates but carry the map CRS in the `.prj`;
2. only interpretations and drillholes have 3D exports;
3. GeoPackage/DXF are offered even though BlenderGIS’s documented vector importers
   consume Shapefile;
4. there is no section manifest (origin, azimuth, CRS, units, vertical exaggeration);
5. vertical exaggeration is not represented in the 3D export.

The recommended deliverable is a **BlenderGIS preset** that produces a folder of
georeferenced Shapefile layers sharing one `SectionFrame`, plus a manifest and a
minimal README.

---

## 2. Current implementation

| Layer | Exporter | Geometry | Coordinates | BlenderGIS status |
| :--- | :--- | :--- | :--- | :--- |
| 3D interpretations | [`Interpretation3DExporter`](../../exporters/interpretation_3d_exporter.py#L36) | `PolygonZ` | map X/Y from section origin + azimuth, Z elevation | ✅ usable |
| Drillhole traces (real) | [`DrillholeTrace3DExporter`](../../exporters/drillhole_3d_exporter.py#L35) | `LineStringZ` | actual `x_3d`, `y_3d`, `z` | ✅ usable |
| Drillhole intervals (real) | [`DrillholeInterval3DExporter`](../../exporters/drillhole_3d_exporter.py#L145) | `LineStringZ` | actual `x_3d`, `y_3d`, `z` | ✅ usable |
| Drillhole traces/intervals (projected) | same | `LineStringZ` | nearest point on the section line (`x_proj`, `y_proj`, `z`) | ✅/⚠️ on the section plane |
| Topography 2D | [`ProfileLineVectorExporter`](../../exporters/profile_exporters.py#L32) | 2D line | `QgsPointXY(dist, elev)` but `crs` is the map CRS | ❌ wrong georeference |
| Geology 2D | [`GeologyVectorExporter`](../../exporters/profile_exporters.py#L84) | 2D lines | `(dist, elev)` with map CRS | ❌ wrong georeference |
| Structures 2D | [`StructureVectorExporter`](../../exporters/profile_exporters.py#L171) | 2D lines | `(dist, elev)` with map CRS | ❌ wrong georeference |
| Interpretations 2D | [`Interpretation2DExporter`](../../exporters/interpretation_exporters.py#L32) | 2D polygons/lines | profile coordinates with map CRS | ❌ wrong georeference |

The 3D interpretation transform is in
[`geometry.py`](../../exporters/interpretation_3d/geometry.py#L28-L67):

```text
east  = origin_x + distance * cos(azimuth)
north = origin_y + distance * sin(azimuth)
elev  = profile_y / vertical_exaggeration   # currently 1.0
```

Drillhole “real” exports use the true trajectory; “projected” exports collapse each
point to its nearest position on the section line, so both remain map coordinates.

The 2D exporters pass the map CRS while writing profile coordinates. Any GIS consumer,
including BlenderGIS, will interpret those coordinates in the map CRS and place the
layer at the wrong location. This is a correctness issue independent of Blender.

---

## 3. BlenderGIS constraints

From the BlenderGIS README, wiki and shapefile importer:

- vector import is documented for **Shapefile** (`PolygonZ`, `PolyLineZ`, etc. are
  recognized), plus raster/GeoTIFF and OSM;
- the importer supports **Z geometry**, but not MultiPatch; elevation can come from
  geometry, a field, a ground object or be flat;
- by default all features are merged into **one mesh**, and merged imports do **not**
  carry attribute data; importing separate objects preserves attributes and allows
  naming by field, but is slow for thousands of features;
- there is **no documented vector GeoPackage importer**; `core/basemaps/gpkg.py`
  is for basemap caching, not vector layers;
- DXF is not a GIS import path in BlenderGIS; it belongs to Blender’s separate DXF
  importer;
- CRS must be specified on import; BlenderGIS stores a scene origin to keep
  projected coordinates near the Blender origin, and reprojects subsequent imports to
  the scene CRS;
- the wiki explicitly warns that longitude/latitude Shapefiles lose precision because
  Blender uses float32; use a suitable projected CRS.

References:

- <https://github.com/domlysz/blendergis>
- <https://github.com/domlysz/blendergis/wiki/Shapefile-import>
- <https://github.com/domlysz/blendergis/wiki/Georeferencing-management>
- <https://github.com/domlysz/blendergis/blob/master/operators/io_import_shp.py>

> The wiki itself notes that it is still being updated for Blender 2.8; verify the
> current Blender 4.x behavior empirically before freezing the import workflow.

**Consequences**:

1. The BlenderGIS preset must force `.shp` and write the `.prj`.
2. Do not ship a single geology mesh if unit colors are required; either split by
   unit into one Shapefile per unit, or document “import as separate objects” and its
   performance cost.
3. A geographic CRS is not acceptable for a BlenderGIS preset; reproject to a metric
   CRS before export.
4. Set the Blender scene CRS **before** the first import; all layers should use that
   CRS.
5. Configure camera clipping for the scene extent, as the wiki recommends.

---

## 4. Proposed architecture

### 4.1 `SectionFrame`

A single immutable transform shared by every 3D layer:

```python
@dataclass(frozen=True)
class SectionFrame:
    origin: QgsPointXY
    azimuth_rad: float
    crs: QgsCoordinateReferenceSystem
    section_id: str
    length: float
    vertical_exaggeration: float = 1.0

    def to_map(self, distance: float, elevation: float) -> QgsPoint:
        x = self.origin.x() + distance * math.cos(self.azimuth_rad)
        y = self.origin.y() + distance * math.sin(self.azimuth_rad)
        return QgsPoint(x, y, elevation)
```

Rules:

- `origin` is the first vertex of the selected 2-vertex section line;
- `azimuth` is measured in the **projected** CRS, not in degrees;
- if the line CRS is geographic, reproject the line (and export) to a metric CRS
  first; never mix degrees and metres;
- `distance` is in horizontal map units and `elevation` in vertical units;
- `vertical_exaggeration` is metadata by default: export **true Z** and let Blender
  scale it. If a baked option is offered, record the factor in the manifest.

All new 3D exports must use this object; the existing interpretation 3D transform
should be refactored to consume it instead of duplicating the formula.

### 4.2 BlenderGIS bundle

Add a high-level export mode that writes:

```text
blendergis/
  section_<id>_topography.shp
  section_<id>_geology_<unit>.shp   # optional split by unit
  section_<id>_structures.shp
  section_<id>_interpretations.shp
  drillholes_<id>_traces.shp
  drillholes_<id>_intervals.shp
  manifest.json
  README.txt
```

Each Shapefile must ship its `.shp`, `.shx`, `.dbf`, `.prj` and `.cpg` sidecars.

### 4.3 Layer contract

| Layer | Geometry | Required attributes | Notes |
| :--- | :--- | :--- | :--- |
| Topography | `LineStringZ` | `section_id`, `dist`, `elev` | One feature per profile |
| Geology | `PolygonZ` or `LineStringZ` | `unit`, `unit_id`, `color`, `section_id` | Polygon strips need a documented baseline Z; one file per unit is preferred because merged imports lose attributes |
| Structures | `PointZ` or `LineStringZ` | `dip`, `strike`, `type`, `section_id` | Add short plane traces if a line representation is preferred |
| Interpretations | `PolygonZ` | `id`, `name`, `type`, `color`, `created_at` | Existing fields |
| Drillhole traces | `LineStringZ` | `hole_id` | Use “Real 3D” for BlenderGIS; split by hole only if per-hole attributes are needed |
| Drillhole intervals | `LineStringZ` | `hole_id`, `from_depth`, `to_depth`, `unit` | Existing fields; same merge/attribute caveat |

Optional fields: `source_layer`, `crs_epsg`, `elevation_datum`, `vertical_exaggeration`.

### 4.4 Manifest

`manifest.json` is not consumed by BlenderGIS, but it makes the bundle reproducible and
scriptable:

```json
{
  "schema": 1,
  "section": {
    "id": "secc1",
    "crs": "EPSG:32617",
    "origin": [500000.0, 8000000.0],
    "azimuth_deg": 123.4,
    "length": 850.0,
    "units": {"horizontal": "m", "vertical": "m"}
  },
  "vertical_exaggeration": 1.0,
  "layers": [
    {"name": "topography", "file": "section_secc1_topography.shp", "geometry": "LineStringZ"},
    {"name": "geology", "file": "section_secc1_geology.shp", "geometry": "PolygonZ"},
    {"name": "structures", "file": "section_secc1_structures.shp", "geometry": "PointZ"},
    {"name": "interpretations", "file": "section_secc1_interpretations.shp", "geometry": "PolygonZ"},
    {"name": "drillhole_traces", "file": "drillholes_secc1_traces.shp", "geometry": "LineStringZ"},
    {"name": "drillhole_intervals", "file": "drillholes_secc1_intervals.shp", "geometry": "LineStringZ"}
  ]
}
```

Include `crs_wkt` when the CRS is custom or cannot be resolved to an EPSG code.

---

## 5. Correctness fixes

### 5.1 2D profile exports

The 2D vectors are valid drawings but not georeferenced. Choose one policy:

- **Recommended**: keep them as profile drawings, write a local/undefined CRS and add
  `dist`/`elev` fields; document that they are not for GIS import.
- Alternative: add a separate `profile_2d` namespace and never pass the map CRS.

Do not silently write map CRS on `(dist, elev)` coordinates. That breaks BlenderGIS
and any other GIS consumer.

### 5.2 Metric CRS

For the BlenderGIS preset:

1. take the section line CRS;
2. if it is geographic, reproject the line to an appropriate metric CRS (UTM zone or
   user-selected);
3. build the `SectionFrame` in that CRS;
4. write the same CRS to every `.prj`.

Record both `source_crs` and `export_crs` in the manifest if they differ.

### 5.3 Vertical exaggeration

Export true elevations by default. If the UI profile is vertically exaggerated, do not
double-apply it:

- `display_elev = true_elev * ve` is a view concern;
- the 3D bundle stores `true_elev` and `ve` in the manifest;
- Blender can scale Z by `ve` per collection if desired.

### 5.4 Large coordinates

Projected coordinates can be large (UTM northings around 8,000,000). BlenderGIS
already stores a scene origin to keep coordinates near the Blender origin; set the
scene CRS/origin before importing and validate precision. Keep the georeferenced
Shapefile as the authoritative export; only add a local-origin variant if a specific
Blender/BlenderGIS workflow cannot preserve the scene origin.

---

## 6. UI and workflow

Add a **BlenderGIS** preset rather than changing existing defaults:

- in `Settings → Advanced`:
  - “Export for BlenderGIS”;
  - force 3D interpretations;
  - force real drillhole coordinates;
  - force Shapefile;
- optionally add a dedicated **Export → BlenderGIS bundle** action;
- keep `.gpkg` for QGIS and `.dxf` for CAD;
- show a warning if the section line CRS is geographic and reprojection is not possible.

Suggested user flow:

1. Select a two-vertex section line.
2. Generate the preview/profile.
3. Export the BlenderGIS bundle.
4. In Blender, set the scene CRS to the manifest CRS.
5. Import the Shapefiles; BlenderGIS reads Z from the geometry.
6. Convert lines to curves, polygons to meshes with Solidify, and color by
   `unit`/`color`.

---

## 7. Blender-side helper (optional, P2)

A small script can:

- read `manifest.json`;
- import each Shapefile with BlenderGIS;
- create one collection per layer;
- assign a material from `unit_color`/`color`;
- bevel drillhole curves;
- add an orthographic camera normal to the section plane;
- set clipping and unit scale.

This is an aid, not a substitute for the georeferenced export contract.

---

## 8. Implementation plan

### P0 — make BlenderGIS export correct

1. Add `SectionFrame` and tests for start/end/azimuth/Z.
2. Add 3D exporters for topography, geology and structures; reuse the frame.
3. Add `BlenderGIS` preset (SHP + real 3D) and manifest/README.
4. Reproject to a metric CRS in the preset; reject/warn on geographic input.
5. Split geology by unit (or document separate-object import) so `unit`/`color`
   survive BlenderGIS’s merged-mesh mode.
6. Stop writing the map CRS on 2D profile vectors; document local coordinates.
7. Validate with BlenderGIS in Blender 4.x: set scene CRS first, import all layers,
   check attributes, Z and camera clipping.

### P1 — usability and fidelity

1. Reproject geographic lines to a metric CRS automatically or explicitly.
2. Add unit colors/palette and structure attributes.
3. Add vertical-exaggeration metadata and an optional baked mode.
4. Add integration tests that inspect SHP geometry type, `.prj`, fields and Z.

### P2 — ecosystem

1. Blender helper script and sample `.blend`.
2. Optional glTF/OBJ export with materials for non-BlenderGIS users.
3. GeoPackage multi-layer bundle for QGIS alongside the SHP bundle.

---

## 9. Acceptance criteria

- [ ] All BlenderGIS layers share one `SectionFrame` and one CRS.
- [ ] Every `.shp` has `.shx`, `.dbf`, `.prj` and `.cpg`.
- [ ] Topography, geology, structures and interpretations import at the correct
      map location, not near the origin.
- [ ] Interpretations are vertical polygons in map X/Y with real Z.
- [ ] Drillhole “real” traces intersect the section at the expected positions;
      “projected” traces lie on the section plane.
- [ ] A section in EPSG:32617 (UTM) imports correctly in BlenderGIS with the DEM.
- [ ] The Blender scene CRS is set before the first import; subsequent layers reproject
      consistently.
- [ ] Unit/color attributes survive (split files or separate-object import).
- [ ] A geographic source either reprojects cleanly or produces an explicit warning;
      no degrees are shipped in a BlenderGIS bundle.
- [ ] No MultiPatch geometry is required; `PolygonZ`/`LineStringZ` import correctly.
- [ ] Camera clipping is configured for the scene extent.
- [ ] Vertical exaggeration is recorded and not double-applied.
- [ ] The 2D profile drawings are clearly marked as local and are not advertised as
      georeferenced GIS layers.
- [ ] BlenderGIS smoke test: import all layers, apply materials, render a section view.

---

## 10. Open questions

1. Should geology be exported as closed `PolygonZ` strips or as `LineStringZ`
   contacts? Polygons are better for colored volumes; lines are simpler and preserve
   contacts exactly.
2. Which metric CRS should be chosen automatically: UTM zone of the section centroid,
   the project CRS if projected, or a user-selected CRS?
3. Do we need a local-origin bundle for Blender precision, in addition to the
   georeferenced one?
4. Is a Blender helper script part of the plugin release or a separate companion
   repository?
5. Which Blender/BlenderGIS versions are the supported baseline (Blender 4.x LTS)?
