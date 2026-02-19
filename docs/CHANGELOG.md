# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- `SafeLoader` utility for resilient module imports and error handling.

### Changed
- Refactorized plugin initialization (`SecInterp` class) to use lazy loading.
- Decoupled domain services in `ProfileController` using `SafeLoader` for better resilience.

### Added
- **i18n**: Localización complementaria para Hindi (`hi`) e Indonesio (`id`), ampliando la cobertura al mercado asiático.
- **Auditoría**: Publicado Roadmap Técnico para la modernización de `qgis-manage` (soporte `.pluginignore` y parcheo de RCC).
- **Desarrollo**: Nueva guía de despliegue y problemas conocidos para desarrolladores en `docs/maintainer`.
- **i18n**: Localización profunda de la guía de usuario para 7 idiomas prioritarios (FR, DE, IT, PT_BR, RU, ZH_CN, JA), cubriendo tutoriales y funciones avanzadas.
- **i18n**: Sistema de compilación automática de catálogos `.mo` integrado en el flujo de documentación.
- **Arquitectura**: Nuevo sistema de validación modular basado en Pipeline y micro-validadores (`IValidator`).
- **Arquitectura**: Descomposición de `StateManager` en componentes especializados para persistencia y gestión de estado de UI.

### Fixed
- **Estabilidad**: Corregida la suite de tests unitarios para sincronizar con la nueva estructura modular de validación.

### Changed
- **Refactorización**: Reducción masiva de complejidad ciclomática en `StateManager` (CC 70) y `ProjectValidator` (CC 44).

## [3.0.1] - 2026-02-17
### Added
- Comprehensive return type hints across Core, GUI, and Exporters for better IDE support and stability.
- Robust signal disconnection mechanism in main dialog using `StateManager` tracking to prevent memory leaks (22 leaks resolved).
- Expanded i18n support to 11 languages (added Hindi and Japanese).
- **Estabilidad**: Suite de tests elevada a **386 tests OK** (Docker), validando la coexistencia de rastreo de señales y mocks.
- **Estabilidad**: Corregida la suite de tests de integración avanzada resolviendo la pérdida de atributos en `MockQgsFeature` y el parsing de WKT en `MockQgsGeometry`.
- **Exporters**: Asegurada la integridad de coordenadas Z en las exportaciones Shapefile mediante el uso de tipos nativos `Z`.
- **Mocks**: Implementado un sistema de `getFeatures` dinámico y cooperativo en `MockQgsMapLayer`.
- **Build**: Nueva lógica en `Makefile` y `build_docs.sh` para empaquetado ligero y despliegue externo de APIs.

### Changed
- Modernized type annotations to use `| None` syntax.
- Standardized geometry utility imports to use `qgis.PyQt`.
- **Documentación**: Desacoplamiento de la documentación de la API del paquete de ayuda offline integrado en el plugin.
- Applied project-wide code formatting with Black and Ruff.

## [3.0.0] - 2026-02-14
### Fixed
- **Exportación**: Corregido `AttributeError` crítico en `ExportService` implementando resolución explícita de IDs de capa a objetos `QgsMapLayer`.
- **Arquitectura**: Eliminadas referencias obsoletas a `message_manager` y `settings_manager`, completando la transición fuera del patrón Facade.
- **UX**: Mejorada la visibilidad de mensajes de éxito/error, mostrándolos ahora también en el panel de resultados del plugin.

### Added
- **Calidad**: Eliminación sistemática de números mágicos (`PLR2004`) en todo el proyecto, reemplazándolos con constantes nombradas.
- **Documentación**: Cobertura del 100% en docstrings para `core/` y `gui/` (cumplimiento de reglas `D10x`).
- **Auditoría**: Actualización a `qgis-plugin-analyzer` v1.7.0 con soporte para el nuevo comando `qgis-analyzer`.
- **Documentación**: Clarificación global entre nombre de herramienta (`qgis-plugin-analyzer`) y comando CLI (`qgis-analyzer`).
- **Auditoría Estricta**: Habilitadas reglas de Ruff para Complejidad (`C901`), Argumentos (`PLR0913`), Valores Mágicos (`PLR2004`) y Docstrings (`D10x`).
- **Docs Dev**: Reporte de incidencias técnicas en el analizador de plugins.
- **I18n**: Soporte expandido a 8 idiomas con automatización mediante `ai-context-core`.

