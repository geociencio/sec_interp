# SecInterp - Detailed Project Architecture

> **Comprehensive Technical Documentation for the SecInterp QGIS Plugin**
> Version 3.4.0 | Last Updated: 2026-09-19

---

## 📑 Table of Contents

1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [System Architecture](#system-architecture)
4. [GUI Layer - User Interface](#gui-layer---user-interface)
5. [Core Layer - Business Logic](#core-layer---business-logic)
6. [Exporters Layer - Data Export](#exporters-layer---data-export)
7. [Design Principles](#design-principles)
8. [Extensibility](#extensibility)
9. [Project Metrics](#project-metrics)
10. [Quality Assurance & Security Scanning](#quality-assurance--security-scanning)

---

## 🎯 Overview

**SecInterp** (Section Interpreter) is a QGIS plugin designed for extracting and visualizing geological data in cross-sections. The plugin allows geologists to generate topographic profiles, project geological outcrops, and analyze structural data in a unified 2D view.

### Key Features

- ✅ **Interactive Preview System** with real-time rendering.
- ✅ **Parallel Processing** for complex geological intersections.
- ✅ **Adaptive LOD** (Level of Detail) based on zoom.
- ✅ **Measurement Tools** with automatic snapping.
- ✅ **Drillhole Support** with 3D→2D trajectory projection.
- ✅ **Multi-format Export** (SHP, GPKG, DXF, CSV, PDF, SVG).

---

## 📂 Directory Structure

The project organization follows a highly modular architecture based on the **Separation of Concerns** (SoC) principle, decoupling the interface, business logic, and export formats. Each layer has a distinct responsibility and communicates through well-defined interfaces.

```
sec_interp/
├── __init__.py                      # Plugin entry point (registers with QGIS)
├── sec_interp_plugin.py             # Root class (SecInterp) - QGIS plugin lifecycle
├── metadata.txt                     # QGIS Plugin metadata (name, version, dependencies)
├── Makefile                         # Automation (deploy, tests, docs, security, release)
│
├── core/                            # ⚙️ Business Logic (Core Layer) - QGIS-Agnostic
│   │   # Zero QGIS dependencies - pure Python, thread-safe, testable in isolation
│   ├── controller.py                # Orchestrator (ProfileController) - Central coordinator
│   ├── config.py                    # Configuration management (typed settings, defaults)
│   ├── data_cache.py                # Caching layer (LRU, TTL, invalidation strategies)
│   ├── exceptions.py                # Custom exception hierarchy (SecInterpError, ValidationError, etc.)
│   ├── performance_metrics.py       # Performance tracking (@track decorator, metrics collection)
│   │
│   ├── interfaces/                  # Abstract Base Classes for Dependency Injection
│   │   │   # Define contracts; implementations in services/; enables mocking in tests
│   │   ├── profile_interface.py     # IProfileService - Topography, sampling, profiles
│   │   ├── geology_interface.py     # IGeologyService - Intersections, geological units
│   │   ├── drillhole_interface.py   # IDrillholeService - 3D trajectories, 2D projections
│   │   ├── structure_interface.py   # IStructureService - Structural data, stereonets
│   │   ├── preview_interface.py     # IPreviewService - Render data prep, LOD computation
│   │   ├── export_interface.py      # IExportService - Export orchestration, format registry
│   │   ├── cache_interface.py       # ICacheService - Caching strategy abstraction
│   │   └── i_renderer_3d.py         # IRenderer3D - 3D visualization abstraction
│   │
│   ├── models/                      # Domain Models and Settings
│   │   └── settings_model.py        # SettingsModel - Typed configuration with validation
│   │
│   ├── services/                    # Concrete Service Implementations
│   │   │   # Business logic; consume interfaces; no QGIS GUI imports
│   │   ├── profile_service.py       # ProfileService - DEM sampling, profile generation
│   │   ├── geology_service.py       # GeologyService - Polygon/line intersections, unit processing
│   │   ├── structure_service.py     # StructureService - Strike/dip validation, stereonet data
│   │   ├── drillhole_service.py     # DrillholeService - Orchestrates drillhole sub-system
│   │   ├── export_service.py        # ExportService - Format registry, DTO→Exporter routing
│   │   ├── preview_service.py       # PreviewService - Render DTOs, LOD, parameter hashing
│   │   ├── access_control_service.py# AccessControlService - License, feature gates, permissions
│   │   │
│   │   ├── drillhole/               # Drillhole Processing Sub-system
│   │   │   │   # Modular pipeline: Collar → Survey → Trajectory → Projection
│   │   │   ├── collar_processor.py  # CollarProcessor - Collar validation, CRS transform
│   │   │   ├── survey_processor.py  # SurveyProcessor - Azimuth/dip interpolation, smoothing
│   │   │   ├── interval_processor.py# IntervalProcessor - Lithology/assay merging, validation
│   │   │   ├── projection_engine.py # ProjectionEngine - 3D→2D section plane projection
│   │   │   └── trajectory_engine.py # TrajectoryEngine - Minimum curvature, tangential, etc.
│   │   │
│   │   └── geology/                 # Geology Processing Sub-system (extensible package)
│   │
│   ├── validation/                  # Modular Validation Pipeline
│   │   │   # Composable validators; coordinated by ValidationPipeline
│   │   ├── base_validator.py        # BaseValidator - Abstract base, result aggregation
│   │   ├── pipeline.py              # ValidationPipeline - Runs validators, collects results
│   │   ├── layer_validator.py       # LayerValidator - CRS, geometry type, field schema
│   │   ├── field_validator.py       # FieldValidator - Required fields, types, domains
│   │   ├── path_validator.py        # PathValidator - File/dir existence, permissions, safety
│   │   ├── project_validator.py     # ProjectValidator - Cross-layer consistency checks
│   │   ├── project_validators.py    # ProjectValidators - Composite rule sets
│   │   ├── validation_helpers.py    # ValidationHelpers - Shared utilities, error formatting
│   │   └── validators.py            # Validators - Convenience functions, common checks
│   │
│   ├── domain/                      # Domain Layer (Entities & DTOs)
│   │   │   # Immutable data transfer objects; layer communication contracts
│   │   │   # ProfileData, GeologySegment, DrillholeData, ExportDTO, RenderDTO, etc.
│   │
│   └── utils/                       # Specialized Utilities (QGIS-Agnostic)
│       │   # Pure Python helpers; no QGIS imports
│       ├── drillhole.py             # Drillhole calculations, transformations, survey math
│       ├── geology.py               # Geological computations, unit conversions, stratigraphy
│       ├── geometry_utils/          # Advanced geometry (intersections, buffers, simplification)
│       ├── i18n.py                  # Translation helpers, locale management, pluralization
│       ├── io.py                    # File I/O, serialization, format handling (safe loaders)
│       ├── metadata_reader.py       # QGIS layer metadata extraction (fields, CRS, extent)
│       ├── parsing.py               # Text/CSV/XML parsing with error recovery, type inference
│       ├── rendering.py             # Render-ready data preparation, symbolization helpers
│       ├── safe_loader.py           # Safe YAML/JSON loading with schema validation
│       ├── sampling.py              # Statistical sampling, profile point generation, LOD
│       └── spatial.py               # Spatial queries, R-tree indexing, CRS operations
│
├── gui/                             # 🖥️ User Interface (GUI Layer) - QGIS-Dependent
│   │   # All QGIS imports (qgis.core, qgis.gui, PyQt5) contained here
│   │   # Extracts data → DTOs → calls Core services → converts results back to QGIS
│   ├── main_dialog.py               # Main Dialog (SecInterpDialog) - Manager orchestrator
│   ├── main_dialog_config.py        # Dialog configuration (constants, defaults, enums)
│   ├── main_dialog_utils.py         # Dialog utilities (helpers, formatters, validators)
│   │
│   ├── # --- Managers (Orchestration) ---
│   ├── dialog_signal_manager.py     # Centralized Signal/Slot connections (avoids spaghetti)
│   ├── dialog_input_manager.py      # Input layer selection, schema validation, compatibility
│   ├── dialog_preview_manager.py    # Preview canvas lifecycle, axes, LOD, render triggering
│   ├── dialog_export_manager.py     # Export UI → ExportService mapping, format options
│   ├── dialog_interpretation_manager.py# Interpretation state, user drawing, 2D/3D toggle
│   ├── dialog_state_manager.py      # Session persistence, UI defaults, window geometry
│   ├── dialog_settings_persistence.py# QSettings-based plugin configuration persistence
│   ├── dialog_tool_manager.py       # QgsMapTool lifecycle (pan, measure, interpret tools)
│   ├── layer_notification_manager.py# QGIS layer tree changes → UI updates
│   ├── ui_status_manager.py         # Status bar, progress, notifications, user messages
│   │
│   ├── # --- Rendering Engine ---
│   ├── preview_renderer.py          # Main canvas renderer; orchestrates specialized renderers
│   ├── preview_layer_factory.py     # Temporary memory layers for preview visualization
│   ├── preview_axes_manager.py      # Coordinate axes, grids, scale bars, annotations
│   ├── preview_reporter.py          # Textual/tabular reports from preview data
│   ├── preview_param_hasher.py      # Parameter hashing for LOD cache invalidation
│   ├── preview_state.py             # Viewport, scale, visibility, layer state encapsulation
│   ├── legend_widget.py             # Dynamic legend synchronized with renderers
│   │
│   ├── adapters/                    # UI Adapters (QGIS widgets ↔ Internal models)
│   │   │   # Bridge layer; data transformation, validation, signal bridging
│   ├── dialogs/                     # Secondary Dialogs (settings, about, import/export wizards)
│   │
│   ├── renderers/                   # Specialized Canvas Renderers (Renderer Pattern)
│   │   │   # Each handles one visual domain; compose in PreviewRenderer
│   │   ├── base_renderer.py         # BaseRenderer - Common utilities, symbol helpers
│   │   ├── topo_renderer.py         # TopoRenderer - Profiles, elevation, sampling points
│   │   ├── geology_renderer.py      # GeologyRenderer - Units, contacts, boundaries, labels
│   │   ├── drillhole_renderer.py    # DrillholeRenderer - Traces, intervals, projections
│   │   ├── structure_renderer.py    # StructureRenderer - Strike/dip symbols, stereonets
│   │   ├── interpretation_renderer.py# InterpretationRenderer - User-drawn geology
│   │   └── color_manager.py         # ColorManager - Palettes, legends, accessibility
│   │
│   ├── tasks/                       # QgsTask Background Workers (Thread Safety)
│   │   │   # Heavy computation off main thread; progress reporting; cancellation
│   │   ├── geology_task.py          # GeologyTask - Intersection calculations in background
│   │   └── drillhole_task.py        # DrillholeTask - Trajectory processing in background
│   │
│   ├── tools/                       # QgsMapTool Implementations (Interactive Editing)
│   │   │   # Map canvas interaction: pan, measure, draw interpretations
│   ├── ui/                          # Layouts and Components
│   │   └── pages/                   # Tab-based Page Components (modular UI sections)
│   │
│   └── services/                    # GUI-Specific Services (QGIS-dependent helpers)
│       │   # Thin adapters; e.g., QGIS layer → DTO conversion
│
├── exporters/                       # 📤 Export Layer - Format-Specific Output
│   │   # Factory Pattern via BaseExporter; consume core/domain DTOs only
│   │   # Zero QGIS GUI imports; QGIS core only for geometry creation
│   ├── base_exporter.py             # BaseExporter (ABC) - export() contract, result types
│   ├── vector_exporter.py           # VectorExporter - GPKG/SHP/DXF unified vector export
│   ├── dxf_exporter.py              # DxfExporter - CAD-compatible DXF (layers, blocks)
│   ├── profile_exporters.py         # ProfileExporters - Profile data tables (CSV, XLSX)
│   ├── csv_exporter.py              # CsvExporter - Raw data export, streaming
│   ├── interpretation_3d_exporter.py# Interpretation3DExporter - 3D geology (GPKG 3D, CityJSON)
│   ├── interpretation_exporters.py  # InterpretationExporters - Interpretation formats
│   ├── drillhole_3d_exporter.py     # Drillhole3DExporter - 3D traces & intervals (Z-aware)
│   ├── drillhole_exporters.py       # DrillholeExporters - Drillhole-specific formats
│   ├── pdf_exporter.py              # PdfExporter - Professional layouts, legends, multi-page
│   ├── svg_exporter.py              # SvgExporter - Vector graphics, scalable diagrams
│   └── image_exporter.py            # ImageExporter - PNG/JPG raster, high-DPI, tiles
│
├── docs/                            # 📚 Documentation
│   │   # Architecture, ADRs, manuals, maintenance logs, API reference
│   ├── ARCHITECTURE_EN.md           # This file - Detailed architecture
│   ├── ARCHITECTURE.mmd             # Mermaid diagram source
│   ├── CORE_DISTINCTION_GUIDE_EN.md # Core/GUI separation guide
│   ├── DEVELOPMENT_LOG.md           # Development history
│   ├── MAINTENANCE_LOG.md           # Maintenance records
│   └── maintenance/                 # Session reports, audit results
│
├── tests/                           # 🧪 Test Suite (Mock-First, unittest)
│   │   # No QGIS required for core tests; BaseTestCase provides mocks
│   ├── base_test.py                 # BaseTestCase - Mock injection, temp dirs, cleanup
│   ├── core/                        # Core logic tests (standalone, fast)
│   │   ├── test_algorithms.py       # Intersection, sampling, trajectory algorithms
│   │   ├── test_geology_service.py  # GeologyService behavior
│   │   ├── test_drillhole_service.py# DrillholeService, sub-system components
│   │   ├── test_export_service.py   # ExportService routing, format registry
│   │   ├── test_preview_service.py  # PreviewService, LOD, parameter hashing
│   │   └── test_validation/         # Validation pipeline, individual validators
│   ├── gui/                         # GUI tests (with QGIS mocks)
│   │   ├── test_main_dialog.py      # Manager coordination, signal wiring
│   │   ├── test_renderers.py        # Renderer output validation
│   │   └── test_tasks.py            # QgsTask execution, progress, cancellation
│   ├── integration/                 # Full QGIS integration tests (requires QGIS)
│   │   ├── test_export_workflow.py  # End-to-end export pipelines
│   │   └── test_preview_workflow.py # Preview rendering, interaction
│   └── benchmarks/                  # Performance benchmarks
│       ├── test_geometry_benchmarks.py# Geometry ops, intersection throughput
│       └── test_rendering_benchmarks.py# Renderer performance, LOD scaling
│
├── scripts/                         # 🔧 Build & Utility Scripts
│   ├── security_scan.py             # Security Scanner (Bandit + detect-secrets + Flake8)
│   ├── build_docs.sh                # Documentation Builder (Sphinx, API docs)
│   └── i18n/                        # Translation Scripts
│       ├── update-strings.sh        # Extract translatable strings (pylupdate5)
│       ├── apply_full.py            # Apply master translations
│       └── update_metadata_languages.py# Update metadata.txt with supported locales
│
└── resources/                       # 🎨 Icons, Styles, Qt Resources
    ├── icons/                       # Plugin icons (toolbar, menu, tools)
    ├── styles/                      # QML layer styles, symbology
    ├── resources.qrc                # Qt Resource Collection (compiled to resources.py)
    └── resources.py                 # Compiled resources (auto-generated)
```

---

## 🏗️ System Architecture

### Complete Architecture Diagram

```mermaid
graph TD
    classDef module fill:#f9f,stroke:#333,stroke-width:2px;
    classDef manager fill:#e1f5fe,stroke:#0277bd,stroke-width:2px;
    classDef service fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef interface fill:#fff3e0,stroke:#ef6c00,stroke-width:2px,stroke-dasharray: 5 5;
    classDef exporter fill:#fce4ec,stroke:#c2185b,stroke-width:2px;
    classDef task fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;
    classDef renderer fill:#e0f2f1,stroke:#00695c,stroke-width:2px;

    %% ========== ENTRY POINT ==========
    QGIS[QGIS Application]
    PLUGIN[sec_interp_plugin.py<br/>SecInterp Class<br/>Plugin Root]

    %% ========== GUI LAYER ==========
    subgraph GUI["🖥️ GUI Layer - User Interface"]
        direction TB

        MAIN[main_dialog.py<br/>SecInterpDialog]

        subgraph MANAGERS["Managers (Orchestration)"]
            direction TB
            SIGNALS_MGR[dialog_signal_manager.py<br/>DialogSignalManager]:::manager
            INPUT_MGR[dialog_input_manager.py<br/>DialogInputManager]:::manager
            PREVIEW_MGR[dialog_preview_manager.py<br/>PreviewManager]:::manager
            EXPORT_MGR[dialog_export_manager.py<br/>ExportManager]:::manager
            INTERP_MGR[dialog_interpretation_manager.py<br/>InterpretationManager]:::manager
            STATE_MGR[dialog_state_manager.py<br/>DialogStateManager]:::manager
            SETTINGS_MGR[dialog_settings_persistence.py<br/>SettingsPersistence]:::manager
            TOOL_MGR[dialog_tool_manager.py<br/>ToolManager]:::manager
            LAYER_NOTIF[layer_notification_manager.py<br/>LayerNotificationManager]:::manager
            UI_STATUS[ui_status_manager.py<br/>UIStatusManager]:::manager
        end

        subgraph RENDERING["Rendering Engine"]
            direction TB
            LAYER_FACTORY[preview_layer_factory.py<br/>PreviewLayerFactory]
            AXES_MGR[preview_axes_manager.py<br/>PreviewAxesManager]
            RENDERER[preview_renderer.py<br/>PreviewRenderer]
            REPORTER[preview_reporter.py<br/>PreviewReporter]
            PARAM_HASH[preview_param_hasher.py<br/>PreviewParamHasher]
            PREVIEW_STATE[preview_state.py<br/>PreviewState]
        end

        subgraph RENDERERS["Specialized Renderers"]
            direction TB
            BASE_RENDERER[renderers/base_renderer.py<br/>BaseRenderer]:::renderer
            TOPO_RENDERER[renderers/topo_renderer.py<br/>TopoRenderer]:::renderer
            GEOLOGY_RENDERER[renderers/geology_renderer.py<br/>GeologyRenderer]:::renderer
            DRILLHOLE_RENDERER[renderers/drillhole_renderer.py<br/>DrillholeRenderer]:::renderer
            STRUCT_RENDERER[renderers/structure_renderer.py<br/>StructureRenderer]:::renderer
            INTERP_RENDERER[renderers/interpretation_renderer.py<br/>InterpretationRenderer]:::renderer
            COLOR_MGR[renderers/color_manager.py<br/>ColorManager]:::renderer
        end

        subgraph WORKERS["Async Tasks (QgsTask)"]
            direction TB
            TASK_ORCH[preview_task_orchestrator.py<br/>PreviewTaskOrchestrator]:::task
            GEOLOGY_TASK[tasks/geology_task.py<br/>GeologyTask]:::task
            DRILL_TASK[tasks/drillhole_task.py<br/>DrillholeTask]:::task
        end

        subgraph TOOLS["Map Tools"]
            direction TB
            MAP_TOOLS[tools/<br/>QgsMapTool Implementations]
        end

        subgraph UI_PAGES["UI Components"]
            direction TB
            PAGES[ui/pages/<br/>Tab-based Pages]
            ADAPTERS[adapters/<br/>UI Adapters]
            LEGEND[legend_widget.py<br/>LegendWidget]
        end

        MAIN --> MANAGERS
        MAIN --> RENDERING
        MAIN --> RENDERERS
        MAIN --> WORKERS
        MAIN --> TOOLS
        MAIN --> UI_PAGES
        MAIN --> LEGEND

        MANAGERS --> RENDERING
        MANAGERS --> WORKERS
        MANAGERS --> UI_PAGES

        WORKERS --> TASK_ORCH
        RENDERING --> RENDERERS
    end

    %% ========== CORE LAYER ==========
    subgraph CORE["⚙️ Core Layer - Business Logic"]
        direction TB

        CONTROLLER[controller.py<br/>ProfileController]

        subgraph INTERFACES["Abstractions (DI) - interfaces/"]
            direction TB
            I_PROF[interfaces/profile_interface.py<br/>IProfileService]:::interface
            I_GEOL[interfaces/geology_interface.py<br/>IGeologyService]:::interface
            I_DRILL[interfaces/drillhole_interface.py<br/>IDrillholeService]:::interface
            I_STRUCT[interfaces/structure_interface.py<br/>IStructureService]:::interface
            I_PREVIEW[interfaces/preview_interface.py<br/>IPreviewService]:::interface
            I_EXPORT[interfaces/export_interface.py<br/>IExportService]:::interface
            I_CACHE[interfaces/cache_interface.py<br/>ICacheService]:::interface
            I_RENDER3D[interfaces/i_renderer_3d.py<br/>IRenderer3D]:::interface
        end

        subgraph SERVICES["Concrete Services - services/"]
            direction TB
            PROF_SVC[services/profile_service.py<br/>ProfileService]:::service
            GEOL_SVC[services/geology_service.py<br/>GeologyService]:::service
            STRUCT_SVC[services/structure_service.py<br/>StructureService]:::service
            DRILL_SVC[services/drillhole_service.py<br/>DrillholeService]:::service
            EXPORT_SVC[services/export_service.py<br/>ExportService]:::service
            PREVIEW_SVC[services/preview_service.py<br/>PreviewService]:::service
            ACCESS_SVC[services/access_control_service.py<br/>AccessControlService]:::service

            subgraph DRILLHOLE_PKG["Drillhole Sub-system"]
                direction TB
                COLLAR_PROC[drillhole/collar_processor.py<br/>CollarProcessor]
                SURVEY_PROC[drillhole/survey_processor.py<br/>SurveyProcessor]
                INTERVAL_PROC[drillhole/interval_processor.py<br/>IntervalProcessor]
                PROJ_ENGINE[drillhole/projection_engine.py<br/>ProjectionEngine]
                TRAJ_ENGINE[drillhole/trajectory_engine.py<br/>TrajectoryEngine]

                DRILL_SVC --> COLLAR_PROC
                DRILL_SVC --> SURVEY_PROC
                DRILL_SVC --> INTERVAL_PROC
                DRILL_SVC --> TRAJ_ENGINE
                COLLAR_PROC --> PROJ_ENGINE
                SURVEY_PROC --> TRAJ_ENGINE
                TRAJ_ENGINE --> PROJ_ENGINE
            end

            subgraph GEOLOGY_PKG["Geology Sub-system"]
                direction TB
                GEOLOGY_DIR[services/geology/<br/>Geology Module]
                GEOL_SVC --> GEOLOGY_DIR
            end
        end

        subgraph MODELS["Domain Models - models/"]
            direction TB
            SETTINGS_MODEL[models/settings_model.py<br/>SettingsModel]
        end

        subgraph DOMAIN["Domain Layer - domain/"]
            direction TB
            ENTITIES[Entities & DTOs<br/>ProfileData, GeologySegment,<br/>DrillholeData, etc.]
        end

        subgraph VALIDATION["Validation Pipeline - validation/"]
            direction TB
            BASE_VAL[base_validator.py<br/>BaseValidator]
            PIPELINE[pipeline.py<br/>ValidationPipeline]
            LAYER_VAL[layer_validator.py<br/>LayerValidator]
            FIELD_VAL[field_validator.py<br/>FieldValidator]
            PATH_VAL[path_validator.py<br/>PathValidator]
            PROJECT_VAL[project_validator.py<br/>ProjectValidator]
            PROJECT_VALS[project_validators.py<br/>ProjectValidators]
            HELPERS[validation_helpers.py<br/>ValidationHelpers]
            VALIDATORS[validators.py<br/>Validators]
        end

        subgraph UTILS["Utilities - utils/"]
            direction TB
            DRILL_UTIL[drillhole.py<br/>Drillhole Utils]
            GEOL_UTIL[geology.py<br/>Geology Utils]
            GEOM_UTIL[geometry_utils/<br/>Geometry Utilities]
            I18N_UTIL[i18n.py<br/>i18n Utils]
            IO_UTIL[io.py<br/>IO Utils]
            META_UTIL[metadata_reader.py<br/>Metadata Reader]
            PARSE_UTIL[parsing.py<br/>Parsing Utils]
            RENDER_UTIL[rendering.py<br/>Rendering Utils]
            SAFE_LOADER[safe_loader.py<br/>Safe Loader]
            SAMPLE_UTIL[sampling.py<br/>Sampling Utils]
            SPATIAL_UTIL[spatial.py<br/>Spatial Utils]
        end

        CONTROLLER --> INTERFACES
        INTERFACES -.-> SERVICES
        SERVICES --> MODELS
        SERVICES --> DOMAIN
        SERVICES --> VALIDATION
        SERVICES --> UTILS
        CONTROLLER --> VALIDATION
    end

    %% ========== EXPORTERS LAYER ==========
    subgraph EXPORTERS["📤 Exporters Layer"]
        direction TB

        BASE_EXPORT[exporters/base_exporter.py<br/>BaseExporter]:::exporter

        subgraph VECTOR["Vector Exporters"]
            direction TB
            VEC_EXPORT[exporters/vector_exporter.py<br/>VectorExporter<br/>GPKG/SHP/DXF]:::exporter
            DXF_EXPORT[exporters/dxf_exporter.py<br/>DxfExporter]:::exporter
        end

        subgraph PROFILE["Profile Exporters"]
            direction TB
            PROF_EXPORT[exporters/profile_exporters.py<br/>ProfileExporters]:::exporter
            CSV_EXPORT[exporters/csv_exporter.py<br/>CsvExporter]:::exporter
        end

        subgraph INTERP_3D["3D Geologic Export"]
            direction TB
            INTERP_3D[exporters/interpretation_3d_exporter.py<br/>Interpretation3DExporter]:::exporter
            INTERP_EXP[exporters/interpretation_exporters.py<br/>InterpretationExporters]:::exporter
        end

        subgraph DRILL_3D["3D Drillhole Export"]
            direction TB
            DRILL_3D[exporters/drillhole_3d_exporter.py<br/>Drillhole3DExporter]:::exporter
            DRILL_EXP[exporters/drillhole_exporters.py<br/>DrillholeExporters]:::exporter
        end

        subgraph DOCUMENT["Document Exporters"]
            direction TB
            PDF_EXPORT[exporters/pdf_exporter.py<br/>PdfExporter]:::exporter
            SVG_EXPORT[exporters/svg_exporter.py<br/>SvgExporter]:::exporter
            IMG_EXPORT[exporters/image_exporter.py<br/>ImageExporter]:::exporter
        end

        BASE_EXPORT --> VEC_EXPORT
        BASE_EXPORT --> PROF_EXPORT
        BASE_EXPORT --> INTERP_3D
        BASE_EXPORT --> DRILL_3D
        BASE_EXPORT --> PDF_EXPORT
        BASE_EXPORT --> SVG_EXPORT
        BASE_EXPORT --> IMG_EXPORT
        VEC_EXPORT --> DXF_EXPORT
        PROF_EXPORT --> CSV_EXPORT
        INTERP_3D --> INTERP_EXP
        DRILL_3D --> DRILL_EXP
    end

    %% ========== CONNECTIONS ==========
    QGIS --> PLUGIN
    PLUGIN --> MAIN

    %% GUI -> Core
    PREVIEW_MGR --> PREVIEW_SVC
    EXPORT_MGR --> EXPORT_SVC
    INTERP_MGR --> DRILL_SVC
    INTERP_MGR --> GEOL_SVC
    TOOL_MGR --> CONTROLLER

    %% Workers -> Controller
    TASK_ORCH --> CONTROLLER
    GEOLOGY_TASK --> CONTROLLER
    DRILL_TASK --> CONTROLLER

    %% Core -> Exporters
    EXPORT_SVC --> EXPORTERS

    %% Styles
    classDef plugin fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
    class PLUGIN plugin
```

---

## 🖥️ GUI Layer - User Interface

### 1. Manager-Based Orchestration (main_dialog.py)

**Main Class**: `SecInterpDialog`
**Responsibility**: The main dialog no longer contains business logic. It coordinates specialized **Managers** that handle specific lifecycle events and UI state.

#### Key Managers (10 Specialized Managers)

| Manager | File | Responsibility |
|---------|------|----------------|
| `DialogSignalManager` | `dialog_signal_manager.py` | Centralizes all signal/slot connections to avoid spaghetti code. |
| `DialogInputManager` | `dialog_input_manager.py` | Manages input layer selection, schema validation, and layer compatibility. |
| `PreviewManager` | `dialog_preview_manager.py` | Coordinates the preview canvas, axes, LOD calculation, and render triggering. |
| `ExportManager` | `dialog_export_manager.py` | Maps UI selections to the `ExportService` in the Core layer. |
| `InterpretationManager` | `dialog_interpretation_manager.py` | Handles 2D/3D geological interpretation state and user interactions. |
| `DialogStateManager` | `dialog_state_manager.py` | Manages session persistence and UI defaults restoration. |
| `SettingsPersistence` | `dialog_settings_persistence.py` | Handles QSettings-based persistence for plugin configuration. |
| `ToolManager` | `dialog_tool_manager.py` | Manages `QgsMapTool` lifecycle (pan, measure, interpret tools). |
| `LayerNotificationManager` | `layer_notification_manager.py` | Listens to QGIS layer tree changes and updates UI accordingly. |
| `UIStatusManager` | `ui_status_manager.py` | Manages status bar messages, progress indicators, and user notifications. |

### 2. Rendering Engine

**Responsibility**: Handles all preview canvas rendering with adaptive LOD and specialized renderers.

#### Core Rendering Components

| Component | File | Responsibility |
|---------|------|----------------|
| `PreviewRenderer` | `preview_renderer.py` | Main canvas renderer orchestrating specialized renderers. |
| `PreviewLayerFactory` | `preview_layer_factory.py` | Creates temporary memory layers for preview visualization. |
| `PreviewAxesManager` | `preview_axes_manager.py` | Manages coordinate axes, grids, and scale annotations. |
| `PreviewReporter` | `preview_reporter.py` | Generates textual/tabular reports from preview data. |
| `PreviewParamHasher` | `preview_param_hasher.py` | Hashes render parameters for LOD cache invalidation. |
| `PreviewState` | `preview_state.py` | Encapsulates preview viewport, scale, and visibility state. |

#### Specialized Renderers (Renderer Pattern)

| Renderer | File | Responsibility |
|----------|------|----------------|
| `BaseRenderer` | `renderers/base_renderer.py` | Abstract base with common rendering utilities. |
| `TopoRenderer` | `renderers/topo_renderer.py` | Renders topography profiles with elevation data. |
| `GeologyRenderer` | `renderers/geology_renderer.py` | Renders geological units, contacts, and structures. |
| `DrillholeRenderer` | `renderers/drillhole_renderer.py` | Renders drillhole traces, intervals, and projections. |
| `StructureRenderer` | `renderers/structure_renderer.py` | Renders structural measurements (strike/dip, foliations). |
| `InterpretationRenderer` | `renderers/interpretation_renderer.py` | Renders user-drawn geological interpretations. |
| `ColorManager` | `renderers/color_manager.py` | Centralized color palette and legend management. |

**LOD Optimization Methods** (in `PreviewRenderer`):

| Method | Purpose | Algorithm |
|--------|---------|-----------|
| `_decimate_line_data()` | Line simplification | Douglas-Peucker |
| `_calculate_curvature()` | Local curvature calculation | Angle between segments |
| `_adaptive_sample()` | Adaptive sampling | Curvature-based density |

### 3. Async Task System (QgsTask)

**Responsibility**: Offloads heavy computation to background threads keeping UI responsive.

| Task | File | Responsibility |
|------|------|----------------|
| `PreviewTaskOrchestrator` | `preview_task_orchestrator.py` | Queues, prioritizes, and monitors background tasks. |
| `GeologyTask` | `tasks/geology_task.py` | Background geological intersection calculations. |
| `DrillholeTask` | `tasks/drillhole_task.py` | Background drillhole trajectory processing. |

### 4. Map Tools & UI Components

- **Map Tools** (`tools/`): `QgsMapTool` implementations for interactive editing (pan, measure, interpretation drawing).
- **UI Pages** (`ui/pages/`): Tab-based page components for each plugin section.
- **UI Adapters** (`adapters/`): Adapters bridging QGIS widgets to internal models.
- **LegendWidget** (`legend_widget.py`): Dynamic legend synchronized with renderers.

## ⚙️ Core Layer - Business Logic

### 1. Interface-Driven Design (interfaces/)

**Pattern**: Dependency Injection (DI) via Abstract Base Classes (ABCs)
**Responsibility**: All services are defined as interfaces. The `ProfileController` consumes interfaces, allowing for easy mocking during testing and replacement of logic without affecting the GUI.

```python
class IGeologyService(abc.ABC):
    @abc.abstractmethod
    def calculate_intersections(self, profile: ProfileData) -> List[GeologySegment]:
        pass
```

#### Core Interfaces (8 Interfaces)

| Interface | File | Purpose |
|-----------|------|---------|
| `IProfileService` | `interfaces/profile_interface.py` | Topography extraction, sampling, profile generation. |
| `IGeologyService` | `interfaces/geology_interface.py` | Geological intersection algorithms, unit processing. |
| `IDrillholeService` | `interfaces/drillhole_interface.py` | Drillhole data processing, 3D→2D projection. |
| `IStructureService` | `interfaces/structure_interface.py` | Structural data validation and processing. |
| `IPreviewService` | `interfaces/preview_interface.py` | Preview orchestration, LOD calculation, render data prep. |
| `IExportService` | `interfaces/export_interface.py` | Export orchestration, format registry, DTO conversion. |
| `ICacheService` | `interfaces/cache_interface.py` | Caching strategy for expensive computations. |
| `IRenderer3D` | `interfaces/i_renderer_3d.py` | 3D visualization abstraction for drillholes/geology. |

### 2. ProfileController (controller.py)

**Responsibility**: Central orchestrator coordinating all services through their interfaces.

#### Concrete Services (7 Services)

| Service | File | Responsibility |
|---------|------|----------------|
| `ProfileService` | `services/profile_service.py` | Topography extraction, sampling logic, profile generation. |
| `GeologyService` | `services/geology_service.py` | Core intersection algorithms (outcrops, polygons, units). |
| `StructureService` | `services/structure_service.py` | Structural data processing, validation, stereonets. |
| `DrillholeService` | `services/drillhole_service.py` | 3D trajectory calculation, 2D section projection, interval management. |
| `ExportService` | `services/export_service.py` | Central orchestrator for Exporters layer, format registry. |
| `PreviewService` | `services/preview_service.py` | Preview data preparation, LOD computation, render DTOs. |
| `AccessControlService` | `services/access_control_service.py` | License validation, feature gating, user permissions. |

#### Drillhole Sub-system (5 Components)

| Component | File | Responsibility |
|-----------|------|----------------|
| `CollarProcessor` | `drillhole/collar_processor.py` | Collar data validation, coordinate transformation. |
| `SurveyProcessor` | `drillhole/survey_processor.py` | Survey data (azimuth/dip) processing, interpolation. |
| `IntervalProcessor` | `drillhole/interval_processor.py` | Lithology/assay interval management, merging. |
| `TrajectoryEngine` | `drillhole/trajectory_engine.py` | 3D trajectory calculation (minimum curvature, etc.). |
| `ProjectionEngine` | `drillhole/projection_engine.py` | 3D→2D projection onto section plane. |

#### Geology Sub-system
- Modular geology processing in `services/geology/` (separate package).

### 3. Domain Layer

- **Domain Models** (`models/settings_model.py`): `SettingsModel` for typed configuration.
- **Entities & DTOs** (`domain/`): Immutable data transfer objects (`ProfileData`, `GeologySegment`, `DrillholeData`, etc.) for layer communication.

### 4. Validation Pipeline (validation/)

Modular validation framework with 8 validators coordinated by `ValidationPipeline`:

| Validator | File | Scope |
|-----------|------|-------|
| `BaseValidator` | `base_validator.py` | Abstract base with common validation utilities. |
| `ValidationPipeline` | `pipeline.py` | Orchestrates validators, aggregates results. |
| `LayerValidator` | `layer_validator.py` | QGIS layer structure, CRS, geometry type validation. |
| `FieldValidator` | `field_validator.py` | Attribute field names, types, required fields. |
| `PathValidator` | `path_validator.py` | File/directory paths, permissions, existence. |
| `ProjectValidator` | `project_validator.py` | Project-level consistency (layers, settings). |
| `ProjectValidators` | `project_validators.py` | Composite project validation rules. |
| `ValidationHelpers` | `validation_helpers.py` | Shared validation utilities, error formatting. |
| `Validators` | `validators.py` | Convenience functions for common validations. |

### 5. Utilities (utils/)

12 specialized utility modules:

| Utility | File | Purpose |
|---------|------|---------|
| Drillhole Utils | `drillhole.py` | Drillhole-specific calculations, transformations. |
| Geology Utils | `geology.py` | Geological computations, unit conversions. |
| Geometry Utils | `geometry_utils/` | Advanced geometry operations (intersections, buffers). |
| i18n Utils | `i18n.py` | Translation helpers, locale management. |
| IO Utils | `io.py` | File I/O, serialization, format handling. |
| Metadata Reader | `metadata_reader.py` | QGIS layer metadata extraction. |
| Parsing Utils | `parsing.py` | Text/CSV/XML parsing with error recovery. |
| Rendering Utils | `rendering.py` | Render-ready data preparation. |
| Safe Loader | `safe_loader.py` | Safe YAML/JSON loading with schema validation. |
| Sampling Utils | `sampling.py` | Statistical sampling, profile point generation. |
| Spatial Utils | `spatial.py` | Spatial queries, indexing, CRS operations. |

## 📤 Exporters Layer

The Exporters layer implements the **Factory Pattern** via `BaseExporter` abstract class. All exporters consume QGIS-agnostic DTOs from `core/domain`.

### Export Hierarchy

```
BaseExporter (ABC)
├── VectorExporter → DxfExporter
│   ├── GPKG, SHP, DXF output
│   └── Layer-based feature export
├── ProfileExporters → CsvExporter
│   ├── Profile data (CSV, Excel)
│   └── Sampling results export
├── Interpretation3DExporter → InterpretationExporters
│   ├── 3D geological interpretations (Z-aware)
│   └── GeoPackage 3D, CityJSON
├── Drillhole3DExporter → DrillholeExporters
│   ├── 3D drillhole traces (Z-aware)
│   └── Interval data as 3D cylinders
├── PdfExporter
│   ├── Professional layouts with legends
│   └── Multi-page section reports
├── SvgExporter
│   ├── Vector graphics for publications
│   └── Scalable section diagrams
└── ImageExporter
    ├── PNG/JPG raster output
    └── High-DPI for presentations
```

### Key Exporters

| Exporter | File | Formats | Purpose |
|----------|------|---------|---------|
| `VectorExporter` | `vector_exporter.py` | GPKG, SHP, DXF | Unified vector export for sections. |
| `DxfExporter` | `dxf_exporter.py` | DXF | CAD-compatible export. |
| `ProfileExporters` | `profile_exporters.py` | CSV, XLSX | Profile data tables, sampling results. |
| `CsvExporter` | `csv_exporter.py` | CSV | Raw data export. |
| `Interpretation3DExporter` | `interpretation_3d_exporter.py` | GPKG 3D, CityJSON | 3D geological interpretations. |
| `InterpretationExporters` | `interpretation_exporters.py` | Multiple | Interpretation-specific formats. |
| `Drillhole3DExporter` | `drillhole_3d_exporter.py` | GPKG 3D, WellKnown Text | 3D drillhole traces & intervals. |
| `DrillholeExporters` | `drillhole_exporters.py` | Multiple | Drillhole-specific formats. |
| `PdfExporter` | `pdf_exporter.py` | PDF | Professional section layouts. |
| `SvgExporter` | `svg_exporter.py` | SVG | Vector graphics for reports. |
| `ImageExporter` | `image_exporter.py` | PNG, JPG | Raster images for presentations. |

### Format Decoupling

All exporters implement:
- `export(dto: ExportDTO, output_path: Path) -> ExportResult`
- Consume only `core/domain` DTOs (no QGIS dependencies)
- Return structured `ExportResult` with metadata (files created, features exported, warnings)

## 🎨 Design Principles

SecInterp v3.4.0 follows industry-standard architectural patterns to ensure high quality and testability.

### Core Architectural Patterns
- **Manager Pattern (GUI)**: Decouples the main window from individual feature logic (Export, Preview, etc.).
- **Dependency Injection (Core)**: Uses `core/interfaces` to decouple the `ProfileController` from concrete service implementations.
- **Factory Pattern (Exporters)**: The `ExportService` dynamically selects the appropriate `BaseExporter` subclass.
- **Observer Pattern (Signals)**: Extensive use of `PyQt5.QtCore.pyqtSignal` for asynchronous communication between Core and GUI.
- **DTO Pattern (Data Transfer Objects)**: All data passing between layers is encapsulated in immutable DTOs from `core/domain`.

### SOLID & Clean Code
- **Interface Segregation**: Clients only depend on the specific service interfaces they need.
- **Single Responsibility**: Each Manager and Service handles a unique, atomic part of the plugin workflow.
- **Thread Safety**: Long-running operations only use `QgsTask` to avoid blocking the QGIS main thread.

---

## 🚀 Extensibility

### Adding a New Service
1. Define the interface in `core/interfaces/` (inheriting from `abc.ABC`).
2. Implement the concrete service in `core/services/`.
3. Register the service in `controller.py` and inject it into the `ProfileController`.

### Adding a New Export Format
1. Inherit from `BaseExporter` in `exporters/`.
2. Implement the `export()` method using QGIS-agnostic logic.
3. Update the `ExportService` to include the new format in its registry.

---

## 📊 Project Metrics

| Metric | Value |
|--------|-------|
| **Python Modules** | 121 |
| **Source Lines of Code (SLOC)** | ~12,633 |
| **Core Layer** | ~55% |
| **GUI Layer** | ~30% |
| **Export Layer** | ~15% |

---

## 🔒 Quality Assurance & Security Scanning

SecInterp implements a multi-layered quality assurance strategy that replicates and extends the QGIS Plugin Portal's automated scanning pipeline.

### 1. Local Security Scanning (Portal-Compatible)

The project includes a custom security scanner (`scripts/security_scan.py`) that runs the **exact same tools** used by QGIS Plugin Portal:

| Tool | Severity | Purpose | Configuration |
|------|----------|---------|---------------|
| **Bandit** | CRITICAL (Blocking) | Static analysis for Python security vulnerabilities (shell injection, pickle, eval, hardcoded secrets, weak crypto, SQL injection) | `.bandit` (excludes tests/scripts, 78 tests enabled) |
| **detect-secrets** | CRITICAL (Blocking) | Scans for hardcoded credentials, API keys, private keys, high-entropy strings | `.secrets.baseline` (27 detectors, heuristic filters, excludes tests/venv) |
| **Flake8** | INFO (Non-blocking) | Code quality, PEP 8 style, syntax errors, undefined names | `.flake8` (max-line-length=100, max-complexity=15, JSON output) |

**Run locally:**
```bash
make security-scan          # Full portal-compatible scan
make pylint                 # Additional static analysis
make pep8                   # Ruff-based style check (faster)
```

### 2. QGIS Plugin Analyzer (Deep Auditing)

For architectural and deep code quality audits beyond Portal scanning:

```bash
# Security (Bandit + detect-secrets)
uv run qgis-analyzer analyze security .

# Internationalization coverage
uv run qgis-analyzer analyze i18n .

# Performance (UI blocks, expensive loops, signal leaks)
uv run qgis-analyzer analyze performance .

# Architecture (Core/GUI separation, QGIS API usage, circular deps)
uv run qgis-analyzer analyze architecture .

# Full HTML report
uv run qgis-analyzer analyze . --report
```

**Workflow**: `/audit-plugin` (agent `@auditor` with skills: project-context, coding-standards, i18n-standards)

### 3. Qt6 / QGIS 4 Migration Readiness

Automated compatibility checking using the **same tool** QGIS Portal runs on upload:

```bash
make qt6-check              # Dry-run check (pyqgis4-checker via Docker)
make qt6-fix                # Auto-migrate enums to scoped Qt6 form (edits files)
```

### 4. Pre-Release Validation Pipeline

Complete validation before any release candidate:

```bash
make pre-release            # Runs: qt6-check + security-scan + docker-test
```

**`docker-test`** executes 361+ integration tests in a clean QGIS Docker environment.

### 5. CI/CD Integration

All tools are configured to run in CI pipelines with:
- **Zero critical Bandit findings** required for merge
- **Zero detect-secrets findings** (above baseline) required for merge
- **Flake8 warnings** reported but non-blocking
- **Full test suite** (unit + integration) must pass

### 6. Configuration Files (Committed to Repo)

| File | Purpose | Portal Compatible |
|------|---------|-------------------|
| `.bandit` | Bandit test selection, exclude dirs | ✅ |
| `.secrets.baseline` | detect-secrets baseline, filters, excludes | ✅ |
| `.flake8` | Flake8 rules, complexity, output format | ✅ |
| `pyproject.toml` | Ruff, pytest, mypy config | ⚠️ (dev only) |

---

## 📝 Final Notes

This document provides a detailed overview of the SecInterp plugin architecture. For development information, please refer to [README_DEV.md](file:///home/jmbernales/qgispluginsdev/sec_interp/README_DEV.md).

**Last Updated**: 2026-09-19
**Plugin Version**: 3.4.0
**Author**: Juan M. Bernales
