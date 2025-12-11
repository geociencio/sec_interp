# SecInterp Plugin Architecture

## Overview

SecInterp is a QGIS plugin for generating geological cross-section profiles. The architecture has been refactored to follow modular design principles with clear separation of concerns.

---

## Directory Structure

```
sec_interp/
├── __init__.py                 # Plugin entry point
├── metadata.txt                # Plugin metadata
├── icon.png                    # Plugin icon
├── logger_config.py            # Logging configuration
│
├── core/                       # Main business logic
│   ├── __init__.py
│   ├── algorithms.py           # Main orchestrator (778 lines)
│   ├── data_cache.py           # Data cache for performance
│   ├── validation.py           # Input validation
│   │
│   ├── services/               # Specialized services
│   │   ├── __init__.py
│   │   ├── profile_service.py      # Topographic profile generation
│   │   ├── geology_service.py      # Geological processing
│   │   └── structure_service.py    # Structure projection
│   │
│   └── utils/                  # Utilities organized by function
│       ├── __init__.py
│       ├── geometry.py         # Spatial geometry operations
│       ├── spatial.py          # Distance and azimuth calculations
│       ├── sampling.py         # Elevation sampling
│       ├── parsing.py          # Structural data parsing
│       ├── rendering.py        # Visualization utilities
│       ├── io.py               # I/O and user messages
│       └── geology.py          # Geological calculations
│
├── gui/                        # User interface
│   ├── __init__.py
│   ├── main_dialog.py          # Main dialog
│   ├── preview_renderer.py     # Preview rendering
│   ├── legend_widget.py        # Legend widget
│   └── ui/                     # Generated UI files
│
├── exporters/                  # Data exporters
│   ├── __init__.py
│   ├── base_exporter.py        # Abstract base class
│   ├── csv_exporter.py         # CSV export
│   ├── shp_exporter.py         # Shapefile export
│   ├── image_exporter.py       # Image export
│   ├── svg_exporter.py         # SVG export
│   └── pdf_exporter.py         # PDF export
│
├── resources/                  # Plugin resources
├── i18n/                       # Translations
├── docs/                       # Documentation
├── tests/                      # Unit tests
└── scripts/                    # Utility scripts
```

---

## Main Components

### 1. Core - Business Logic

#### `algorithms.py` - Main Orchestrator
**Responsibility:** Coordinate the plugin's main workflow

**Main Class:** `SecInterp`
- Initializes services and components
- Handles UI events
- Coordinates data processing
- Manages result export

**Dependencies:**
- `ProfileService` - Profile generation
- `GeologyService` - Geological processing
- `StructureService` - Structure projection
- `DataCache` - Data caching
- `PreviewRenderer` - Preview rendering

#### `data_cache.py` - Data Cache
**Responsibility:** Cache processed data to improve performance

**Functionality:**
- Topographic profile caching
- Geological data caching
- Structural data caching
- Cache invalidation on input changes

---

### 2. Services - Specialized Services

#### `ProfileService` - Topographic Profiles
**Responsibility:** Generate elevation profiles along section lines

**Main Method:**
```python
generate_topographic_profile(
    line_layer: QgsVectorLayer,
    raster_layer: QgsRasterLayer,
    band_number: int
) -> list[tuple[float, float]]
```

**Functionality:**
- Line densification at raster resolution
- Elevation sampling at densified points
- Distance calculation along line

#### `GeologyService` - Geological Processing
**Responsibility:** Calculate intersections between section line and outcrop polygons

**Main Method:**
```python
generate_geological_profile(
    line_layer: QgsVectorLayer,
    raster_layer: QgsRasterLayer,
    outcrop_layer: QgsVectorLayer,
    outcrop_name_field: str,
    band_number: int
) -> list[tuple[float, float, str]]
```

**Functionality:**
- Line-polygon intersection
- Elevation sampling at intersection points
- Geological formation name association

#### `StructureService` - Structure Projection
**Responsibility:** Project structural measurements (strike/dip) onto section plane

**Main Method:**
```python
project_structures(
    line_layer: QgsVectorLayer,
    structural_layer: QgsVectorLayer,
    buffer_distance: float,
    line_azimuth: float,
    dip_field: str,
    strike_field: str
) -> list[tuple[float, float, float, float]]
```

**Functionality:**
- Spatial filtering with buffer
- Structural measurement parsing
- Apparent dip calculation
- Section plane projection

