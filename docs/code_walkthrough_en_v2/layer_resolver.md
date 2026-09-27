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

> [!abstract] One-line summary
> Centralized layer-resolution service (with a class-level singleton cache) converting ID, name or object references into valid `QgsMapLayer`s via `QgsProject`, so no dialog repeats `mapLayer`/`mapLayersByName` logic.

**Path**: `gui/adapters/layer_resolver.py` (113 lines)
**Main class**: `LayerResolver` (plus the legacy `resolve_layer` function)
**Layer**: GUI · Adapter (Extract side, depends on `QgsProject`)
**Tags**: #secinterp #gui #adapters

---

## 🎯 Why does this file exist?

Every plugin dialog receives layers as IDs stored in settings, names picked in
combos, or already-resolved objects. Without a single choke point, each page
would repeat `QgsProject.instance().mapLayer(...)` with its own failure branches:

| Problem | Solution |
|---------|----------|
| Three reference shapes (ID, name, object) in every dialog | `LayerResolver.resolve(layer_ref)` accepts all three |
| Repeated `project.mapLayer()` per transaction is costly | Class-level `_cache` with a double key (ID + name) |
| Deleted layers leave dangling cache references | `isValid()` check on cache read + `invalidate()` / `clear_cache()` |
| Legacy code imports a loose `resolve_layer` | Legacy `resolve_layer()` wrapper delegating to the class |

> [!important] Architectural note
> It lives in `gui/adapters` because it depends on `QgsProject.instance()` — the
> core is forbidden from resolving layers (see the rule in `core/AGENTS.md`). It is
> a **Registry/Cache singleton** (class-level state, only `classmethod`s, no
> instances): the cache lives for the whole QGIS session unless invalidated.

---

## 🧬 Relationship diagram

```mermaid
graph TD
    LR["LayerResolver"]
    CACHE["_cache: dict[str, QgsMapLayer]"]
    PROJ["QgsProject.instance()"]
    WRAP["resolve_layer() (legacy)"]

    DLG["GUI dialogs / pages"]
    VAL["validation_extractor._resolve_layer"]
    LNM["layer_notification_manager"]

    DLG -->|resolve(ref)| LR
    WRAP -.->|delegates| LR
    LR --> CACHE
    LR -->|mapLayer / mapLayersByName| PROJ
    VAL -.->|parallel logic, no cache| PROJ
    LNM -.->|invalidates on layer change| LR

    classDef gui fill:#ffe08a,stroke:#b8860b,stroke-width:2px,color:#000
    class LR,CACHE,WRAP,DLG,VAL,LNM gui
    classDef qgis fill:#d0bfff,stroke:#5f3dc4,stroke-width:2px,color:#000
    class PROJ qgis
```

> [!tip] How to read
> Solid arrow = uses; dashed = delegates or parallel logic. `LayerResolver` is the
> only cached path to `QgsProject`; `validation_extractor` resolves on its own
> without a cache (see observations).

---

## 📦 Imports — architectural reading

```python
# gui/adapters/layer_resolver.py
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qgis.core import QgsProject

if TYPE_CHECKING:
    from qgis.core import QgsMapLayer
```

| # | Observation |
|---|-------------|
| ① | A single runtime QGIS import (`QgsProject`): the module only needs the project — no layers, no geometries. |
| ② | `QgsMapLayer` only under `TYPE_CHECKING`: **zero runtime cost** and zero circular-import risk; annotates signatures only. |
| ③ | No `qgis.PyQt`, no `self.tr()`, no logger: no user messages or diagnostics — failure branches are silent (`None`). |
| ④ | No core or sibling-adapter imports: the lowest dependency leaf of `gui/adapters` (nothing inside the package depends on it, everything may use it). |
| ⑤ | `Any` for `layer_ref` and `project`: the signature literally accepts anything and decides by duck-typing (`hasattr(layer_ref, "isValid")`). |

---

## 🏗️ Structure inventory

**Class:** `class LayerResolver` — 6 `classmethod`s + 1 class attribute.

**Attribute:**
- `_cache: dict[str, QgsMapLayer]` — class-level cache (shared across the session).

**Methods:**
- `resolve(layer_ref, use_cache=True)` — entry point: object → cache → ID → name.
- `_resolve_from_cache(ref_str, use_cache)` — read with validation and self-cleaning.
- `_resolve_by_id(project, ref_str)` — `project.mapLayer(ref)` + double caching (ID and name).
- `_resolve_by_name(project, ref_str)` — `project.mapLayersByName(ref)` + double caching (name and ID).
- `clear_cache()` — empties the whole cache.
- `invalidate(layer_id)` — removes one key.

**Module function:**
- `resolve_layer(layer_ref)` — legacy wrapper delegating to `LayerResolver.resolve`.

---

## 📁 Files in the package

