---
tags:
  - secinterp
  - code-walkthrough
  - gui
  - adapters
aliases:
  - layer_resolver.py
  - LayerResolver
  - resolve_layer
cssclass: secinterp-note
---

# `gui/adapters/layer_resolver.py`

> [!abstract] Resumen en una línea
> Servicio centralizado de resolución de capas (con caché singleton a nivel de clase) que convierte referencias ID, nombre u objeto en `QgsMapLayer` válidas vía `QgsProject`, para que ningún diálogo repita la lógica de `mapLayer`/`mapLayersByName`.

**Ruta**: `gui/adapters/layer_resolver.py` (113 líneas)
**Clase principal**: `LayerResolver` (más la función legado `resolve_layer`)
**Capa**: GUI · Adapter (lado Extract, depende de `QgsProject`)
**Tags**: #secinterp #gui #adapters

---

## 🎯 ¿Por qué existe este archivo?

Cada diálogo del plugin recibe capas como IDs guardados en settings, nombres
elegidos en combos u objetos ya resueltos. Sin un punto único, cada página
repetiría `QgsProject.instance().mapLayer(...)` con sus propias ramas de fallo:

| Problema | Solución |
|----------|----------|
| Tres formas de referencia (ID, nombre, objeto) en cada diálogo | `LayerResolver.resolve(layer_ref)` acepta las tres |
| `project.mapLayer()` repetido en cada transacción es costoso | Caché de clase `_cache` con doble clave (ID + nombre) |
| Capas eliminadas dejan referencias colgadas en caché | Validación `isValid()` al leer caché + `invalidate()` / `clear_cache()` |
| Código antiguo importa un `resolve_layer` suelto | Wrapper legado `resolve_layer()` que delega en la clase |

> [!important] Nota arquitectónica
> Vive en `gui/adapters` porque depende de `QgsProject.instance()` — el core
> tiene prohibido resolver capas (ver regla en `core/AGENTS.md`). Es un
> **Registry/Cache singleton** (estado a nivel de clase, solo `classmethod`s, sin
> instancias): la caché vive durante toda la sesión QGIS salvo invalidación.

---

## 🧬 Diagrama de relaciones

```mermaid
graph TD
    LR["LayerResolver"]
    CACHE["_cache: dict[str, QgsMapLayer]"]
    PROJ["QgsProject.instance()"]
    WRAP["resolve_layer() (legado)"]

    DLG["Diálogos / páginas GUI"]
    VAL["validation_extractor._resolve_layer"]
    LNM["layer_notification_manager"]

    DLG -->|resolve(ref)| LR
    WRAP -.->|delega| LR
    LR --> CACHE
    LR -->|mapLayer / mapLayersByName| PROJ
    VAL -.->|lógica paralela sin caché| PROJ
    LNM -.->|invalida al cambiar capas| LR

    classDef gui fill:#ffe08a,stroke:#b8860b,stroke-width:2px,color:#000
    class LR,CACHE,WRAP,DLG,VAL,LNM gui
    classDef qgis fill:#d0bfff,stroke:#5f3dc4,stroke-width:2px,color:#000
    class PROJ qgis
```

> [!tip] Cómo leer
> Flecha sólida = usa; punteada = delega o lógica paralela. `LayerResolver` es el
> único camino con caché hacia `QgsProject`; `validation_extractor` resuelve por
> su cuenta sin caché (ver observaciones).

---

## 📦 Imports — lectura arquitectónica

```python
# gui/adapters/layer_resolver.py
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qgis.core import QgsProject

if TYPE_CHECKING:
    from qgis.core import QgsMapLayer
```

| # | Observación |
|---|-------------|
| ① | Un único import QGIS en runtime (`QgsProject`): el módulo solo necesita el proyecto, ni capas ni geometrías. |
| ② | `QgsMapLayer` solo bajo `TYPE_CHECKING`: **cero coste en runtime** y cero riesgo de import circular; solo anota firmas. |
| ③ | Sin `qgis.PyQt`, sin `self.tr()`, sin logger: no hay mensajes de usuario ni diagnóstico — las ramas de fallo son silenciosas (`None`). |
| ④ | Sin imports del core ni de otros adapters: la hoja de dependencias más baja de `gui/adapters` (nada depende de él dentro del paquete, todo puede usarlo). |
| ⑤ | `Any` para `layer_ref` y `project`: la firma acepta literalmente cualquier cosa y decide por duck-typing (`hasattr(layer_ref, "isValid")`). |

---

## 🏗️ Inventario de estructura

**Clase:** `class LayerResolver` — 6 `classmethod`s + 1 atributo de clase.

**Atributo:**
- `_cache: dict[str, QgsMapLayer]` — caché a nivel de clase (compartida por toda la sesión).

