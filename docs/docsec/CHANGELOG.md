# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.4.0] - 2026-03-29

### Added
- **i18n**: Achieved 100% complete translation for the UI across all 13 supported languages.
- **Testing**: Added comprehensive Integration Tests for Vector Drivers (GPKG, SHP, DXF).
- **Export (GeoPackage)**: Implemented unified GeoPackage layer appending under unique section subdirectories (`[SectionName]/`).
- **Interpretations**: Added full bi-directional "Vector Layer Mode" synchronization between QGIS Vector Layers and internal features.
- Unified export system supporting **DXF**, **GeoPackage**, and **Shapefile** for all data types.
- Robust 3D interpretation export with automatic coordinate transformation.
- Persistent export settings across sessions.

### Changed
- **i18n**: Rewrote translation injection (`apply_full.py`) with `ElementTree` for stable XML parsing and safe placeholder handling.
- **Plugin Ecosystem**: Refined `Makefile` logic to recursively capture deep source files for full translation propagation.
- **Parsing**: Restored and improved structural string parsing logic capable of handling multiple combined dip/strike notations simultaneously.
- Refactored `ExportService` to decouple 2D and 3D drillhole exports for better accuracy.
- Enhanced `TrajectoryEngine` with mandatory interval points at start/end depths.
- Reduced cyclomatic complexity in export orchestration logic.

### Fixed
- **Export (DXF/GPKG)**: Resolved a critical signature mismatch in `ExportService._export_drillholes_3d` where `DXFExporter` was being incorrectly used for specialized 3D drillhole data.
- **Type Safety**: Verified an 89.0% Return Type Hint coverage and bypassed a regex parsing bug in `qgis-plugin-analyzer`, correctly adding remaining missing hints to internal methods in `drillhole` and `export` services.
- **Tooling**: Updated `ai-context-core` to **v3.3.0**, resolving the aggregation bug in project reports and enabling specialized **QGIS Standards Compliance** analysis.
- **DXF**: Fixed critical failure during field creation by stripping unsupported attributes for DXF format.
- **Drillholes**: Resolved duplicated entries in logs and missing segments for very short geological intervals.
- **Stability**: Fixed `KeyError: 0` in `DXFExporter` when processing empty or malformed feature sets.
- **UI**: Fixed export format reset issue by synchronizing `SettingsPage` with `ConfigService`.


## [3.3.0] - 2026-03-14

### ✨ Added
- **Core**: Standardized `DrillholeProjection` as a Dataclass DTO. Implemented Return Type Hints (~45% core coverage).
- **Architecture**: Full preparation for **QGIS 4.x** by ensuring all Qt dependencies use `qgis.PyQt`.
- **Infrastructure**: Refined `.qgisignore` to remove development noise from the final package.

### 🔧 Changed
- **Architecture**: Standardized all `QgsSettings` keys to the `SecInterp/` prefix (PascalCase).
- **Export**: The config service now correctly loads format values (GPKG, DXF) and naming patterns from persistent preferences.
- **Architecture**: Replaced unsafe `contextlib.suppress` with explicit exception handling and logging.
- **Rendering**: Migrated 3D exporters to `Rule-Based Rendering` to guarantee style integrity in QGIS.
- **GUI**: Increased GUI test coverage to **91%**, including background task orchestration logic.

### 🐞 Fixed
- **Stability**: Resolved critical memory leaks and orphaned `QgsRubberBand` objects.
- **UI**: Fixed preview widget regression via a robust signal restoration loop in `SignalManager`.
- **Mocks**: Fixed arithmetic errors in Qt mocks for layout calculations in headless environments.
### 🚀 New Features
- **Testing**: Massive test suite expansion reaching **450 successful tests** in Docker.
- **Automation**: Documentation-as-code system to dynamically update `TESTING_STATUS.md`.
- **Integration**: New suite for 3D vertical projections in Cartesian coordinate systems.
- **Security**: Path Traversal protection across all exporters via absolute path resolution.
- **Validation**: Type and range validation for preview parameters in `PreviewParams`.

