# Refactor core/utils/geometry.py

Refactor `core/utils/geometry.py` to address high complexity and redundant boilerplate code when calling QGIS processing algorithms.

## Proposed Changes

### [MODIFY] [geometry.py](file:///home/jmbernales/qgispluginsdev/sec_interp/core/utils/geometry.py)

#### 1. Abstraction of Processing Algorithms
- **Enhance `run_processing_algorithm`**: Keep as a low-level wrapper for `processing.run`.
- **New `run_geometry_operation`**: A higher-level helper that:
    - Takes a `QgsGeometry`, `CRS`, and algorithm details.
    - Creates a temporary memory layer.
    - Runs the algorithm.
    - Extracts the resulting geometry.
    - Handles timeouts and errors.

#### 2. Simplification of Main Functions
- **`create_buffer_geometry`**: Rewrite to use `run_geometry_operation`.
- **`densify_line_by_interval`**: Rewrite to use `run_geometry_operation`.
- This removes roughly 40-50 lines of duplicate boilerplate.

#### 3. Improvement of Vertex Extraction
- **`get_line_vertices`**: Implement a more robust version that can optionally return all vertices from all parts instead of just the first one.
- **`extract_all_vertices`**: New helper to flatten multipart geometries into a single list of points.

#### 4. Type Hints and Documentation
- Ensure all functions have full type hints (using `typing` module).
- Update docstrings to follow Google style consistently.
- Add more examples to docstrings.

#### 5. Optimization
- Ensure `filter_features_by_buffer` continues to use `QgsSpatialIndex` efficiently.
- Add a check for empty geometries at the start of all functions.

## Verification Plan

### Automated Tests
- Run existing tests to ensure no regressions:
  ```bash
  pytest tests/unit/test_geometry_utils.py
  ```
- Run the project analyzer to verify complexity reduction:
  ```bash
  python analyze_project_optfixed.py
  ```

### Manual Verification
- Test buffer and densification in the QGIS plugin preview to ensure visual correctness.
