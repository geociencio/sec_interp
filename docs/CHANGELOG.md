# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- **Preview Status Bar**: Added a status bar to the preview area displaying real-time cursor coordinates, map scale, and Coordinate Reference System (CRS).
- **Preview Panning**: Enabled the Pan tool (`QgsMapToolPan`) by default in the preview canvas for better interaction.
- **Programmatic UI**: Complete migration from `.ui` files to a pure Python user interface using `layouts` and `widgets`, improving maintainability and flexibility.
- **3-Column Layout**: Redesigned the main dialog into a responsive 3-column layout (Sidebar, Settings, Preview) with a collapsible Settings panel.
- **Drillhole Placeholder**: Added basic structure for future Drillhole integration.

### Changed
- **Layer Selection**: All layer comboboxes (DEM, Cross-section, Geology, Structures) now default to an empty selection ("Choose layer...") to preventing accidental usage of incorrect layers.
- **Preview Axis Labeling**: Improved `PreviewRenderer` to correctly align axis labels (Y-axis labels to the left, X-axis labels below) using data-defined properties, fixing misalignment issues.
- **Band Selection Width**: Increased the minimum width of the band selection combobox in the DEM page to ensure band numbers are fully visible.
- **Preview Rendering**: Updated `PreviewRenderer` to use `QgsPalLayerSettings.Property.OffsetQuad` for label placement compatibility with QGIS 3.x API.

### Fixed
- **AttributeError Fixes**: Resolved multiple `AttributeError` exceptions caused by legacy widget references in validation and preview logic after the UI refactor.
- **Type Errors**: Fixed `TypeError` in `PreviewRenderer` by using explicit `QgsPalLayerSettings.Placement` enums.
- **Legacy Code Removal**: Removed obsolete references to `resources.qrc` and `.ui` file loading.

