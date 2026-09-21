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

#### `GeologyService`
- **`build_segments(context, feedback=None)`**: Intersects section lines with geological geometry.
- **Returns**: `List[GeologySegment]`.

#### `StructureService`
- **`project_structures(context, feedback=None)`**: Projects 3D structural data and calculates apparent dip.
- **Formula**: `tan(beta) = tan(alpha) * |cos(strike - azimuth)|`.

#### `DrillholeService`
- **`process_context(context, feedback=None)`**: Full drillhole pipeline.
- **Architecture**: Decomposed into `CollarProcessor`, `SurveyProcessor`, `IntervalProcessor`, `TrajectoryEngine`, `ProjectionEngine`.

#### `PreviewService`
- **`generate_all(params, transform_context)`**: Orchestrates topography + structures for the preview.
- **`calculate_max_points(canvas_width, manual_max, auto_lod)`**: Adaptive LOD.

#### `AccessControlService`
- **`can_export_3d()`**: Gates 3D export via `QgsSettings` (`SecInterp/enable_3d`).

#### Export package (`core/services/export/`)
- **`ExportService.export_data(output_folder, params, ...)`**: facade over `handlers/` (one per data type).
- **Note**: topography extraction lives in the GUI adapter `gui/adapters/profile_extractor.py`
  (`ProfileExtractor.extract_profile`), not in `core/services/`.

---

## 🛡️ Validation Framework

Modularized in `core/validation/`:
- **FieldValidator**: Numeric and existence checks.
- **LayerValidator**: CRS, geometry, and feature count validation.
- **PathValidator**: Security and permission handling.
- **ProjectValidator**: High-level orchestration.

---

## 🧬 Key Data Structures

### `GeologySegment`
Used to represent both surface outcrops and drillhole intervals (QGIS-agnostic: WKT, not `QgsGeometry`).
```python
@dataclass
class GeologySegment:
    unit_name: str
    geometry_wkt: DomainGeometry | None
    attributes: dict[str, Any]
    points: list[tuple[float, float]]
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
    attributes: dict[str, Any]
```