**Métodos:**
- `resolve(layer_ref, use_cache=True)` — punto de entrada: objeto → caché → ID → nombre.
- `_resolve_from_cache(ref_str, use_cache)` — lectura con validación y auto-limpieza.
- `_resolve_by_id(project, ref_str)` — `project.mapLayer(ref)` + doble caché (ID y nombre).
- `_resolve_by_name(project, ref_str)` — `project.mapLayersByName(ref)` + doble caché (nombre e ID).
- `clear_cache()` — vacía la caché completa.
- `invalidate(layer_id)` — elimina una clave concreta.

**Función de módulo:**
- `resolve_layer(layer_ref)` — wrapper legado que delega en `LayerResolver.resolve`.

---

## 📁 Archivos del paquete

El resolver vive en el paquete `gui/adapters/` (fase Extract completa):

| Archivo | Líneas | Rol |
|---|--:|---|
| `__init__.py` | 7 | Docstring del paquete: contrato Extract-then-Compute |
| `drillhole_extractor.py` | 369 | `DrillholeExtractor` → `DrillholeContext` |
| `geology_extractor.py` | 235 | `GeologyExtractor` → `GeologyContext` |
| `geometry.py` | 226 | Helpers QGIS de geometría y muestreo DEM |
| `layer_resolver.py` | 113 | `LayerResolver` + `resolve_layer` (esta nota) |
| `structure_extractor.py` | 226 | `SectionContext` + `StructureExtractor` |
| `validation_extractor.py` | 176 | `resolve_layer_metadata`, `build_validation_params` |
| `feature_fetcher.py` | 84 | `DataFetcher` (lecturas bulk de hijas) |
| `profile_extractor.py` | 86 | `ProfileExtractor` → `ProfileData` |

---

## 📖 Recorrido método por método

### `resolve` — punto de entrada en 4 pasos

```python
@classmethod
def resolve(cls, layer_ref: Any, use_cache: bool = True) -> QgsMapLayer | None:
    if layer_ref is None:
        return None
    # 0. Check if it's already a valid QgsMapLayer
    if not isinstance(layer_ref, str):
        if hasattr(layer_ref, "isValid") and layer_ref.isValid():
            return layer_ref
        return None
    ref_str = str(layer_ref)
    # 1. Check cache first
    cached_layer = cls._resolve_from_cache(ref_str, use_cache)
    if cached_layer:
        return cached_layer
    project = QgsProject.instance()
    # 2. Try resolving by ID
    layer = cls._resolve_by_id(project, ref_str)
    if layer:
        return layer
    # 3. Try resolving by Name (fallback)
    return cls._resolve_by_name(project, ref_str)
```

| Paso | Detalle |
|------|---------|
| **0. Objeto** | No-`str` con `isValid()` verdadero se devuelve tal cual (cero I/O); no-`str` inválido o sin `isValid` → `None`. |
| **1. Caché** | Solo para `str`; respeta `use_cache=False` (lectura fresca, p. ej. tras eliminar una capa). |
| **2. Por ID** | `mapLayer(id)` — el camino canónico y más rápido. |
| **3. Por nombre** | `mapLayersByName(name)` — respaldo para settings antiguos que guardaron nombres. |

> [!note] El orden importa
> ID antes que nombre porque los IDs son únicos y estables; un nombre podría
> coincidir con varias capas (`mapLayersByName` devuelve lista y se toma la
> primera válida). Un `str` que sea a la vez ID de una capa y nombre de otra
> resuelve siempre a la del ID.

### `_resolve_from_cache` — lectura con auto-limpieza

```python
@classmethod
def _resolve_from_cache(cls, ref_str: str, use_cache: bool) -> QgsMapLayer | None:
    if use_cache and ref_str in cls._cache:
        cached_layer = cls._cache[ref_str]
        if cached_layer and cached_layer.isValid():
            return cached_layer
        # Invalidate broken cache
        del cls._cache[ref_str]
    return None
```

La caché nunca devuelve capas muertas: si la capa cacheada ya no es válida
(capa eliminada del proyecto), la entrada se borra al leerla (invalidación
perezosa) y el flujo continúa hacia `mapLayer`. Sin excepción, sin log.

### `_resolve_by_id` — resolución canónica + doble caché

```python
@classmethod
def _resolve_by_id(cls, project: Any, ref_str: str) -> QgsMapLayer | None:
    layer = project.mapLayer(ref_str)
    if layer and layer.isValid():
        cls._cache[ref_str] = layer
        # Also cache by name if possible
        cls._cache[layer.name()] = layer
        return layer
    return None
```