### Fixed
- **Hotfix**: Corregido bug en `DrillholeService` que causaba `AttributeError` al procesar sondajes sin capas opcionales (Survey/Intervals) configuradas.
- **Validación**: Fortalecida la validación de la ruta de salida en el diálogo principal para evitar el botón "Save" habilitado sin ruta válida.
- **UI**: Corregido typo en `DialogStatusManager` (`btn_save`) que impedía la correcta gestión de estado del botón de exportación.
- **UI**: Añadida capa de seguridad en `ExportManager` para validar la existencia de una carpeta de salida antes de iniciar el proceso.

### Changed
- **Linter**: Endurecimiento de la configuración de `pyproject.toml` para reflejar la calidad real del código.
- **Arquitectura**: Descomposición de `DrillholeService` para mejorar la mantenibilidad y modularidad.
- **Access Control**: Implementación de `AccessControlService` para gestión de funcionalidades.

### Fixed
- Actualizada dependencia a `ai-context-core>=3.2.1` para corregir errores de segmentación de i18n (scope `gui_only`).
- Corregida omisión de configuración de i18n en el agregador de resultados de QGIS.
- Corregido matching de rutas recursivas en el análisis de cumplimiento de QGIS.
- Añadida opción `--i18n-scope` al comando `ai-ctx qgis`.

## [2.10.0] - 2026-02-08
### Fixed
- **Estabilidad Total**: Resueltos todos los fallos en la suite de pruebas (347/347 tests pasando).
- **Exportación**: Corregido `TypeError` crítico en `StructureService` durante la proyección de estructuras.
- **UI**: Corregidos `AttributeError` en componentes de vista previa (`PreviewParamHasher`, `MockQWidget`).
- **Integración**: Reparado el error de importación en tests de integración, permitiendo ejecución headless exitosa.


## [2.10.0-dev] - 2026-02-06
### Added
- **Arquitectura Gen 3**: Implementada la Capa de Consciencia con Memoria Semántica, Auditoría Proactiva y Observabilidad.
- **Preparación 3D**: Introducción de `SpatialMeta` DTO para transporte unificado de datos 2D/3D.
- **Interfaces**: Definición de `IRenderer3D` para futuros motores de renderizado.
- **Testing**: Integración de `pytest`, `pytest-qt` y `pytest-mock` en el entorno de desarrollo.
- **Documentación Core**: Cobertura masiva de docstrings (Google Style) en servicios, dominio y utilidades geométricas.

### Changed
- **Refactorización Core**: Reducción masiva de la complejidad ciclomática (CC < 8) en 8 hotspots críticos.
- **Modularización de Servicios**: Fragmentación de `DrillholeService` y `GeologyService` en componentes especializados (`DataFetcher`, `ProfileSampler`, `OutcropProcessor`).
- **Desacoplamiento**: La lógica de proyección de trayectorias ahora es independiente de la UI de previsualización.
- **Limpieza**: Consolidación y estandarización del sub-paquete `geometry_utils`.
- **Mantenibilidad**: Corrección estructural de docstrings de módulo para cumplimiento estricto con PEP 257.

### Fixed
- **Integridad**: Corregida la exportación de tipos de dominio en `__init__.py`.
- **Tests**: Actualizada la suite de pruebas unitarias para compatibilidad con la arquitectura delegada.