### 🔧 Changes
- **Compatibility**: 100% compliance with QGIS 4.x agnostic API (`qgis.PyQt`).
- **UI**: Refactored `PreviewLayerFactory` with shared geometry/exaggeration helpers.
- **GUI**: Standardized `DialogSettingsPersistence` to reduce repetitive code.

### 🐞 Fixes
- **Core**: Regression in `TrajectoryEngine` buffer filtering.
- **Stability**: Fixed `TypeError` in dependency injection and `IndexError` in drillhole projections.
- **Memory**: Resolved leaks in `QgsRubberBand` and missing signal disconnections.
- **Mocks**: Robust testing environment with unique layer IDs and strict geometry validation.

### 🚀 Key Features
- **i18n & GUI**: Massive automatic translation of missing strings for all 14 supported languages. Added translatable validation messages.
- **Export**: Added debug logging and i18n support for exporters. Added 'Reset to defaults' button for export options.
- **Architecture**: Modularized `ProjectValidator` using the Pipeline pattern. Decomposed `StateManager` into specialized components.
- **Stability**: Removed circular imports in the validation module. Stabilized `QCoreApplication` imports in tests.

## [3.0.1] - 2026-02-17
### 🚀 Quality & Stability
- **Signal Management**: Resolved 22 signal leaks, achieving full interface stability.
- **Languages**: Expanded support to 11 languages with the addition of Hindi and Indonesian.
- **Tests**: Reached 361 tests with 100% success rate in headless environments.
- **Refactoring**: Removed unnecessary dependencies, eliminated dead code, and decoupled UI modules.

### 🛠️ Infrastructure Improvements
- **Architecture Consolidation**:
  - Strengthened dependency injection in the plugin core.
- **Quality & Automation**:
  - Updated to `qgis-plugin-analyzer` v1.7.0 for more rigorous compliance auditing.
  - Strict linter configuration (Ruff) focused on complexity reduction and documentation improvement.

### 🐛 Fixes (Hotfixes)
- Fixed critical error in `DrillholeService` when optional Survey and Interval layers were missing.
- Fixed output file validation in the UI to prevent incomplete exports.
- Stabilized async task management (`QgsTask`) to prevent crashes when closing the main dialog.

---

## [2.5.0] - 2026-01-01

### 🚀 Key Features
- **3D Interpretation Export**:
  - Export geological interpretations as real 3D Shapefiles (PolygonZ).
  - Vertex-by-vertex affine transformation ensuring geometric integrity of complex subsurface structures (e.g., overturned folds).
- **Settings Hub**: New sidebar page for plugin configuration.
- **User Guide**: Complete documentation with integrated screenshots.

### 🛠️ Improvements
- **Attribute Inheritance**: Optimized inheritance algorithm for structural measurements.
- **UI**: Data export panel with real-time summary of available data types.
- **Workflow Security**: Implemented `conventional-pre-commit` to guarantee high-quality, parsable commits.

### 🐛 Fixes
- Fixed `QVariant` serialization error when exporting data with boolean and numeric fields.
- Fixed drillhole trajectory projection error in CRS with different vertical units.
- Resolved UI alignment issues when switching between different data input pages.

---

## [2.4.0] - 2025-12-28

### 🚀 New Features
- **Internationalization**: Full multilingual support with 8 initial languages and automated translation pipeline.
- **QGIS Standards Compliance**: Achieved **100.0/100** in QGIS Compliance and **69.1/100** in Quality Score.
- **Documentation**: Auto-generation of `TESTING_STATUS.md` and unified architecture documentation.

