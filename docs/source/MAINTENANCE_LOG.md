# SecInterp - Maintenance & Release Log

This document serves as the central record for project history, release procedures, and past refactoring analysis.

---

### [v2.7.0 Plan - Phase 1] - 2026-01-15
- **Mock Infrastructure Overhaul**: Implemented `ModuleProxy` and `MockSignal` to stabilize the QGIS test environment. Resolved attribute errors and reference loss during mock resets. Added `indexFromName` to `MockQgsFields` for better API parity.
- **Config Fix**: Completed missing `reset_defaults()` logic in `ConfigService`.
- **Workflow Update**: Simplified `inicia-sesion` by removing `make deploy` and standardizing the test execution command.

## 🚀 Release Process

### [Unreleased]
 Process

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

### [2.7.0] - (In-Progress) 2026-01-13
- **Infrastructure Evolution**:
    - **Centralized Logging**: Refactored `logger_config.py` to use a root logger with hierarchical propagation. Unified performance monitoring with the new system.
    - **Automated Sphinx Docs**: Implementation of `conf.py` (autodoc/napoleon) and `build_docs.sh` to decouple documentation from the repository.
    - **External Build Strategy**: Documentation now exports to `../sec_interp_docs` as default, keeping the core repository clean.
    - **Repository Hygiene**: Removed 100+ tracked HTML files and updated `.gitignore` to prevent future pollution.
    - **Makefile Integration**: New `apidoc`, `docs`, and `docs-clean` targets for simplified developer workflow.
- **Data Integrity Core**:
    - **Native Validation**: Implemented hierarchical models using `dataclasses` in `core/models/settings_model.py`.
    - **Robust Config Service**: Refactored `ConfigService` to use mass-loading with validation (`get_all_settings`), replacing loose dictionaries.
    - **Testing Suite**: Added `tests/core/test_settings_model.py` and `test_config_integration.py` ensuring type safety and range audits.
- **Enhanced 3D Export**:
    - **Drillhole traces & intervals**: Implemented `DrillholeTrace3DExporter` and `DrillholeInterval3DExporter` for high-fidelity 3D output (PolygonZ/LineStringZ).
    - **Flexible Coordinate Modes**: Added support for both "Original 3D" and "Projected 3D" (cross-section space) coordinates.
    - **UI Integration**: Integrated export controls in `Export` tab for intuitive user workflow.
    - **Verification**: Established a robust 3D validation suite in `tests/exporters/test_drillhole_3d_exporter.py`.

### [2.7.0] - (Planning) 2026-01-09
- **Infrastructure Planning**:
    - **Native Validation**: Transition to `dataclasses` based models (replacing Pydantic proposal).
    - **External Sphinx**: Strategy for out-of-repo documentation build and repository HTML cleanup.
    - **Docker Consolidation**: Planned `make docker-test` integration.
- **Enhanced 3D Export**:
    - Design for Original and Projected 3D exports for Drillhole Traces and Intervals.
    - Planned UI integration in Settings/Advanced.

### [2.6.1] - 2026-01-09
- **Stabilization**:
    - **Test Suite**: Resolved major mock pollution issues and finalized 312 stable tests.
    - **Mock Infrastructure**: Implemented explicit `MockQListWidget` for stable GUI inheritance.
- **Internationalization**:
    - Translated Measure tool results and default interpretation naming.

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
- **Architecture & Refactoring (2026-01-08)**:
    - **Async Evolution**: Refactored threading model to use `QgsTask` for background geology generation, improving stability and preventing UI freezes.
    - **Exporter Modularization**: Deep refactoring of all vector exporters (`shp`, `drillhole`, `profile`, `interpretation_3d`) to reduce complexity (mccabe < 7) and improve modularity.
    - **Quality & Debt Cleanup**: Significant improvement in type hint coverage (Params: 62.1% -> 76.4%) and documentation style across core services, tools, and UI pages.
    - **Workflow Security**: Implemented `conventional-pre-commit` and restored `COMMIT_GUIDELINES.md` to guarantee high-quality, parsable commits.
    - **Test Stability**: Enhanced mocking infrastructure for asynchronous tasks and QGIS ecosystem components.

### [2.5.0] - 2026-01-03
- **Major Features**:
    - **3D Export**: Interpretation export as real 3D Shapefiles (PolygonZ).
    - **Settings Hub**: New sidebar page for plugin configuration management.
    - **Documentation**: User Guide fully integrated with screenshots.
- **Critical Fixes (Hotfixes)**:
    - **Attribute Inheritance**: Resolved regression in drillhole processing (tuple handling) and `GeologySegment` polymorphism.
    - **Serialization**: Fixed `QVariant` JSON serialization error.
- **Workflow Optimization**:
    - **Context Awareness**: Enhanced `.agent/workflows/` (start/close) to mandate context analysis and logging, ensuring continuity.
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
