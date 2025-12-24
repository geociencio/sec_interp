# Walkthrough - Profile Alignment Fix (V3)

The alignment between topographic and geological profiles has been perfected using a **Snap to Surface** strategy.

## The Problem
Visual inspection revealed that while internal points were aligned (thanks to V2), the Start/End points of geological units often "popped" above or below the topographic line. This happened because those boundary points fall *between* grid samples, and the raw raster elevation there often differs from the linear interpolation of the topographic line.

## The Solution (V3)

### [geology_service.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/services/geology_service.py)

- **Snap to Interpolated Surface**:
    - Instead of querying the raster for the elevation of geological boundaries (Start/End of units), we now **interpolate** their elevation from the Topographic Master Profile.
    - This forces the geological line to lie exactly on the piecewise linear segments of the topographic line, regardless of the underlying raster roughness.
    - Inner grid points explicitly use the pre-calculated master profile elevations.

## Verification

### Manual Verification
1. Open QGIS and reload the plugin.
2. Generate a profile with Geology.
3. Zoom in to the contact between two geological units or the start/end of an outcrop.
4. **Success Criteria**: The transition point should lie exactly on the blue topographic line. There should be zero vertical separation.

# Walkthrough - LOD Optimization (Phase 1)

Phase 1 of Level of Detail (LOD) optimization introduces data decimation to improve performance with large datasets.

## Features Implemented

### [preview_renderer.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/preview_renderer.py)
- **Data Decimation**: Added [_decimate_line_data](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/preview_renderer.py#76-124) using the Douglas-Peucker algorithm to simplify line geometries.
- **Render Logic**: Updated render methods to accept a `max_points` parameter and simplify data before creating QGIS geometries.

### UI Changes
- **Preview Widget**: Added a "Max Preview Points" spinbox (default 1000) to control the target number of points in the preview.
- **Persistence**: The setting is saved and restored between sessions.
- **LOD Optimization (Phase 1)**: Basic data decimation with user-controlled point count.
- **Adaptive Sampling (Phase 2)**: Added "Auto" mode to dynamically adjust point count based on window size.
- **Zoom-Based LOD (Phase 3)**: Automatically increases detail when zooming in to preserve line quality.
- **Measurement Tool**: Measure distances and slopes directly on the profile.

## Verification Steps

### LOD Optimization
1. **Manual Mode**: Uncheck "Auto" and adjust "Max Points" spinbox. Verify preview updates closer to/further from original shape.
2. **Auto Mode**: Check "Auto". Resize the side panel or window. Verify "Max Points" is disabled and preview remains sharp without excessive points.
3. **Zoom Detail**: Check "Auto". Zoom deep into a section of the line. Wait ~0.5s. You should see the line "snap" to higher detail (smoother curves). Zoom out, and it should return to lower detail for performance.

### Measurement Tool
1. Enable the **"Measure"** button (toggle).
2. Click **Point A** then **Point B** on the profile preview.
3. Observe the red line connecting the points.
4. Check the **"Results"** pane at the bottom for:
   - Distance (total)
   - Horizontal (dx) and Vertical (dy) distance
   - Slope (degrees)
5. **Right-click** to reset the measurement.
6. Untoggle the button to return to Pan mode.
3. Open the plugin dialog.
4. Load a large dataset (long section line or high-res DEM).
5. Set "Max Preview Points" to a low value (e.g., 100) and click Preview.
6. Observe the simplified line (fewer vertices).
7. Set "Max Preview Points" to a high value (e.g., 10000) and click Preview.
8. Observe the detailed line.
9. Verify that changing the value updates the preview immediately.
