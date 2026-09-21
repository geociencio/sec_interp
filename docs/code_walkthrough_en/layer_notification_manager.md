---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - cache
aliases:
  - layer_notification_manager.py
  - LayerNotificationManager
cssclass: secinterp-note
---

# `gui/layer_notification_manager.py`

> [!abstract] One-line summary
> Wires each active QGIS layer's `dataChanged` signal to `DataCache.invalidate`, normalizing drill buckets (`drill_*` → `drill`) and making the section layer invalidate the **whole** cache.

**Path**: `gui/layer_notification_manager.py` (73 lines)
**Class**: `LayerNotificationManager`
**Layer**: GUI · Managers (QGIS → core bridge)
**Tags**: #secinterp #gui #cache

---

## 🎯 Why does this file exist?

`DataCache` is valid as long as the layers do not change. If the user edits a layer in QGIS, cached data becomes stale. This manager is the **bridge** between QGIS signals and core invalidation.

| Problem | Solution |
|---------|----------|
| The user edits a layer and sees stale data | `dataChanged` → `DataCache.invalidate(bucket)` |
| Core is QGIS-agnostic and cannot listen to signals | Wiring lives in `gui/`; core only exposes `invalidate()` |
| Three drill layers share one cache bucket | `_DRILL_BUCKETS` normalizes to `drill` |
| The section line is the base geometry for everything | The `section` bucket invalidates the entire cache |
| Reconnecting would leave orphan callbacks | `connect()` starts with `disconnect()` (idempotent) |

> [!important] Core boundary
> Core (`DataCache`) **does not import QGIS**. This manager, in `gui/`, is the one that knows `QgsMapLayer.dataChanged` and calls the pure `invalidate` method. It is an event adapter.

---

## 🧬 Relationship diagram

```mermaid
graph TD
    IV["plugin/input_validator.py<br/>_get_and_validate_inputs"] -->|connect(layers)| LNM["LayerNotificationManager"]
    IV -->|disconnect_layer_notifications| LNM
    SP["sec_interp_plugin.py<br/>SafeLoader.lazy_load"] -->|data_cache| LNM
    LNM --> DC["DataCache (core)"]
    LNM -->|dataChanged.connect| L1["topo (raster)"]
    LNM -->|dataChanged.connect| L2["section (line)"]
    LNM -->|dataChanged.connect| L3["geol (outcrop)"]
    LNM -->|dataChanged.connect| L4["struct"]
    LNM -->|dataChanged.connect| L5["drill_collar / survey / interval → drill"]
    CB["_create_invalidation_callback(bucket)"] -.->|closure| LNM

    classDef gui fill:#4ecdc4,stroke:#0a9396,stroke-width:2px,color:#000
    classDef core fill:#ffd43b,stroke:#e67700,stroke-width:2px,color:#000
    class IV,SP,LNM,L1,L2,L3,L4,L5,CB gui
    class DC core
```

> [!tip] How to read
> Yellow = core. The manager is the boundary: it listens to QGIS and calls core.

---

## 📦 Imports — architectural reading

```python
from __future__ import annotations
import contextlib
from typing import Any

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

_DRILL_BUCKETS = {"drill_collar", "drill_survey", "drill_interval"}
```

| # | Observation |
|---|-------------|
| ① | **Zero QGIS imports**: the layer arrives as `Any`, keeping the module testable with fakes. |
| ② | `contextlib.suppress(Exception)` tolerates already-dead disconnections. |
| ③ | `_DRILL_BUCKETS` is the module's only normalization constant. |

---

## 🧱 Code walkthrough — `LayerNotificationManager`

### `__init__(data_cache)`

```python
def __init__(self, data_cache: Any) -> None:
    self.data_cache = data_cache
    self._connected_layers: list[tuple[Any, Any]] = []
```

It stores the cache and the list of `(layer, callback)` pairs so it can disconnect **exactly** the connected callback (not any slot).

### `connect(layers)` — idempotent and normalized

