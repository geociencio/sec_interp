# Level-of-Detail (LOD) Optimization for Preview Rendering

## Performance Issue

**Current State:** `PreviewRenderer` renders all data points without optimization, causing performance issues with large datasets.

**Problem:** When rendering profiles with thousands of points:
- Slow rendering (>1 second for 10k+ points)
- Unnecessary detail at preview zoom levels
- Poor user experience with large datasets

---

## Proposed LOD Techniques

### 1. **Data Decimation** (Simplest, Highest Impact)

Reduce number of points while preserving visual fidelity.

**Algorithm: Douglas-Peucker Line Simplification**
- Reduces points while maintaining shape
- Configurable tolerance based on zoom level
- Already available in QGIS: `QgsGeometry.simplify()`

**Implementation:**
```python
def _decimate_line_data(self, data, tolerance=None, max_points=1000):
    """Decimate line data using Douglas-Peucker algorithm.
    
    Args:
        data: List of (x, y) tuples
        tolerance: Simplification tolerance (auto-calculated if None)
        max_points: Maximum points to keep
        
    Returns:
        Decimated list of (x, y) tuples
    """
    if len(data) <= max_points:
        return data
    
    # Create QgsGeometry from points
    points = [QgsPointXY(x, y) for x, y in data]
    line = QgsGeometry.fromPolylineXY(points)
    
    # Auto-calculate tolerance if not provided
    if tolerance is None:
        extent = line.boundingBox()
        tolerance = max(extent.width(), extent.height()) / 500
    
    # Simplify
    simplified = line.simplify(tolerance)
    
    # Extract points
    if simplified.isMultipart():
        result_points = simplified.asMultiPolyline()[0]
    else:
        result_points = simplified.asPolyline()
    
    return [(p.x(), p.y()) for p in result_points]
```

---

### 2. **Adaptive Sampling** (Medium Complexity)

Sample more densely in areas of high curvature, less in flat areas.

**Algorithm: Ramer-Douglas-Peucker with Adaptive Tolerance**
- Higher tolerance in flat areas
- Lower tolerance in curved areas
- Preserves important features

**Implementation:**
```python
def _adaptive_sample(self, data, min_tolerance=0.1, max_tolerance=10.0):
    """Adaptively sample data based on local curvature.
    
    Args:
        data: List of (x, y) tuples
        min_tolerance: Minimum tolerance for high-detail areas
        max_tolerance: Maximum tolerance for low-detail areas
        
    Returns:
        Adaptively sampled data
    """
    if len(data) < 100:
        return data
    
    # Calculate local curvature
    curvatures = self._calculate_curvature(data)
    
    # Determine tolerance based on average curvature
    avg_curvature = sum(curvatures) / len(curvatures)
    
    if avg_curvature > 0.5:  # High curvature
        tolerance = min_tolerance
    elif avg_curvature < 0.1:  # Low curvature
        tolerance = max_tolerance
    else:  # Medium curvature
        tolerance = (min_tolerance + max_tolerance) / 2
    
    return self._decimate_line_data(data, tolerance)
```

---

### 3. **Progressive Rendering** (Advanced)

Render low-detail first, then progressively add detail.

**Strategy:**
1. Initial render with heavily decimated data (fast)
2. Background thread adds detail progressively
3. User sees something immediately, detail fills in

**Implementation:**
```python
def _progressive_render(self, data, levels=3):
    """Create multiple LOD levels for progressive rendering.
    
    Args:
        data: Full resolution data
        levels: Number of LOD levels
        
    Returns:
        List of LOD levels, from coarsest to finest
    """
    lod_levels = []
    
    for i in range(levels):
        # Exponentially increasing detail
        max_points = 100 * (2 ** i)
        decimated = self._decimate_line_data(data, max_points=max_points)
        lod_levels.append(decimated)
    
    # Add full resolution as final level
    lod_levels.append(data)
    
    return lod_levels
```

---

### 4. **Zoom-Based LOD** (Best for Interactive Use)

Adjust detail level based on zoom/extent.

**Strategy:**
- Far zoom: Very decimated (100-500 points)
- Medium zoom: Moderately decimated (500-2000 points)
- Close zoom: Full detail or lightly decimated

**Implementation:**
```python
def _get_lod_for_extent(self, data, extent, canvas_size):
    """Determine appropriate LOD based on view extent.
    
    Args:
        data: Full resolution data
        extent: QgsRectangle of current view
        canvas_size: QSize of canvas
        
    Returns:
        Appropriately decimated data
    """
    # Calculate pixels per data point
    data_extent = self._calculate_data_extent(data)
    pixels_per_unit = canvas_size.width() / extent.width()
    
    # If we have more than 2 points per pixel, decimate
    points_per_pixel = len(data) * pixels_per_unit / data_extent.width()
    
    if points_per_pixel > 2:
        # Target 1-2 points per pixel
        target_points = int(canvas_size.width() * 2)
        return self._decimate_line_data(data, max_points=target_points)
    
    return data
```

---

## Implementation Plan

