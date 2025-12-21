# Implementation Plan - PreviewRenderer Fragmentation

Refactor the `PreviewRenderer` class (Complexity: 130) by decomposing it into specialized components.

## Proposed Changes

### GUI Components

#### [NEW] [preview_layer_factory.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/preview_layer_factory.py)
Move all layer creation and symbology logic here.
- `create_topo_layer()`
- `create_geol_layer()`
- `create_struct_layer()`
- `create_drillhole_trace_layer()`
- `create_drillhole_interval_layer()`
- Symbology helper methods.

#### [NEW] [preview_axes_manager.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/preview_axes_manager.py)
Handle grid lines, axis labels, and axis styling.
- `create_axes_layer()`
- `create_axes_labels_layer()`
- `_get_nice_interval()`

#### [NEW] [preview_optimizer.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/preview_optimizer.py)
Geometric optimization logic.
- `decimate()`
- `adaptive_sample()`
- `calculate_curvature()`

#### [NEW] [preview_legend_renderer.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/preview_legend_renderer.py)
Legend drawing logic.
- `draw_legend()`

#### [MODIFY] [preview_renderer.py](file:///home/jmbernales/qgispluginsdev/sec_interp/gui/preview_renderer.py)
Refactor as an orchestrator.
- Initialize sub-components.
- Update `render()` to delegate work.
- Maintain existing API for backward compatibility.

## Verification Plan

### Automated Tests
- Run `analyze_project_optfixed.py` to verify the reduction in complexity.
- Verify that standard preview generation still works (manual testing).
- Verify Y-axis labels cover the full depth of drillholes (e.g., -100m).

#### [NEW] [Y-Axis Label Fix]
Refine `PreviewAxesManager` to ensure grid lines and labels encompass the full extent.
- Update `y_start` and `y_end` logic to bound the data.
- Remove strict clipping `if y_draw >= extent.yMinimum()` to allow labels on the bounding intervals.
- Apply similar improvements to the X-axis.

### Manual Verification
1. Open the plugin.
2. Generate a preview with all layers enabled (Topography, Geology, Structures, Drillholes).
3. Verify axes and labels are correctly rendered.
4. Verify the legend is correctly drawn.
5. Export to PNG/PDF to verify legend rendering on external devices.
