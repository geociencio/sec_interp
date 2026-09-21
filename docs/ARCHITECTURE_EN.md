# SecInterp - Detailed Project Architecture

> **Comprehensive Technical Documentation for the SecInterp QGIS Plugin**
> Version 3.8.0 | Last Updated: 2026-09-20

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

<!-- Directory tree is linkified: each Python module links to its vault note (Obsidian [[slug]] + GitHub Markdown). See docs/code_walkthrough/Index.md -->
- `sec_interp/` — plugin root → [[layer_plugin]] · [[plugin_mixins]]
  - `__init__.py` — Plugin entry point (registers with QGIS) → [[__init__]] · [doc](code_walkthrough/__init__.md)
  - `sec_interp_plugin.py` — Root class `SecInterp` (facade) → [[sec_interp_plugin]] · [doc](code_walkthrough/sec_interp_plugin.md)
  - `plugin/` — Plugin mixins composed by `SecInterp` → [[plugin_mixins]] · [doc](code_walkthrough/plugin_mixins.md)
    - `plugin/lifecycle.py` — `PluginLifecycleMixin` (`add_action`, `initGui`, `run`, `unload`) → [[plugin_mixins]]
    - `plugin/input_validator.py` — `InputValidationMixin` (`_get_and_validate_inputs`) → [[plugin_mixins]]
    - `plugin/render_pipeline.py` — `RenderPipelineMixin` (`draw_preview`) → [[plugin_mixins]]
  - `metadata.txt` — QGIS plugin metadata
  - `Makefile` — Automation (deploy, tests, docs)
  - `logger_config.py` → [[logger_config]] · [doc](code_walkthrough/logger_config.md)
- `core/` ⚙️ — Business Logic (QGIS-agnostic, thread-safe) → [[layer_core]]
  - `controller.py` — Orchestrator `ProfileController` → [[controller]] · [doc](code_walkthrough/controller.md)
  - `config.py` → [[config]] · [doc](code_walkthrough/config.md)
  - `data_cache.py` → [[data_cache]] · [doc](code_walkthrough/data_cache.md)
  - `exceptions.py` → [[exceptions]] · [doc](code_walkthrough/exceptions.md)
  - `performance_metrics.py` → [[performance_metrics]] · [doc](code_walkthrough/performance_metrics.md)
  - `domain/` — DTOs `ProfileData`, `GeologySegment` → [[domain]] · [[layer_core_domain]] · [doc](code_walkthrough/domain.md)
  - `interfaces/` — ABCs for DI (`IGeologyService`, `IDrillholeService`, `IPreviewService`, …) → [[layer_core_interfaces]]
  - `models/settings_model.py` — Typed settings → [[layer_core_models]]
  - `validation/` — Modular pipeline → [[validation]] · [[layer_core_validation]] · [doc](code_walkthrough/validation.md)
    - `validation/pipeline.py`, `layer_validator.py`, `field_validator.py`, `path_validator.py`, `project_validator.py` → [[validation]]
  - `utils/` — Helpers (pure Python) → [[layer_core_utils]]
    - `utils/safe_loader.py` → [[safe_loader]] · [doc](code_walkthrough/safe_loader.md)
    - `utils/i18n.py` → [[i18n]] · [doc](code_walkthrough/i18n.md)
    - `utils/geometry_utils/` (`measurement.py`, `optimization.py`, `processing.py`) → [[layer_core_utils_geometry_utils]]
  - `services/` — Concrete implementations → [[layer_core_services]]
    - `services/geology_service.py` → [[geology_service]] · [doc](code_walkthrough/geology_service.md)
    - `services/structure_service.py` → [[structure_service]] · [doc](code_walkthrough/structure_service.md)
    - `services/drillhole_service.py` → [[drillhole_service]] · [doc](code_walkthrough/drillhole_service.md)
    - `services/export_service.py` — 13-line compatibility shim → [[export_service]] · [doc](code_walkthrough/export_service.md)
    - `services/export/` — Export package (orchestrator + handlers) → [[export_package]] · [[layer_core_services_export]] · [doc](code_walkthrough/export_package.md)
      - `services/export/orchestrator.py`, `path_resolver.py`, `map_settings_factory.py`, `compat.py`
      - `services/export/handlers/` (topography, geology, structures, drillholes, drillholes_3d, interpretations, axes) → [[layer_core_services_export_handlers]]
    - `services/preview_service.py` → [[preview_service]] · [doc](code_walkthrough/preview_service.md)
    - `services/access_control_service.py` → [[access_control_service]] · [doc](code_walkthrough/access_control_service.md)
    - `services/drillhole/` — Drillhole pipeline → [[layer_core_services_drillhole]]
      - `services/drillhole/collar_processor.py` → [[collar_processor]] · [doc](code_walkthrough/collar_processor.md)
      - `services/drillhole/survey_processor.py` → [[survey_processor]] · [doc](code_walkthrough/survey_processor.md)
      - `services/drillhole/interval_processor.py` → [[interval_processor]] · [doc](code_walkthrough/interval_processor.md)
      - `services/drillhole/projection_engine.py` → [[projection_engine]] · [doc](code_walkthrough/projection_engine.md)
      - `services/drillhole/trajectory_engine.py` → [[trajectory_engine]] · [doc](code_walkthrough/trajectory_engine.md)
