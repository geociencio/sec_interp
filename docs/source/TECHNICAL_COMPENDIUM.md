# SecInterp - Technical Compendium

This document consolidates technical research, geophysical algorithms, and API references for the **SecInterp** plugin.

---

## 🔬 Scientific & Geophysical Research

### 1. Integration of Geophysics
The plugin is prepared for future integration of deep geophysical data:
- **Potential (SP)**: Projections use normalized dot product for section alignment and absolute elevation calculation ($Z_{collar} - Depth$).
- **VES (SEV)**: Resistivity models are visualized as blocks on a logarithmic scale ($\log_{10}(Rho)$) using thickness-to-elevation conversion.

### 2. Drillhole Modeling
- **Desurveying**: Trayectories are calculated using the **Average Angle Method** (Tangential tracking).
- **Projection**: 3D trajectories are mapped to the 2D plane by calculating distance along the section line while preserving absolute Z.

### 3. Core Algorithms
- **Distance & Sampling**: We use `QgsDistanceArea.measureLine()` and direct `dataProvider()` access for DEM sampling, yielding a ~30% performance boost over high-level processing algorithms.
- **Adaptive LOD**: Uses the **Douglas-Peucker (RDP)** algorithm for line simplification and a curvature-based hysteresis logic to adjust sampling density dynamically during zoom.

---

## 🔧 API Reference

### Core Services (`core/services/`)

#### `ProfileService`
- **`generate_topographic_profile(line_lyr, raster_lyr, band)`**: Samples raster data along a line.
- **Returns**: `List[Tuple[float, float]]` (distance, elevation).

#### `GeologyService`
- **`generate_geological_profile(...)`**: Intersects section lines with geological geometry.
- **Returns**: `List[GeologySegment]`.

#### `StructureService`
- **`project_structures(...)`**: Projects 3D structural data and calculates apparent dip.
- **Formula**: `tan(beta) = tan(alpha) * |cos(strike - azimuth)|`.

#### `DrillholeService`
- **`project_collars()`** & **`process_intervals()`**: Handle full 3D→2D pipeline for drillholes.

---

## 🛡️ Validation Framework

Modularized in `core/validation/`:
- **FieldValidator**: Numeric and existence checks.
- **LayerValidator**: CS, geometry, and feature count validation.
- **PathValidator**: Security and permission handling.
- **ProjectValidator**: High-level orchestration.

---

## 🧬 Key Data Structures

### `GeologySegment`
Used to represent both surface outcrops and drillhole intervals.
```python
@dataclass
class GeologySegment:
    unit_name: str
    points: List[Tuple[float, float]]
    geometry: QgsGeometry
    attributes: Dict[str, Any]
```

### `StructureMeasurement`
```python
@dataclass
class StructureMeasurement:
    distance: float
    elevation: float
    apparent_dip: float
    original_dip: float
    original_strike: float
```
