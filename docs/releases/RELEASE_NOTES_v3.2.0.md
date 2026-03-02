# Release v3.2.0 - QGIS 4.x Readiness & Structural Refinement

## Highlights
This release focuses on ensuring 100% compatibility with QGIS 4.x (API-agnostic principles), massive test suite expansion, and significant structural refactoring for better performance and maintainability.

### 🚀 Added
- **Testing**: Massive expansion reaching **450+ successful tests** in Docker.
- **Automation**: "Documentation-as-Code" system for dynamic `TESTING_STATUS.md` updates.
- **Integration**: New suite for 3D vertical projections in Cartesian coordinate systems.
- **Security**: Path Traversal protection in all data exporters.
- **Validation**: Type and range validation for preview parameters.

### 🛠️ Changed
- **Compatibility**: 100% compliance with QGIS 4.x (`qgis.PyQt`).
- **UI**: Refactored `PreviewLayerFactory` with shared geometry helpers.
- **GUI**: Standardized `DialogSettingsPersistence` and widget resets.

### 🐞 Fixed
- **Core**: Regression in `TrajectoryEngine` buffer filtering.
- **Stability**: Fixed `TypeError` in dependency injection and `IndexError` in drillhole projections.
- **Memory**: Resolved leaks in `QgsRubberBand` and signal disconnections.
- **Mocks**: Enhanced testing environment with unique layer IDs and strict geometry validation.

---
**Published Artifacts**: `sec_interp.3.2.0.zip`
**Date**: 2026-03-02
