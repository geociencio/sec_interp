# SecInterp — Geological Interpretation for QGIS

![QGIS](https://img.shields.io/badge/QGIS-3.28%2B%20%7C%204.x-green.svg)
![Qt](https://img.shields.io/badge/Qt-5%20%7C%206-blue.svg)
![License](https://img.shields.io/badge/License-GPL--2.0--or--later-blue.svg)
[![Version](https://img.shields.io/badge/Version-3.12.1-green.svg)](https://plugins.qgis.org/plugins/sec_interp/)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![Maintainability](https://img.shields.io/badge/Maintainability-99.9%2F100-brightgreen)
![Tests](https://img.shields.io/badge/tests-pass-brightgreen.svg)
![Linting](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
![Managed with uv](https://img.shields.io/badge/managed%20with-uv-blueviolet)
![i18n](https://img.shields.io/badge/i18n-14%20Languages-blue.svg)

**SecInterp** (Section Interpreter) is a professional QGIS plugin for extracting and
visualising geological data along cross-sections. It builds high-fidelity topographic
profiles, projects outcrops and structural measurements with CRS-aware sampling, and
places 3D drillhole traces and intervals on a unified 2D section — with live symbology,
configurable legends and 2D/3D interpretation export.

![SecInterp v3.12.1 main window](docs/source/images/ui_main_dialog.png)
*The SecInterp workspace: six sections, an interactive preview and a project-aware legend.*

**Latest release:** v3.12.1 · [QGIS plugin repository](https://plugins.qgis.org/plugins/sec_interp/) ·
[User Guide](https://geociencio.github.io/sec_interp_docs/USER_GUIDE.html)

---

## 🆕 What's New in v3.12.1

### 🔁 Symbology settings are now idempotent
Opening and closing the dialog repeatedly no longer stacks internal signal connections.
A symbology change now produces **one** preview refresh, and the reset button performs
**one** reset, even after several open/close cycles.

### 🎨 Portal polish
The plugin ships a **128×128** icon exported from the SVG master, and the `about` field
now describes inputs, outputs, QGIS/Qt support, dependencies and license for reviewers.
Fresh packages pass the portal artifact check with zero warnings.

### 🧰 Leaner packaging
The plugin runtime has **no external Python dependencies**: the analyzer, context and
documentation tools are development-only. `qgis-manage` 0.15 and `qgis-analyzer` 1.19.1
drive the release gates.

This patch builds on the v3.12.0 features: exact section-line selection, Interpretation
Settings, the QGIS-agnostic core and the module-size refactor. See
[v3.12.1 release notes](docs/releases/notes/v3.12.1.md) and
[CHANGELOG.md](docs/CHANGELOG.md) for details.

---

## 🌟 Key Features

### 1. Interactive Preview System
- **Real-time visualisation** of topography, geology, structures and drillholes along any
  section line.
- **Adaptive level of detail (LOD)** and parallel processing keep large sections smooth.
- **Measurement tools** with snapping to vertices, plus distance, slope and gradient.
- **Collapsible panels** for a larger canvas and a project-aware legend.

![Section preview with all layers](docs/source/images/preview_all.png)
*Preview with topography, geology, structures and drillholes.*

### 2. Data Extraction
- **Topography**: elevation profiles from any DEM, with CRS-aware line → raster sampling.
- **Geology**: polygon outcrops projected onto the section, preserving valid boundaries.
- **Structure**: dip/strike measurements with buffer zones and apparent-dip calculations.
- **Drillholes**: collars, surveys and intervals projected as traces and interval
  cylinders.

### 3. Geological Interpretation & 3D
- **Interactive drawing** of interpretation polygons on the profile, with snapping to
  topography, drillhole contacts and existing vertices.
- **Attribute inheritance** from geology overlaps and nearby drillhole intervals, with
  manual overrides.
- **PolygonZ export**: 2D interpretations become real 3D geometries on the section plane.

![Interpretation properties](docs/source/images/guide_interpretation_tool_2.png)
*Digitising an interpretation polygon and its properties.*

### 4. Live Symbology & Legend
- **Symbology tab**: live styling of topography, structures, drillhole traces and
  interpretations without modifying the source layers.
- **Per-unit editor**: hide, recolour, rename and reorder geological and drillhole units.
- **Legend layout**: position, font size and a maximum number of items; geology units and
  drillhole lithologies are grouped separately.

![Symbology settings](docs/source/images/guide_settings_symbology.png)
*Symbology tab: styles apply live to the preview and the exported section.*

### 5. Professional Export
- **Formats**: **SHP**, **CSV**, **DXF**, **PDF**, **SVG**, **PNG** and **GeoPackage**.
- **Layout**: map-ready output for CAD, reports and publications, with the configured
  legend and symbology.

---

## 📋 Requirements

- **QGIS**: 3.28 LTR or newer, including **QGIS 4.x**.
- **Python**: 3.9+ (the version bundled with QGIS 3.28; development uses 3.12).
- **Qt**: Qt5 and Qt6 through `qgis.PyQt` (no separate runtime dependency).
- **Dependencies**: none beyond QGIS. The analysis/context tools used by maintainers are
  development-only.

---

## 🚀 Installation

### From the QGIS plugin repository
1. Open QGIS.
2. Go to **Plugins → Manage and Install Plugins**.
3. Search for `SecInterp` and click **Install Plugin**.

### From a ZIP file
1. Download `sec_interp.3.12.0.zip` from the
   [releases page](https://github.com/geociencio/sec_interp/releases).
2. Open QGIS → **Plugins → Manage and Install Plugins → Install from ZIP**.
3. Select the file and click **Install**.

---

## 📖 Quick Start

The full walkthrough is in the [**User Guide**](https://geociencio.github.io/sec_interp_docs/USER_GUIDE.html).

1. **Prepare data**: load a DEM (raster), geology (polygons), structures (points) and,
   optionally, drillholes.
2. **Open SecInterp** from the toolbar.
3. **Configure the sections**:
   - **DEM / Raster**: select the elevation raster and band.

     ![DEM configuration](docs/source/images/guide_dem_setup.png)

   - **Section Line**: choose the `fid — label` feature, its label field and the buffer.

     ![Section line configuration](docs/source/images/guide_section_setup.png)

   - **Geology**: select the outcrop layer and its name field.

     ![Geology configuration](docs/source/images/guide_geology_setup.png)

   - **Structural**: select the layer and the dip/strike fields.

     ![Structural configuration](docs/source/images/guide_structure_setup.png)

   - **Drillholes** (optional): configure collars, surveys and intervals.

     ![Drillhole collars](docs/source/images/guide_drillhole_collars.png)

     ![Drillhole survey](docs/source/images/guide_drillhole_survey.png)

     ![Drillhole intervals](docs/source/images/guide_drillhole_intervals.png)

4. **Preview**: click **Preview**. Zoom with the wheel; the detail level adapts
   automatically. Collapse the left panel and the Results section for more canvas.

   ![Preview with panels collapsed](docs/source/images/preview_panels_collapsed.png)

5. **Style and export**: use **Settings → Symbology** for live styles and the legend, then
   **Export** (image/vector) or **Save** (profile data and 3D outputs).

---

## 🛠 For Developers

Contributions are welcome.

- **Source**: [github.com/geociencio/sec_interp](https://github.com/geociencio/sec_interp)
- **Documentation**:
  - [User Guide](https://geociencio.github.io/sec_interp_docs/USER_GUIDE.html)
  - [Architecture](https://geociencio.github.io/sec_interp_docs/ARCHITECTURE.html)
  - [Development Guide](https://geociencio.github.io/sec_interp_docs/DEVELOPMENT_GUIDE.html)
  - [Maintenance Log](https://geociencio.github.io/sec_interp_docs/MAINTENANCE_LOG.html)
  - [Technical Compendium](https://geociencio.github.io/sec_interp_docs/TECHNICAL_COMPENDIUM.html)
- **Setup and tests** (Python 3.12 + `uv`):
  ```bash
  uv sync                          # install the development environment
  PYTHONPATH=.. uv run python3 -m unittest discover tests
  make pre-release                 # mypy, analyzer, i18n, Qt6, security and Docker tests
  ```
- **Deploy to QGIS 4** for manual testing:
  ```bash
  make deploy QGIS_VERSION=4       # builds docs/resources and deploys to the local profile
  ```
- **Docker tests** run the suite inside the official QGIS image:
  ```bash
  make docker-build
  make docker-test
  ```
- **Releases** are manual from `main`; see
  [docs/releases/SCHEDULE.md](docs/releases/SCHEDULE.md).

---

## 📄 License

This project is licensed under the GNU General Public License **v2.0 or later**
(GPL-2.0-or-later). See [LICENSE](LICENSE) for the notice and the full
[GPL-2.0](LICENSE-GPL-2.0.txt) / [GPL-3.0](LICENSE-GPL-3.0.txt) texts.
