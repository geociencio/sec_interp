# SecInterp - Detailed Project Architecture

> **Complete Technical Documentation for the SecInterp QGIS Plugin**
> Version 2.7.0 | Last update: 2026-01-18

---

## 📑 Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [GUI Layer - User Interface](#gui-layer---user-interface)
4. [Core Layer - Business Logic](#core-layer---business-logic)
5. [Exporters Layer - Data Export](#exporters-layer---data-export)
6. [Main Data Flows](#main-data-flows)
7. [Design Patterns](#design-patterns)
8. [External Dependencies](#external-dependencies)
9. [Performance Optimizations](#performance-optimizations)
10. [Project Metrics](#project-metrics)

---

(overview)=
## 🎯 Overview

**SecInterp** (Section Interpreter) is a QGIS plugin designed for the extraction and visualization of geological data in cross-sections. The plugin allows geologists to generate topographic profiles, project geological outcrops, and analyze structural data in a unified 2D view.

### Main Features

- ✅ **Interactive Preview System** with real-time rendering
- ✅ **Parallel Processing** for complex geological intersections
- ✅ **Adaptive LOD** (Level of Detail) based on zoom
- ✅ **Measurement Tools** with automatic snapping
- ✅ **Drillhole Support** with 3D→2D projection
- ✅ **Multi-format Export** (SHP, CSV, PDF, SVG, PNG)

---

## 📂 Directory Structure

The project organization follows a clear modular structure to separate the interface, business logic, and utilities.

```
sec_interp/
├── __init__.py                 # Plugin entry point
├── sec_interp_plugin.py        # Root class (SecInterp)
├── metadata.txt                # QGIS metadata
├── Makefile                    # Automation (deploy, docs)
│
├── core/                       # ⚙️ Business Logic (Core Layer)
│   ├── controller.py           # Orchestrator (ProfileController)
│   ├── algorithms.py           # Pure intersection logic
│   ├── models/                 # Dataclasses and settings models
│   ├── services/               # Specialized services
│   │   ├── profile_service.py  # Topography and sampling
│   │   ├── geology_service.py  # Geological intersections
│   │   ├── structure_service.py# Structural projection
│   │   ├── drillhole_service.py# Desurvey and 3D intervals
│   │   └── preview_service.py  # Preview orchestrator
│   ├── validation/             # 🛡️ 3-Level Validation Architecture
│   │   ├── validators.py       # Level 1: Reusable Type/Range validators
│   │   ├── validation_helpers.py# Level 2: Business field constraints
│   │   └── project_validator.py# Level 3: Cross-layer domain logic
│   └── utils/                  # Utilities (Geometry, Spatial, etc.)
│
├── gui/                        # 🖥️ User Interface (GUI Layer)
│   ├── main_dialog.py          # Main dialog (Simplified)
│   ├── preview_renderer.py     # Native PyQGIS rendering
│   ├── tasks/                  # 🚀 Asynchronous QgsTasks
│   │   ├── geology_task.py     # Background geology intersection
│   │   └── drillhole_task.py   # Background drillhole projection
│   ├── managers/               # 🧩 UI Logic Managers
│   │   ├── interpretation_mgr.py # Interpretation persistence
│   │   └── message_mgr.py      # Feedback and alerts
│   ├── ui/                     # Components and Pages (Layouts)
│   └── tools/                  # Map tools (Measure Tool)
│
├── exporters/                  # 📤 Export Layer
│   ├── base_exporter.py        # Export interface
│   ├── shp_exporter.py         # Generic Shapefile exporter
│   ├── profile_exporters.py    # Specific profile exporters
│   └── drillhole_exporters.py  # Drillhole exporters
│
├── docs/                       # 📚 Technical documentation and manuals
├── tests/                      # 🧪 Unit test suite
└── resources/                  # 🎨 Icons and Qt resources
```

---

(system-architecture)=
## 🏗️ System Architecture

### Full Architecture Diagram

```mermaid
graph TB
    %% ========== ENTRY POINT ==========
    QGIS[QGIS Application]
    INIT[__init__.py<br/>Entry Point]
    PLUGIN[sec_interp_plugin.py<br/>SecInterp Class<br/>Plugin Root]

    %% ========== GUI LAYER ==========
    subgraph GUI["🖥️ GUI Layer - User Interface"]
        direction TB

        MAIN[main_dialog.py<br/>SecInterpDialog<br/>~350 lines]

        subgraph MANAGERS["Managers"]
            SIGNALS_MGR[main_dialog_signals.py<br/>SignalManager]
            DATA_MGR[main_dialog_data.py<br/>DataAggregator]
            PREVIEW_MGR[main_dialog_preview.py<br/>PreviewManager]
            EXPORT_MGR[main_dialog_export.py<br/>ExportManager]
            VALIDATION_MGR[main_dialog_validation.py<br/>DialogValidator]
            INTERP_MGR[interpretation_manager.py<br/>InterpretationManager]
            MSG_MGR[message_manager.py<br/>MessageManager]
            CONFIG_MGR[main_dialog_config.py<br/>DialogDefaults]
        end

        RENDERER[preview_renderer.py<br/>PreviewRenderer<br/>~280 lines]
        LEGEND[legend_widget.py<br/>LegendWidget]

        subgraph TOOLS["🛠️ Tools"]
            MEASURE[measure_tool.py<br/>ProfileMeasureTool]
            INTERP_TOOL[interpretation_tool.py<br/>InterpretationTool]
        end

        subgraph UI_WIDGETS["📦 UI Components"]
            UI_MAIN[main_window.py<br/>SecInterpMainWindow]
            UI_PAGES[Page Classes:<br/>DemPage, SectionPage,<br/>GeologyPage, StructPage,<br/>DrillholePage]
        end
    end

    %% ========== CORE LAYER ==========
    subgraph CORE["⚙️ Core Layer - Business Logic"]
        direction TB

        CONTROLLER[controller.py<br/>ProfileController<br/>~280 lines]

        subgraph SERVICES["🔧 Services"]
            PROFILE_SVC[profile_service.py<br/>ProfileService]
            GEOLOGY_SVC[geology_service.py<br/>GeologyService]
            STRUCTURE_SVC[structure_service.py<br/>StructureService]
            DRILLHOLE_SVC[drillhole_service.py<br/>DrillholeService]
        end

        subgraph TASKS["🚀 QGS TASKS (Extract-then-Compute)"]
            GEO_TASK[geology_task.py<br/>GeologyGenerationTask]
            DRILL_TASK[drillhole_task.py<br/>DrillholeGenerationTask]
        end

        subgraph VALIDATION_PKG["🛡️ Validation Architecture"]
            LEVEL1[validators.py<br/>Type/Range Checks]
            LEVEL2[validation_helpers.py<br/>Business Logic]
            LEVEL3[project_validator.py<br/>Domain Interaction]
        end

        METRICS[performance_metrics.py<br/>Performance Profiling]
        TYPES[types.py<br/>Data Models]

        subgraph UTILS["🔨 Utilities"]
            GEOM_UTILS[geometry.py]
            DRILL_UTILS[drillhole.py]
            GEOLOGY_UTILS[geology.py]
            SPATIAL_UTILS[spatial.py]
            SAMPLING_UTILS[sampling.py]
        end
    end

    %% ========== EXPORTERS LAYER ==========
    subgraph EXPORTERS["📤 Exporters Layer - Export"]
        direction TB

        ORCHESTRATOR[orchestrator.py<br/>DataExportOrchestrator]
        BASE_EXP[base_exporter.py<br/>BaseExporter]

        subgraph EXPORT_FORMATS["Export Formats"]
            SHP_EXP[shp_exporter.py<br/>ShapefileExporter]
            CSV_EXP[csv_exporter.py<br/>CSVExporter]
            PDF_EXP[pdf_exporter.py<br/>PDFExporter]
            SVG_EXP[svg_exporter.py<br/>SVGExporter]
            IMG_EXP[image_exporter.py<br/>ImageExporter]
            PROFILE_EXP[profile_exporters.py<br/>Profile/Geology/Struct]
            DRILL_EXP[drillhole_exporters.py<br/>2D Traces/Intervals]
            DRILL_3D[drillhole_3d_exporter.py<br/>3D Traces/Intervals]
            INTERP_3D[interpretation_3d_exporter.py<br/>3D Polygons]
        end
    end

    %% ========== CONNECTIONS ==========
    QGIS -->|loads| INIT
    INIT -->|delegates| PLUGIN
    PLUGIN -->|initializes| MAIN

    MAIN -->|delegates| MANAGERS
    MAIN -->|uses| UI_MAIN

    PREVIEW_MGR -->|renders with| RENDERER
    PREVIEW_MGR -->|updates| LEGEND
    PREVIEW_MGR -->|activates| TOOLS
    PREVIEW_MGR -->|launches| TASKS
    TASKS -->|uses| SERVICES

    EXPORT_MGR -->|delegates to| ORCHESTRATOR
    VALIDATION_MGR -->|validates with| VALIDATION_PKG

    CONTROLLER -->|orchestrates| SERVICES
    SERVICES -->|uses| UTILS
    SERVICES -->|uses| ALGORITHMS

    ORCHESTRATOR -->|delegates to| EXPORT_FORMATS

    RENDERER -->|uses| QGIS_GUI
    CONTROLLER -->|uses| QGIS_CORE
    MAIN -->|uses| PYQT5

    classDef entryPoint fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px,color:#fff
    classDef guiLayer fill:#4ecdc4,stroke:#0a9396,stroke-width:2px,color:#000
    classDef coreLayer fill:#95e1d3,stroke:#38a169,stroke-width:2px,color:#000
    classDef exportLayer fill:#ffd93d,stroke:#f59e0b,stroke-width:2px,color:#000
    classDef externalLayer fill:#a8dadc,stroke:#457b9d,stroke-width:2px,color:#000

    class QGIS,PLUGIN entryPoint
    class MAIN,PREVIEW_MGR,EXPORT_MGR,VALIDATION_MGR,CONFIG_MGR,RENDERER,LEGEND,MEASURE guiLayer
    class CONTROLLER,ALGORITHMS,PROJ_VAL,CACHE,METRICS,TYPES coreLayer
    class PROFILE_SVC,GEOLOGY_SVC,STRUCTURE_SVC,DRILLHOLE_SVC,PARALLEL_GEO coreLayer
    class ORCHESTRATOR,BASE_EXP,SHP_EXP,CSV_EXP,PDF_EXP,SVG_EXP,IMG_EXP,PROFILE_EXP,DRILL_EXP exportLayer
    class QGIS_CORE,QGIS_GUI,PYQT5 externalLayer
```

---

## 🧩 Visualizing Mermaid Diagrams in VS Code

You can preview Mermaid diagrams in VS Code with the **Mermaid Editor** extension (installed). Quick steps:

1. Open this file `docs/ARCHITECTURE.md`.
2. Place the cursor inside a ```mermaid``` block and open the command palette (Ctrl+Shift+P) → "Open Mermaid Editor" or "Preview Mermaid".
3. Alternatively, use the Markdown preview (Ctrl+Shift+V) if you have `Markdown Preview Mermaid Support` (already installed).

Quick Example (edit this block and save to see the preview):

```mermaid
graph LR
  A[User] --> B[SecInterpPlugin]
  B --> C[Generate Profile]
  C --> D[Export SVG/PNG]
```

---

(gui-layer---user-interface)=
## 🖥️ GUI Layer - User Interface

### 1. SecInterpDialog (main_dialog.py)

**Main Class**: `SecInterpDialog`
**Inherits from**: `SecInterpMainWindow`
**Lines of code**: ~350 (Unified logic handled by Managers)
**Responsibility**: Simplified main dialog that coordinates components via Managers

#### Key Components

```python
class SecInterpDialog(SecInterpMainWindow):
    """Dialog for the SecInterp QGIS plugin."""

    def __init__(self, iface=None, plugin_instance=None, parent=None):
        # Logic Managers
        self.signal_manager = DialogSignalManager(self)
        self.data_aggregator = DialogDataAggregator(self)

        # Operation Managers
        self.validator = DialogValidator(self)
        self.preview_manager = PreviewManager(self)
        self.export_manager = ExportManager(self)
        self.status_manager = DialogStatusManager(self)
        self.settings_manager = DialogSettingsManager(self)
        self.interpretation_manager = InterpretationManager(self)
        self.message_manager = MessageManager(self)

        # Widgets
        self.legend_widget = LegendWidget(self.preview_widget.canvas)
        self.pan_tool = QgsMapToolPan(self.preview_widget.canvas)
        self.measure_tool = ProfileMeasureTool(self.preview_widget.canvas)
```

#### Main Methods

| Method | Description | Location |
|--------|-------------|-----------|
| `_init_managers()` | Initializes dedicated managers | `main_dialog.py` |
| `get_selected_values()` | Facade for the DataAggregator | `main_dialog.py` |
| `get_all_values()` | Actual data aggregation from pages | `main_dialog_data.py` |
| `connect_all()` | Bulk signal connection | `main_dialog_signals.py` |
| `preview_profile_handler()` | Delegated to PreviewManager | `main_dialog.py` |
| `export_preview()` | Delegated to ExportManager | `main_dialog.py` |
| `update_button_state()` | Delegated to StatusManager | `main_dialog.py` |

#### Signals and Slots

```python
# Button connections
self.preview_widget.btn_preview.clicked.connect(self.preview_profile_handler)
self.preview_widget.btn_export.clicked.connect(self.export_preview)
self.preview_widget.btn_measure.toggled.connect(self.toggle_measure_tool)

# Checkbox connections
self.preview_widget.chk_topo.stateChanged.connect(self.update_preview_from_checkboxes)
self.preview_widget.chk_geol.stateChanged.connect(self.update_preview_from_checkboxes)
self.preview_widget.chk_struct.stateChanged.connect(self.update_preview_from_checkboxes)
self.preview_widget.chk_drillholes.stateChanged.connect(self.update_preview_from_checkboxes)

# Layer connections
self.page_dem.raster_combo.layerChanged.connect(self.update_button_state)
self.page_section.line_combo.layerChanged.connect(self.update_button_state)
```

---

### 2. PreviewManager (main_dialog_preview.py)

**Class**: `PreviewManager`
**Lines of code**: ~250
**Responsibility**: Manages preview generation and updates

#### Main Methods

```python
class PreviewManager:
    def generate_preview(self) -> Tuple[bool, str]:
        """Generates preview with validation and error handling."""

    def update_from_checkboxes(self):
        """Updates preview when visualization options change."""

    def _get_validated_inputs(self) -> Optional[Dict]:
        """Obtains and validates inputs from the dialog."""

    def _process_data(self, inputs: Dict) -> Tuple:
        """Processes data using the controller."""
```

---

### 3. PreviewRenderer (preview_renderer.py)

**Class**: `PreviewRenderer`
**Lines of code**: ~280
**Methods**: 20
**Responsibility**: Renders the preview canvas using native PyQGIS

#### Renderer Architecture

```mermaid
graph LR
    A[render] --> B[_create_topo_layer]
    A --> C[_create_geol_layer]
    A --> D[_create_struct_layer]
    A --> E[_create_drillhole_layers]
    A --> F[_create_axes_layer]
    A --> G[_create_axes_labels_layer]

    B --> H[_decimate_line_data]
    B --> I[_adaptive_sample]
    C --> H
    D --> J[_interpolate_elevation]

    H --> K[QgsVectorLayer]
    I --> K
    J --> K
```

#### LOD Optimization Methods

| Method | Purpose | Algorithm |
|--------|-----------|-----------|
| `_decimate_line_data()` | Line simplification | Douglas-Peucker |
| `_calculate_curvature()` | Local curvature calculation | Angle between segments |
| `_adaptive_sample()` | Adaptive sampling | Curvature-based |

#### Usage Example

```python
renderer = PreviewRenderer(canvas)

canvas, layers = renderer.render(
    topo_data=[(0, 100), (10, 105), ...],
    geol_data=[GeologySegment(...), ...],
    struct_data=[StructureMeasurement(...), ...],
    vert_exag=2.0,
    dip_line_length=50.0,
    max_points=1000,
    preserve_extent=False
)
```

---

### 4. ProfileMeasureTool (measure_tool.py)

**Class**: `ProfileMeasureTool`
**Inherits from**: `QgsMapTool`
**Responsibility**: Measurement tool with snapping

#### Features

- ✅ **Snapping to vertices** of visible layers
- ✅ **Distance calculation** (Euclidean)
- ✅ **Slope calculation** (slope in degrees)
- ✅ **Real-time visualization** with rubber band

#### Signals

```python
measurementChanged = pyqtSignal(float, float, float, float)  # dx, dy, dist, slope
measurementCleared = pyqtSignal()
```

---

(core-layer---business-logic)=
## ⚙️ Core Layer - Business Logic

### 1. ProfileController (controller.py)

**Class**: `ProfileController`
**Lines of code**: ~280
**Responsibility**: Orchestrates the data generation services

#### Architecture

```python
class ProfileController:
    def __init__(self):
        self.profile_service = ProfileService()
        self.geology_service = GeologyService()
        self.structure_service = StructureService()
        self.drillhole_service = DrillholeService()
        self.data_cache = DataCache()
```

#### Main Method

```python
def generate_profile_data(self, values: Dict[str, Any]) -> Tuple[List, Any, Any, Any, List[str]]:
    """Unified method to generate all profile components.

    Returns:
        tuple: (profile_data, geol_data, struct_data, drillhole_data, messages)
    """
    # 1. Topography
    profile_data = self.profile_service.generate_topographic_profile(...)

    # 2. Geology (if layer exists)
    if outcrop_layer:
        geol_data = self.geology_service.generate_geological_profile(...)

    # 3. Structures (if layer exists)
    if structural_layer:
        struct_data = self.structure_service.project_structures(...)

    # 4. Drillholes (if layer exists)
    if collar_layer:
        collars = self.drillhole_service.project_collars(...)
        drillhole_data = self.drillhole_service.process_intervals(...)

    return profile_data, geol_data, struct_data, drillhole_data, messages
```

---

### 2. GeologyService (geology_service.py)

**Class**: `GeologyService`
**Lines of code**: ~540
**Methods**: 8
**Responsibility**: Generates geological profiles by intersecting polygons

#### Processing Flow

```mermaid
sequenceDiagram
    participant Client
    participant GeoService as GeologyService
    participant Utils as Utils

    Client->>GeoService: generate_geological_profile()
    GeoService->>GeoService: _generate_master_profile_data()

    %% Optimized PyQGIS Intersection
    GeoService->>GeoService: QgsFeatureRequest.setFilterRect()

    loop For each candidate feature
        GeoService->>GeoService: QgsGeometry.intersection()
        GeoService->>GeoService: _process_intersection_geometry()
        GeoService->>Utils: interpolate_elevation()
        Utils-->>GeoService: elevation_points
    end

    GeoService-->>Client: List[GeologySegment]
```

#### Key Methods

| Method | Description |
|--------|-------------|
| `generate_geological_profile()` | Main method that orchestrates the process |
| `_generate_master_profile_data()` | Generates grid of points and elevations |
| `_perform_intersection()` | Executes QGIS intersection algorithm |
| `_process_intersection_feature()` | Processes each intersection feature |
| `_create_segment_from_geometry()` | Creates GeologySegment from geometry |

#### Return Type

```python
@dataclass
class GeologySegment:
    unit_name: str
    points: List[Tuple[float, float]]  # (distance, elevation)
    geometry: QgsGeometry
    attributes: Dict[str, Any]
```

---

### 3. StructureService (structure_service.py)

**Class**: `StructureService`
**Lines of code**: 216
**Methods**: 7
**Responsibility**: Projects structural measurements (dip/strike)

#### Projection Algorithm

```mermaid
graph TD
    A[Structural Measurement] --> B[Create Buffer]
    B --> C[Filter Structures]
    C --> D[For each structure]
    D --> E[Project point to line]
    E --> F[Interpolate elevation]
    F --> G[Calculate apparent dip]
    G --> H[StructureMeasurement]
```

#### Apparent Dip Calculation

The formula used is:

```
apparent_dip = arctan(tan(true_dip) × |cos(strike - section_azimuth)|)
```

Implemented in `utils.calculate_apparent_dip()`.

#### Return Type

```python
@dataclass
class StructureMeasurement:
    distance: float
    elevation: float
    apparent_dip: float
    original_dip: float
    original_strike: float
    attributes: Dict[str, Any]
```

---

### 4. DrillholeService (drillhole_service.py)

**Class**: `DrillholeService`
**Lines of code**: 319
**Methods**: 4
**Responsibility**: Processes and projects drillhole data

#### Processing Flow

```mermaid
graph TB
    A[Collar Layer] --> B[project_collars]
    C[Survey Layer] --> D[process_intervals]
    E[Interval Layer] --> D

    B --> F[Collar Points]
    F --> D

    D --> G[Desurvey Drillhole]
    G --> H[Project to Section]
    H --> I[Create Segments]
    I --> J[Drillhole Data]
```

---

(validation-architecture)=
## 🛡️ 3-Level Validation Architecture

The project implements a robust, tiered validation system to ensure data integrity across all layers without external dependencies like Pydantic.

### Level 1: Type & Range Validation (Dataclass Layer)
- **Location**: `core/models/settings_model.py` using `core/validation/validators.py`.
- **Purpose**: Immediate feedback during object instantiation.
- **Mechanism**: `__post_init__` hooks use reusable validators (e.g., `validate_and_clamp`).
- **Example**: Ensuring vertical exaggeration is within `(0.1, 10.0)`.

### Level 2: Business Field Validation (Form Layer)
- **Location**: `core/validation/field_validator.py`.
- **Purpose**: Validates individual fields based on plugin-specific business rules.
- **Mechanism**: Checks for required fields, valid data types in QGIS layers, and mandatory combinations.

### Level 3: Domain & Cross-Layer Validation (Project Layer)
- **Location**: `core/validation/project_validator.py`.
- **Purpose**: Validates the relationship between different layers and the project state.
- **Mechanism**: Checks if the section line intersects the DEM extent, or if drillholes fall within the buffer zone.

---

(drillhole-service)=

#### Main Methods

**1. project_collars()**

Projects collar points to the section line.

```python
def project_collars(
    self,
    collar_layer: QgsVectorLayer,
    line_geom: QgsGeometry,
    line_start: QgsPointXY,
    distance_area: QgsDistanceArea,
    buffer_width: float,
    collar_id_field: str,
    use_geometry: bool,
    collar_x_field: str,
    collar_y_field: str,
    collar_z_field: str,
    collar_depth_field: str,
    dem_layer: Optional[QgsRasterLayer],
) -> List[Dict]:
    """Returns list of dictionaries with collar_id, distance, elevation, depth."""
```

**2. process_intervals()**

Processes intervals and generates 2D traces.

```python
def process_intervals(
    self,
    collar_points: List[Dict],
    collar_layer: QgsVectorLayer,
    survey_layer: QgsVectorLayer,
    interval_layer: QgsVectorLayer,
    # ... more parameters
) -> Tuple[List[GeologySegment], List[Dict]]:
    """Returns (geology_segments, drillhole_traces)."""
```

---

### 5. Utilities (core/utils/)

#### geometry.py (345 lines)

**Geometric Operations with QGIS Core API**

| Function | Description |
|---------|-------------|
| `create_memory_layer()` | Creates temporary in-memory layer |
| `extract_all_vertices()` | Extracts geometry vertices (multipart-safe) |
| `get_line_vertices()` | Extracts line vertices |
| `run_processing_algorithm()` | Runs QGIS algorithm with error handling |
| `create_buffer_geometry()` | Creates buffer using `native:buffer` |
| `filter_features_by_buffer()` | Filters features with spatial index |
| `densify_line_by_interval()` | Densifies line with `native:densifygeometriesgivenaninterval` |

#### drillhole.py (7,297 lines)

**Drillhole Processing**

| Function | Description |
|---------|-------------|
| `desurvey_drillhole()` | Calculates 3D trajectory from survey |
| `project_drillhole_to_section()` | Projects 3D trace to 2D plane |
| `interpolate_intervals()` | Interpolates intervals on trace |

#### sampling.py (3,783 lines)

**Sampling and Interpolation**

| Function | Description |
|---------|-------------|
| `interpolate_elevation()` | Interpolates elevation on grid |
| `sample_raster_along_line()` | Samples raster along a line |

---

### 6. DataCache (data_cache.py)

**Class**: `DataCache`
**Lines of code**: 7,883
**Responsibility**: Cache of processed data

#### Cache Strategy

```python
class DataCache:
    def get_cache_key(self, inputs: Dict) -> str:
        """Generates a unique key based on relevant inputs."""
        # Considers: layers, bands, buffer, vertical exaggeration

    def get(self, key: str) -> Optional[Dict]:
        """Retrieves data from cache."""

    def set(self, key: str, data: Dict) -> None:
        """Stores data in cache."""

    def clear(self) -> None:
        """Clears the entire cache."""
```

---

(exporters-layer---data-export)=
## 📤 Exporters Layer - Data Export

### 1. DataExportOrchestrator (orchestrator.py)

**Class**: `DataExportOrchestrator`
**Lines of code**: 148
**Responsibility**: Coordinates exports to multiple formats

#### Main Method

```python
def export_data(
    self,
    output_folder: Path,
    values: Dict[str, Any],
    profile_data: List[Tuple],
    geol_data: Optional[List[Any]],
    struct_data: Optional[List[Any]],
    drillhole_data: Optional[List[Any]] = None
) -> List[str]:
    """Exports generated data to CSV and Shapefile using lazy imports."""

    # Lazy import of exporters
    from sec_interp.exporters import (
        AxesShpExporter,
        CSVExporter,
        GeologyShpExporter,
        ProfileLineShpExporter,
        StructureShpExporter,
        DrillholeTraceShpExporter,
        DrillholeIntervalShpExporter,
    )

    # Export topography
    csv_exporter.export(output_folder / "topo_profile.csv", ...)
    ProfileLineShpExporter({}).export(output_folder / "profile_line.shp", ...)

    # Export geology
    if geol_data:
        csv_exporter.export(output_folder / "geol_profile.csv", ...)
        GeologyShpExporter({}).export(output_folder / "geol_profile.shp", ...)

    # Export structures
    if struct_data:
        csv_exporter.export(output_folder / "structural_profile.csv", ...)
        StructureShpExporter({}).export(output_folder / "structural_profile.shp", ...)

    # Export drillholes
    if drillhole_data:
        DrillholeTraceShpExporter({}).export(output_folder / "drillhole_traces.shp", ...)
        DrillholeIntervalShpExporter({}).export(output_folder / "drillhole_intervals.shp", ...)

    return result_msg
```

---

### 2. Exporter Hierarchy

```mermaid
classDiagram
    class BaseExporter {
        <<abstract>>
        +export(path, data)
    }

    class CSVExporter {
        +export(path, data)
    }

    class ShapefileExporter {
        +export(path, data)
    }

    class ImageExporter {
        +export(path, map_settings)
    }

    class PDFExporter {
        +export(path, map_settings)
    }

    class SVGExporter {
        +export(path, map_settings)
    }

    BaseExporter <|-- CSVExporter
    BaseExporter <|-- ShapefileExporter
    BaseExporter <|-- ImageExporter
    BaseExporter <|-- PDFExporter
    BaseExporter <|-- SVGExporter

    ShapefileExporter <|-- ProfileLineShpExporter
    ShapefileExporter <|-- GeologyShpExporter
    ShapefileExporter <|-- StructureShpExporter
    ShapefileExporter <|-- AxesShpExporter
    ShapefileExporter <|-- DrillholeTraceShpExporter
    ShapefileExporter <|-- DrillholeIntervalShpExporter
```

---

(main-data-flows)=
## 🔄 Main Data Flows

### Flow 1: Preview Generation

```mermaid
sequenceDiagram
    participant User
    participant Dialog as SecInterpDialog
    participant PreviewMgr as PreviewManager
    participant Controller
    participant Services
    participant Renderer
    participant Canvas

    User->>Dialog: Click "Preview Profile"
    Dialog->>PreviewMgr: generate_preview()

    PreviewMgr->>PreviewMgr: _get_validated_inputs()
    PreviewMgr->>Controller: generate_profile_data(inputs)

    par Parallel Processing
        Controller->>Services: ProfileService.generate_topographic_profile()
        Services-->>Controller: profile_data

        Controller->>Services: GeologyService.generate_geological_profile()
        Services-->>Controller: geol_data

        Controller->>Services: StructureService.project_structures()
        Services-->>Controller: struct_data

        Controller->>Services: DrillholeService.project_collars()
        Services->>Services: DrillholeService.process_intervals()
        Services-->>Controller: drillhole_data
    end

    Controller-->>PreviewMgr: (profile, geol, struct, drill, msgs)

    PreviewMgr->>Renderer: render(profile, geol, struct, drill, vert_exag, ...)
    Renderer->>Renderer: _create_topo_layer()
    Renderer->>Renderer: _create_geol_layer()
    Renderer->>Renderer: _create_struct_layer()
    Renderer->>Renderer: _create_drillhole_layers()
    Renderer->>Renderer: _create_axes_layer()

    Renderer->>Canvas: setLayers(layers)
    Renderer->>Canvas: zoomToFullExtent()
    Renderer-->>PreviewMgr: (canvas, layers)

    PreviewMgr-->>Dialog: success
    Dialog-->>User: Display Preview
```

---

### Flow 2: Data Export

```mermaid
sequenceDiagram
    participant User
    participant Dialog
    participant ExportMgr as ExportManager
    participant Controller
    participant Orchestrator
    participant Exporters

    User->>Dialog: Click "Save"
    Dialog->>ExportMgr: export_data()

    ExportMgr->>Controller: generate_profile_data(inputs)
    Controller-->>ExportMgr: (profile, geol, struct, drill, msgs)

    ExportMgr->>Orchestrator: export_data(folder, values, data...)

    Orchestrator->>Exporters: CSVExporter.export("topo_profile.csv")
    Exporters-->>Orchestrator: success

    Orchestrator->>Exporters: ProfileLineShpExporter.export("profile_line.shp")
    Exporters-->>Orchestrator: success

    Orchestrator->>Exporters: GeologyShpExporter.export("geol_profile.shp")
    Exporters-->>Orchestrator: success

    Orchestrator->>Exporters: StructureShpExporter.export("structural_profile.shp")
    Exporters-->>Orchestrator: success

    Orchestrator->>Exporters: DrillholeTraceShpExporter.export("drillhole_traces.shp")
    Exporters-->>Orchestrator: success

    Orchestrator-->>ExportMgr: result_messages
    ExportMgr-->>Dialog: success
    Dialog-->>User: "All files saved to: {folder}"
```

---

### Flow 3: Parallel Geological Processing

```mermaid
sequenceDiagram
    participant Main as Main Thread
    participant GeoService as GeologyService
    participant ParallelGeo as ParallelGeologyService
    participant Worker as GeologyProcessingThread

    Main->>GeoService: generate_geological_profile()
    GeoService->>ParallelGeo: process_async(line, raster, outcrop, field, band)

    ParallelGeo->>Worker: start()
    Note over Worker: QThread Worker

    Worker->>Worker: run()
    Worker->>Worker: _generate_master_profile_data()
    Worker->>Worker: _perform_intersection()

    loop For each feature
        Worker->>Worker: _process_intersection_feature()
    end

    Worker->>ParallelGeo: finished.emit(results)
    ParallelGeo->>GeoService: return results
    GeoService-->>Main: List[GeologySegment]
```

---

(design-patterns)=
## 🎨 Design Patterns

### 1. MVC (Model-View-Controller)

```
Model:      Services + Algorithms + Types
View:       GUI Widgets + Renderer
Controller: ProfileController
```

### 2. Strategy Pattern

Different exporters implement the same `BaseExporter` interface:

```python
class BaseExporter(ABC):
    @abstractmethod
    def export(self, path: Path, data: Dict) -> bool:
        pass

class CSVExporter(BaseExporter):
    def export(self, path: Path, data: Dict) -> bool:
        # CSV Specific implementation

class ShapefileExporter(BaseExporter):
    def export(self, path: Path, data: Dict) -> bool:
        # Shapefile Specific implementation
```

### 3. Observer Pattern

PyQt5 Signals/Slots for communication between components:

```python
# Signal
measurementChanged = pyqtSignal(float, float, float, float)

# Slot
def update_measurement_display(self, dx, dy, dist, slope):
    msg = f"Distance: {dist:.2f} m..."
    self.results_text.setHtml(msg)

# Connection
self.measure_tool.measurementChanged.connect(self.update_measurement_display)
```

### 4. Facade Pattern

`ProfileController` acts as a facade for the services:

```python
class ProfileController:
    def generate_profile_data(self, values):
        # Orchestrates multiple services
        profile = self.profile_service.generate_topographic_profile(...)
        geol = self.geology_service.generate_geological_profile(...)
        struct = self.structure_service.project_structures(...)
        drill = self.drillhole_service.process_intervals(...)
        return profile, geol, struct, drill, msgs
```

### 5. Factory Pattern

Exporter Factory:

```python
def get_exporter(ext: str, settings: Dict) -> BaseExporter:
    exporters = {
        '.png': ImageExporter,
        '.jpg': ImageExporter,
        '.pdf': PDFExporter,
        '.svg': SVGExporter,
    }
    exporter_class = exporters.get(ext)
    return exporter_class(settings)
```

### 6. Singleton Pattern (Implicit)

`DataCache` is instantiated once in the controller.

### 7. Template Method Pattern

`BaseExporter` defines the template, subclasses implement details:

```python
class BaseExporter(ABC):
    def export(self, path, data):
        self._validate(data)
        self._prepare(data)
        self._write(path, data)
        self._finalize()

    @abstractmethod
    def _write(self, path, data):
        pass
```

---

(external-dependencies)=
## 🌐 External Dependencies

### QGIS Core API

```python
from qgis.core import (
    QgsVectorLayer,        # Vector layers
    QgsRasterLayer,        # Raster layers
    QgsGeometry,           # Geometric operations
    QgsProcessing,         # Processing algorithms
    QgsSpatialIndex,       # Spatial indices
    QgsCoordinateTransform,# Coordinate transformations
    QgsDistanceArea,       # Distance calculations
    QgsProject,            # QGIS Project
    QgsFeature,            # Features
    QgsField,              # Fields
    QgsWkbTypes,           # Geometry types
)
```

**Main use**: All geometric operations, spatial processing, and layer management.

### QGIS GUI API

```python
from qgis.gui import (
    QgsMapCanvas,          # Map canvas
    QgsMapTool,            # Map tools
    QgsMapLayer,           # Map layers
    QgsMapLayerComboBox,   # Layer combo boxes
    QgsFileWidget,         # File widget
)
```

**Main use**: User interface, interactive tools, specialized widgets.

### PyQt5

```python
from PyQt5.QtCore import (
    Qt,                    # Qt constants
    QVariant,              # Data types
    pyqtSignal,            # Signals
    pyqtSlot,              # Slots
)

from PyQt5.QtWidgets import (
    QDialog,               # Dialogs
    QWidget,               # Base widgets
    QPushButton,           # Buttons
    QCheckBox,             # Checkboxes
    QSpinBox,              # Spin boxes
    QComboBox,             # Combo boxes
    QLabel,                # Labels
    QGroupBox,             # Group boxes
    QVBoxLayout,           # Vertical layouts
    QHBoxLayout,           # Horizontal layouts
)

from PyQt5.QtGui import (
    QColor,                # Colors
    QFont,                 # Fonts
    QPen,                  # Drawing pens
    QBrush,                # Fill brushes
)
```

**Main use**: Complete UI framework, signals/slots, layouts, widgets.

---

(performance-optimizations)=
## ⚡ Performance Optimizations

### 1. Adaptive Level of Detail (LOD)

**Implemented in**: `PreviewRenderer`

```python
def _decimate_line_data(self, data, tolerance=None, max_points=1000):
    """Simplifies lines using Douglas-Peucker."""
    if len(data) <= max_points:
        return data

    # Calculate automatic tolerance
    if tolerance is None:
        x_range = max(p[0] for p in data) - min(p[0] for p in data)
        tolerance = x_range / (max_points * 2)

    # Apply Douglas-Peucker
    simplified = self._douglas_peucker(data, tolerance)
    return simplified
```

**Benefit**: Reduces 10,000+ points to ~1,000 without significant visual loss.

### 2. Curvature-based Adaptive Sampling

```python
def _adaptive_sample(self, data, min_tolerance=0.1, max_tolerance=10.0, max_points=1000):
    """Samples more densely in high-curvature areas."""
    curvatures = self._calculate_curvature(data)

    # Normalize curvatures
    max_curv = max(curvatures)
    normalized = [c / max_curv for c in curvatures]

    # Tolerance inversely proportional to curvature
    tolerances = [
        max_tolerance - (max_tolerance - min_tolerance) * n
        for n in normalized
    ]

    # Apply Douglas-Peucker with variable tolerance
    return self._douglas_peucker_adaptive(data, tolerances)
```

**Benefit**: Preserves important details (tight curves) while simplifying straight areas.

### 3. Parallel Geological Processing

**Implemented in**: `ParallelGeologyService`

```python
class ParallelGeologyService(QObject):
    finished = pyqtSignal(list)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)

    def process_async(self, line_lyr, raster_lyr, outcrop_lyr, field, band):
        """Processes geology in a separate thread."""
        self.worker = GeologyProcessingThread(...)
        self.worker.finished.connect(self.finished.emit)
        self.worker.start()
```

**Benefit**: UI remains responsive during heavy processing.

### 4. Processed Data Cache

**Implemented in**: `DataCache`

```python
def get_cache_key(self, inputs: Dict) -> str:
    """Generates a unique key based on relevant inputs."""
    key_parts = [
        inputs.get("raster_layer"),
        inputs.get("selected_band"),
        inputs.get("crossline_layer"),
        inputs.get("buffer_distance"),
        # DOES NOT include: vertexag, dip_scale_factor (only for display)
    ]
    return hashlib.md5(str(key_parts).encode()).hexdigest()
```

**Benefit**: Avoids re-processing when only display parameters change.

### 5. Spatial Index for Filtering

**Implemented in**: `geometry.filter_features_by_buffer()`

```python
def filter_features_by_buffer(features_layer, buffer_geometry):
    """Filters features using a spatial index."""
    # 1. Build spatial index
    index = QgsSpatialIndex(features_layer.getFeatures())

    # 2. Fast search by bounding box
    candidate_ids = index.intersects(buffer_geometry.boundingBox())

    # 3. Precise filtering of candidates only
    filtered = []
    for fid in candidate_ids:
        feature = features_layer.getFeature(fid)
        if feature.geometry().intersects(buffer_geometry):
            filtered.append(feature)

    return filtered
```

**Benefit**: O(log n) instead of O(n) for spatial filtering.

---

(project-metrics)=
## 📊 Project Metrics

### Code Statistics

| Metric | Value |
|---------|-------|
| **Python Modules** | ~60 files |
| **Total Lines of Code** | ~15,000 LOC |
| **Core Lines of Code** | ~8,000 LOC |
| **GUI Lines of Code** | ~5,000 LOC |
| **Exporters Lines of Code** | ~2,000 LOC |
| **Main Classes** | 25+ |
| **Functions/Methods** | 200+ |

### Distribution by Layer

```mermaid
pie title Code Distribution by Layer
    "Core (53%)" : 8000
    "GUI (33%)" : 5000
    "Exporters (13%)" : 2000
```

### Complexity by Module

| Module | Lines | Classes | Methods | Complexity |
|--------|--------|--------|---------|-------------|
| `sec_interp_plugin.py`| ~600 | 1 | 15 | Medium |
| `main_dialog.py` | ~340 | 1 | 12 | Low/Medium |
| `main_dialog_signals.py`| ~200 | 1 | 10 | Medium |
| `main_dialog_data.py` | ~150 | 1 | 8 | Medium |
| `preview_renderer.py` | 1,190 | 1 | 20 | High |
| `controller.py` | 192 | 1 | 4 | Low |
| `core/validation/` | ~800 | 0 | 25 | Medium |
| `geology_service.py` | 244 | 1 | 8 | Medium |
| `structure_service.py` | 216 | 1 | 7 | Medium |
| `drillhole_service.py` | 319 | 1 | 4 | Medium |
| `geometry.py` | 345 | 0 | 10 | Medium |
| `orchestrator.py` | 148 | 1 | 1 | Low |

### Dependencies

```mermaid
graph LR
    A[SecInterp Plugin] --> B[QGIS Core API]
    A --> C[QGIS GUI API]
    A --> D[PyQt5]

    B --> E[Python 3.x]
    C --> E
    D --> E

    style A fill:#ff6b6b
    style B fill:#4ecdc4
    style C fill:#4ecdc4
    style D fill:#95e1d3
    style E fill:#ffd93d
```

### Feature Coverage

| Feature | Status | Coverage |
|---------------|--------|-----------|
| Topographic Profile | ✅ Complete | 100% |
| Geological Projection | ✅ Complete | 100% |
| Structural Projection | ✅ Complete | 100% |
| Drillhole Projection | ✅ Complete | 100% |
| Interactive Preview | ✅ Complete | 100% |
| Measurement Tools | ✅ Complete | 100% |
| CSV Export | ✅ Complete | 100% |
| Shapefile Export | ✅ Complete | 100% |
| PDF Export | ✅ Complete | 100% |
| SVG Export | ✅ Complete | 100% |
| PNG/JPG Export | ✅ Complete | 100% |
| Adaptive LOD | ✅ Complete | 100% |
| Parallel Processing | ✅ Complete | 100% |
| Data Cache | ✅ Complete | 100% |

---

## 🔗 References

- [Source Code](file:///home/jmbernales/qgispluginsdev/sec_interp)
- [Main README](file:///home/jmbernales/qgispluginsdev/sec_interp/README.md)
- [User Guide](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/USER_GUIDE.md)
- [Architecture Graph](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/sec_interp_architecture_graph.md)
- [QGIS API Documentation](https://qgis.org/pyqgis/master/)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)

---

## 🎨 Design Principles

The SecInterp plugin has been designed following robust software engineering principles to ensure quality and maintainability.

### SOLID Principles

- **SRP (Single Responsibility Principle)**: Each service (Profile, Geology, Structure, Drillhole) has a single, clear responsibility.
- **OCP (Open/Closed Principle)**: Exporters are easily extensible through the abstract base class without modifying the core logic.
- **LSP (Liskov Substitution Principle)**: All concrete exporters can subtitute the `BaseExporter` class.
- **ISP (Interface Segregation Principle)**: Service interfaces are focused on their specific domain.
- **DIP (Dependency Inversion Principle)**: The controller depends on abstractions and injected services, not on heavy concrete implementations.

### Other Patterns and Principles
- **DRY (Don't Repeat Yourself)**: Intensive use of `utils` modules to centralize mathematical and spatial calculations.
- **Separation of Concerns**: Clear distinction between the GUI Layer (Managers), Core Layer (Services), and Data Layer (DataCache).

---

## 🚀 Extensibility

Quick guide for developers wishing to expand the plugin.

### Adding a New Service
1. Create the new file in `core/services/` (e.g., `seismic_service.py`).
2. Implement the service logic following the pattern of other services.
3. Register the service in `controller.py` within the `ProfileController` constructor.
4. Add the orchestrator method in the controller and connect it to `PreviewManager`.

### Adding a New Export Format
1. Create a class in `exporters/` that inherits from `BaseExporter`.
2. Implement the required `export()` method.
3. Register the new exporter in the factory in `orchestrator.py` or the specific export modules.

---

## 📦 Deployment

The plugin uses a `Makefile`-based system to facilitate local deployment and packaging.

- **Main command**: `make deploy` (Copies files to the QGIS plugins directory).
- **Process**:
  - Temporary files (`.pyc`, etc.) are cleaned.
  - Resources and translations are copied.
  - Synchronized with the local QGIS directory for immediate testing.

---

## 📝 Final Notes

This document provides a detailed view of the SecInterp plugin architecture. For development information, see [README_DEV.md](file:///home/jmbernales/qgispluginsdev/sec_interp/README_DEV.md).

**Last update**: 2026-01-18
**Plugin Version**: 2.7.0
**Author**: Juan M. Bernales