## [2.9.0] - 2026-02-01
### Added
- **Arquitectura**: Descomposición de `DrillholeService` (Monolito) en procesadores especializados (`CollarProcessor`, `SurveyProcessor`, `IntervalProcessor`, `ProjectionEngine`).
- **Arquitectura**: Modularización del sistema de tipos `core.types` en un paquete con separación de responsabilidades (`domain_types`, `task_inputs`, `dtos`).
- **Core**: Centralized profile context preparation in `prepare_profile_context`.
- **Utils**: Unified attribute detachment using `extract_feature_attributes`.
- **Stability**: Enhanced `PYTHONPATH` robustness in Docker and local environments.

### Changed
- **Arquitectura**: Consolidación de Fase 3: Unificación de todos los servicios core (Geology, Structure, Drillhole) bajo el patrón de flujo de datos desacoplado (Domain-Pure logic).
- **Core**: Reducción drástica de complejidad ciclomática en el núcleo de procesamiento de sondajes.
- **Calidad**: Eliminación de ~300 líneas de código legacy y adopción del patrón Facade para servicios principales.
- **Core**: Reducción de redundancia mediante la centralización de lógica de muestreo de elevación y configuración de sección.
- **Imports**: Estandarización de importaciones internas usando el prefijo `sec_interp.` para evitar conflictos de identidad de clases.

### Fixed
- **Geometry**: Resolución definitiva del error `'QgsGeometry' object has no attribute 'clone'` mediante el uso de constructores de clonación robustos compatibles con todas las versiones de QGIS 3.x.
- **Tests**: Resolución de fallos en `assertRaises` causados por carga duplicada de módulos en el `PYTHONPATH`.
- **Geology**: Corrección de formateo en la generación asíncrona de segmentos geológicos.

## [2.8.0] - 2026-01-25
### Added
- Nuevo DTO `DrillholeTaskInput` para procesamiento asíncrono desacoplado.
- Soporte para geometrías WKT en `GeologySegment`.
- **UI**: Added checkbox to toggle legend visibility in the preview widget.
- **Core**: Centralized section azimuth and field mapping calculation in services.
- **Mocks**: Added `azimuth` method to `MockQgsPointXY`.

### Changed
- Refactorización mayor de `GeologyService` y `DrillholeService` para eliminar dependencias directas de QGIS durante el cálculo.
- Estabilización y robustecimiento de mocks de QGIS en la suite de pruebas.
- Migración de DTOs de dominio para usar tipos primitivos de Python.
- **Tech Debt**: Refactored `GeologyService` to improve maintainability by reducing method length.

### Fixed
- **UI**: Fixed bug where legend remained visible on canvas after toggling checkbox.
- **Export**: Fixed legend leakage in PNG, PDF, and SVG exports when visibility was disabled.
- **Docs**: Fixed visibility of Python docstrings in Sphinx output by implementing proper mocking and deferred type evaluation.
- **Tests**: Core decoupled tests fixed in Docker by synchronizing `GeologySegment` schema and implementing environment isolation (Mocks vs Real API).
- **Docker**: Optimized `Dockerfile` to execute test suites in isolated processes to prevent state contamination.

## [2.7.0] - 2026-01-18

### Added
- **GUI**: New sidebar-based navigation (replaces tabs) for improved workflow and native QGIS aesthetics.
- **GUI**: Centralized validation manager (`DialogValidationManager`) and message system (`MessageManager`).
- **Core**: Robust **3-Level Validation Architecture** (Type, Business Logic, and Domain).
- **Core**: Enhanced 3D Export for Drillhole Traces and Geological Intervals (PolygonZ/LineStringZ).
- **Infrastructure**: Dockerized QA environment (`make docker-test`) with stable mock system.
- **Infrastructure**: Automated Sphinx API documentation with external build support.
- **Internationalization (i18n)**: Comprehensive support for English and Spanish across the entire interface.

