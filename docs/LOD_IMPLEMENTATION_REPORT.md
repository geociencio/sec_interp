# Level-of-Detail (LOD) Implementation Report

**Date:** 2025-12-10

## 1. Overview

To address performance issues with large datasets in the preview canvas, a multi-phase Level-of-Detail (LOD) optimization strategy was implemented. This document details the implemented features, how they work, and how to use them in the user interface.

The implementation is based on the plan outlined in `docs/lod_optimization_plan.md`.

## 2. Implemented Features

The LOD system is implemented in three main phases, which are now present in the codebase:

- **Phase 1: Basic Decimation**: A manual, point-based simplification method.
- **Phase 2: Adaptive Sampling**: A curvature-based simplification method.
- **Phase 3: Zoom-Based LOD**: An automatic simplification method based on the preview's zoom level.

## 3. How It Works

The core of the LOD system resides in `gui/preview_renderer.py` and is managed by `gui/main_dialog_preview.py`.

### 3.1. Phase 1: Basic Decimation

- **Method**: `_decimate_line_data(data, max_points)` in `PreviewRenderer`.
- **Logic**: This method uses the Douglas-Peucker algorithm, provided by `QgsGeometry.simplify()`. It calculates a simplification `tolerance` based on the desired number of `max_points`. This provides a simple and effective way to reduce the number of vertices in a line while preserving its general shape.
- **Usage**: This is the default LOD method when "Auto" mode is disabled.

### 3.2. Phase 2: Adaptive Sampling

- **Methods**: `_calculate_curvature(data)` and `_adaptive_sample(data)` in `PreviewRenderer`.
- **Logic**:
    1.  `_calculate_curvature` computes a simple metric for the "bend" at each vertex in the line.
    2.  `_adaptive_sample` calculates the *average* curvature for the entire line.
    3.  Based on this average, it determines a simplification `tolerance`. Lines with higher average curvature (more complex) get a smaller tolerance (more detail is preserved), while flatter lines get a larger tolerance (more simplification).
    4.  It then calls `_decimate_line_data` with this dynamically calculated tolerance.
- **Note**: This is a simplified version of true adaptive sampling, as it uses a single tolerance for the whole line rather than varying it per segment.

### 3.3. Phase 3: Zoom-Based LOD ("Auto" Mode)

- **Methods**: `_on_extents_changed()` and `_update_lod_for_zoom()` in `PreviewManager`.
- **Logic**:
    1.  When the preview canvas is zoomed or panned, the `extentsChanged` signal is emitted.
    2.  This triggers `_on_extents_changed`, which starts a 200ms debounce timer. This prevents re-rendering on every single small mouse movement during a pan/zoom operation.
    3.  Once the timer finishes, `_update_lod_for_zoom` is called.
    4.  This method calculates the zoom ratio (how zoomed in the user is) and determines a new target for `max_points`. A closer zoom results in a higher target for `max_points`, providing more detail.
    5.  It then re-renders the preview with this new `max_points` value.

## 4. How to Use in the UI

The LOD features are controlled by a set of widgets in the "Preview" panel:

![LOD Controls](images/lod_controls.png) <!-- It would be good to add an image here later -->

- **Max Points `[ 1000 ]`**: This `QSpinBox` is active when **"Auto" is unchecked**. It allows you to manually set the maximum number of points for the preview. Higher values give more detail but may reduce performance.

- **Auto `☑`**: When **checked**, this enables **Phase 3 (Zoom-Based LOD)**.
    - The "Max Points" spinner is disabled.
    - The level of detail will automatically adjust as you zoom and pan the preview.
    - This is the recommended mode for general use.

- **Adaptive `☑`**: When **checked**, this enables **Phase 2 (Adaptive Sampling)**.
    - This can be used in combination with both "Manual" and "Auto" modes.
    - Instead of just decimating to a target number of points, it will first analyze the line's curvature to perform a more intelligent simplification.
    - It is recommended to keep this checked for better visual results.

### Recommended Usage:

- For general exploration, keep **Auto** and **Adaptive** checked.
- If you need to see a specific number of points or if the automatic adjustment is not desired, uncheck **Auto** and set the **Max Points** manually.