Al resolver por ID también cachea **por nombre**: la próxima búsqueda por nombre
acierta en caché sin tocar el proyecto. `project` se tipa `Any` para no atar el
módulo a la clase concreta en tests (mock-first).

### `_resolve_by_name` — respaldo por nombre + doble caché

```python
@classmethod
def _resolve_by_name(cls, project: Any, ref_str: str) -> QgsMapLayer | None:
    layers_by_name = project.mapLayersByName(ref_str)
    if layers_by_name:
        for lyr in layers_by_name:
            if lyr.isValid():
                cls._cache[ref_str] = lyr
                cls._cache[lyr.id()] = lyr
                return lyr
    return None
```

Espejo del anterior: cachea por nombre **y por ID**. Itera la lista porque puede
haber homónimos; devuelve la primera válida. Si ninguna es válida, `None` sin
cachear nada (no se cachean fallos: un reintento posterior puede acertar).

### `clear_cache` / `invalidate` — gestión del ciclo de vida

```python
@classmethod
def clear_cache(cls) -> None:
    """Clear the internal layer cache."""
    cls._cache.clear()

@classmethod
def invalidate(cls, layer_id: str) -> None:
    """Remove a specific layer from the cache."""
    if layer_id in cls._cache:
        del cls._cache[layer_id]
```

`clear_cache()` es el martillo (cambio de proyecto, recarga de tests);
`invalidate(layer_id)` el bisturí (el `layer_notification_manager` lo llama
cuando una capa cambia o se elimina). Nótese la asimetría: `invalidate` borra
una sola clave, pero la capa puede estar cacheada bajo dos (ID y nombre) — la
segunda queda huérfana hasta que la auto-limpieza de `_resolve_from_cache` la
detecte (ver observaciones).

### `resolve_layer` — wrapper legado

```python
def resolve_layer(layer_ref: Any) -> QgsMapLayer | None:
    """Resolve a layer reference. (Legacy wrapper).

    Delegates to LayerResolver for backward compatibility.
    """
    return LayerResolver.resolve(layer_ref)
```

Compatibilidad hacia atrás con un solo default (`use_cache=True`). El código
nuevo debe llamar a `LayerResolver.resolve` directamente.

---

## 🔄 Flujo de datos

| Fase | Entrada | Transformación | Salida |
|------|---------|----------------|--------|
| Guarda | `None` | retorno inmediato | `None` |
| Objeto | no-`str` | `hasattr(isValid)` + `isValid()` | capa tal cual o `None` |
| Caché | `str` | lookup + `isValid()` (auto-limpieza si muerta) | capa o seguir |
| Por ID | `ref_str` | `project.mapLayer` + doble caché | capa o seguir |
| Por nombre | `ref_str` | `project.mapLayersByName` + doble caché | capa o `None` |

---

## 🏛️ Patrones de diseño presentes

| Patrón | Dónde | Propósito |
|--------|-------|-----------|
| **Registry / Singleton (caché de clase)** | `_cache` + `classmethod`s | Una sola caché por sesión sin instanciar |
| **Cache-aside con doble clave** | `_resolve_by_id` / `_resolve_by_name` | ID y nombre calientan la misma entrada |
| **Lazy invalidation** | `_resolve_from_cache` | Las entradas muertas se purgan al leerlas |
| **Facade legado** | `resolve_layer()` | API antigua delegando en la nueva |

---

## 🧾 Resumen de la API

| Símbolo | Firma / Hereda | Uso típico |
|---------|----------------|------------|
| `LayerResolver` | clase solo-`classmethod` (no instanciar) | `LayerResolver.resolve(ref)` |
| `resolve` | `(layer_ref: Any, use_cache=True) -> QgsMapLayer \| None` | ID, nombre u objeto → capa |
| `_resolve_from_cache` | `(ref_str, use_cache) -> QgsMapLayer \| None` | lectura con purga |
| `_resolve_by_id` | `(project, ref_str) -> QgsMapLayer \| None` | camino canónico |
| `_resolve_by_name` | `(project, ref_str) -> QgsMapLayer \| None` | respaldo por nombre |
| `clear_cache` | `() -> None` | cambio de proyecto / tests |
| `invalidate` | `(layer_id: str) -> None` | capa eliminada o cambiada |
| `resolve_layer` | `(layer_ref) -> QgsMapLayer \| None` | compatibilidad legada |

---

## 🛡️ Manejo de errores

| Situación | Comportamiento |
|-----------|----------------|
| `layer_ref is None` | `None` inmediato |
| Objeto sin `isValid` o inválido | `None` (sin excepción) |
| Entrada de caché muerta | se borra y se sigue resolviendo |
| `mapLayer` devuelve `None`/inválido | se intenta por nombre |
| Nombre sin coincidencias | `None` (no se cachean fallos) |