### Phase 1: Basic Decimation (Quick Win)
1. Add `_decimate_line_data()` method to `PreviewRenderer`
2. Apply decimation in `_create_topo_layer()` before creating geometry
3. Apply decimation in `_create_geol_layer()` for each unit
4. Add user setting for max preview points (default: 1000)

### Phase 2: Adaptive Sampling
1. Implement curvature calculation
2. Add `_adaptive_sample()` method
3. Use adaptive sampling for topography (high curvature areas)
4. Make it optional via settings

### Phase 3: Zoom-Based LOD
1. Track current extent in renderer
2. Implement `_get_lod_for_extent()`
3. Re-render on zoom change with appropriate LOD
4. Cache multiple LOD levels

---

## Files to Modify

### 1. `gui/preview_renderer.py`
**Add Methods:**
- `_decimate_line_data(data, tolerance, max_points)`
- `_calculate_curvature(data)` (for adaptive sampling)
- `_adaptive_sample(data, min_tol, max_tol)`
- `_get_lod_for_extent(data, extent, size)`

**Modify Methods:**
- `_create_topo_layer()` - Apply decimation before geometry creation
- `_create_geol_layer()` - Apply decimation per geological unit
- `_create_struct_layer()` - Optionally decimate if many structures

### 2. `gui/main_dialog.py`
**Add Settings:**
- Max preview points slider (100-10000, default 1000)
- Enable/disable adaptive sampling checkbox
- LOD quality preset (Low/Medium/High)

### 3. `core/validation.py`
**Add Validation:**
- `validate_lod_settings(max_points, quality)` - Validate LOD parameters

---

## Performance Benchmarks (Expected)

| Dataset Size | Current Time | With LOD (1000pts) | Improvement |
|--------------|--------------|-------------------|-------------|
| 1,000 points | ~50ms | ~50ms | 0% (no change) |
| 5,000 points | ~200ms | ~60ms | 70% faster |
| 10,000 points | ~800ms | ~70ms | 91% faster |
| 50,000 points | ~5000ms | ~100ms | 98% faster |

---

## User Experience Improvements

### Before LOD:
- ❌ Slow preview with large datasets
- ❌ Unresponsive UI during rendering
- ❌ Unnecessary detail at overview zoom

### After LOD:
- ✅ Fast preview regardless of dataset size
- ✅ Responsive UI
- ✅ Appropriate detail for zoom level
- ✅ Option to see full detail when zoomed in

---

## Configuration Options

### Settings Dialog
```python
# LOD Settings Group
lod_enabled = True  # Enable/disable LOD
max_preview_points = 1000  # Maximum points in preview
adaptive_sampling = False  # Use adaptive sampling
lod_quality = "Medium"  # Low/Medium/High preset

# Quality Presets
PRESETS = {
    "Low": {"max_points": 500, "tolerance_factor": 2.0},
    "Medium": {"max_points": 1000, "tolerance_factor": 1.0},
    "High": {"max_points": 2000, "tolerance_factor": 0.5},
}
```

---

## Testing Strategy

### Unit Tests
```python
def test_decimation_preserves_shape():
    """Test that decimation preserves overall shape."""
    # Create test data with known shape
    data = generate_sine_wave(1000)
    decimated = renderer._decimate_line_data(data, max_points=100)
    
    # Verify shape is preserved
    assert len(decimated) <= 100
    assert shape_similarity(data, decimated) > 0.95

def test_decimation_performance():
    """Test that decimation improves performance."""
    large_data = generate_random_profile(10000)
    
    start = time.time()
    renderer._create_topo_layer(large_data)
    time_full = time.time() - start
    
    decimated = renderer._decimate_line_data(large_data, max_points=1000)
    start = time.time()
    renderer._create_topo_layer(decimated)
    time_decimated = time.time() - start
    
    assert time_decimated < time_full * 0.5  # At least 50% faster
```

### Integration Tests
- Test with real-world large datasets
- Verify visual quality at different zoom levels
- Test memory usage with LOD vs without

---

## Benefits

✅ **Performance**: 70-98% faster rendering for large datasets  
✅ **Scalability**: Handles datasets of any size  
✅ **User Experience**: Responsive UI, instant previews  
✅ **Flexibility**: Configurable quality/performance tradeoff  
✅ **Backward Compatible**: Works with existing code  

---

## Risks & Mitigation

### Risk: Loss of Detail
**Mitigation:** 
- Make LOD optional
- Provide quality presets
- Show full detail on export

### Risk: Complexity
**Mitigation:**
- Start with simple decimation (Phase 1)
- Add advanced features incrementally
- Comprehensive testing

### Risk: User Confusion
**Mitigation:**
- Clear UI labels
- Tooltips explaining LOD
- Sensible defaults

---

## References

- [Douglas-Peucker Algorithm](https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm)
- [QGIS QgsGeometry.simplify()](https://qgis.org/pyqgis/master/core/QgsGeometry.html#qgis.core.QgsGeometry.simplify)
- [Level of Detail (Computer Graphics)](https://en.wikipedia.org/wiki/Level_of_detail_(computer_graphics))

---

**Priority:** Medium-High (Performance Improvement)  
**Effort:** Medium (Phase 1: 2-3 hours, Full: 6-8 hours)  
**Impact:** High (Significantly improves UX with large datasets)
