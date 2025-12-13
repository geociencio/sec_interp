# SecInterp — Geological Interpretation for QGIS

![QGIS](https://img.shields.io/badge/QGIS-3.0%2B-green.svg)
![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)
![Version](https://img.shields.io/badge/Version-1.1-orange.svg)

**SecInterp** (Section Interpreter) is a QGIS plugin designed to streamline the extraction and visualization of geological data for cross-section interpretation. It allows geologists to quickly generate topographic profiles, project geological outcrops, and analyze structural data in a unified 2D view.

---

## 🌟 Key Features

### 1. Interactive Preview System
*   **Real-time Visualization**: Instantly view topography, geology, and structures along any drawn section line.
*   **Performance**: Uses **Parallel Processing** to handle complex geological intersections without freezing QGIS.
*   **Adaptive Level of Detail (LOD)**: Automatically adjusts data density based on zoom level for smooth navigation.
*   **Measurement Tools**: Measure distances and calculate slopes/gradients directly on the profile view.

### 2. Data Extraction
*   **Topography**: Extracts elevation profiles from any DEM raster.
*   **Geology**: Projects polygon outcrops onto the section line, respecting valid lithological boundaries.
*   **Structure**: Projects dip/strike measurements with configurable buffer zones and apparent dip calculations.

### 3. Professional Export
*   **Formats**: Export directly to **SHP**, **CSV**, **DXF**, **PDF**, **SVG**, or **PNG**.
*   **Layout**: Results are ready for CAD integration or reporting.

---

## 🚀 Installation

### From QGIS Repository
1. Open QGIS.
2. Go to **Plugins > Manage and Install Plugins**.
3. Search for `SecInterp`.
4. Click **Install Plugin**.

### From ZIP File
1. Download the latest `sec_interp_v1.1.zip` from releases.
2. Open QGIS.
3. Go to **Plugins > Manage and Install Plugins > Install from ZIP**.
4. Select the file and click **Install**.

---

## 📖 Quick Start Guide

1. **Prepare Data**: Load your DEM (Raster), Geology (Polygons), and Structure (Points) layers in QGIS.
2. **Launch Plugin**: Click the **SecInterp** icon in the toolbar.
3. **Select Line**: Use the "Select Line" tool to pick a section line from a layer, or draw one interactively.
4. **Configure Layers**:
    *   **DEM**: Select your elevation raster and band.
    *   **Geology**: Select the outcrop layer and the lithology attribute field.
    *   **Structure**: Select the point layer and dip/strike fields.
5. **Preview**: Click **Preview Profile**. The view will update asynchronously.
    *   *Tip: Use the scroll wheel to zoom in/out. The detail level will adapt automatically.*
6. **Export**: Go to the "Export" tab to save your profile to your preferred format.

---

## 🛠 For Developers

This plugin is open-source and welcomes contributions.

- **Source Code**: [GitHub Repository](https://github.com/geociencio/sec_interp)
- **Technical Docs**: See the [Wiki](https://github.com/geociencio/sec_interp/wiki) or `docs/` folder.
- **Development Setup**: See `README_DEV.md` for virtualenv and testing instructions.

---

## 📄 License

This project is licensed under the GNU General Public License v3.0. See `LICENSE` for details.
