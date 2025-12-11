# Changelog Reference - v1.1 (Draft)

## New Features

### 🚀 Performance & Visualization
*   **Adaptive Level of Detail (LOD)**: Implemented a smart rendering system for the profile preview.
    *   **Decimation**: Automatically reduces the number of points drawn based on the screen resolution, ensuring smooth performance even with high-density data.
    *   **Dynamic Zoom**: Detail levels automatically adjust as you zoom in and out, providing high precision when needed and fast rendering for overview.

### 📏 Interactive Tools
*   **Profile Measurement Tool**: Added a new interactive tool to the preview toolbar.
    *   Allows users to draw lines on the profile to measure distances.
    *   Real-time display of **Slope** (degrees), **Distance** (linear), **Horizontal Distance** (dx), and **Vertical Distance** (dy).
    *   Visual feedback with a "rubber band" line.

### 🖥️ User Experience (UI/UX)
*   **Dynamic UI Logic**: The preview checkboxes ("Show Topography", "Show Geology", "Show Structure") now intuitively enable or disable based on the data you have selected.
    *   Prevents invalid configurations by ensuring a **Section Line** is always selected before preview options are available.
    *   Provides immediate visual feedback on missing requirements.

## Bug Fixes & Improvements

*   **Deployment**: Fixed a critical issue where the `measure_tool` module was missing from the deployed package, causing `ModuleNotFoundError`.
*   **Compatibility**: Updated `QgsRubberBand` usage to align with modern QGIS API standards (fixed `TypeError` on newer 3.x versions).
*   **Stability**: Resolved various import errors and improved type safety in validation logic.

## Technical Details (For Developers)
*   New package `sec_interp.gui.tools` created to house interactive map tools.
*   Implemented `is_complete()` method pattern across UI page classes for robust state validation.
*   Updated `scripts/deploy.sh` to include new modular components automatically.