- `gui/` 🖥️ — UI Layer (QGIS-dependent) → [[layer_gui]]
  - `gui/main_dialog.py` — `SecInterpDialog` orchestrator → [[main_dialog]] · [doc](code_walkthrough/main_dialog.md)
  - `gui/dialog_*_mixin.py` — Message / lifecycle / facade mixins → [[dialog_mixins]] · [doc](code_walkthrough/dialog_mixins.md)
  - `gui/adapters/` — Extract phase (QGIS → DTOs) → [[adapters]] · [[layer_gui_adapters]] · [doc](code_walkthrough/adapters.md)
    - `adapters/drillhole_extractor.py` → [[drillhole_extractor]] · [doc](code_walkthrough/drillhole_extractor.md)
    - `adapters/geology_extractor.py` → [[geology_extractor]] · [doc](code_walkthrough/geology_extractor.md)
    - `adapters/structure_extractor.py` → [[structure_extractor]] · [doc](code_walkthrough/structure_extractor.md)
    - `adapters/validation_extractor.py` → [[validation_extractor]] · [doc](code_walkthrough/validation_extractor.md)
    - `adapters/profile_extractor.py` → [[profile_service]] · [doc](code_walkthrough/profile_service.md)
    - `adapters/feature_fetcher.py`, `layer_resolver.py`, `geometry.py` → [[adapters]]
  - Managers (orchestration)
    - `dialog_signal_manager.py` → [[signal_manager]] · [doc](code_walkthrough/signal_manager.md)
    - `dialog_input_manager.py` → [[input_manager]] · [doc](code_walkthrough/input_manager.md)
    - `dialog_preview_manager.py` → [[dialog_preview_manager]] · [[preview_mixins]] · [doc](code_walkthrough/dialog_preview_manager.md)
    - `dialog_export_manager.py` → [[dialog_export_manager]] · [doc](code_walkthrough/dialog_export_manager.md)
    - `dialog_interpretation_manager.py` → [[interpretation_manager]] · [[interpretation_mixins]] · [doc](code_walkthrough/interpretation_manager.md)
    - `dialog_state_manager.py` → [[state_manager]] · [doc](code_walkthrough/state_manager.md)
    - `dialog_settings_persistence.py` → [[state_manager]] · [doc](code_walkthrough/state_manager.md)
    - `dialog_tool_manager.py` → [[tool_manager]] · [doc](code_walkthrough/tool_manager.md)
    - `layer_notification_manager.py` → [[layer_notification_manager]] · [doc](code_walkthrough/layer_notification_manager.md)
    - `ui_status_manager.py` → [[ui_status_manager]] · [doc](code_walkthrough/ui_status_manager.md)
  - `dialogs/` — Modal dialogs → [[layer_gui_dialogs]]
    - `dialogs/interpretation_properties_dialog.py` → [[layer_gui_dialogs]]
  - Rendering Engine
    - `preview_renderer.py` → [[preview_renderer]] · [doc](code_walkthrough/preview_renderer.md)
    - `preview_layer_factory.py` → [[preview_layer_factory]] · [doc](code_walkthrough/preview_layer_factory.md)
    - `preview_axes_manager.py` → [[preview_axes_manager]] · [doc](code_walkthrough/preview_axes_manager.md)
    - `preview_reporter.py` → [[preview_state]] · [doc](code_walkthrough/preview_state.md)
    - `preview_state.py` → [[preview_state]] · [doc](code_walkthrough/preview_state.md)
    - `legend_widget.py` — dynamic legend
  - `renderers/` → [[renderers]] · [[layer_gui_renderers]] · [doc](code_walkthrough/renderers.md)
    - `renderers/base_renderer.py`, `topo/geology/drillhole/structure/interpretation_renderer.py`, `color_manager.py`
  - `tasks/` (`geology_task.py`, `drillhole_task.py`) → [[tasks]] · [[layer_gui_tasks]] · [doc](code_walkthrough/tasks.md)
  - `tools/` — Interactive map tools → [[layer_gui_tools]]
    - `tools/measure_tool.py` → [[measure_tool]] · [doc](code_walkthrough/measure_tool.md)
    - `tools/interpretation_tool.py` → [[interpretation_tool]] · [doc](code_walkthrough/interpretation_tool.md)
    - `tools/snapper.py`
  - `ui/` — Programmatic window + sidebar → [[layer_gui_ui]]
    - `ui/main_window.py`, `ui/sidebar.py` → [[ui_pages]] · [doc](code_walkthrough/ui_pages.md)
    - `ui/pages/` — Tab-based pages → [[layer_gui_ui_pages]]
      - `ui/pages/base_page.py`, `dem_page.py`, `section_page.py`, `geology_page.py`, `structure_page.py`, `interpretation_page.py`, `preview_page.py` → [[ui_pages]]
      - `ui/pages/drillhole_page.py` → [[drillhole_page]] · [doc](code_walkthrough/drillhole_page.md)
      - `ui/pages/drillhole/` (collar / survey / interval tabs) → [[drillhole_tabs]] · [[layer_gui_ui_pages_drillhole]] · [doc](code_walkthrough/drillhole_tabs.md)
      - `ui/pages/settings_page.py` → [[settings_page]] · [doc](code_walkthrough/settings_page.md)
      - `ui/pages/settings/` (default / advanced / info tabs + persistence) → [[settings_tabs]] · [[layer_gui_ui_pages_settings]] · [doc](code_walkthrough/settings_tabs.md)
