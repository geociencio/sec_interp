# SecInterp API Reference

This document provides a reference for the core services, utility functions, and main classes in the SecInterp plugin.

## Core Services (`core/services/`)

The core logic of the plugin is encapsulated in a set of services, each responsible for a specific domain.

---

### `ProfileService`

Handles the generation of the topographic profile.

**`generate_topographic_profile(line_lyr, raster_lyr, band_number)`**
- **Description**: Samples elevation data from a raster layer along a line feature.
- **Parameters**:
    - `line_lyr` (QgsVectorLayer): The line layer for the cross-section.
    - `raster_lyr` (QgsRasterLayer): The DEM layer.
    - `band_number` (int): The raster band to sample.
- **Returns**: `list[tuple[float, float]]` - A list of `(distance, elevation)` tuples.

---

### `GeologyService`

Handles the processing of geological outcrop data.

**`generate_geological_profile(line_lyr, raster_lyr, outcrop_lyr, outcrop_name_field, band_number)`**
- **Description**: Intersects the section line with geological outcrop polygons and samples the elevation, creating a geological profile. Uses an internal "master profile" for accurate elevation snapping.
- **Parameters**:
    - `line_lyr` (QgsVectorLayer): The cross-section line.
    - `raster_lyr` (QgsRasterLayer): The DEM for elevation data.
    - `outcrop_lyr` (QgsVectorLayer): The geology polygon layer.
    - `outcrop_name_field` (str): The attribute field in `outcrop_lyr` containing the geology unit names.
    - `band_number` (int): The raster band to sample.
- **Returns**: `list[tuple[float, float, str]]` - A list of `(distance, elevation, unit_name)` tuples.

---

### `StructureService`

Handles the projection of structural measurement points.

**`project_structures(line_lyr, struct_lyr, buffer_m, line_az, dip_field, strike_field)`**
- **Description**: Filters structural data points within a buffer of the section line and calculates the apparent dip for projection onto the 2D section.
- **Parameters**:
    - `line_lyr` (QgsVectorLayer): The cross-section line.
    - `struct_lyr` (QgsVectorLayer): The point layer with structural data.
    - `buffer_m` (float): The buffer distance to search for points.
    - `line_az` (float): The azimuth of the cross-section line.
    - `dip_field` (str): The attribute field for dip values.
    - `strike_field` (str): The attribute field for strike values.
- **Returns**: `list[tuple[float, float]]` - A list of `(distance, apparent_dip)` tuples.

## Main Classes

---

### `SecInterp` (`core/algorithms.py`)

The main orchestrator class for the plugin.

- **`__init__(iface)`**: Initializes the plugin, services, UI, and data cache.
- **`run()`**: Shows the main dialog and connects UI signals to handlers.
- **`process_data()`**: The main data processing workflow. Handles caching, calls the appropriate services, and triggers the preview rendering.
- **`save_profile_line()`**: Orchestrates the saving of generated data using the exporter classes.
- **`draw_preview(...)`**: Calls the `PreviewRenderer` to draw the data on the canvas.

---

### `PreviewRenderer` (`gui/preview_renderer.py`)

Responsible for rendering the interactive preview.

- **`render(...)`**: The main rendering method. It takes the data for topography, geology, and structures and creates the necessary memory layers to display on the canvas. It also handles the creation of axes and labels.
- **`_decimate_line_data(...)`**: Implements LOD Phase 1 using Douglas-Peucker simplification.
- **`_adaptive_sample(...)`**: Implements LOD Phase 2 by calculating an adaptive tolerance based on line curvature.

## Key Utility Functions (`core/utils/`)

---

### `core.utils.geology.calculate_apparent_dip(strike, dip, line_azimuth)`
- **Description**: Calculates the apparent dip of a plane as seen on a vertical cross-section.
- **Returns**: `float` - The apparent dip angle in degrees.

### `core.utils.parsing.parse_strike(value)` and `parse_dip(value)`
- **Description**: Parses strike and dip values that can be either numeric or in string format (e.g., "N 30 E", "45 SW").
- **Returns**: `float` or `(float, float)` - The parsed angle(s) in degrees.

### `core.utils.sampling.interpolate_elevation(profile_data, distance)`
- **Description**: Linearly interpolates an elevation value at a specific distance along a profile.
- **Returns**: `float` - The interpolated elevation.
