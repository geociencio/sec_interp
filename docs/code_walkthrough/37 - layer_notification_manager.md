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

> [!abstract] Resumen en una línea
> Conecta `layer.dataChanged` → `DataCache.invalidate` (por bucket) para invalidación automática.

**Ruta**: `gui/layer_notification_manager.py` (73 líneas)
**Clase**: `LayerNotificationManager`
**Capa**: GUI
**Tags**: #secinterp #gui #cache

---

## 🎯 ¿Por qué existe este archivo?

Si el usuario edita una capa, el caché debe invalidarse. Este manager **cablea**:

| Bucket | Capas |
|--------|-------|
| `section` → invalida **todo** | línea base |
| `drill_*` → `drill` | collar/survey/interval |
| `topo/geol/struct` | raster/line/outcrop/structure |

---

## 🧱 API

```python
class LayerNotificationManager:
    def __init__(self, data_cache): ...
    def connect(self, layers: dict[str, QgsMapLayer]): ...  # layer.dataChanged → invalidate(bucket)
    def disconnect(self): ...  # suppress + clear
    def _create_invalidation_callback(self, bucket): ...  # closure con bucket
```

---

## 🔗 Notas relacionadas

- [[10 - controller]] — posee `DataCache`
- [[28 - data_cache]] — buckets/TTL

---

*Nota 37 de la bóveda SecInterp Code Walkthrough — v3.8.0*
