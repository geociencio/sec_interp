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

> [!abstract] Resumen en una línea
> Cablea la señal `dataChanged` de cada capa QGIS activa a `DataCache.invalidate`, normalizando los buckets de sondeo (`drill_*` → `drill`) y haciendo que la capa de sección invalide **todo** el caché.

**Ruta**: `gui/layer_notification_manager.py` (73 líneas)
**Clase**: `LayerNotificationManager`
**Capa**: GUI · Managers (puente QGIS → core)
**Tags**: #secinterp #gui #cache

---

## 🎯 ¿Por qué existe este archivo?

El caché de `DataCache` es válido mientras las capas no cambien. Si el usuario edita una capa en QGIS, los datos cacheados quedan obsoletos. Este manager es el **puente** entre las señales QGIS y la invalidación del core.

| Problema | Solución |
|----------|----------|
| El usuario edita una capa y ve datos viejos | `dataChanged` → `DataCache.invalidate(bucket)` |
| El core es QGIS-agnóstico y no puede escuchar señales | El wiring vive en `gui/`; el core solo expone `invalidate()` |
| Tres capas de sondeo comparten un mismo bucket de caché | `_DRILL_BUCKETS` normaliza a `drill` |
| La línea de sección es geometría base de todo | El bucket `section` invalida el caché completo |
| Reconectar dejaría callbacks huérfanos | `connect()` empieza con `disconnect()` (idempotente) |

> [!important] Frontera Core
> El core (`DataCache`) **no importa QGIS**. Este manager, en `gui/`, es quien conoce `QgsMapLayer.dataChanged` y llama al método puro `invalidate`. Es un adaptador de eventos.

---

## 🧬 Diagrama de relaciones

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

> [!tip] Cómo leer
> Amarillo = core. El manager es la frontera: escucha QGIS y llama al core.

---

## 📦 Imports — lectura arquitectónica

```python
from __future__ import annotations
import contextlib
from typing import Any

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

_DRILL_BUCKETS = {"drill_collar", "drill_survey", "drill_interval"}
```

| # | Observación |
|---|-------------|
| ① | **Cero imports de QGIS**: la capa llega como `Any`, lo que mantiene el módulo testeable con fakes. |
| ② | `contextlib.suppress(Exception)` tolera desconexiones ya caídas. |
| ③ | `_DRILL_BUCKETS` es la única constante de normalización del módulo. |

---

## 🧱 Recorrido del código — `LayerNotificationManager`

### `__init__(data_cache)`

```python
def __init__(self, data_cache: Any) -> None:
    self.data_cache = data_cache
    self._connected_layers: list[tuple[Any, Any]] = []
```

Guarda el caché y la lista de pares `(layer, callback)` para poder desconectar **exactamente** el callback conectado (no cualquier slot).

### `connect(layers)` — idempotente y con normalización

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

| `bucket` recibido | `cache_bucket` aplicado |
|-------------------|-------------------------|
| `topo` | `topo` |
| `section` | `section` |
| `geol` | `geol` |
| `struct` | `struct` |
| `drill_collar` | `drill` |
| `drill_survey` | `drill` |
| `drill_interval` | `drill` |

El diccionario lo construye `plugin/input_validator.py::_collect_active_layers()` a partir de `PreviewParams`.

### `disconnect()` — limpieza tolerante

```python
def disconnect(self) -> None:
    for layer, callback in self._connected_layers:
        with contextlib.suppress(Exception):
            layer.dataChanged.disconnect(callback)
    self._connected_layers.clear()
    logger.debug("Layer signals disconnected")
```

### `_create_invalidation_callback(bucket)` — la closure

```python
def _create_invalidation_callback(self, bucket: str):
    """The ``section`` bucket is the base geometry and invalidates all cache buckets."""

    def callback() -> None:
        if bucket == "section":
            return self.data_cache.invalidate()
        return self.data_cache.invalidate(bucket)

    return callback
```

> [!important] Por qué `section` invalida todo
> La línea de sección es la **geometría base** de toda la sección: si cambia, topografía, geología, estructuras y sondeos dejan de ser válidos. `DataCache.invalidate()` sin argumentos vacía todos los buckets (`topo`, `geol`, `struct`, `drill`).

---

## 🏛️ Patrones de diseño presentes

| Patrón | Dónde | Propósito |
|--------|-------|-----------|
| **Adapter (event bridge)** | `LayerNotificationManager` | Señal QGIS → método core |
| **Closure / Factory of callbacks** | `_create_invalidation_callback` | Captura el bucket por conexión |
| **Idempotent connect** | `connect()` → `disconnect()` | Evita callbacks duplicados |
| **Tracked connections** | `_connected_layers` | Desconexión precisa |
| **Graceful degradation** | `contextlib.suppress(Exception)` | Limpieza segura |

---

## 🧾 Resumen de la API

| Símbolo | Firma | Uso típico |
|---------|-------|------------|
| `LayerNotificationManager(data_cache)` | `__init__` | Crear con `controller.data_cache` |
| `connect(layers)` | `dict[str, Any] -> None` | Armar notificaciones tras validar |
| `disconnect()` | `-> None` | Desarmar al limpiar el diálogo |
| `_create_invalidation_callback(bucket)` | `-> Callable[[], None]` | Closure de invalidación |
| `_DRILL_BUCKETS` | `set[str]` | Normalización `drill_*` → `drill` |

---

## 👀 Observaciones y notas

> [!success] Fortalezas
> - **Frontera limpia**: core sigue siendo QGIS-agnóstico; solo el GUI conoce `dataChanged`.
> - Normalización explícita de buckets de sondeo.
> - `connect()` idempotente y `disconnect()` preciso por callback.

> [!warning] Puntos de atención
> - `logger.debug` llama a `layer.name()`: asume que el objeto capa implementa la API de `QgsMapLayer`.
> - `_create_invalidation_callback` anota `bucket: str` pero no `-> Callable`; el tipo de retorno queda implícito.
> - Solo se invalida al `dataChanged`; cambios de **estilo** o de definición de campos no necesariamente lo emiten.
> - El bucket `main` que usa `controller` no se notifica aquí: no está mapeado en `_collect_active_layers`.

> [!question] Preguntas abiertas
> - ¿Debería escucharse también `layerModified`/`repaintRequested` para cubrir más mutaciones?
> - ¿Conviene que `DataCache` exponga el conjunto de buckets válidos para evitar strings mágicos?

---

## 🔗 Notas relacionadas

- [[data_cache]] — `invalidate(bucket)` y TTL por bucket
- [[controller]] — dueño de `DataCache`
- [[sec_interp_plugin]] — crea el manager vía `SafeLoader.lazy_load`
- [[plugin_mixins]] — `InputValidationMixin` conecta/desconecta
- [[Index]] — índice de la bóveda

---

*Nota de la bóveda SecInterp Code Walkthrough — v3.8.0*