### 🔧 Changes
- **Refactoring**:
  - Wrapped all user-facing strings with `self.tr()` or `QCoreApplication.translate()`.
  - Created `.ts` translation files for 8 languages.
  - Implemented `apply_full.py` for automated i18n maintenance.
  - Reduced Ruff linting errors from 287 to 261 (9% improvement).
  - Fixed syntax errors from automated refactoring.
  - Normalized whitespace across 158 files.
  - Quality Score: 69.1/100, QGIS Compliance: 100.0/100.

### Fixed
- **Critical Bug Fixes**:
  - Fixed missing `QgsProject` import in `preview_axes_manager.py` that caused crashes when rendering previews.
  - Fixed preview rendering by explicitly assigning the project CRS to in-memory layers.
  - Fixed `RuntimeError` in Page classes calling `super().__init__()` before `self.tr()`.
  - Fixed empty translations by removing `type="unfinished"` attributes from `.ts` files.
  - Fixed XML corruption in Russian translation file.
  - Fixed false positive `ValidationError` for drillhole layers.
- **Translation System Fixes**:
  - Fixed `lrelease` compilation by properly handling multiple locales in Makefile.
  - Created translation injection scripts for efficient `.ts` file population.
  - Verified translation loading with unit tests.

### Documentation
- Updated all `core/` modules with Google-style docstrings.
- Created complete walkthrough documenting all architectural improvements.
- Added session artifacts tracking development progress.

## [2.3.0] - 2025-12-25
### Added
- **Enhanced Multi-Point Measurement Tool**:
  - Polyline tracing support with unlimited measurement points.
  - Dedicated "**Finish**" button to explicitly complete the measurement.
  - Full metrics: Total 3D distance, horizontal distance, elevation change, and average slope.
  - Persistent visual feedback with green vertex markers and measurement lines after completion.
  - Auto-restart on new measurement for improved workflow.
- **Structural Improvement Plan - Phase 1 (Architectural Decoupling)**:
  - Extracted `DialogToolManager` to encapsulate map tool handling and mouse wheel events.
  - Centralized preview generation logic in `PreviewManager`.
  - Removed PyQt dependencies from `core/validation` using enum-based `FieldType`.
- **Structural Improvement Plan - Phase 2 (Complexity Reduction)**:
  - Modularized `core/utils/geometry.py` into `extraction`, `processing`, and `filtering` subpackages.
  - Refactored `DrillholeService.process_intervals` with extracted private methods.
  - Implemented adaptive Level of Detail (LOD) for topographic profiles.
- **Structural Improvement Plan - Phase 3 (Performance Optimization)**:
  - Robust cache system with hash-based invalidation in `PreviewManager`.
  - Spatial indexing (`QgsSpatialIndex`) for efficient drillhole filtering.
  - Achieved 84ms render time for 6km cross-sections.
- **Structural Improvement Plan - Phase 4 (Documentation)**:
  - Created `ARCHITECTURE.md` with unified technical documentation.
  - Created `DEVELOPMENT_GUIDE.md` for developer onboarding.
  - Improved docstring coverage to 75.9%.

### Changed
- **Code Quality Improvements**:
  - Quality score increased from 71.1 to 74.4 (+4.6%).
  - Removed obsolete typing imports (`Dict`/`List` → `dict`/`list`).
  - Fixed import order and organization across all modules.
  - Improved error handling with `logger.exception` instead of `logger.error`.

### Fixed
- **Critical Bug Fixes**:
  - Fixed `ModuleNotFoundError` for `geometry_utils` subpackage in deployment.
  - Resolved `NameError` for `Optional` in `profile_service.py`.
  - Fixed `AttributeError` in measurement tool (access via `DialogToolManager`).
  - Fixed `TypeError` in `create_buffer_geometry` signature (added `crs` and `segments` parameters).
  - Fixed `UnboundLocalError` in `PreviewManager` cache handling.
  - Added CRS transformation support in `filter_features_by_buffer` utility.
  - Implemented field validation for drillhole processing to prevent `KeyError`.
  - Fixed missing `logger` definition in `preview_service.py`.
