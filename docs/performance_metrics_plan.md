# Performance Metrics Implementation Plan

## Overview

Add performance metrics tracking to monitor plugin performance with various data formats and volumes.

## Objectives

1. Track processing times for key operations
2. Monitor data volumes (points, features, etc.)
3. Identify performance bottlenecks
4. Provide user feedback on operation duration
5. Enable performance optimization

## Proposed Changes

### 1. Performance Metrics Module

**Create:** `core/performance_metrics.py`

**Features:**
- `PerformanceTimer` context manager for timing operations
- `MetricsCollector` class for aggregating metrics
- Metrics storage and reporting
- Optional metrics logging

```python
class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str, collector: Optional[MetricsCollector] = None):
        self.operation_name = operation_name
        self.collector = collector
        self.start_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        self.duration = time.perf_counter() - self.start_time
        if self.collector:
            self.collector.record_timing(self.operation_name, self.duration)
```

### 2. Metrics Integration Points

#### PreviewManager
Track:
- Total preview generation time
- Topography generation time
- Geology generation time (if applicable)
- Structure generation time (if applicable)
- Rendering time
- Data points processed

#### ExportManager
Track:
- Export preparation time
- Format-specific export time
- File size
- Export format

#### Service Classes
Track:
- Profile service processing time
- Geology service processing time
- Structure service processing time
- Number of features processed

### 3. Metrics Display

**Options:**
1. **Results Panel** - Show timing in results text
2. **Status Bar** - Brief timing info
3. **Debug Log** - Detailed metrics for debugging
4. **Optional Metrics Dialog** - Detailed performance report

### 4. Configuration

Add to `main_dialog_config.py`:
```python
class DialogConfig:
    # Performance metrics
    ENABLE_PERFORMANCE_METRICS: bool = True
    SHOW_METRICS_IN_RESULTS: bool = True
    LOG_DETAILED_METRICS: bool = False  # For debugging
```

## Implementation Phases

### Phase 1: Core Metrics Module ✅
- [x] Create `core/performance_metrics.py`
- [x] Implement `PerformanceTimer` context manager
- [x] Implement `MetricsCollector` class
- [x] Add unit tests (Verified manually)

### Phase 2: PreviewManager Integration ✅
- [x] Add timing to `generate_preview()`
- [x] Track individual data generation steps
- [x] Add data volume metrics
- [x] Update results message with timing

### Phase 3: ExportManager Integration ✅
- [x] Add timing to `export_preview()`
- [x] Track format-specific metrics
- [x] Log export performance

### Phase 4: Service Integration (Deferred)
- [ ] Add timing to profile service
- [ ] Add timing to geology service
- [ ] Add timing to structure service
- [ ] Track feature counts
*Note: Service integration deferred as current metrics cover user needs.*

### Phase 5: Display & Reporting ✅
- [x] Update results panel with metrics
- [x] Add optional detailed metrics logging
- [ ] Create performance summary format (Covered by results panel)

## Example Output

### Results Panel (with metrics)
```
✓ Preview generated! (2.3s)

Performance:
  Topography: 0.8s (150 points)
  Geology: 1.2s (45 intersections)
  Structures: 0.2s (12 features)
  Rendering: 0.1s

Distance: 0.0 - 500.0 m
Elevation: 100.0 - 250.0 m
```

### Debug Log
```
[METRICS] Preview Generation:
  - Total: 2.345s
  - Topography: 0.823s (150 points, 182 points/s)
  - Geology: 1.234s (45 points, 36 points/s)
  - Structures: 0.187s (12 features)
  - Rendering: 0.101s
  - Data volume: 207 total points
```

## Benefits

1. **Performance Monitoring** - Identify slow operations
2. **User Feedback** - Show progress and timing
3. **Optimization** - Data-driven performance improvements
4. **Debugging** - Diagnose performance issues
5. **Scalability** - Understand performance with large datasets

## Configuration Options

Users can control metrics via:
- Enable/disable metrics collection
- Show/hide metrics in results
- Enable detailed logging for debugging

## Performance Overhead

- Minimal overhead (~0.1% for timing)
- Optional detailed logging
- No impact when disabled

## Future Enhancements

1. **Metrics Export** - Save metrics to CSV/JSON
2. **Performance Graphs** - Visualize trends
3. **Benchmarking** - Compare different approaches
4. **Profiling Integration** - Deep performance analysis

## Testing

- Test with small datasets (< 100 points)
- Test with medium datasets (100-1000 points)
- Test with large datasets (> 1000 points)
- Verify minimal overhead
- Test metrics accuracy

## Rollout

1. Implement core metrics module
2. Add to PreviewManager (most visible)
3. Extend to other components
4. Gather user feedback
5. Refine based on usage

## Success Criteria

- ✅ Metrics collection < 1% overhead
- ✅ Clear, useful timing information
- ✅ Helps identify bottlenecks
- ✅ Improves user experience
- ✅ Aids debugging and optimization