---

### 3. Utils - Organized Utilities

#### `geometry.py` - Geometric Operations
**Helper Functions:**
- `create_memory_layer()` - Create temporary layers
- `get_line_vertices()` - Extract line vertices
- `run_processing_algorithm()` - Execute QGIS algorithms

**Main Functions:**
- `create_buffer_geometry()` - Create buffers using native algorithms
- `filter_features_by_buffer()` - Spatial filtering with R-tree index
- `densify_line_by_interval()` - Densify lines at regular intervals

#### `spatial.py` - Spatial Calculations
- `calculate_line_azimuth()` - Calculate line azimuth
- `get_line_start_point()` - Get start point
- `create_distance_area()` - Create distance measurement object

#### `sampling.py` - Elevation Sampling
- `sample_elevation_along_line()` - Sample elevation along line
- `prepare_profile_context()` - Prepare profile context
- `interpolate_elevation()` - Interpolate elevation at point

#### `parsing.py` - Structural Data Parsing
- `parse_strike()` - Parse strike (numeric or field notation)
- `parse_dip()` - Parse dip (numeric or field notation)
- `cardinal_to_azimuth()` - Convert cardinal directions to azimuth

#### `rendering.py` - Visualization Utilities
- `calculate_bounds()` - Calculate data bounds
- `create_coordinate_transform()` - Create coordinate transformation
- `calculate_interval()` - Calculate axis intervals

#### `io.py` - I/O and Messages
- `create_shapefile_writer()` - Create shapefile writer
- `show_user_message()` - Show user messages with logging

#### `geology.py` - Geological Calculations
- `calculate_apparent_dip()` - Calculate apparent dip

---

### 4. GUI - User Interface

#### `main_dialog.py` - Main Dialog
**Responsibility:** Main user interface

**Functionality:**
- Layer and parameter selection
- Input validation
- Preview generation
- Result export

#### `preview_renderer.py` - Preview Rendering
**Responsibility:** Render interactive previews

**Functionality:**
- Topographic profile rendering
- Geological data rendering
- Projected structure rendering
- Vertical exaggeration handling

---

### 5. Exporters - Data Exporters

#### Exporter Architecture
**Pattern:** Factory + Strategy

**Base Class:** `BaseExporter` (abstract)
- Defines common interface for all exporters
- Consistent error handling

**Concrete Exporters:**
- `CSVExporter` - CSV export
- `ShapefileExporter` - Shapefile export
- `ImageExporter` - PNG/JPG export
- `SVGExporter` - SVG export
- `PDFExporter` - PDF export

**Factory:** `get_exporter(extension, settings)`
- Selects appropriate exporter by extension
- Configures exporter with settings

---

## Data Flow

### Profile Generation

```
User selects layers → Input validation
                          ↓
            SecInterp.process_profile_data()
                          ↓
            ┌─────────────┴─────────────┐
            ↓                           ↓
    ProfileService              GeologyService
    (topography)                (geology)
            ↓                           ↓
            └─────────────┬─────────────┘
                          ↓
                StructureService
                (structures)
                          ↓
                PreviewRenderer
                (visualization)
```

### Data Export

```
User requests export → Path validation
                            ↓
                    Data generation
                    (ProfileService, etc.)
                            ↓
                    Factory selects
                    appropriate exporter
                            ↓
                    Exporter writes
                    output files
```

---

## Design Patterns

### 1. Service Layer Pattern
**Location:** `core/services/`

**Purpose:** Separate business logic into specialized services

**Benefits:**
- Separation of concerns
- Facilitates testing
- More maintainable code

### 2. Factory Pattern
**Location:** `exporters/__init__.py`

**Purpose:** Create appropriate exporters by file type

**Benefits:**
- Extensibility
- Decoupling
- Centralized configuration

### 3. Strategy Pattern
**Location:** `exporters/`

**Purpose:** Interchangeable export strategies

**Benefits:**
- Flexibility
- Easy to add new formats
- Clean code

### 4. Helper Functions Pattern
**Location:** `core/utils/geometry.py`

**Purpose:** Reusable functions to eliminate duplication

