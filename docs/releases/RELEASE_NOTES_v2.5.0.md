# v2.5.0: 3D Export & Advanced Control

**Release Date:** 2026-01-01

### 🚀 Major Features
- **3D Interpretation Export**:
  - **True 3D Geometry**: Export your 2D geological interpretations as fully topological 3D Shapefiles (`PolygonZ`).
  - **Robust Projection**: Implemented a **Vertex-Wise Affine Transformation** algorithm that handles complex subsurface geometries, including overturned folds, by transforming each vertex independently based on the profile azimuth.
  - **Native QGIS Integration**: Replaced legacy logic with modern QGIS Core API (`QgsPolygon`, `QgsLineString`, `QgsVectorFileWriter`) for maximum stability and performance.

- **Advanced Plugin Control**:
  - **Settings Page**: A new dedicated section in the sidebar for managing plugin configuration and preferences.
  - **Access Control Service**: New infrastructure `AccessControlService` to manage restricted "Pro" features.
  - **Feature Toggling**: Users can now enable/disable 3D export capabilities via the new Settings interface.
  - **Persistence**: Settings are automatically saved and restored across sessions using `QgsSettings`.

### 🏗️ Improvements
- **Geometric Robustness**: Significant improvements in how complex geological shapes are handled during 3D projection.
- **UI UX**: Seamless integration of the Settings page into the existing sidebar navigation workflow.
- **Testing**: Added comprehensive unit tests for geometric transformations and azimuth calculations.

### 🔧 Infrastructure & Tooling
- **Release Automation**: Updated workflows to utilize **`qgis-plugin-manager`** and the **QGIS Plugin Analyzer** tool.
- **Modern Analysis**: Migrated project analysis to the standalone **`qgis-analyzer`** command for better metrics and compliance tracking.
- **Documentation**: Updated directory structure maps and release process documentation to reflect the new architecture.

### 📝 Documentation
- **Updated Release Process**: Refined `RELEASE_PROCESS.md` with new tooling instructions.
- **Updated Development Guide**: Instructions for using the new analyzer CLI.
- **Project Structure**: Updated file maps to include new services and UI pages.
