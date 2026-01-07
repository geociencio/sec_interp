# SecInterp - Maintenance & Release Log

This document serves as the central record for project history, release procedures, and past refactoring analysis.

---

## 🚀 Release Process

Follow these steps to prepare and release a new version of **SecInterp**.

### 1. Preparation
- **Update Metadata**: Increment `version` in `metadata.txt`.
- **Sync Project Brain**: Update `.ai-context/project_brain.md`.
- **Update Changelog**: Add the new version to the top of the [Project History](#-project-history) section below.
- **Update User Guide**: Ensure screenshots and feature descriptions in `docs/USER_GUIDE.md` are current.

### 2. Packaging (Clean Build)
To ensure no development files (like tests or .git) are included in the distribution zip, use the `git archive` method:

```bash
# Check exports-ignore in .gitattributes first
# Then run the package command
make package VERSION=main
mv sec_interp.zip sec_interp_vX.Y.Z.zip
```

### 3. Distribution & QGIS Repository
- **Tagging**: `git tag vX.Y.Z -m "Release description"`
- **GitHub**: Create a new Release and attach the ZIP.
- **QGIS Repo**: Upload the ZIP to [plugins.qgis.org](https://plugins.qgis.org/).
    - ⚠️ **CRITICAL**: The ZIP MUST contain a `LICENSE` file and NO `__pycache__` folders.
    - The repository will reject any package with `.pyc` files for security reasons.
    - Verified ZIP structure with `unzip -t sec_interp.zip`.

---

## 📜 Project History

### [2.6.0] - 2026-01-05
- **Quality Assurance**:
    - **Native Integration Tests**: Implementation of `BaseIntegrationTest` for headless QGIS execution.
    - **Workflow Validation**: New automated tests for Interpretation, Measurement, and 3D Export using real QGIS API.
- **Docker Integration**:
    - Full containerization of the test environment for CI/CD readiness.
    - Automated dependency management via `uv` within Docker.
    - Optimized build workflows with `.dockerignore` and permission handling.
- **Performance**:
    - **Benchmarks Suite**: Implementation of performance tests for Geometry and Exports using `unittest`.
    - **SLA Verification**: Established baseline metrics for critical operations (Shapefile Write < 5s, Projection < 0.1s).

### [2.5.0] - 2026-01-03
- **Major Features**:
    - **3D Export**: Interpretation export as real 3D Shapefiles (PolygonZ).
    - **Settings Hub**: New sidebar page for plugin configuration management.
- **Data Persistence**: Overhauled `DialogSettingsManager` for robust restoration with multi-scope support (`SecInterp`/`SecInterpUI`) and layer name fallback.
- **Stability & QA**:
    - Enabled project-wide Ruff rules (`F401`, `F841`, `I001`).
    - Implemented proactive auto-save on Preview and Dialog Accept.
    - Resolved critical `AttributeError` in validation logic and Geology Rendering.
    - Forced disk synchronization for configs (`sync()`).
- **Test Infrastructure**: Enhanced `MockQgsProject` and `MockQWidget` to support persistence and modern Qt patterns.

### [2.2.0] - 2025-12-22
- **Documentation Globalization**: 100% of documentation (including Architecture) translated to English.
- **Build Optimization**: Slimmed final ZIP package and removed redundant source code views from help.
- **Architectural Evolution**: Moved main `SecInterp` class to `sec_interp_plugin.py`.
- **Validation Refactor**: Modularized `core/validation/` package.
- **GUI Decoupling**: Fragmented `SecInterpDialog` into specialized managers.
- **LOD Optimization**: Implemented adaptive Level of Detail for previews.

### [2.1.0] - 2025-12-17
- **Feature**: Snap-Enabled Measurement Tool.
- **Fix**: Resolved Snapping configuration attribute errors.

### [2.0.0] - 2025-12-14
- **Feature**: Full Drillhole Integration (Projection & Intervals).
- **Export**: Added drillhole trace and interval Shapefile exporters.

### [1.1.0] - 2025-12-12
- **Performance**: Asynchronous parallel processing for geology.
- **Feature**: Adaptive Sampling and Measurement Tool.

---

## 📁 Historical Refactoring Notes

For detailed information on past major refactoring sessions, refer to the following summaries:

> [!NOTE]
> **Refactoring 2025-12-21**: Significant reduction of `main_dialog.py` size (from 1k to ~300 lines) by moving logic to managers and core services.
> See `docs/docsec/archive/` for original walkthroughs if deep historical context is needed.