The resolver lives in the `gui/adapters/` package (the full Extract phase):

| File | Lines | Role |
|---|--:|---|
| `__init__.py` | 7 | Package docstring: Extract-then-Compute contract |
| `drillhole_extractor.py` | 369 | `DrillholeExtractor` → `DrillholeContext` |
| `geology_extractor.py` | 235 | `GeologyExtractor` → `GeologyContext` |
| `geometry.py` | 226 | QGIS geometry helpers and DEM sampling |
| `layer_resolver.py` | 113 | `LayerResolver` + `resolve_layer` (this note) |
| `structure_extractor.py` | 226 | `SectionContext` + `StructureExtractor` |
| `validation_extractor.py` | 176 | `resolve_layer_metadata`, `build_validation_params` |
| `feature_fetcher.py` | 84 | `DataFetcher` (bulk child reads) |
| `profile_extractor.py` | 86 | `ProfileExtractor` → `ProfileData` |

---

## 📖 Method-by-method walkthrough

### `resolve` — 4-step entry point

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

| Step | Detail |
|------|--------|
| **0. Object** | Non-`str` with a truthy `isValid()` is returned as-is (zero I/O); invalid non-`str` or without `isValid` → `None`. |
| **1. Cache** | `str` only; honours `use_cache=False` (fresh read, e.g. after deleting a layer). |
| **2. By ID** | `mapLayer(id)` — the canonical, fastest path. |
| **3. By name** | `mapLayersByName(name)` — fallback for legacy settings that stored names. |

> [!note] Order matters
> ID before name because IDs are unique and stable; a name may match several
> layers (`mapLayersByName` returns a list and the first valid one wins). A `str`
> that is both one layer's ID and another's name always resolves to the ID one.

### `_resolve_from_cache` — self-cleaning read

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

The cache never returns dead layers: when the cached layer is no longer valid
(layer removed from the project), the entry is deleted on read (lazy
invalidation) and the flow continues to `mapLayer`. No exception, no log.

### `_resolve_by_id` — canonical resolution + double cache

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

Resolving by ID also caches **by name**: the next name lookup hits the cache
without touching the project. `project` is typed `Any` to keep the module
decoupled from the concrete class in tests (mock-first).

### `_resolve_by_name` — name fallback + double cache

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

Mirror of the previous one: caches by name **and by ID**. Iterates the list
because homonyms may exist; returns the first valid one. When none is valid,
`None` with nothing cached (failures are not cached: a later retry may succeed).

### `clear_cache` / `invalidate` — lifecycle management

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

`clear_cache()` is the hammer (project switch, test reload);
`invalidate(layer_id)` the scalpel (`layer_notification_manager` calls it when a
layer changes or is removed). Note the asymmetry: `invalidate` deletes a single
key, but the layer may be cached under two (ID and name) — the twin stays
orphaned until `_resolve_from_cache` self-cleaning spots it (see observations).

### `resolve_layer` — legacy wrapper

```python
def resolve_layer(layer_ref: Any) -> QgsMapLayer | None:
    """Resolve a layer reference. (Legacy wrapper).

    Delegates to LayerResolver for backward compatibility.
    """
    return LayerResolver.resolve(layer_ref)
```

Backward compatibility with a single default (`use_cache=True`). New code should
call `LayerResolver.resolve` directly.

---

## 🔄 Data flow

| Phase | Input | Transformation | Output |
|-------|-------|----------------|--------|
| Guard | `None` | immediate return | `None` |
| Object | non-`str` | `hasattr(isValid)` + `isValid()` | layer as-is or `None` |
| Cache | `str` | lookup + `isValid()` (self-clean when dead) | layer or continue |
| By ID | `ref_str` | `project.mapLayer` + double cache | layer or continue |
| By name | `ref_str` | `project.mapLayersByName` + double cache | layer or `None` |

---

## 🏛️ Design patterns present

| Pattern | Where | Purpose |
|---------|-------|---------|
| **Registry / Singleton (class cache)** | `_cache` + `classmethod`s | One cache per session with no instantiation |
| **Cache-aside with double key** | `_resolve_by_id` / `_resolve_by_name` | ID and name warm the same entry |
| **Lazy invalidation** | `_resolve_from_cache` | Dead entries purged on read |
| **Legacy facade** | `resolve_layer()` | Old API delegating to the new one |

---

## 🧾 API summary

| Symbol | Signature / Inherits | Typical use |
|--------|----------------------|-------------|
| `LayerResolver` | `classmethod`-only class (do not instantiate) | `LayerResolver.resolve(ref)` |
| `resolve` | `(layer_ref: Any, use_cache=True) -> QgsMapLayer \| None` | ID, name or object → layer |
| `_resolve_from_cache` | `(ref_str, use_cache) -> QgsMapLayer \| None` | purging read |
| `_resolve_by_id` | `(project, ref_str) -> QgsMapLayer \| None` | canonical path |
| `_resolve_by_name` | `(project, ref_str) -> QgsMapLayer \| None` | name fallback |
| `clear_cache` | `() -> None` | project switch / tests |
| `invalidate` | `(layer_id: str) -> None` | removed or changed layer |
| `resolve_layer` | `(layer_ref) -> QgsMapLayer \| None` | legacy compatibility |

