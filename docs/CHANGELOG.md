# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- [To be documented during the phase]

### Changed
- [To be documented during the phase]

### Fixed
- **Linting**: Resolved project-wide W503/W504 binary operator conflicts and F401/F811 unused import violations.
- **Formatting**: Standardized the entire codebase using `black` and `ruff`.

## [3.5.0] - 2026-04-28

### Added
- **Generation 6 Agentic Autonomy**: Implemented `memory_prune.py`, `context_selector.py`, and `metrics_report.py` for autonomous maintenance and observability.
- **Strict Quality Gate**: Enforced CC <= 10 project-wide with automated pre-push audits.
- **100% Documentation**: Achieved full Google-style docstring coverage for all classes and methods.
- **QGIS 4.x Readiness**: Metadata and core services updated for Qt6/QGIS 4.x compatibility.
- **Type Hinting**: Reached 100% return type coverage and >97% parameter coverage.

### Fixed
- **Signal Leaks**: Resolved critical memory leak in Interpretation Page storage selector.
- **Spatial Indexing**: Optimized feature iteration in Interpretation Manager.
- **Linting**: Cleared all Flake8 and Ruff warnings across the codebase.

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

### Added
- **Core**: Standardized `DrillholeProjection` as a Dataclass DTO across `DrillholeService`. Implemented explicit Return Type Hints (covering ~45% of core).
- **Architecture**: Achieved **100% QGIS 4.x Readiness** by ensuring all Qt dependencies use `qgis.PyQt` (API-agnostic principle).
- **Documentation**: New automated "Documentation-as-Code" system for testing and architectural metrics.
- **Infrastructure**: Refined `.qgisignore` to eliminate 80% of development noise from the final package.

### Changed
- **Architecture**: Replaced unsafe `contextlib.suppress` with explicit exception handling and logging in `controller.py`.
- **Rendering**: Migrated 3D Exporters to `Rule-Based Rendering` for cross-version coordinate and style integrity.
- **GUI**: Raised GUI testing coverage to **91%**, including full orchestration logic for background tasks.

### Fixed
- **Stability**: Resolved critical memory leaks and "orphaned" `QgsRubberBand` instances in `measure_tool.py`.
- **UI**: Fixed "Dead Status Bar" regression in preview widget by implementing a robust signal restoration loop in `SignalManager`.
- **Mocks**: Fixed arithmetic `TypeError` in Qt mocks, allowing for verified headless layout calculations.

## [3.2.0] - 2026-03-02
### Added
- **Testing**: Massive expansion of the test suite reaching **455 successful tests** in Docker.
- **Automation**: Implemented "Documentation-as-Code" system for dynamic updating of `TESTING_STATUS.md`.
- **Testing**: New integration suite for 3D vertical projections in Cartesian coordinate systems.
- **Security**: Path Traversal protection in all data exporters via absolute path resolution.
- **Validation**: Type and range validation for preview parameters in `PreviewParams`.

### Changed
- **Compatibility**: 100% compliance with QGIS 4.x API-agnostic principles (`qgis.PyQt`).
- **UI**: Refactored `PreviewLayerFactory` to use shared geometry/exaggeration helpers (extracted `_apply_exaggeration`, `_to_qgs_points`).
- **GUI**: Standardized `DialogSettingsPersistence` to reduce boilerplate in session management and widget resets.

### Fixed
- **Core**: Fixed regression in `TrajectoryEngine` affecting buffer filtering.
- **Integration**: Restored translation loading for systems using `SafeLoader`.
- **Memory**: Resolved memory leaks due to unreleased `QgsRubberBand` and missing signal disconnections in reset/clear buttons.
- **Stability**: Fixed critical system exception capture, allowing for clean QGIS termination.
- **Stability**: Fixed layer resolution via centralized `LayerResolver` with cache.
- **Testing**: Fixed 4 legacy skipped tests in `test_utils.py` by updating mocks to native API.
- **Validation**: Unified project validation logic, eliminating duplication in DTOs.
- **UX**: Implemented reactive progress reporting for drillhole generation in the UI (added `progress_changed` signal).
- **Mocks**: Robust testing environment with support for unique layer IDs and strict geometry and field validation.
- **Stability**: Fixed `TypeError` in `ProfileController` due to dependency injection mismatch and `DrillholeProjection` subscriptable error in rendering.
- **Core**: Fixed `IndexError` in `TrajectoryEngine` for drillholes outside the section plane.

## [3.1.0] - 2026-02-19
### Added
- `SafeLoader` utility for resilient module imports and error handling.
- **i18n**: Localización complementaria para Hindi (`hi`) e Indonesio (`id`), ampliando la cobertura al mercado asiático.
- **Auditoría**: Publicado Roadmap Técnico para la modernización de `qgis-manage` (soporte `.pluginignore` y parcheo de RCC).
- **Desarrollo**: Nueva guía de despliegue y problemas conocidos para desarrolladores en `docs/maintainer`.
- **i18n**: Localización profunda de la guía de usuario para 7 idiomas prioritarios (FR, DE, IT, PT_BR, RU, ZH_CN, JA), cubriendo tutoriales y funciones avanzadas.

### Changed
- Refactorized plugin initialization (`SecInterp` class) to use lazy loading.
- Decoupled domain services in `ProfileController` using `SafeLoader` for better resilience.

## [3.0.0] - 2026-02-14
### Added
- **i18n**: Soporte expandido a 8 idiomas (Hindi, Japonés, Inglés, Español, etc.).
- **Calidad**: 100% Docstrings y CC <= 10 en servicios core.

### Fixed
- **Exportación**: Resolución de IDs de capa en `ExportService`.

## [2.0.0] - 2025-12-14
### Added
- **Major Feature**: Integración de Sondajes (Proyección e Intervalos).
