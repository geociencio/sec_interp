# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.4.0] - 2025-12-25
### Added
- **Internationalization (I18n) Support**:
  - Multi-language support for 5 languages: Spanish (ES), French (FR), German (DE), Russian (RU), Portuguese Brazil (PT_BR).
  - Complete translation of UI strings using Qt's translation system.
  - Automatic language detection based on QGIS locale.
  - Translation files (`.ts`) and compiled binaries (`.qm`) for all supported languages.
  - Scripts for translation management (`update-strings.sh`, `compile-strings.sh`).
- **Code Quality Infrastructure**:
  - Pre-commit hooks configured with ruff, trailing-whitespace, end-of-file-fixer, and YAML/TOML validators.
  - Automated code quality checks on every commit.
  - Project analyzer with metrics history tracking (`.ai-context/metrics_history.json`).
- **Development Tools**:
  - Metrics history logging for tracking code quality evolution over time.
  - Enhanced project analysis script with performance optimizations.

### Changed
- **Major Architectural Refactoring (Phases 1-6)**:
  - **Phase 1 - Architecture & Decoupling**: Defined service interfaces using `abc.ABC` and `typing.Protocol`, implemented dependency injection in Manager classes.
  - **Phase 2 - Error Handling & Logging**: Created domain-specific exception hierarchy, implemented centralized error handling, migrated to structured logging.
  - **Phase 3 - Performance & Optimization**: Advanced CacheManager with TTL and LOD awareness, optimized spatial operations, vectorized geometry calculations.
  - **Phase 4 - Async & Resource Management**: Refined `AsyncGeologyProcessor` with cancellation tokens, implemented robust resource cleanup with Context Managers.
  - **Phase 5 - Validation & Modernization**: Used `dataclasses` for parameter handling, refined type hinting with Protocols, modernized to Python 3.10+ features.
  - **Phase 6 - Documentation & DevExp**: Standardized docstrings to Google format across all `core/` modules, comprehensive I18n implementation.
- **Code Quality Improvements**:
  - Replaced deprecated `typing.Dict/List/Tuple` with modern `dict/list/tuple` syntax.
  - Reduced Ruff linting errors from 287 to 261 (9% improvement).
  - Fixed syntax errors from automated refactoring.
  - Normalized whitespace in 158 files.
  - Quality score: 69.1/100, QGIS compliance: 100.0/100.

### Fixed
- **Critical Bug Fixes**:
  - Fixed missing `QgsProject` import in `preview_axes_manager.py` causing preview rendering crashes.
  - Fixed preview rendering by explicitly assigning Project CRS to memory layers.
  - Fixed `RuntimeError` in Page classes by calling `super().__init__()` before `self.tr()`.
  - Fixed empty translations by removing `type="unfinished"` attributes from `.ts` files.
  - Fixed Russian translation file XML corruption.
  - Fixed false positive `ValidationError` for drillhole layers.
- **Translation System Fixes**:
  - Fixed `lrelease` compilation by properly handling multiple locales in Makefile.
  - Created translation injection scripts for efficient population of `.ts` files.
  - Verified translation loading with unit tests.

### Documentation
- Updated all `core/` modules with Google-style docstrings.
- Created comprehensive walkthrough documenting all architectural improvements.
- Added session artifacts tracking development progress.

## [2.3.0] - 2025-12-25
### Added
- **Enhanced Multi-Point Measurement Tool**:
  - Support for polyline tracing with unlimited measurement points.
  - Dedicated "**Finalize**" button for explicit measurement completion.
  - Comprehensive metrics: Total 3D distance, Horizontal distance, Elevation change, and Average slope.
  - Persistent visual feedback with green vertex markers and measurement lines after finalization.
  - Auto-reset on new measurement for improved workflow.
- **Structural Improvement Plan - Phase 1 (Architectural Decoupling)**:
  - Extracted `DialogToolManager` to encapsulate map tool handling and mouse wheel events.
  - Centralized preview generation logic in `PreviewManager`.
  - Eliminated PyQt dependencies from `core/validation` using enum-based `FieldType`.
- **Structural Improvement Plan - Phase 2 (Complexity Reduction)**:
  - Modularized `core/utils/geometry.py` into `extraction`, `processing`, and `filtering` sub-packages.
  - Refactored `DrillholeService.process_intervals` with extracted private methods.
  - Implemented adaptive Level of Detail (LOD) for topographic profiles.
- **Structural Improvement Plan - Phase 3 (Performance Optimization)**:
  - Robust cache system with hash-based invalidation in `PreviewManager`.
  - Spatial indexing (`QgsSpatialIndex`) for efficient drillhole filtering.
  - Achieved 84ms rendering time for 6km cross-sections.
- **Structural Improvement Plan - Phase 4 (Documentation)**:
  - Created `ARCHITECTURE.md` with unified technical documentation.
  - Created `DEVELOPMENT_GUIDE.md` for developer onboarding.
  - Improved docstring coverage to 75.9%.

### Changed
- **Code Quality Improvements**:
  - Quality score increased from 71.1 to 74.4 (+4.6%).
  - Removed deprecated typing imports (`Dict`/`List` → `dict`/`list`).
  - Fixed import order and organization across all modules.
  - Improved error handling with `logger.exception` instead of `logger.error`.

