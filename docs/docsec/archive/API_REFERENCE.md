# SecInterp API Reference

This document provides a technical reference for the core services, utility functions, and main classes in the SecInterp plugin (v2.2.0).

## Core Services (`core/services/`)

The core logic of the plugin is encapsulated in a set of services, each responsible for a specific domain.

---

### `ProfileService`

Handles the generation of the topographic profile and fundamental sampling.

**`generate_topographic_profile(line_lyr, raster_lyr, band_number)`**
- **Description**: Samples elevation data from a raster layer along a line feature.
- **Parameters**:
    - `line_lyr` (QgsVectorLayer): The line layer for the cross-section.
    - `raster_lyr` (QgsRasterLayer): The DEM layer.
    - `band_number` (int): The raster band to sample.
- **Returns**: `list[tuple[float, float]]` - A list of `(distance, elevation)` tuples.

---

### `GeologyService`

Handles the processing of geological outcrop intersection data.

**`generate_geological_profile(...)`**
- **Description**: Intersects the section line with geological unit polygons. Returns rich `GeologySegment` objects.
- **Returns**: `List[GeologySegment]` - A list of segments containing unit names, coordinates, and attributes.

---

### `StructureService`

Handles the projection of structural measurement points.

**`project_structures(...)`**
- **Description**: Projects structural measurements into the 2D section plane, calculating apparent dip.
- **Returns**: `List[StructureMeasurement]` - Dataclass containing projected coordinates and calculated dip.

---

### `DrillholeService`

Handles 3D to 2D projection and processing of drillhole data.

**`project_collars(...)`**
- **Description**: Projects collar points onto the section line within a specified buffer.
- **Returns**: `List[Tuple]` - (hole_id, dist_along, elevation, offset, depth).

**`process_intervals(...)`**
- **Description**: Orchestrates desurvey, projection, and interval interpolation.
- **Returns**: `Tuple[List[GeologySegment], List[Dict]]` - Geological segments and trace geometries.

## Main Classes

---

### `SecInterp` (`sec_interp_plugin.py`)

The main entry point class for the QGIS plugin.

- **`initGui()`**: Initializes the plugin's UI components and toolbar icons.
- **`run()`**: Main entry point for the plugin's interactive dialog.

---

### `SecInterpDialog` (`gui/main_dialog.py`)

The primary user interface manager.

- **`__init__()`**: Orchestrates specialized managers (`DialogSignalManager`, `DialogDataAggregator`).
- **`preview_profile_handler()`**: Triggers the generation and rendering of the profile preview.
- **`export_preview()`**: Handles the export of the current session data to multiple formats.

---

### `PreviewRenderer` (`gui/preview_renderer.py`)

Responsible for rendering the interactive preview using PyQGIS.

- **`render(...)`**: The main rendering method. Coordinates the fragmented render components:
    - `PreviewLayerFactory`: Logic for creating memory layers.
    - `PreviewAxesManager`: Grid and axis rendering.
    - `PreviewOptimizer`: Douglas-Peucker and Adaptive sampling (LOD).
    - `PreviewLegendRenderer`: Legend generation.

## Validation Framework (`core/validation/`)

The plugin uses a modular validation system organized into specialized modules:

- **`field_validator`**: Checks for numeric types, integer ranges, and field existence.
- **`layer_validator`**: Validates QGIS layers, feature counts, and geometry types.
- **`path_validator`**: Ensures safe path handling and write permissions.
- **`project_validator`**: High-level orchestration through the `ProjectValidator` class and `ValidationParams`.

## Key Utility Functions (`core/utils/`)

---

### `core.utils.geology.calculate_apparent_dip(strike, dip, line_azimuth)`
- **Returns**: `float` - The apparent dip angle as projected on the section.

### `core.utils.drillhole.calculate_drillhole_trajectory(...)`
- **Description**: Performs the desurveying calculation for 3D drillhole traces.

### `core.utils.sampling.sample_raster_along_line(...)`
- **Description**: Core routine for DEM sampling used by the `ProfileService`.
