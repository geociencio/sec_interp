# SecInterp — Geological Interpretation for QGIS

![QGIS](https://img.shields.io/badge/QGIS-3.0%2B-green.svg)
![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)
![Version](https://img.shields.io/badge/Version-3.6.0-orange.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![QGIS Compliance](https://img.shields.io/badge/QGIS--Compliance-52.6%2F100-yellow)
![Code Quality](https://img.shields.io/badge/Code--Quality-94.2%2F100-green)
![Tests](https://img.shields.io/badge/tests-pass-brightgreen.svg)
![Linting](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
![Managed with uv](https://img.shields.io/badge/managed%20with-uv-blueviolet)
![i18n](https://img.shields.io/badge/i18n-14%20Languages-blue.svg)

**SecInterp** (Section Interpreter) is a professional QGIS plugin designed for industrial-grade extraction and visualization of geological data. It empowers geologists to generate high-fidelity topographic profiles, project outcrops with structural integrity, and perform complex 3D drillhole analysis within a unified 2D cross-section environment.

![Hero Image](file:///home/jmbernales/.gemini/antigravity/brain/570578c0-675f-4359-95d0-61f75ff1cbcf/sec_interp_final_pro_mockup_1768774790346.png)
*SecInterp v3.6.0: Next-Gen Stability & QGIS 4 Ready.*

---

## 🆕 What's New in v3.6.0
**Phase: Next-Gen Stability, Spatial Optimization & QGIS 4 Ready**

### 🚀 QGIS 4.x & Qt6 Full Compatibility
- **API Bridging**: Implemented dynamic enum resolution and the `qt6_compat` compatibility layer to bridge strict API changes between PyQt5 and PyQt6 (e.g., `QImage` formats, `QPainter` styles, and `QDialog.Accepted`).
- **Thread-Safe Architecture**: Eradicated legacy UI threading issues and segmentation faults using robust asynchronous task anchoring.
- **Deferred Signal Emission**: Implemented `QTimer.singleShot` patterns to safely pass complex geodata from background threads to the main Qt event loop.

### ⚡ Spatial Performance Optimization
- **QgsSpatialIndex Integration**: Completely overhauled the Interpretation Manager's spatial inheritance algorithms. Shifted from O(N*M) pure Python distance checks to native C++ `QgsSpatialIndex` nearest-neighbor lookups.
- **Geological Precision**: Attribute inheritance now accurately measures perpendicular distances against geological line geometries instead of isolated points, achieving extreme performance gains (sub-second lookups for >10,000 entities).

### 🛡️ Asynchronous Rendering Stability
- **Re-entry Locks**: Added strict rendering flags in the `PreviewRenderer` to prevent race conditions during rapid preview regeneration.
- **Graceful Lifecycle Management**: Enhanced cleanup methods and C++ memory management for layer objects, ensuring zero-crash teardowns.
- **Legend Resilience**: Hardened UI components to fail silently and recover smoothly during rapid canvas repaints.

### 📦 Modernized Deployment (`qgis-manage`)
- **Multi-Version Support**: Unified CLI deployment supporting both QGIS 3 (`~/.local/share/QGIS/QGIS3/...`) and QGIS 4 (`~/.local/share/QGIS/QGIS4/...`) profiles.
- **Automated Module Discovery**: `Makefile` now automatically finds and packages all Python source files via advanced `find` logic, eliminating missing module errors.

### ✨ Sustained Quality Gates
- **Cyclomatic Complexity**: Successfully refactored massive monolithic patches to ensure all project functions strictly comply with CC <= 10.
- **Testing**: 620+ fully passing unit and integration tests, verified across both local and Docker environments.

See [CHANGELOG.md](docs/CHANGELOG.md) for complete details.

---

## 🌟 Key Features

### 1. Interactive Preview System
*   **Real-time Visualization**: Instantly view topography, geology, and structures along any drawn section line.
*   **Performance**: Uses **Parallel Processing** to handle complex geological intersections without freezing QGIS.
*   **Adaptive Level of Detail (LOD)**: Automatically adjusts data density based on zoom level for smooth navigation.
*   **Measurement Tools**: Measure distances and calculate slopes/gradients directly on the profile view with automatic **Snapping** to vertices.
*   **Drillhole Support**: Project 3D drillhole traces and geological intervals (sondajes) onto the 2D cross-section plane.

![Main Interface](docs/images/ui_main_dialog.png)
*Fig 1. Main interface showing topography and projected geology.*

### 2. Data Extraction
*   **Topography**: Extracts elevation profiles from any DEM raster.
*   **Geology**: Projects polygon outcrops onto the section line, respecting valid lithological boundaries.
*   **Structure**: Projects dip/strike measurements with configurable buffer zones and apparent dip calculations.

### 3. Geological Interpretation
*   **Interactive Drawing**: Draw interpretation polygons directly on the profile view.
*   **Smart Snapping**: Accurately snap vertices to existing topographic or geological features.
*   **Auto-Color**: Automatically assigns vivid colors to distinguish new interpretations.
*   **Undo/Redo**: Flexible editing with right-click undo support during drawing.

### 4. Professional Export
*   **Formats**: Export directly to **SHP**, **CSV**, **DXF**, **PDF**, **SVG**, or **PNG**.
*   **Layout**: Results are ready for CAD integration or reporting.

---

## 📋 Requirements

Before installing **SecInterp**, ensure your system meets the following requirements:

*   **QGIS**: 3.28 LTR or superior (including QGIS 4.x).
*   **Python**: 3.10 or superior (included with QGIS).
*   **Dependencies**: The plugin uses standard QGIS and PyQt libraries (fully compatible with both Qt5 and Qt6 via `qgis.PyQt`). Advanced analysis and development tools (like the **QGIS Plugin Analyzer** tool, executed via the `qgis-analyzer` command, and `ai-context-core`) are only required for developers and auditors.

---

## 🚀 Installation

### From QGIS Repository
1. Open QGIS.
2. Go to **Plugins > Manage and Install Plugins**.
3. Search for `SecInterp`.
4. Click **Install Plugin**.

### From ZIP File
1. Download the latest `sec_interp_v3.6.0.zip` from releases.
2. Open QGIS.
3. Go to **Plugins > Manage and Install Plugins > Install from ZIP**.
4. Select the file and click **Install**.

---

## 📖 Quick Start Guide

For detailed instructions, please see the [**User Guide**](https://geociencio.github.io/sec_interp_docs/USER_GUIDE.html).

1. **Prepare Data**: Load your DEM (Raster), Geology (Polygons), and Structure (Points) layers in QGIS.
2. **Launch Plugin**: Click the **SecInterp** icon in the toolbar.
3. **Configure Layers**:
    *   **DEM**: Select your elevation raster and band.

        ![Layer Setup](docs/images/workflow_01_select_dem.png)

    *   **Cross-section**: Select the line layer that defines your profile.

        ![Layer Setup](docs/images/workflow_03_select_section_line.png)

    *   **Geology**: Select the outcrop layer and the lithology attribute field.

        ![Layer Setup](docs/images/workflow_05_geology_setup.png)

    *   **Structure**: Select the point layer and dip/strike fields.

        ![Layer Setup](docs/images/workflow_06_structural_setup.png)

    *   **Drillholes (Optional)**: Configure Collars, Survey, and Intervals in the **Drillholes** page to project 2D drillhole traces.

        ![Collar Setup](docs/images/workflow_07_drillhole_collar_setup.png)

        ![Survey Setup](docs/images/workflow_08_drillhole_survey_setup.png)

        ![Interval Setup](docs/images/workflow_09_drillhole_interval_setup.png)

4. **Preview**: Click **Preview Profile**. The view will update asynchronously.

    ![Preview Generated](docs/images/workflow_04_preview_generated.png)

    *   *Tip: Use the scroll wheel to zoom in/out. The detail level will adapt automatically.*
    *   *Tip: Colapse panels to the left, and Results colapse down to save space.*

    ![Preview Collapsed](docs/images/workflow_04_preview_panels_colapsed.png)

5. **Export**: Use the **Export** button in the preview toolbar or go to the **Settings** page for batch export configuration.

---

## 🛠 For Developers

This plugin is open-source and welcomes contributions.

- **Source Code**: [GitHub Repository](https://github.com/geociencio/sec_interp)
- **Documentation**:
  - [**User Guide**](https://geociencio.github.io/sec_interp_docs/USER_GUIDE.html): How to use the plugin.
  - [**Architecture**](https://geociencio.github.io/sec_interp_docs/ARCHITECTURE.html): Technical design and patterns.
  - [**Development Guide**](https://geociencio.github.io/sec_interp_docs/DEVELOPMENT_GUIDE.html): Code standards and setup.
  - [**Maintenance Log**](https://geociencio.github.io/sec_interp_docs/MAINTENANCE_LOG.html): Changelog and release procedures.
  - [**Technical Compendium**](https://geociencio.github.io/sec_interp_docs/TECHNICAL_COMPENDIUM.html): Geophysical research and details.
- **Development Setup**: Use the `Makefile` and the [**Development Guide**](https://geociencio.github.io/sec_interp_docs/DEVELOPMENT_GUIDE.html).
- **Testing with Docker** (Recommended):
  Esta suite ejecuta los **tests** del proyecto dentro de un contenedor QGIS oficial (`qgis/qgis:latest`), garantizando un entorno reproducible y libre de conflictos de dependencias locales.
  ```bash
  make docker-build  # Build the test image
  make docker-test   # Run the full test suite inside a container
  ```

---

## 📄 License

This project is licensed under the GNU General Public License v3.0. See `LICENSE` for details.