- `exporters/` 📤 — Factory `BaseExporter` → [[layer_exporters]]
  - `base_exporter.py` → [[base_exporter]] · [doc](code_walkthrough/base_exporter.md)
  - `vector_exporter.py` → [[vector_exporter]] · [doc](code_walkthrough/vector_exporter.md)
  - `dxf_exporter.py` → [[dxf_exporter]] · [doc](code_walkthrough/dxf_exporter.md)
  - `profile_exporters.py` / `csv_exporter.py` → [[profile_exporters]] · [[csv_exporter]] · [doc](code_walkthrough/csv_exporter.md)
  - `interpretation_3d_exporter.py` → [[interpretation_3d_exporter]] · [doc](code_walkthrough/interpretation_3d_exporter.md)
  - `interpretation_exporters.py` → [[interpretation_exporters]] · [doc](code_walkthrough/interpretation_exporters.md)
  - `drillhole_3d_exporter.py` → [[drillhole_3d_exporter]] · [doc](code_walkthrough/drillhole_3d_exporter.md)
  - `drillhole_exporters.py` → [[drillhole_exporters]] · [doc](code_walkthrough/drillhole_exporters.md)
  - `pdf_exporter.py` → [[pdf_exporter]] · [doc](code_walkthrough/pdf_exporter.md)
  - `svg_exporter.py` → [[svg_exporter]] · [doc](code_walkthrough/svg_exporter.md)
  - `image_exporter.py` → [[image_exporter]] · [doc](code_walkthrough/image_exporter.md)
- `docs/` 📚 — `ARCHITECTURE_EN.md` (this file) · `ARCHITECTURE.mmd` · `code_walkthrough/` vault
- `tests/` 🧪 — `base_test.py`, `core/`, `gui/`, `integration/`, `benchmarks/` (Mock-First, `unittest`)
- `scripts/` 🔧 — `security_scan.py` · `build_docs.sh` · `i18n/` · `sync_vault_mirrors.sh`
- `resources/` 🎨 — `icons/`, `styles/`, `resources.qrc` → `resources.py`