```python
def connect(self, layers: dict[str, Any]) -> None:
    self.disconnect()
    for bucket, layer in layers.items():
        if not layer:
            continue

        cache_bucket = "drill" if bucket in _DRILL_BUCKETS else bucket
        callback = self._create_invalidation_callback(cache_bucket)
        layer.dataChanged.connect(callback)
        self._connected_layers.append((layer, callback))
        logger.debug(
            f"Connected cache invalidation to layer: {layer.name()} -> bucket: {cache_bucket}"
        )
```

| Incoming `bucket` | Applied `cache_bucket` |
|-------------------|------------------------|
| `topo` | `topo` |
| `section` | `section` |
| `geol` | `geol` |
| `struct` | `struct` |
| `drill_collar` | `drill` |
| `drill_survey` | `drill` |
| `drill_interval` | `drill` |

The dictionary is built by `plugin/input_validator.py::_collect_active_layers()` from `PreviewParams`.

### `disconnect()` — tolerant cleanup

```python
def disconnect(self) -> None:
    for layer, callback in self._connected_layers:
        with contextlib.suppress(Exception):
            layer.dataChanged.disconnect(callback)
    self._connected_layers.clear()
    logger.debug("Layer signals disconnected")
```

### `_create_invalidation_callback(bucket)` — the closure

```python
def _create_invalidation_callback(self, bucket: str):
    """The ``section`` bucket is the base geometry and invalidates all cache buckets."""

    def callback() -> None:
        if bucket == "section":
            return self.data_cache.invalidate()
        return self.data_cache.invalidate(bucket)

    return callback
```

> [!important] Why `section` invalidates everything
> The section line is the **base geometry** of the entire section: if it changes, topography, geology, structures, and drillholes are no longer valid. `DataCache.invalidate()` with no arguments empties all buckets (`topo`, `geol`, `struct`, `drill`).

---

## 🏛️ Design patterns present

| Pattern | Where | Purpose |
|---------|-------|---------|
| **Adapter (event bridge)** | `LayerNotificationManager` | QGIS signal → core method |
| **Closure / Callback factory** | `_create_invalidation_callback` | Captures the bucket per connection |
| **Idempotent connect** | `connect()` → `disconnect()` | Avoids duplicate callbacks |
| **Tracked connections** | `_connected_layers` | Precise disconnection |
| **Graceful degradation** | `contextlib.suppress(Exception)` | Safe cleanup |

---

## 🧾 API summary

| Symbol | Signature | Typical use |
|--------|-----------|-------------|
| `LayerNotificationManager(data_cache)` | `__init__` | Create with `controller.data_cache` |
| `connect(layers)` | `dict[str, Any] -> None` | Arm notifications after validation |
| `disconnect()` | `-> None` | Disarm on dialog cleanup |
| `_create_invalidation_callback(bucket)` | `-> Callable[[], None]` | Invalidation closure |
| `_DRILL_BUCKETS` | `set[str]` | `drill_*` → `drill` normalization |

---

## 👀 Observations and notes

> [!success] Strengths
> - **Clean boundary**: core stays QGIS-agnostic; only the GUI knows `dataChanged`.
> - Explicit drill-bucket normalization.
> - Idempotent `connect()` and precise per-callback `disconnect()`.

> [!warning] Points of attention
> - `logger.debug` calls `layer.name()`: it assumes the layer object implements the `QgsMapLayer` API.
> - `_create_invalidation_callback` annotates `bucket: str` but not `-> Callable`; the return type stays implicit.
> - Only `dataChanged` is invalidated; **style** or field-definition changes may not emit it.
> - The `main` bucket used by `controller` is not notified here: it is not mapped in `_collect_active_layers`.

> [!question] Open questions
> - Should `layerModified`/`repaintRequested` also be listened to, to cover more mutations?
> - Should `DataCache` expose the set of valid buckets to avoid magic strings?

---

## 🔗 Related notes

- [[data_cache]] — `invalidate(bucket)` and per-bucket TTL
- [[controller]] — owns `DataCache`
- [[sec_interp_plugin]] — creates the manager via `SafeLoader.lazy_load`
- [[plugin_mixins]] — `InputValidationMixin` connects/disconnects
- [[Index]] — vault index

---

*Note of the SecInterp Code Walkthrough vault — v3.8.0*