---

## 🛡️ Error handling

| Situation | Behaviour |
|-----------|-----------|
| `layer_ref is None` | Immediate `None` |
| Object without `isValid` or invalid | `None` (no exception) |
| Dead cache entry | deleted, resolution continues |
| `mapLayer` returns `None`/invalid | name lookup attempted |
| Name with no matches | `None` (failures not cached) |

> [!tip] Deliberate silence
> No branch raises or logs: the caller (GUI page or validator) decides whether
> `None` means "missing optional layer" or "showable error". A design decision,
> not an omission — though it complicates debugging broken settings.

---

## 🧪 Associated tests

No dedicated tests under `tests/gui/` (there is no `test_layer_resolver.py`);
indirect coverage and available base:

- `tests/base_test.py` — `QgsProject` mocks (`mock_core`) with which a future test can fake `mapLayer`/`mapLayersByName`.
- `tests/gui/test_main_dialog_validation_manager.py` — exercises layer resolution via the validator.
- `tests/core/test_project_validator.py` — validates already-resolved metadata (the step after `resolve`).
- `tests/integration/test_async_orchestrators.py` — composition with resolved layers.

> [!warning] Coverage gap
> The module is trivially mock-testable (6 methods, no geometry): ID cache, name
> fallback, dead-entry purge, `use_cache=False` and `invalidate` are five
> textbook cases for a `test_layer_resolver.py`.

---

## 🧵 Thread-safety, cache and i18n

| Aspect | Detail |
|--------|--------|
| **Thread** | `QgsProject.instance()` is only safe on the main thread: always resolve before launching the `QgsTask`, never inside `run()`. |
| **Cache** | Unlocked class dict: safe on the single-threaded GUI (GIL + one reader/writer); never share with background threads. |
| **Lifecycle** | The cache outlives dialog runs: call `clear_cache()` on project switch. |
| **i18n** | Nothing to translate: no user messages in the module (returns `None`; the GUI translates on display). |

---

## 📐 `LayerResolver` vs `validation_extractor._resolve_layer`

| Aspect | `LayerResolver.resolve` | `validation_extractor._resolve_layer` |
|--------|-------------------------|---------------------------------------|
| Cache | yes (double-key `_cache`) | no (resolves every time) |
| Object input | duck-typing (`hasattr isValid`) | `isinstance(layer_ref, QgsMapLayer)` |
| Name fallback | `mapLayersByName` | manual `mapLayers().values()` iteration |
| `use_cache=False` | supported | not applicable |
| Consumers | dialogs in general | `resolve_layer_metadata` (validation) |

> [!tip] Pending convergence
> Both implement "ID → name". `validation_extractor` could delegate to
> `LayerResolver` and get caching for free; today they are duplicated.

---

## 👀 Observations and notes

> [!success] Strengths
> - Single resolution point with documented order (object → cache → ID → name).
> - Double cache (ID + name) warms both lookup directions.
> - Lazy purge of dead entries: never returns removed layers.
> - `TYPE_CHECKING` for `QgsMapLayer`: annotation with zero runtime cost.

> [!warning] Points of attention
> - `invalidate` deletes one key; the twin entry (name↔ID) stays orphaned until lazy purge.
> - Silent failures (`None`, no log): a setting with a broken ID is indistinguishable from "optional layer".
> - No lock: resolving from `QgsTask.run()` is forbidden (`QgsProject` is not thread-safe anyway).
> - `project` typed `Any` dilutes the contract in `_resolve_by_id`/`_resolve_by_name`.

> [!question] Open questions
> - Unify `validation_extractor._resolve_layer` on top of `LayerResolver`?
> - Add `logger.debug` on failures to diagnose broken settings?
> - Delete both keys (ID + name) in `invalidate` by looking the object up in the cache?

---

## 🔗 Related notes

- [[Index]] — vault index
- [[gui_adapters]] — Extract adapters package note
- [[validation_extractor]] — `resolve_layer_metadata` (parallel cache-less resolution)
- [[layer_validator]] — core validator of resolved layers
- [[project_validator]] — project validator over metadata
- [[controller]] — `ProfileController` (receives resolved layers via `PreviewParams`)
- [[dtos]] — `PreviewParams` holding the layer references
- [[core_validation]] — QGIS-agnostic validation after resolution

---

*Note of the SecInterp Code Walkthrough v2 vault — v3.9.0*