> [!tip] En Obsidian este árbol es navegable: cada `[[slug]]` abre la nota de la bóveda y alimenta el Graph View. En GitHub/Sphinx usa el link `[doc](code_walkthrough/slug.md)` relativo. Los espejos en `docs/code_walkthrough*/ARCHITECTURE_EN.md` se re-sincronizan con `bash scripts/sync_vault_mirrors.sh`.


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
            I_GEOL[interfaces/geology_interface.py<br/>IGeologyService]:::interface
            I_DRILL[interfaces/drillhole_interface.py<br/>IDrillholeService]:::interface
            I_STRUCT[interfaces/structure_interface.py<br/>IStructureService]:::interface
            I_PREVIEW[interfaces/preview_interface.py<br/>IPreviewService]:::interface
            I_CACHE[interfaces/cache_interface.py<br/>ICacheService]:::interface
            I_RENDER3D[interfaces/i_renderer_3d.py<br/>IRenderer3D]:::interface
        end

        subgraph SERVICES["Concrete Services - services/"]
            direction TB
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
| `DialogSignalManager` | `dialog_signal_manager.py` → [[signal_manager]] | Centralizes all signal/slot connections to avoid spaghetti code. |
| `DialogInputManager` | `dialog_input_manager.py` → [[input_manager]] | Manages input layer selection, schema validation, and layer compatibility. |
| `PreviewManager` | `dialog_preview_manager.py` → [[dialog_preview_manager]] | Coordinates the preview canvas, axes, LOD calculation, and render triggering. |
| `ExportManager` | `dialog_export_manager.py` → [[dialog_export_manager]] | Maps UI selections to the `ExportService` in the Core layer. |
| `InterpretationManager` | `dialog_interpretation_manager.py` → [[interpretation_manager]] | Handles 2D/3D geological interpretation state and user interactions. |
| `DialogStateManager` | `dialog_state_manager.py` → [[state_manager]] | Manages session persistence and UI defaults restoration. |
| `SettingsPersistence` | `dialog_settings_persistence.py` → [[state_manager]] | Handles QSettings-based persistence for plugin configuration. |
| `ToolManager` | `dialog_tool_manager.py` → [[tool_manager]] | Manages `QgsMapTool` lifecycle (pan, measure, interpret tools). |
| `LayerNotificationManager` | `layer_notification_manager.py` → [[layer_notification_manager]] | Listens to QGIS layer tree changes and updates UI accordingly. |
| `UIStatusManager` | `ui_status_manager.py` → [[ui_status_manager]] | Manages status bar messages, progress indicators, and user notifications. |

### 2. Rendering Engine

**Responsibility**: Handles all preview canvas rendering with adaptive LOD and specialized renderers.

#### Core Rendering Components

| Component | File | Responsibility |
|---------|------|----------------|
| `PreviewRenderer` | `preview_renderer.py` → [[preview_renderer]] | Main canvas renderer orchestrating specialized renderers. |
| `PreviewLayerFactory` | `preview_layer_factory.py` → [[preview_layer_factory]] | Creates temporary memory layers for preview visualization. |
| `PreviewAxesManager` | `preview_axes_manager.py` → [[preview_axes_manager]] | Manages coordinate axes, grids, and scale annotations. |
| `PreviewReporter` | `preview_reporter.py` → [[preview_state]] | Generates textual/tabular reports from preview data. |
| `PreviewParamHasher` | `preview_param_hasher.py` → [[dialog_preview_manager]] | Hashes render parameters for LOD cache invalidation. |
| `PreviewState` | `preview_state.py` → [[preview_state]] | Encapsulates preview viewport, scale, and visibility state. |

#### Specialized Renderers (Renderer Pattern)

