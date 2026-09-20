---
tags:
  - secinterp
  - code-walkthrough
  - core
  - performance
aliases:
  - performance_metrics.py
  - MetricsCollector
cssclass: secinterp-note
---

# 29 — `core/performance_metrics.py`

> [!abstract] One-line summary
> Tracks **timings, counts, and memory** per operation with `MetricsCollector` + `PerformanceTimer` / `@performance_monitor`.

**Path**: `core/performance_metrics.py` (321 lines)
**Classes**: `MetricsCollector`, `PerformanceTimer`
**Decorator**: `performance_monitor`
**Layer**: Core
**Tags**: #secinterp #core #performance

---

## 🎯 Why does this file exist?

Without metrics, the preview feels "slow" without data. This module:

| What it measures | How |
|------------------|-----|
| Duration per phase | `MetricsCollector.record_timing("Total Preview Generation", sec)` |
| Point/segment counts | `record_count("topo_points", n)` |
| Memory peak | `tracemalloc` + `track_memory` |
| Auto logging | `@performance_monitor` or `with PerformanceTimer(...)` |

> [!tip] Used in `PreviewManager` and all `*_service.build_*` via `@performance_monitor`.

---

## 🧱 `MetricsCollector`

```python
class MetricsCollector:
    def __init__(self):
        self.timings: dict[str, float] = {}
        self.counts: dict[str, int] = {}
        self.metadata: dict[str, Any] = {}
        self._start_time = time.perf_counter()

    def record_timing(self, operation: str, duration: float): ...
    def record_count(self, metric: str, count: int): ...
    def add_metadata(self, key, value): ...
    def get_summary(self) -> dict[str, Any]: ...
    def clear(self): ...
```

---

## 🧱 `PerformanceTimer` and decorator

```python
@contextmanager
def performance_timer(operation: str, collector: MetricsCollector):
    start = time.perf_counter()
    yield
    collector.record_timing(operation, time.perf_counter() - start)

class PerformanceTimer:  # context manager with logger.debug
    def __enter__(self): self._t0 = time.perf_counter()
    def __exit__(self, *a): self.collector.record_timing(self.name, time.perf_counter()-self._t0)

def performance_monitor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        collector = kwargs.get("metrics") or MetricsCollector()
        with PerformanceTimer(func.__name__, collector):
            return func(*args, **kwargs)
    return wrapper
```

---

## 🔗 Related notes

- [[10 - controller]] — accumulates `metrics`
- [[21 - dialog_preview_manager]] — `PerformanceTimer("Total Preview Generation")`

---

*Note 29 of the SecInterp Code Walkthrough vault — v3.8.0*
