# SecInterp - Complete Technical Documentation

**QGIS Plugin for Geological Data Extraction**  
**Version**: 0.3  
**Author**: Juan M. Bernales  
**Date**: 2025-12-07

---

## 📑 Table of Contents

1. [Introduction](#introduction)
2. [General Architecture](#general-architecture)
3. [Entry Point](#entry-point)
4. [Main Modules](#main-modules)
5. [Services](#services)
6. [Utilities](#utilities)
7. [Mathematical Formulas](#mathematical-formulas)
8. [Data Flow](#data-flow)
9. [Exporters](#exporters)
10. [Graphical Interface](#graphical-interface)

---

## 1. Introduction

### 1.1 Purpose

SecInterp is a QGIS plugin designed to extract and visualize geological data along cross-sections. It allows:

- Generate topographic profiles from a DEM
- Extract geological contacts from outcrop layers
- Project structural measurements (strike/dip)
- Visualize results in an interactive canvas
- Export data to multiple formats (CSV, Shapefile, images)

### 1.2 Technologies Used

- **QGIS**: 3.x (PyQGIS API)
- **Python**: 3.9+
- **Qt**: PyQt5 (graphical interface)
- **Processing**: QGIS native algorithms
- **Output formats**: CSV, SHP, PNG, JPG, SVG, PDF

---

## 2. General Architecture

### 2.1 Project Structure

```
sec_interp/
├── __init__.py                 # Plugin entry point
├── core/                       # Business logic
│   ├── algorithms.py          # Main SecInterp class
│   ├── services/              # Specialized services
│   │   ├── profile_service.py
│   │   ├── geology_service.py
│   │   └── structure_service.py
│   ├── utils/                 # Modular utilities
│   │   ├── geometry.py
│   │   ├── spatial.py
│   │   ├── rendering.py
│   │   └── io.py
│   ├── data_cache.py          # Cache system
│   ├── performance_metrics.py # Performance metrics
│   ├── types.py               # Type definitions
│   └── validation.py          # Data validation
├── gui/                        # Graphical interface
│   ├── main_dialog.py         # Main dialog
│   ├── main_dialog_*.py       # Modular components
│   ├── preview_renderer.py    # Preview renderer
│   └── legend_widget.py       # Legend widget
├── exporters/                  # Data exporters
│   ├── csv_exporter.py
│   ├── shp_exporter.py
│   └── image_exporter.py
└── resources/                  # Resources (icons, UI)
```

### 2.2 Design Patterns

The plugin uses several design patterns:

1. **Service Layer Pattern**: Separation of business logic into services
2. **Strategy Pattern**: Different exporters for different formats
3. **Singleton Pattern**: Shared data cache
4. **Observer Pattern**: UI updates based on events
5. **Factory Pattern**: Exporter creation by format

---

## 3. Entry Point

### 3.1 Plugin Initialization

**File**: `__init__.py`

```python
def classFactory(iface):
    """Function called by QGIS to load the plugin.
    
    Args:
        iface (QgsInterface): QGIS interface
        
    Returns:
        SecInterp: Plugin instance
    """
    from .core.algorithms import SecInterp
    return SecInterp(iface)
```

**Initialization flow**:

1. QGIS detects the plugin in the plugins directory
2. Reads `metadata.txt` to get plugin information
3. Calls `classFactory(iface)` to create the instance
4. The plugin registers in QGIS menu and toolbar

### 3.2 Main Class: SecInterp

**File**: `core/algorithms.py`

```python
class SecInterp:
    """Main implementation of SecInterp plugin.
    
    Responsibilities:
    - QGIS integration (menu, toolbar, actions)
    - Main dialog management
    - Processing services orchestration
    - Data cache handling
    - Export coordination
    """
```

#### 3.2.1 Constructor

```python
def __init__(self, iface):
    """Initializes the plugin.
    
    Steps:
    1. Saves reference to iface
    2. Initializes i18n translator
    3. Creates service instances
    4. Initializes data cache
    5. Creates preview renderer
    """
    self.iface = iface
    self.plugin_dir = Path(__file__).parent.parent
    
    # Processing services
    self.profile_service = ProfileService()
    self.geology_service = GeologyService()
    self.structure_service = StructureService()
    
    # Cache and renderer
    self.data_cache = DataCache()
    self.preview_renderer = PreviewRenderer()
```

#### 3.2.2 Main Methods

**`initGui()`**: Creates UI elements in QGIS

```python
def initGui(self):
    """Creates menu and toolbar in QGIS."""
    icon_path = str(self.plugin_dir / "icon.png")
    
    self.add_action(
        icon_path,
        text=self.tr("Section Interpretation"),
        callback=self.run,
        parent=self.iface.mainWindow()
    )
```

**`run()`**: Shows the main dialog

```python
def run(self):
    """Runs the plugin by showing the dialog."""
    if not hasattr(self, 'dlg') or self.dlg is None:
        self.dlg = SecInterpDialog(self.iface, self)
    
    self.dlg.show()
    result = self.dlg.exec_()
    
    if result == QDialog.Accepted:
        self.process_data()
```

**`process_data()`**: Processes profile data

```python
def process_data(self):
    """Orchestrates data processing with cache.
    
    Flow:
    1. Gets and validates inputs from dialog
    2. Generates cache key
    3. Checks if data is in cache
    4. If not, generates new data
    5. Renders preview
    6. Updates UI with results
    """
```

---

## 4. Main Modules

### 4.1 Data Cache (`core/data_cache.py`)

In-memory cache system to avoid unnecessary reprocessing.

```python
class DataCache:
    """In-memory cache for profile data.
    
    Stores:
    - Topographic profiles
    - Geological data
    - Structural data
    - Processing metadata
    """
    
    def __init__(self):
        self._topo_cache: Dict[str, ProfileData] = {}
        self._geol_cache: Dict[str, GeologyData] = {}
        self._struct_cache: Dict[str, StructureData] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
```

**Key methods**:

```python
def get_cache_key(self, params: Dict[str, Any]) -> str:
    """Generates unique key from parameters.
    
    Algorithm:
    1. Filters QGIS objects (uses ID/source instead of memory address)
    2. Sorts parameters alphabetically
    3. Concatenates into string
    4. Generates MD5 hash
    
    Returns:
        32-character hexadecimal MD5 hash
    """
    key_parts = []
    for k, v in sorted(params.items()):
        if k.endswith('_obj') or k in ['raster_layer', ...]:
            if hasattr(v, 'id'):
                key_parts.append(f"{k}:{v.id()}")
            elif hasattr(v, 'source'):
                key_parts.append(f"{k}:{v.source()}")
        else:
            key_parts.append(f"{k}:{str(v)}")
    
    import hashlib
    return hashlib.md5("".join(key_parts).encode('utf-8')).hexdigest()
```

### 4.2 Performance Metrics (`core/performance_metrics.py`)

Performance metrics system.

```python
class PerformanceTimer:
    """Context manager to measure operation times.
    
    Usage:
        with PerformanceTimer("operation_name", collector) as timer:
            # code to measure
            pass
        # timer.duration contains the time in seconds
    """
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration = time.perf_counter() - self.start_time
        
        if self.collector:
            self.collector.record_metric(self.operation_name, self.duration)
```

**Format functions**:

```python
def format_duration(seconds: float) -> str:
    """Formats duration in readable format.
    
    Examples:
        0.0001 s -> "100µs"
        0.5 s -> "500ms"
        2.5 s -> "2.5s"
    """
    if seconds < 0.001:
        return f"{seconds*1000000:.0f}µs"
    if seconds < 1.0:
        return f"{seconds*1000:.0f}ms"
    return f"{seconds:.1f}s"
```

### 4.3 Types (`core/types.py`)

Type definitions for type hints.

```python
from typing import List, Tuple

# Type for topographic profile: list of (distance, elevation)
ProfileData = List[Tuple[float, float]]

# Type for geological data: list of (distance, elevation, unit)
GeologyData = List[Tuple[float, float, str]]

# Type for structural data: list of (distance, apparent_dip)
StructureData = List[Tuple[float, float]]
```

---

## 5. Services

Services encapsulate geological data processing logic.

### 5.1 ProfileService

**File**: `core/services/profile_service.py`

**Purpose**: Generate topographic profiles from a DEM.

```python
class ProfileService:
    """Service for topographic profile generation."""
    
    def generate_topographic_profile(
        self,
        line_lyr: QgsVectorLayer,
        raster_lyr: QgsRasterLayer,
        band_number: int = 1,
    ) -> ProfileData:
        """Generates topographic profile by sampling elevation along the line.
        
        Algorithm:
        1. Gets section line geometry
        2. Densifies line according to raster resolution
        3. Samples elevation at each vertex
        4. Calculates distance from start
        5. Returns list of (distance, elevation)
        
        Args:
            line_lyr: Vector layer with section line
            raster_lyr: Raster layer (DEM) for elevation
            band_number: Raster band to sample
            
        Returns:
            List of tuples (distance_m, elevation_m)
            
        Raises:
            ValueError: If layer has no features or invalid geometry
        """
```

**Detailed implementation**:

```python
def generate_topographic_profile(self, line_lyr, raster_lyr, band_number=1):
    # 1. Get line feature
    line_feat = next(line_lyr.getFeatures(), None)
    if not line_feat:
        raise ValueError("Line layer has no features")
    
    # 2. Validate geometry
    geom = line_feat.geometry()
    if not geom or geom.isNull():
        raise ValueError("Line geometry is not valid")
    
    # 3. Create distance measurement object
    da = scu.create_distance_area(line_lyr.crs())
    
    # 4. Sample elevation along the line
    # Uses native densification algorithm + raster sampling
    points = scu.sample_elevation_along_line(
        geom, raster_lyr, band_number, da
    )
    
    # 5. Convert to tuples (distance, elevation)
    values = [(round(p.x(), 1), round(p.y(), 1)) for p in points]
    
    return values
```

**Sampling process** (in `utils`):

```
Original line:     A--------B
                   |        |
Densified:         A--x--x--B
                   |  |  |  |
Raster sampling:   ↓  ↓  ↓  ↓
Elevations:        [e1,e2,e3,e4]
Distances:         [0, d1,d2,d3]
```

### 5.2 GeologyService

**File**: `core/services/geology_service.py`

**Purpose**: Extract geological contacts by intersecting line with polygons.

```python
class GeologyService:
    """Service for geological profile generation."""
    
    def generate_geological_profile(
        self,
        line_lyr: QgsVectorLayer,
        raster_lyr: QgsRasterLayer,
        outcrop_lyr: QgsVectorLayer,
        outcrop_name_field: str,
        band_number: int = 1,
    ) -> GeologyData:
        """Generates geological profile by intersecting line with outcrops.
        
        Algorithm:
        1. Intersects section line with outcrop polygons
        2. For each intersection segment:
           a. Densifies according to raster resolution
           b. Samples elevation at each point
           c. Gets geological unit name
           d. Calculates distance from start
        3. Sorts by distance
        4. Returns list of (distance, elevation, unit)
        
        Returns:
            List of tuples (distance_m, elevation_m, unit_name)
        """
```

**Detailed implementation**:

```python
def generate_geological_profile(self, line_lyr, raster_lyr, outcrop_lyr, 
                                outcrop_name_field, band_number=1):
    # 1. Validate inputs
    line_feat = next(line_lyr.getFeatures(), None)
    if not line_feat:
        raise ValueError("Line layer has no features")
    
    line_geom = line_feat.geometry()
    line_start = scu.get_line_start_point(line_geom)
    
    # 2. Intersect using QGIS native algorithm
    result = processing.run(
        "native:intersection",
        {
            "INPUT": line_lyr,
            "OVERLAY": outcrop_lyr,
            "INPUT_FIELDS": [],
            "OVERLAY_FIELDS": [],  # Keeps ALL geology fields
            "OUTPUT": "memory:",
        }
    )
    
    intersection_layer = result["OUTPUT"]
    
    # 3. Process each intersection segment
    values = []
    for feature in intersection_layer.getFeatures():
        geom = feature.geometry()
        
        # Handle MultiLineString and LineString
        geometries_to_process = []
        if geom.wkbType() in [QgsWkbTypes.LineString, ...]:
            geometries_to_process.append(geom)
        elif geom.wkbType() in [QgsWkbTypes.MultiLineString, ...]:
            for part in geom.asMultiPolyline():
                line_geom = QgsGeometry.fromPolylineXY(part)
                geometries_to_process.append(line_geom)
        
        # 4. Densify and sample each geometry
        for process_geom in geometries_to_process:
            # Calculate interval based on raster resolution
            interval = scu.calculate_step_size(process_geom, raster_lyr)
            
            # Densify using native algorithm
            densified_geom = scu.densify_line_by_interval(process_geom, interval)
            vertices = scu.get_line_vertices(densified_geom)
            
            # 5. Sample each vertex
            for pt in vertices:
                # Distance from line start
                dist = da.measureLine(line_start, pt)
                
                # Elevation from raster
                res = raster_lyr.dataProvider().identify(
                    pt, QgsRaster.IdentifyFormatValue
                ).results()
                elev = res.get(band_number, 0.0)
                
                # Geological unit name
                unit_name = feature[outcrop_name_field]
                
                values.append((round(dist, 1), round(elev, 1), unit_name))
    
    # 6. Sort by distance
    values.sort(key=lambda x: x[0])
    
    return values
```

**Intersection diagram**:

```
Section line:     A-----------B
                  |           |
Polygons:        [U1] [U2] [U3]
                  |    |    |
Intersection:    [s1] [s2] [s3]
                  |    |    |
Densification:   [•••][•••][•••]
                  |    |    |
Result:          [(d,e,U1), (d,e,U2), (d,e,U3), ...]
```

### 5.3 StructureService

**File**: `core/services/structure_service.py`

**Purpose**: Project structural measurements to section plane.

```python
class StructureService:
    """Service for structural measurement projection."""
    
    def project_structures(
        self,
        line_lyr: QgsVectorLayer,
        struct_lyr: QgsVectorLayer,
        buffer_m: int,
        line_az: float,
        dip_field: str,
        strike_field: str,
    ) -> StructureData:
        """Projects structural measurements to section plane.
        
        Algorithm:
        1. Creates buffer around section line
        2. Filters structures within buffer
        3. For each structure:
           a. Parses strike and dip
           b. Validates ranges (strike: 0-360°, dip: 0-90°)
           c. Calculates apparent dip
           d. Calculates distance along section
        4. Sorts by distance
        5. Returns list of (distance, apparent_dip)
        
        Returns:
            List of tuples (distance_m, apparent_dip_degrees)
        """
```

**Detailed implementation**:

```python
def project_structures(self, line_lyr, struct_lyr, buffer_m, line_az, 
                      dip_field, strike_field):
    # 1. Validate line
    line_feat = next(line_lyr.getFeatures(), None)
    line_geom = line_feat.geometry()
    line_start = scu.get_line_start_point(line_geom)
    
    # 2. Create buffer using native algorithm
    buffer_geom = scu.create_buffer_geometry(
        line_geom, line_lyr.crs(), buffer_m, segments=25
    )
    
    # 3. Filter features spatially (uses R-tree spatial index)
    filtered_features = scu.filter_features_by_buffer(
        struct_lyr, buffer_geom, line_lyr.crs()
    )
    
    # 4. Process each structure
    projected_structs = []
    for f in filtered_features:
        struct_geom = f.geometry()
        p = struct_geom.asPoint()
        
        # Distance along line
        dist = da.measureLine(line_start, p)
        
        # Parse strike and dip
        strike_raw = f[strike_field]
        dip_raw = f[dip_field]
        
        strike = scu.parse_strike(strike_raw)  # Supports "N 15° E" or "15"
        dip_angle, _ = scu.parse_dip(dip_raw)  # Supports "22° SW" or "22"
        
        # Validate ranges
        is_valid, _ = vu.validate_angle_range(strike, "Strike", 0.0, 360.0)
        if not is_valid:
            continue
        
        is_valid, _ = vu.validate_angle_range(dip_angle, "Dip", 0.0, 90.0)
        if not is_valid:
            continue
        
        # Calculate apparent dip
        app_dip = scu.calculate_apparent_dip(strike, dip_angle, line_az)
        
        projected_structs.append((round(dist, 1), round(app_dip, 1)))
    
    # 5. Sort by distance
    projected_structs.sort(key=lambda x: x[0])
    
    return projected_structs
```

---

## 6. Utilities

### 6.1 Geometry Utils (`core/utils/geometry.py`)

Geometric operations using QGIS native algorithms.

**Main functions**:

```python
def create_buffer_geometry(geometry, crs, distance, segments=25):
    """Creates buffer using native:buffer.
    
    Advantages over QgsGeometry.buffer():
    - Better CRS handling
    - More robust with complex geometries
    - Uses optimized GEOS algorithm
    """

def filter_features_by_buffer(features_layer, buffer_geometry, buffer_crs):
    """Filters features using R-tree spatial index.
    
    Algorithm:
    1. Builds spatial index (R-tree) of features
    2. Searches candidates using bounding box (fast)
    3. Filters precisely with intersects() (slow, but only candidates)
    
    Complexity:
    - Without index: O(n) where n = total features
    - With index: O(log n + k) where k = features in buffer
    """

def densify_line_by_interval(geometry, interval):
    """Densifies line using native:densifygeometriesgivenaninterval.
    
    Adds vertices at regular intervals.
    More precise than manual interpolation.
    """
```

### 6.2 Spatial Utils (`core/utils/spatial.py`)

Basic spatial calculations.

```python
def calculate_line_azimuth(line_geom):
    """Calculates line azimuth.
    
    Formula:
        azimuth = atan2(Δx, Δy) * 180/π
        
    Where:
        Δx = x2 - x1
        Δy = y2 - y1
        
    Result normalized to 0-360°
    """
    line = line_geom.asPolyline()
    p1, p2 = line[0], line[1]
    
    azimuth = math.degrees(math.atan2(p2.x() - p1.x(), p2.y() - p1.y()))
    
    if azimuth < 0:
        azimuth += 360
    
    return azimuth

def create_distance_area(crs):
    """Creates configured QgsDistanceArea object.
    
    Configures:
    - Source CRS
    - Ellipsoid for geodesic calculations
    - Transformation context
    """
    da = QgsDistanceArea()
    da.setSourceCrs(crs, QgsProject.instance().transformContext())
    da.setEllipsoid(crs.ellipsoidAcronym())
    return da
```

---

## 7. Mathematical Formulas

### 7.1 Apparent Dip

**Function**: `calculate_apparent_dip(true_strike, true_dip, line_azimuth)`

**Formula**:

```
tan(apparent_dip) = tan(true_dip) × sin(α)
```

Where:
- `α` = angle between plane strike and section azimuth
- `α = strike - line_azimuth`

**Implementation**:

```python
def calculate_apparent_dip(true_strike, true_dip, line_azimuth):
    """Calculates apparent dip in section plane.
    
    Apparent dip is the inclination of a plane measured
    in a direction that is NOT perpendicular to strike.
    
    Args:
        true_strike: True strike (0-360°)
        true_dip: True dip (0-90°)
        line_azimuth: Section line azimuth (0-360°)
        
    Returns:
        Apparent dip in degrees
        
    Example:
        Plane: strike=45°, dip=60°
        Section: azimuth=90°
        
        α = 45° - 90° = -45°
        tan(app_dip) = tan(60°) × sin(-45°)
        tan(app_dip) = 1.732 × (-0.707)
        tan(app_dip) = -1.225
        app_dip = arctan(-1.225) = -50.8°
    """
    alpha = math.radians(true_strike)
    beta = math.radians(true_dip)
    theta = math.radians(line_azimuth)
    
    app_dip = math.degrees(
        math.atan(math.tan(beta) * math.sin(alpha - theta))
    )
    
    return app_dip
```

**Explanatory diagram**:

```
Plan view:
                N (0°)
                |
                |
    Strike -----+------ E (90°)
    (45°)      /|
              / |
             /  | Section azimuth (90°)
            /   |
           /α   |
          /     |
         
Section view:
         |
         | True dip (60°)
         |/
        /|
       / |
      /  | Apparent dip (50.8°)
     /   |
    /    |
```

### 7.2 Strike Parsing

**Function**: `parse_strike(value)`

Supports multiple formats:

1. **Numeric**: `"45"`, `"120.5"` → direct azimuth
2. **Quadrant**: `"N 30° E"`, `"S 15° W"` → conversion to azimuth

**Quadrant conversion table**:

| Notation | Formula | Example | Azimuth |
|----------|---------|---------|---------|
| N α° E | α | N 30° E | 30° |
| N α° W | 360 - α | N 30° W | 330° |
| S α° E | 180 - α | S 30° E | 150° |
| S α° W | 180 + α | S 30° W | 210° |

**Implementation**:

```python
def parse_strike(value):
    # Try direct numeric conversion
    try:
        return float(value)
    except (ValueError, TypeError):
        pass
    
    # Parse quadrant notation
    text = str(value).replace("°", "").strip().upper()
    match = re.match(r"([NS])\s*(\d+\.?\d*)\s*([EW])", text)
    
    if not match:
        return None
    
    d1, ang, d2 = match.groups()
    ang = float(ang)
    
    # Apply quadrant rules
    if d1 == "N" and d2 == "E":
        strike = ang
    elif d1 == "N" and d2 == "W":
        strike = 360 - ang
    elif d1 == "S" and d2 == "E":
        strike = 180 - ang
    elif d1 == "S" and d2 == "W":
        strike = 180 + ang
    
    return strike % 360
```

### 7.3 Dip Parsing

**Function**: `parse_dip(value)`

Supports:

1. **Numeric**: `"22"`, `"45.5"` → direct dip
2. **With direction**: `"22° SW"`, `"45 NE"` → dip + direction

**Implementation**:

```python
def parse_dip(value):
    text = str(value).replace("°", "").strip().upper()
    
    # Case 1: Number only
    numeric_only = re.match(r"^(\d+\.?\d*)$", text)
    if numeric_only:
        return float(text), None
    
    # Case 2: Number + cardinal direction
    match = re.match(r"(\d+\.?\d*)\s*([NSEW]{1,2})", text)
    if not match:
        return None, None
    
    dip, cardinal = match.groups()
    dip = float(dip)
    
    # Convert cardinal direction to azimuth
    dip_dir = cardinal_to_azimuth(cardinal)
    
    return dip, dip_dir
```

**Cardinal directions table**:

| Cardinal | Azimuth |
|----------|---------|
| N | 0° |
| NE | 45° |
| E | 90° |
| SE | 135° |
| S | 180° |
| SW | 225° |
| W | 270° |
| NW | 315° |

---

**Document created**: 2025-12-07  
**Author**: Antigravity AI  
**Version**: 1.0
