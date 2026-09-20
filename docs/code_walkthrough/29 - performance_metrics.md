---
tags:
  - secinterp
  - code-walkthrough
  - core
  - performance
  - metrics
aliases:
  - performance_metrics.py
  - MetricsCollector
  - PerformanceTimer
cssclass: secinterp-note
---

# 29 — `core/performance_metrics.py`

> [!abstract] Resumen en una línea
> Registra **timings, conteos y memoria** de cada operación con `MetricsCollector` + `PerformanceTimer` / `@performance_monitor`.

**Ruta**: `core/performance_metrics.py` (321 líneas)
**Clases**: `MetricsCollector`, `PerformanceTimer`
**Decorador**: `performance_monitor`
**Funciones**: `performance_timer`, `track_memory`
**Capa**: Core
**Tags**: #secinterp #core #performance #metrics

---

## 🎯 ¿Por qué existe este archivo?

Sin métricas, el preview parece "lento" sin datos. Este módulo:

| Qué mide | Cómo |
|----------|------|
| Duración por fase | `MetricsCollector.record_timing("Total Preview Generation", sec)` |
| Conteo de puntos/segmentos | `record_count("topo_points", n)` |
| Pico de memoria | `tracemalloc` + `track_memory` |
| Log automático | `@performance_monitor` o `with PerformanceTimer(...)` |

> [!tip] Usado en `PreviewManager` y todos los `*_service.build_*` vía `@performance_monitor`.

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
    def get_summary(self) -> dict[str, Any]: ...  # timings + counts + elapsed
    def clear(self): ...
```

---

## 🧱 `PerformanceTimer` y decorador

```python
@contextmanager
def performance_timer(operation: str, collector: MetricsCollector):
    start = time.perf_counter()
    yield
    collector.record_timing(operation, time.perf_counter() - start)

class PerformanceTimer:  # wrapper de context manager con logger.debug
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

## 🔗 Notas relacionadas

- [[10 - controller]] — acumula `metrics`
- [[21 - dialog_preview_manager]] — `PerformanceTimer("Total Preview Generation")`

---

*Nota 29 de la bóveda SecInterp Code Walkthrough — v3.8.0*