- **Preview Rendering Fixes**:
  - Fixed geology disappearing on subsequent preview clicks with unchanged parameters.
  - Fixed drillholes not rendered despite being detected (missing return in `_generate_drillholes()`).
  - Added full diagnostic logging for drillhole trace generation.
  - Improved cache persistence for asynchronous geological data.

## [2.2.0] - 2025-12-21
### Added
- **Architectural Evolution: Modular Core and Clean Entry Point**:
  - Moved main `SecInterp` class to plugin root (`sec_interp_plugin.py`) to strictly separate QGIS integration from business logic.
  - Modularized `validation.py` into specialized `core/validation/` package (Field, Layer, Path, and Project validators).
  - Fragmented `SecInterpDialog` into specialized managers (`DialogSignalManager`, `DialogDataAggregator`) reducing complexity and file size.
  - Refactored Help System to "Native Hybrid" (single-file HTML/CSS) for better performance and UX.
- **Preview & UI Improvements**:
  - Fixed Y-axis labels and grid alignment for negative elevations.
  - Improved axis label spacing and LABEL QUADRANT handling.
  - Fixed toolbar icon loading path after architectural move.
- **Documentation**:
  - Updated "Outputs" documentation with drillhole trace/interval details.
  - Created complete architecture technical documentation.

### Fixed
- Resolved `UI_IMPORT_IN_CORE` architectural violations by moving UI-dependent components out of the core layer.
- Fixed `TypeError` in `PreviewParams` and `AttributeError` at startup by reordering service initialization.
- Fixed field collection bug in `PreviewManager` using `currentField()`.
- Improved Preview Export stability with better size handling.

## [2.1.0] - 2025-12-17
### Added
- **Major Feature: Snap-Enabled Measurement Tool**:
  - Iterative vertex snap logic implementation using `QgsPointLocator`.
  - Manual snap approach that avoids project contamination (does not add temporary layers to `QgsProject`).
  - Performance optimization with locator caching.
- **AI Workflow Improvements**:
  - Enhanced `ai_workflow.py` with Unicode normalization (NFD) for robust keyword extraction (supports accents/special characters).
  - Robust context loading with mandatory project-level files (`AI_CONTEXT.md`, `project_context.json`).


### Fixed
- Fixed critical `AttributeError` in `QgsSnappingConfig` by correctly using `QgsTolerance.Pixels`.
- Removed "temporary layers" warning using manual snap logic.

## [2.0.0] - 2025-12-14
### Added
- **Major Feature: Drillhole Data Handling**:
  - 3D projection of drillhole traces onto 2D profile sections.
  - Auto-calculation of total depths and handling of vertical holes without survey data.
  - Visualization of geological intervals along drillhole traces.
- **Drillhole Data Export**:
  - Export drillhole traces to Shapefile (`drillhole_traces.shp`).
  - Export interval data with attributes to Shapefile (`drillhole_intervals.shp`).

### Changed
- **Major UI Refactoring & Improvements**:
  - New specialized Drillhole Input Page.
  - Enhanced Preview System with dedicated persistent rendering for all data types.
  - Fixed critical rendering bugs (zoom persistence, async updates).
- **Architecture**:
  - Implemented `DrillholeService` for encapsulated logic.
  - Refactored `ProfileController` to orchestrate multiple data services.
  - Unified export logic with extensible Exporter pattern.

## [1.1.0] - 2025-12-12
### Added
- **Performance & Optimization**:
  - Implemented asynchronous parallel processing for geology generation.
  - Integrated Performance Monitor (RAM and Execution Time tracking).
  - Added non-blocking UI during heavy calculations.
- **Preview System Improvements**:
  - Implemented adaptive Level of Detail (LOD) for high-performance rendering.
  - Added Dynamic Zoom-based LOD (detail increases when zooming in).
  - Added Measurement Tool (Distance and Slope/Gradient).

### Changed
- **Architecture & Fixes**:
  - Refactored services to use Command Pattern for parallel execution.
  - Improved CRS handling.