| Renderer | File | Responsibility |
|----------|------|----------------|
| `BaseRenderer` | `renderers/base_renderer.py` → [[renderers]] | Abstract base with common rendering utilities. |
| `TopoRenderer` | `renderers/topo_renderer.py` → [[renderers]] | Renders topography profiles with elevation data. |
| `GeologyRenderer` | `renderers/geology_renderer.py` → [[renderers]] | Renders geological units, contacts, and structures. |
| `DrillholeRenderer` | `renderers/drillhole_renderer.py` → [[renderers]] | Renders drillhole traces, intervals, and projections. |
| `StructureRenderer` | `renderers/structure_renderer.py` → [[renderers]] | Renders structural measurements (strike/dip, foliations). |
| `InterpretationRenderer` | `renderers/interpretation_renderer.py` → [[renderers]] | Renders user-drawn geological interpretations. |
| `ColorManager` | `renderers/color_manager.py` → [[renderers]] | Centralized color palette and legend management. |

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
| `PreviewTaskOrchestrator` | `preview_task_orchestrator.py` → [[tasks]] | Queues, prioritizes, and monitors background tasks. |
| `GeologyTask` | `tasks/geology_task.py` → [[tasks]] | Background geological intersection calculations. |
| `DrillholeTask` | `tasks/drillhole_task.py` → [[tasks]] | Background drillhole trajectory processing. |

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
class IGeologyService(ABC):
    @abstractmethod
    def build_segments(self, context: GeologyContext, feedback: Any | None = None) -> Any:
        """Build geological segments from a detached context."""
