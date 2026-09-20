---
tags:
  - secinterp
  - code-walkthrough
  - core
  - cache
aliases:
  - data_cache.py
  - DataCache
cssclass: secinterp-note
---

# 28 — `core/data_cache.py`

> [!abstract] One-line summary
> In-memory **per-bucket** cache (`topo/geol/struct/drill`) with SHA256 keys and TTL + LOD metadata.

**Path**: `core/data_cache.py` (169 lines)
**Class**: `DataCache(ICacheService)`
**Layer**: Core
**Tags**: #secinterp #core #cache

---

## 🎯 Why does this file exist?

Without caching, every preview recomputes everything. This service:

| Solution | Detail |
|----------|--------|
| **Per-domain buckets** | `topo`, `geol`, `struct`, `drill` (separate) |
| **Hash keys** | `get_cache_key(params: dict)` → SHA256 of sorted `k:v` (QGIS layers → `id()`) |
| **TTL** | `DEFAULT_TTL_SECONDS = 3600` (1 h) + `expiry` per entry |
| **LOD metadata** | `max_points`, `canvas_width` stored alongside data |

> [!important] Cache-Aside
> The controller asks `get(bucket, key)` → if `None`, it computes and `set(bucket, key, data, metadata)`.

---

## 🧱 API

```python
class DataCache(ICacheService):
    def get_cache_key(self, params: dict[str, Any]) -> str: ...  # SHA256
    def get(self, bucket: str, key: str) -> Any | None: ...       # with TTL check
    def set(self, bucket: str, key: str, data: Any, metadata: dict | None = None) -> None: ...
```

| Method | Notes |
|--------|-------|
| `get_cache_key` | Sorts `params` and hashes; `hasattr(v,"id")` for layers |
| `get` | Checks `expiry` via `time.time()` and deletes if expired |
| `set` | Stores `{"data":..., "expiry": now+ttl, **metadata}` |

---

## 🔗 Related notes

- [[10 - controller]] — uses `data_cache.get/set` per domain
- [[27 - config]] — configurable TTL

---

*Note 28 of the SecInterp Code Walkthrough vault — v3.8.0*