### Fixed
- Fixed structure projection consistency.
- Resolved "No valid layers to render" warnings.
- Fixed Dip Scale Factor application.
- Fixed blank rendering issues.

## [1.0.0] - 2025-12-08
### Added
- **Refactoring & Architecture**:
  - Split monolithic modules (algorithms.py, main_dialog.py) into focused components.
  - Modularized exporter ecosystem.
  - Implemented spatial indexing and native QGIS algorithms for performance.
- **Quality Assurance**:
  - Added full type hinting across all modules.
  - Improved test infrastructure with pytest and QGIS support.
  - Implemented security fixes (path traversal protection).
- **Documentation**:
  - Added COMMIT_GUIDELINES.md for standardized commit messages.
  - Added RELEASE_PROCESS.md with version release workflow.
  - Added drilllogs_research.md with future integration requirements.

### Changed
- **Major UI Refactoring - Plugin Manager Style**:
  - Redesigned main dialog with sidebar navigation (QListWidget + QStackedWidget).
  - Replaced absolute positioning with responsive layouts (QVBoxLayout, QHBoxLayout, QSplitter).
  - Integrated native QGIS theme icons for sidebar items.
  - Improved preview/results area proportions with better vertical space management.
- **Code Quality Improvements**:
  - Extracted LegendWidget to separate module (gui/legend_widget.py).
  - Refactored preview_profile_handler with helper methods and early returns.
  - Refactored export_preview with dedicated per-format methods (PNG, JPG, SVG, PDF).
  - Applied SOLID principles throughout the main dialog class.

### Fixed
- Fixed legend rendering and resizing issues.

## [0.3.0] - 2025-12-03
### Changed
- **Major Refactoring - Modular Project Structure**:
  - Reorganized codebase into core/, gui/, resources/ packages.
  - Improved code maintainability and scalability.
  - Better separation of concerns (business logic, UI, resources).
- **Build System**:
  - Updated Makefile for new structure.
  - Refactored deploy.sh for modular deployment.
  - Organized build scripts into scripts/ directory.

### Added
- **Quality Improvements**:
  - Achieved Pylint score 10/10.
  - Specific exception handling throughout the codebase.
  - Complete code documentation.
  - Configured .pylintrc for consistent code quality.
- **Testing & CI/CD**:
  - Added pytest infrastructure with QGIS support.
  - Created initial unit tests.
  - Configured GitHub Actions for automated testing.
  - Test configuration in tests/conftest.py.
- **Documentation**:
  - Added REFACTORING_PR.md with detailed changes.
  - Improved project documentation structure.
  - Added implementation plans for future features.

## [0.2.0] - 2025-11-30
### Changed
- **Major UI Overhaul - Native QGIS Widget Integration**:
  - Replaced standard Qt ComboBoxes with QgsMapLayerComboBox for automatic layer population.
  - Integrated QgsRasterBandComboBox for intelligent raster band selection.
  - Added QgsFileWidget for native file/directory browsing with QGIS integration.
  - Removed manual layer population code - widgets auto-sync with QGIS project.
  - Improved user experience with native QGIS look and feel.
  - Fixed Qt enum syntax for better cross-version compatibility.
- **Code Quality**:
  - Removed 200+ lines of manual widget population code.
  - Cleaner architecture leveraging native QGIS capabilities.

### Added
- **UI Improvements**:
  - Collapsible results panel (QgsCollapsibleGroupBox) for better space management.
  - Read-only results field to prevent accidental edits.
- **New Features**:
  - Flexible parsers for geological structural measurements (dip/strike formats).
  - Complete logging system integrated with QGIS Message Panel.
  - Enhanced validation logic for QgsMapLayer objects.

## [0.1.0] - Initial Release
### Added
- DEM topographic profile extraction.
- Geological outcrop data extraction.
- Structural point data extraction.
- Interactive preview visualization.