```

#### Core Interfaces (6 Interfaces)

| Interface | File | Purpose |
|-----------|------|---------|
| `IGeologyService` | `interfaces/geology_interface.py` → [[layer_core_interfaces]] | `build_segments()` — geological segments from a detached context. |
| `IDrillholeService` | `interfaces/drillhole_interface.py` → [[layer_core_interfaces]] | `process_context()` — drillhole data processing, 3D→2D projection. |
| `IStructureService` | `interfaces/structure_interface.py` → [[layer_core_interfaces]] | `project_structures()` — structural data validation and projection. |
| `IPreviewService` | `interfaces/preview_interface.py` → [[layer_core_interfaces]] | `generate_all()` — preview orchestration and render data prep. |
| `ICacheService` | `interfaces/cache_interface.py` → [[layer_core_interfaces]] | `get/set/invalidate/clear` — caching strategy (typing `Protocol`). |
| `IRenderer3D` | `interfaces/i_renderer_3d.py` → [[layer_core_interfaces]] | `render_3d()`/`clear()` — 3D visualization abstraction. |

### 2. ProfileController (controller.py)

**Responsibility**: Central orchestrator coordinating all services through their interfaces.

#### Concrete Services (6 Services)

| Service | File | Responsibility |
|---------|------|----------------|
| `GeologyService` | `services/geology_service.py` → [[geology_service]] | Core intersection algorithms (outcrops, polygons, units). |
| `StructureService` | `services/structure_service.py` → [[structure_service]] | Structural data processing, validation, stereonets. |
| `DrillholeService` | `services/drillhole_service.py` → [[drillhole_service]] | 3D trajectory calculation, 2D section projection, interval management. |
| `ExportService` | `services/export_service.py` → [[export_service]] | Central orchestrator for Exporters layer, format registry. |
| `PreviewService` | `services/preview_service.py` → [[preview_service]] | Preview data preparation, LOD computation, render DTOs. |
| `AccessControlService` | `services/access_control_service.py` → [[access_control_service]] | License validation, feature gating, user permissions. |

#### Drillhole Sub-system (5 Components)

| Component | File | Responsibility |
|-----------|------|----------------|
| `CollarProcessor` | `drillhole/collar_processor.py` → [[collar_processor]] | Collar data validation, coordinate transformation. |
| `SurveyProcessor` | `drillhole/survey_processor.py` → [[survey_processor]] | Survey data (azimuth/dip) processing, interpolation. |
| `IntervalProcessor` | `drillhole/interval_processor.py` → [[interval_processor]] | Lithology/assay interval management, merging. |
| `TrajectoryEngine` | `drillhole/trajectory_engine.py` → [[trajectory_engine]] | 3D trajectory calculation (minimum curvature, etc.). |
| `ProjectionEngine` | `drillhole/projection_engine.py` → [[projection_engine]] | 3D→2D projection onto section plane. |

#### Geology Sub-system
- Modular geology processing in `services/geology/` (separate package).

### 3. Domain Layer

- **Domain Models** (`models/settings_model.py`): `SettingsModel` for typed configuration.
- **Entities & DTOs** (`domain/`): Immutable data transfer objects (`ProfileData`, `GeologySegment`, `DrillholeData`, etc.) for layer communication.

### 4. Validation Pipeline (validation/)

Modular validation framework with 8 validators coordinated by `ValidationPipeline`:

| Validator | File | Scope |
|-----------|------|-------|
| `BaseValidator` | `base_validator.py` → [[validation]] | Abstract base with common validation utilities. |
| `ValidationPipeline` | `pipeline.py` → [[validation]] | Orchestrates validators, aggregates results. |
| `LayerValidator` | `layer_validator.py` → [[validation]] | QGIS layer structure, CRS, geometry type validation. |
| `FieldValidator` | `field_validator.py` → [[validation]] | Attribute field names, types, required fields. |
| `PathValidator` | `path_validator.py` → [[validation]] | File/directory paths, permissions, existence. |
| `ProjectValidator` | `project_validator.py` → [[validation]] | Project-level consistency (layers, settings). |
| `ProjectValidators` | `project_validators.py` → [[validation]] | Composite project validation rules. |
| `ValidationHelpers` | `validation_helpers.py` → [[validation]] | Shared validation utilities, error formatting. |
| `Validators` | `validators.py` → [[validation]] | Convenience functions for common validations. |

### 5. Utilities (utils/)

12 specialized utility modules:

| Utility | File | Purpose |
|---------|------|---------|
| Drillhole Utils | `drillhole.py` → [[layer_core_utils]] | Drillhole-specific calculations, transformations. |
| Geology Utils | `geology.py` → [[layer_core_utils]] | Geological computations, unit conversions. |
| Geometry Utils | `geometry_utils/` → [[layer_core_utils_geometry_utils]] | Advanced geometry operations (intersections, buffers). |
| i18n Utils | `i18n.py` → [[i18n]] | Translation helpers, locale management. |
| IO Utils | `io.py` → [[layer_core_utils]] | File I/O, serialization, format handling. |
| Metadata Reader | `metadata_reader.py` → [[layer_core_utils]] | QGIS layer metadata extraction. |
| Parsing Utils | `parsing.py` → [[layer_core_utils]] | Text/CSV/XML parsing with error recovery. |
| Rendering Utils | `rendering.py` → [[layer_core_utils]] | Render-ready data preparation. |
| Safe Loader | `safe_loader.py` → [[safe_loader]] | Safe YAML/JSON loading with schema validation. |
| Sampling Utils | `sampling.py` → [[layer_core_utils]] | Statistical sampling, profile point generation. |
| Spatial Utils | `spatial.py` → [[layer_core_utils]] | Spatial queries, indexing, CRS operations. |

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
| `VectorExporter` | `vector_exporter.py` → [[vector_exporter]] | GPKG, SHP, DXF | Unified vector export for sections. |
| `DxfExporter` | `dxf_exporter.py` → [[dxf_exporter]] | DXF | CAD-compatible export. |
| `ProfileExporters` | `profile_exporters.py` → [[profile_exporters]] | CSV, XLSX | Profile data tables, sampling results. |
| `CsvExporter` | `csv_exporter.py` → [[csv_exporter]] | CSV | Raw data export. |
| `Interpretation3DExporter` | `interpretation_3d_exporter.py` → [[interpretation_3d_exporter]] | GPKG 3D, CityJSON | 3D geological interpretations. |
| `InterpretationExporters` | `interpretation_exporters.py` → [[interpretation_exporters]] | Multiple | Interpretation-specific formats. |
| `Drillhole3DExporter` | `drillhole_3d_exporter.py` → [[drillhole_3d_exporter]] | GPKG 3D, WellKnown Text | 3D drillhole traces & intervals. |
| `DrillholeExporters` | `drillhole_exporters.py` → [[drillhole_exporters]] | Multiple | Drillhole-specific formats. |
| `PdfExporter` | `pdf_exporter.py` → [[pdf_exporter]] | PDF | Professional section layouts. |
| `SvgExporter` | `svg_exporter.py` → [[svg_exporter]] | SVG | Vector graphics for reports. |
| `ImageExporter` | `image_exporter.py` → [[image_exporter]] | PNG, JPG | Raster images for presentations. |

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

**Last Updated**: 2026-09-20
**Plugin Version**: 3.4.0
**Author**: Juan M. Bernales
