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

> [!abstract] Resumen en una línea
> Caché en memoria **por buckets** (`topo/geol/struct/drill`) con claves hash SHA256 y TTL + metadata LOD.

**Ruta**: `core/data_cache.py` (169 líneas)
**Clase**: `DataCache(ICacheService)`
**Capa**: Core
**Tags**: #secinterp #core #cache

---

## 🎯 ¿Por qué existe este archivo?

Sin caché, cada preview recalcula todo. Este servicio:

| Solución | Detalle |
|----------|---------|
| **Buckets por dominio** | `topo`, `geol`, `struct`, `drill` (separados) |
| **Claves hash** | `get_cache_key(params: dict)` → SHA256 de `k:v` ordenados (QGIS layers → `id()`) |
| **TTL** | `DEFAULT_TTL_SECONDS = 3600` (1 h) + `expiry` por entrada |
| **Metadata LOD** | `max_points`, `canvas_width` se guardan junto al dato |

> [!important] Cache-Aside
> El controller pregunta `get(bucket, key)` → si `None`, calcula y `set(bucket, key, data, metadata)`.

---

## 🧱 API

```python
class DataCache(ICacheService):
    def get_cache_key(self, params: dict[str, Any]) -> str: ...  # SHA256
    def get(self, bucket: str, key: str) -> Any | None: ...       # con TTL check
    def set(self, bucket: str, key: str, data: Any, metadata: dict | None = None) -> None: ...
```

| Método | Notas |
|--------|-------|
| `get_cache_key` | Ordena `params` y hashea; `hasattr(v,"id")` para capas |
| `get` | Verifica `expiry` con `time.time()` y borra si expiró |
| `set` | Guarda `{"data":..., "expiry": now+ttl, **metadata}` |

---

## 🔗 Notas relacionadas

- [[controller]] — usa `data_cache.get/set` por dominio
- [[config]] — TTL configurable

---

*Nota 28 de la bóveda SecInterp Code Walkthrough — v3.8.0*