**Benefits:**
- DRY (Don't Repeat Yourself)
- Consistency
- Easier maintenance

---

## Design Principles

### SOLID Principles

#### Single Responsibility Principle (SRP)
- Each service has a single responsibility
- Each utils module has a specific function

#### Open/Closed Principle (OCP)
- Exporters extensible without modifying existing code
- Services can be extended through inheritance

#### Dependency Inversion Principle (DIP)
- `SecInterp` depends on abstractions (services)
- Services injected in constructor

### DRY (Don't Repeat Yourself)
- Helper functions eliminate code duplication
- Shared utilities in utils modules

### Separation of Concerns
- GUI separated from business logic
- Services separated by domain
- Utils organized by function

---

## External Dependencies

### QGIS API
- `qgis.core` - QGIS core classes
- `qgis.PyQt` - Qt bindings
- `qgis.processing` - Processing algorithms

### Python Standard Library
- `pathlib` - Path handling
- `math` - Mathematical calculations
- `re` - Regular expressions
- `tempfile` - Temporary files

---

## Testing

### Test Structure
```
tests/
├── test_services/
│   ├── test_profile_service.py
│   ├── test_geology_service.py
│   └── test_structure_service.py
├── test_utils/
│   ├── test_geometry.py
│   ├── test_spatial.py
│   └── test_parsing.py
└── test_exporters/
    └── test_exporters.py
```

### Testing Strategy
- **Unit Tests:** Individual services and utilities
- **Integration Tests:** Complete processing flow
- **UI Tests:** Interface validation (manual)

---

## Performance

### Implemented Optimizations

#### 1. Data Caching
- Caches the results of expensive data generation (topography, geology, structures).
- Avoids re-processing data when only visualization parameters (e.g., colors, vertical exaggeration) change.
- The cache is invalidated when core input parameters (e.g., layers, buffer distance) are modified.

#### 2. Spatial Indexing
- Uses `QgsSpatialIndex` for efficient spatial filtering of structural data points within the user-defined buffer.
- This avoids a linear scan of all points and significantly speeds up processing for large structural datasets.

#### 3. Native Algorithms
- Leverages optimized, C++ based QGIS native processing algorithms (e.g., `native:intersection`, `native:buffer`) where possible for better performance and stability compared to manual Python implementations.

#### 4. Level-of-Detail (LOD) System
A multi-phase LOD system is implemented in the `PreviewRenderer` to ensure the UI remains responsive, even with very large datasets.
- **Phase 1: Basic Decimation**: Reduces the number of vertices for preview rendering using the Douglas-Peucker algorithm (`QgsGeometry.simplify()`). The level of detail is controlled by a "Max Points" setting in the UI.
- **Phase 2: Adaptive Sampling**: A more intelligent simplification that uses the line's curvature to adjust the simplification tolerance. This preserves more detail in complex (high-curvature) areas of the profile. This is enabled via the "Adaptive" checkbox.
- **Phase 3: Zoom-Based LOD**: When "Auto" mode is enabled, the system automatically adjusts the level of detail based on the current zoom level of the preview canvas. Zooming in increases detail, while zooming out reduces it, ensuring optimal performance at any scale.

---

## Deployment

### Deployment Script
**Location:** `scripts/deploy.sh`

**Functionality:**
- Copies files to QGIS plugins directory
- Creates backup of previous installation
- Compiles translations
- Copies complete directory structure

### Command
```bash
make deploy
```

---

## Extensibility

### Adding a New Service

1. Create file in `core/services/`
2. Implement service logic
3. Add to `core/services/__init__.py`
4. Initialize in `SecInterp.__init__()`
5. Use in `SecInterp._process_profile_data()`

### Adding a New Exporter

1. Create class inheriting from `BaseExporter`
2. Implement `export()` method
3. Add to factory in `exporters/__init__.py`
4. Update extension mapping

### Adding a New Utility

1. Determine appropriate module in `core/utils/`
2. Implement function with docstring
3. Add to exports in `core/utils/__init__.py`
4. Use in code where needed

---

## Maintenance

### Code Guidelines
- Follow PEP 8 for Python style
- Use type hints where possible
- Document with Google-style docstrings
- Commits following Conventional Commits

### Future Refactorings
- [ ] Complete unit tests
- [ ] API documentation
- [ ] Additional performance optimization
- [ ] Complete internationalization

---

## Conclusion

The refactored SecInterp plugin architecture follows solid design principles, is well-organized, and is easy to maintain and extend. The separation into services, modular utilities, and helper functions provides a solid foundation for future development.

**Version:** Post-refactoring 2025-12-07  
**Status:** ✅ Stable and in production
