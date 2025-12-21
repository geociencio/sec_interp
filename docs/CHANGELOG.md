# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2025-12-21
### Added
- **Architectural Evolution: Service-Oriented Core**:
  - Implementation of `ExportService` to decouple business logic from the GUI.
  - Creation of `PreviewService` for centralized data generation (Topography, Structures, Drillholes).
  - Modularized `DialogValidator` with specialized `ValidationParams`.
- **GUI Fragmentation & Complexity Reduction**:
  - **`PreviewRenderer` Evolution**: Fragmented into 4 specialized components (`PreviewLayerFactory`, `PreviewAxesManager`, `PreviewOptimizer`, `PreviewLegendRenderer`). Complexity reduced from 130 to 21.8.
  - **`MainDialog` Evolution**: Fragmented `SecInterpDialog` into specialized managers (`DialogSettingsManager`, `DialogStatusManager`, `DialogEntityManager`). Complexity reduced from 95 to 18.
- **Preview Improvements**:
  - Fixed Y-axis labels and grid alignment for negative elevations.
  - Anchored X-labels and vertical grid lines to the grid's floor (y_start).
  - Improved axis label spacing and label QUADRANT handling.

### Fixed
- Resolved `UI_IMPORT_IN_CORE` architectural violations by moving UI-dependent utilities to `gui/`.
- Fixed `TypeError` in `PreviewParams` initialization (missing `dip_scale_factor`).
- Fixed `AttributeError` in startup sequence by reordering core service initialization.
- Fixed field collection bug in `PreviewManager` using `currentField()` instead of `currentData()`.
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