### Changed
- **UX**: Unified terminology across all documentation (Page vs Tab).
- **Docs**: Comprehensive overhaul of `ARCHITECTURE.md` and `USER_GUIDE.md` for phase alignment.
- **Architecture**: Decoupled monolithic `SecInterpDialog` into specialized managers (Interpretation, Cache, Settings, etc.).
- **Code Standards**: Strictly enforced Black formatting, Ruff linting, and Conventional Commits.

### Fixed
- Fixed broken internal documentation links in README.
- Restored backwards compatibility for plugin callers via method proxies in `SecInterpDialog`.
- Stabilized massive mock signal/attribute errors in the testing suite.

### 🧪 Testing & Quality
- Achieved **100% success rate** with 361 tests passing in Docker.
- Optimized mock infrastructure with `ModuleProxy` and `MockSignal`.

## [2.6.0] - 2026-01-09
### 🚀 Infrastructure & DevOps
- **Dockerized CI/CD**:
  - Migrated GitHub Actions pipeline to use `qgis/qgis:latest` image.
  - Enabled native headless testing with `QT_QPA_PLATFORM: offscreen`.
  - Optimized `Dockerfile` for local development parity using `uv`.

### 🏗️ Architecture & Refactoring
- **3D Exporter Optimization**:
  - Significant reduction in cyclomatic complexity for `Interpretation3DExporter`.
  - Refactored monolithic methods into granular, testable private methods.
- **GUI Validation Harmonization**:
  - Decoupled `DialogValidator` from direct UI widget access.
  - Centralized parameter collection via `DialogDataAggregator`.
  - Unified validation rules across `DemPage`, `GeologyPage`, and `StructurePage`.

### 🧪 Testing & Quality
- **Test Suite Stabilization**:
  - Resolved `StopIteration` in GUI tests by fixing mock pollution.
  - Stabilized `BaseTestCase` with aggressive mock resets and class-based `QListWidget` mocking.
  - Final suite: 312 tests passing (Unit + Integration).
- **Performance Benchmarks**:
  - Implemented benchmark suite for geometry processing and 3D export.
  - Established baselines for future regression testing.
- **Type Safety**:
  - Achieved 100% type hint coverage for GUI validation modules.
  - Added Google-style docstrings to critical UI components.
- **Code Standards**:
  - Applied Project-wide formatting with `black`.

### 🌍 Internationalization
- **Measure Tool**:
  - Translated results and "New Interpretation" default name to English.
  - Made measurement results fully localizable via `tr()`.

## [2.5.0] - 2026-01-03
### 🚀 Major Features
- **3D Interpretation Export**:
  - Export geological interpretations as real 3D Shapefiles (PolygonZ).
  - Vertex-wise affine transformation ensuring geometric integrity of complex subsurface structures.
  - Native QGIS API implementation for high-fidelity spatial data.
- **Settings Page**: New sidebar navigation page for advanced plugin configuration and management.

### 🔧 Stability & Improvements
- **Proactive Data Persistence**:
  - Overhauled `DialogSettingsManager` with multi-scope support (`SecInterp`/`SecInterpUI`).
  - Parameters are remembered immediately on successful Preview or dialog Accept, preventing data loss.
  - Robust layer restoration using Layer ID with fallback to Layer Name.
- **Forced Sync**: Immediate configuration writing to disk (`sync()`) for increased reliability.
- **Quality Assurance**:
  - Project-wide Ruff activation (F401, F841, I001) with 250+ automated fixes.
  - Resolved critical `AttributeError` in validation logic and preview rendering.
  - Enhanced Mock infrastructure for 100% reliable test execution.

## [2.4.0] - 2025-12-31
### 🚀 Major Features
- **Internationalization (I18n) System**:
  - Full support for **5 languages**: Spanish (ES), French (FR), German (DE), Russian (RU), Portuguese Brazil (PT_BR).
  - Native Qt translation pipeline (`.ts` → `.qm`) with automatic locale detection from QGIS settings.
  - Dedicated translation management scripts (`update-strings.sh`, `compile-strings.sh`).