### Fixed
- **Critical Bug Fixes**:
  - Fixed `ModuleNotFoundError` for `geometry_utils` sub-package in deployment.
  - Resolved `NameError` for `Optional` in `profile_service.py`.
  - Fixed `AttributeError` in measure tool (access via `DialogToolManager`).
  - Corrected `TypeError` in `create_buffer_geometry` signature (added `crs` and `segments` parameters).
  - Fixed `UnboundLocalError` in `PreviewManager` cache handling.
  - Added CRS transformation support in `filter_features_by_buffer` utility.
  - Implemented field validation for drillhole processing to prevent `KeyError`.
  - Fixed missing `logger` definition in `preview_service.py`.
- **Preview Rendering Fixes**:
  - Fixed geology disappearing on subsequent preview clicks with unchanged parameters.
  - Fixed drillholes not rendering despite being detected (missing return statement in `_generate_drillholes()`).
  - Added comprehensive diagnostic logging for drillhole trace generation.
  - Improved cache persistence for async geology data.

## [2.2.0] - 2025-12-21
### Added
- **Architectural Evolution: Modular Core & Clean Entry Point**:
  - Moved main `SecInterp` class to plugin root (`sec_interp_plugin.py`) to strictly separate QGIS integration from business logic.
  - Modularized `validation.py` into a specialized `core/validation/` package (Field, Layer, Path, and Project validators).
  - Fragmented `SecInterpDialog` into specialized managers (`DialogSignalManager`, `DialogDataAggregator`) reducing complexity and file size.
  - Refactored Help System to "Native Hybrid" (Single-file HTML/CSS) for improved performance and UX.
- **Preview & UI Improvements**:
  - Fixed Y-axis labels and grid alignment for negative elevations.
  - Improved axis label spacing and label QUADRANT handling.
  - Fixed toolbar icon loading path after architectural move.
- **Documentation**:
  - Updated "Outputs" documentation with Drillhole trace/interval details.
  - Created comprehensive technical architecture documentation.

### Fixed
- Resolved `UI_IMPORT_IN_CORE` architectural violations by moving UI-dependent components out of the core layer.
- Fixed `TypeError` in `PreviewParams` and startup `AttributeError` by reordering service initialization.
- Fixed field collection bug in `PreviewManager` using `currentField()`.
- Improved stability of Preview Export with better size handling.

## [2.1.0] - 2025-12-17
### Added
- **Major Feature: Snap-Enabled Measurement Tool**:
  - Implementation of iterative vertex snapping logic using `QgsPointLocator`.
  - Manual snapping approach that avoids project pollution (no temporary layers added to `QgsProject`).
  - Performance optimization with locator caching.
- **AI Workflow Enhancements**:
  - Improved `ai_workflow.py` with Unicode normalization (NFD) for robust keyword extraction (supports accents/special characters).
  - Robust context loading with mandatory project-level files (`AI_CONTEXT.md`, `project_brain.md`).

### Fixed
- Fixed critical `AttributeError` in `QgsSnappingConfig` by correctly using `QgsTolerance.Pixels`.
- Eliminated "temporary scratch layers" warning by using manual snapping logic.

## [2.0.0] - 2025-12-14
### Added
- **Major Feature: Drillhole Data Handling**:
  - 3D Projection of drillhole traces onto 2D profile sections.
  - Auto-calculation of total depths and handling of vertical holes without survey.
  - Visualization of geological intervals along drillhole traces.
- **Drillhole Data Export**:
  - Export drillhole traces to Shapefile (`drillhole_traces.shp`).
  - Export interval data with attributes to Shapefile (`drillhole_intervals.shp`).

### Changed
- **Major UI Refactoring & Enhancements**:
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
  - Implemented asynchronous parallel processing for geological generation.
  - Integrated Performance Monitor (RAM & Execution Time tracking).
  - Added non-blocking UI during heavy calculations.
- **Preview System Enhancements**:
  - Implemented Adaptive Level of Detail (LOD) for high-performance rendering.
  - Added Dynamic Zoom-based LOD (details increase as you zoom in).
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
  - Modularized exporters ecosystem.
  - Implemented spatial indexing and native QGIS algorithms for performance.
- **Quality Assurance**:
  - Added comprehensive type hinting across modules.
  - Enhanced test infrastructure with pytest and QGIS support.
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
  - Refactored export_preview with dedicated methods per format (PNG, JPG, SVG, PDF).
  - Applied SOLID principles throughout main dialog class.

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
  - Organized build scripts in scripts/ directory.

### Added
- **Quality Improvements**:
  - Achieved Pylint score 10/10.
  - Specific exception handling throughout codebase.
  - Comprehensive code documentation.
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
  - Eliminated manual layer population code - widgets auto-sync with QGIS project.
  - Improved user experience with native QGIS look and feel.
  - Fixed Qt enum syntax for better cross-version compatibility.
- **Code Quality**:
  - Removed 200+ lines of manual widget population code.
  - Cleaner architecture leveraging QGIS native capabilities.

### Added
- **UI Enhancements**:
  - Collapsible results panel (QgsCollapsibleGroupBox) for better space management.
  - Read-only results field to prevent accidental edits.
- **New Features**:
  - Flexible parsers for geological structural measurements (dip/strike formats).
  - Comprehensive logging system integrated with QGIS Message Panel.
  - Enhanced validation logic for QgsMapLayer objects.

## [0.1.0] - Initial Release
### Added
- DEM topographic profile extraction.
- Geological outcrop data extraction.
- Structural point data extraction.
- Interactive preview visualization.
