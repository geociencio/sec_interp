# SecInterp — Geological Interpretation for QGIS

![QGIS](https://img.shields.io/badge/QGIS-3.0%2B-green.svg)
![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)
![Version](https://img.shields.io/badge/Version-2.5.0-orange.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![QGIS Compliance](https://img.shields.io/badge/QGIS--Compliance-100%2F100-brightgreen)
![Code Quality](https://img.shields.io/badge/Code--Quality-86.3%2F100-green)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)
![Linting](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
![Managed with uv](https://img.shields.io/badge/managed%20with-uv-blueviolet)
![i18n](https://img.shields.io/badge/i18n-ES%20%7C%20FR%20%7C%20DE%20%7C%20RU%20%7C%20PT%20%7C%20EN-blue.svg)

**SecInterp** (Section Interpreter) is a QGIS plugin designed to streamline the extraction and visualization of geological data for cross-section interpretation. It allows geologists to quickly generate topographic profiles, project geological outcrops, and analyze structural data in a unified 2D view.

---

---

## 🆕 What's New in v2.5.0
**Major Feature: 3D Export & Advanced Control**

- **🧊 3D Interpretation Export**: Export your 2D geological drawings as **true 3D Shapefiles (PolygonZ)**. The plugin now performs robust vertex-wise affine transformation to project complex geometries (including overturned folds) accurately into 3D space.
- **⚙️ Settings Page**: A new dedicated configuration hub in the sidebar for managing plugin preferences.
- **🛡️ Access Control**: Logic to manage Pro/Premium features (currently toggling 3D export).
- **🏗️ Improvements**:
  - Native QGIS API implementation for high-performance geometry creation.
  - Persistent settings across QGIS sessions.
  - Fixes for geometric topology in complex structural scenarios.

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

*   **QGIS**: 3.28 LTR or superior.
*   **Python**: 3.10 or superior (included with QGIS).
*   **Dependencies**: The plugin uses standard QGIS and PyQt5 libraries. Advanced analysis and development tools (like `qgis-plugin-analyzer` and `ai-context-core`) are only required for developers and auditors.

---

## 🚀 Installation

### From QGIS Repository
1. Open QGIS.
2. Go to **Plugins > Manage and Install Plugins**.
3. Search for `SecInterp`.
4. Click **Install Plugin**.

### From ZIP File
1. Download the latest `sec_interp_v2.5.0.zip` from releases.
2. Open QGIS.
3. Go to **Plugins > Manage and Install Plugins > Install from ZIP**.
4. Select the file and click **Install**.

---

## 📖 Quick Start Guide

For detailed instructions, please see the [**User Guide**](docs/USER_GUIDE.md).

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

    *   **Drillholes (Optional)**: Configure Collars, Survey, and Intervals in the "Drillholes" tab to project 2D drillhole traces.

        ![Collar Setup](docs/images/workflow_07_drillhole_collar_setup.png)

        ![Survey Setup](docs/images/workflow_08_drillhole_survey_setup.png)

        ![Interval Setup](docs/images/workflow_09_drillhole_interval_setup.png)

4. **Preview**: Click **Preview Profile**. The view will update asynchronously.

    ![Preview Generated](docs/images/workflow_04_preview_generated.png)

    *   *Tip: Use the scroll wheel to zoom in/out. The detail level will adapt automatically.*
    *   *Tip: Colapse panels to the left, and Results colapse down to save space.*

    ![Preview Collapsed](docs/images/workflow_04_preview_panels_colapsed.png)

5. **Export**: Go to the "Export" tab to save your profile to your preferred format.

---

## 🛠 For Developers

This plugin is open-source and welcomes contributions.

- **Source Code**: [GitHub Repository](https://github.com/geociencio/sec_interp)
- **Documentation**:
    - [**User Guide**](docs/USER_GUIDE.md): How to use the plugin.
    - [**Architecture**](docs/ARCHITECTURE.md): Technical design and patterns.
    - [**Development Guide**](docs/DEVELOPMENT_GUIDE.md): Code standards and setup.
    - [**Maintenance Log**](docs/MAINTENANCE_LOG.md): Changelog and release procedures.
    - [**Technical Compendium**](docs/TECHNICAL_COMPENDIUM.md): Geophysical research and details.
- **Development Setup**: Use the `Makefile` and `DEVELOPMENT_GUIDE.md`.

---

## 📄 License

This project is licensed under the GNU General Public License v3.0. See `LICENSE` for details.