- **New Interpretation Tool**:
  - Interactive **Polygon Drawing**: digitize geological interpretations directly on the profile view.
  - **Smart Snapping**: `ProfileSnapper` engine snaps to vertices/edges of projected layers (tolerance ~12px).
  - **Auto-Styling**: Generates vivid, distinct colors (HSV) for each new interpretation polygon.
  - **UX Enhancements**: "Undo" (Right-click), Rubber-band real-time preview, and intuitive finalize actions.

### 🏗️ Architecture & Core Refactoring
- **Phase 1: Dependency Injection & Interfaces**:
  - Introduced `core/interfaces/` defining strict contracts for all services (`DrillholeInterface`, `GeologyInterface`, etc.).
  - Decoupled `Manager` classes using DI principles.
- **Phase 2: Robust Error Handling**:
  - Unified exception hierarchy in `core/exceptions.py`.
  - Structured logging across the entire application with traceable error contexts.
- **Phase 3: Performance & Caching**:
  - Advanced `CacheManager` with Time-To-Live (TTL) and Level-of-Detail (LOD) awareness.
  - Vectorized geometry calculations for massive speedups in spatial operations.
- **Phase 4: Asynchronous Processing**:
  - `AsyncGeologyProcessor` with cancellation tokens to prevent UI freezes.
  - Proper resource cleanup using Python Context Managers.
- **Phase 5: Modern Python & Validation**:
  - Adopted `dataclasses` for all data transfer objects (DTOs).
  - Strongly typed codebase with `typing.Protocol` and Python 3.10+ syntax.
  - Centralized validation logic in `core/validation/` (Project, Layer, Field validators).
- **Phase 6: GUI Decomposition**:
  - Split monolithic `main_dialog.py` into specialized handlers:
    - `gui/main_dialog_settings.py`
    - `gui/main_dialog_preview.py`
    - `gui/main_dialog_tools.py`
    - `gui/main_dialog_data.py`

### 🔧 Infrastructure & Tooling
- **Modern Package Management**:
  - Migrated to **`uv`** for 10-100x faster dependency resolution.
  - Added `uv.lock` for deterministic, reproducible builds.
  - Centralized all tool configs (Ruff, Pytest, Pylint) into `pyproject.toml`.
- **Code Quality Pipeline**:
  - **Pre-commit Hooks**: strictly enforcing `ruff`, `trailing-whitespace`, and file validity.
  - **Metrics History**: Tracking code quality evolution in `.ai-context/metrics_history.json`.
  - **Strict Linting**: 9% reduction in issues, 100% QGIS Plugin compliance score.

### 🐛 Critical Bug Fixes
- **Stability**: Fixed `QgsProject` import crash in preview axes manager.
- **Rendering**: Fixed coordinate reference system (CRS) transformations for memory layers.
- **I18n**: Fixed Russian XML corruption and empty translation attributes.
- **Logic**: Resolved `super().__init__()` ordering issues in Page classes and validation false positives.

### 📝 Documentation
- **Google-Style Docstrings**: Standardized across all `core/` modules.
- **Research Archive**: Moved internal technical notes to `research/` directory to clean up `docs/`.
- **New Guides**: Added `research/project_docs/ARCHITECTURE_EN.md` and `DEVELOPMENT_GUIDE.md`.

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
  - Robust context loading with mandatory project-level files (`AI_CONTEXT.md`, `project_context.json`).


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
## [Unreleased]

### Agente
- **Integración**: Actualizado `qgis-plugin-analyzer` a v1.9.0 con soporte para subcomandos especializados (`i18n`, `security`, `performance`).
- **Workflow**: Añadido nuevo workflow `/audit-plugin` para auditorías modulares.
- **Skills**: Actualizado `coding-standards` para validar traducciones y seguridad en código nuevo.
- **Procesos**: Incorporado *Quick Scan* en inicio de sesión y validación estricta en releases.
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