> [!tip] Silencio deliberado
> Ninguna rama falla con excepción ni log: el llamador (página GUI o validador)
> decide si `None` es "capa opcional ausente" o "error mostrable". Es una
> decisión de diseño, no un olvido — pero dificulta depurar settings rotos.

---

## 🧪 Tests asociados

Sin tests dedicados en `tests/gui/` (no existe `test_layer_resolver.py`);
cobertura indirecta y base disponible:

- `tests/base_test.py` — mocks de `QgsProject` (`mock_core`) con los que un futuro test puede simular `mapLayer`/`mapLayersByName`.
- `tests/gui/test_main_dialog_validation_manager.py` — ejercita resolución de capas vía el validador.
- `tests/core/test_project_validator.py` — valida metadatos ya resueltos (el paso siguiente a `resolve`).
- `tests/integration/test_async_orchestrators.py` — composición con capas resueltas.

> [!warning] Hueco de cobertura
> El módulo es trivialmente testeable con mocks (6 métodos, sin geometría):
> caché por ID, fallback por nombre, purga de entrada muerta, `use_cache=False`
> e `invalidate` son cinco casos de manual para un `test_layer_resolver.py`.

---

## 🧵 Thread-safety, caché e i18n

| Aspecto | Detalle |
|---------|---------|
| **Hilo** | `QgsProject.instance()` solo es seguro en el hilo principal: resolver siempre antes de lanzar el `QgsTask`, nunca dentro de `run()`. |
| **Caché** | Dict de clase sin lock: seguro en el hilo principal GUI (GIL + un solo hilo lector/escritor); no compartir con hilos de fondo. |
| **Ciclo de vida** | La caché sobrevive entre ejecuciones del diálogo: llamar `clear_cache()` al cambiar de proyecto. |
| **i18n** | Nada que traducir: no hay mensajes de usuario en el módulo (retorna `None`, la GUI traduce al mostrar). |

---

## 📐 `LayerResolver` frente a `validation_extractor._resolve_layer`

| Aspecto | `LayerResolver.resolve` | `validation_extractor._resolve_layer` |
|---------|-------------------------|---------------------------------------|
| Caché | sí (`_cache` doble clave) | no (resuelve cada vez) |
| Entrada objeto | duck-typing (`hasattr isValid`) | `isinstance(layer_ref, QgsMapLayer)` |
| Fallback por nombre | `mapLayersByName` | iteración manual de `mapLayers().values()` |
| `use_cache=False` | soportado | no aplica |
| Consumidores | diálogos en general | `resolve_layer_metadata` (validación) |

> [!tip] Convergencia pendiente
> Ambos implementan "ID → nombre". `validation_extractor` podría delegar en
> `LayerResolver` y heredar la caché gratis; hoy están duplicados.

---

## 👀 Observaciones y notas

> [!success] Fortalezas
> - Punto único de resolución con orden documentado (objeto → caché → ID → nombre).
> - Doble caché (ID + nombre) calienta ambas direcciones de búsqueda.
> - Purga perezosa de entradas muertas: nunca devuelve capas eliminadas.
> - `TYPE_CHECKING` para `QgsMapLayer`: anotación sin coste runtime.

> [!warning] Puntos de atención
> - `invalidate` borra una sola clave; la entrada gemela (nombre↔ID) queda huérfana hasta la purga perezosa.
> - Fallos silenciosos (`None` sin log): un setting con ID roto es indistinguible de "capa opcional".
> - Sin lock: prohibido resolver desde `QgsTask.run()` (además `QgsProject` no es thread-safe).
> - `project` tipado `Any` diluye el contrato en `_resolve_by_id/_resolve_by_name`.

> [!question] Preguntas abiertas
> - ¿Unificar `validation_extractor._resolve_layer` sobre `LayerResolver`?
> - ¿Añadir `logger.debug` en fallos para diagnosticar settings rotos?
> - ¿Borrar ambas claves (ID + nombre) en `invalidate` buscando el objeto en caché?

---

## 🔗 Notas relacionadas

- [[Index]] — índice de la bóveda
- [[gui_adapters]] — nota de paquete de los adapters Extract
- [[validation_extractor]] — `resolve_layer_metadata` (resolución paralela sin caché)
- [[layer_validator]] — validador core de capas ya resueltas
- [[project_validator]] — validador de proyecto sobre metadatos
- [[controller]] — `ProfileController` (recibe capas resueltas vía `PreviewParams`)
- [[dtos]] — `PreviewParams` con las referencias de capa
- [[core_validation]] — validación QGIS-agnóstica posterior a la resolución

---

*Nota de la bóveda SecInterp Code Walkthrough v2 — v3.9.0*
