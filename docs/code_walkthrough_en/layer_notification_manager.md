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

# 37 — `gui/layer_notification_manager.py`

> [!abstract] One-line summary
> Wires `layer.dataChanged` → `DataCache.invalidate` (per bucket) for automatic invalidation.

**Path**: `gui/layer_notification_manager.py` (73 lines)
**Class**: `LayerNotificationManager`
**Layer**: GUI
**Tags**: #secinterp #gui #cache

---

## 🎯 Why does this file exist?

If the user edits a layer, the cache must be invalidated. This manager **wires**:

| Bucket | Layers |
|--------|--------|
| `section` → invalidates **all** | base line |
| `drill_*` → `drill` | collar/survey/interval |
| `topo/geol/struct` | raster/line/outcrop/structure |

---

## 🧱 API

```python
class LayerNotificationManager:
    def __init__(self, data_cache): ...
    def connect(self, layers: dict[str, QgsMapLayer]): ...  # layer.dataChanged → invalidate(bucket)
    def disconnect(self): ...  # suppress + clear
    def _create_invalidation_callback(self, bucket): ...
```

---

## 🔗 Related notes

- [[controller]] — owns `DataCache`
- [[data_cache]] — buckets/TTL

---

*Note 37 of the SecInterp Code Walkthrough vault — v3.8.0*
