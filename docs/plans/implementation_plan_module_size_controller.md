# Implementation Plan — Refactor `core/controller.py` below 300 lines

**Status**: PROPUESTO — pendiente de aprobación del usuario
**Created**: 2026-10-23
**Scope**: `core/controller.py` (465 líneas, 22 atributos de instancia)
**Related**: `docs/plans/Technical_Specification_module_size_gate.md`,
`core/controller.py`, `core/data_cache.py`, `tests/core/test_controller_*.py`

---

## 1. Resumen ejecutivo

`ProfileController` mezcla tres responsabilidades: composición de dependencias,
gestión de caché por componente y cálculo/extracción de cada componente del perfil.
La extracción de los cuatro componentes ocupa ~300 de las 465 líneas y obliga a
tocar el controlador para cualquier cambio de topografía, geología, estructuras o
sondajes.

El plan extrae **caché + procesadores de componentes** a un paquete
`core/services/profile/`, dejando `ProfileController` como fachada de DI y
orquestación. Objetivo: **<300 líneas** (margen ~100 bajo el gate de 400), sin
cambiar la API pública, los mensajes ni la semántica de caché.

**No objetivos**: cambiar el comportamiento de preview/export, alterar
`PreviewParams`, reducir el número de atributos (`GOD_OBJECT`) en esta iteración
(diferido explícitamente, ver §9), o refactorizar los otros 4 módulos >400.

---

## 2. Ground truth

| Hecho | Valor actual |
|---|---|
| `core/controller.py` | **465 líneas** (`wc -l`) |
| Gate de tamaño | **FAIL** (límite 400; objetivo del plan <300) |
| Atributos de `ProfileController` | 22 (`GOD_OBJECT`; fuera de alcance) |
| CC gate | PASS |
| Tests | 778 OK (827 static) |
| Uso externo de `controller.data_cache` | `gui/dialog_facade_mixin.py`, `gui/layer_notification_manager.py`, tests GUI |

Distribución actual:

| Bloque | Líneas aprox. | Responsabilidad |
|---|---:|---|
| `__init__` + DI + `reload_settings` | 33–107 | Composición de servicios |
| `get_cached_data` / `cache_data` | 109–132 | Caché “main” |
| `generate_profile_data` | 133–164 | Orquestación |
| `_component_cache_key` | 165–188 | Hash de inputs |
| `_process_topography` | 189–238 | Extracción + caché + mensaje |
| `_process_geology` | 239–299 | Extracción + servicio + caché + mensajes |
| `_process_structures` | 300–371 | Extracción + proyección + caché + mensajes |
| `_process_drillholes` | 372–465 | Extracción + servicio + caché |

---

## 3. Diseño propuesto

### 3.1 Estructura

```
core/services/profile/
  __init__.py          # exports internos del paquete
  cache.py             # claves de caché por componente (puro, sin Qt)
  errors.py            # errores internos de componente (sin i18n)
  drillholes.py        # process_drillholes(...)
  structures.py        # process_structures(...)
  topography.py        # process_topography(...)   [fase 3]
  geology.py           # process_geology(...)      [fase 3]
```

Cada módulo queda <200 líneas. No se añaden imports `qgis.*`; el gate
`test_architecture_boundary.py` debe seguir verde sin ampliar la allowlist.

### 3.2 Contrato de `ProfileController` (sin cambios públicos)

Se conservan:

- `generate_profile_data(params) -> tuple[...]`
- `get_cached_data(inputs)` / `cache_data(inputs, data)`
- `reload_settings()`
- `self.data_cache` (`DataCache`) y su `.clear()` usado por GUI/tests
- `_process_topography/_geology/_structures/_drillholes` como **wrappers finos**
  (los tests actuales los llaman directamente)

Los wrappers siguen siendo el **límite de traducción**: capturan errores de los
handlers y construyen los mensajes con `self.tr(...)`. Así el contexto de
traducción sigue siendo `ProfileController` y `pylupdate5` no reubica las cadenas.

### 3.3 Caché (`cache.py`)

Funciones puras, sin estado y sin Qt:

```python
def component_cache_key(**parts: Any) -> str: ...
def topography_cache_key(params: PreviewParams) -> str: ...
def geology_cache_key(params: PreviewParams) -> str: ...
def structures_cache_key(params: PreviewParams) -> str: ...
def drillholes_cache_key(params: PreviewParams) -> str: ...
```

Se mueve aquí el hash actual (MD5 sobre pares ordenados, `id()` para capas) y las
listas de inputs que hoy viven dentro de cada `_process_*`. Esto concentra el
hotspot que causó el bug de caché y permite tests unitarios de cada clave.

`DataCache` no cambia: los handlers reciben la instancia y siguen usando
`cache.get(bucket, key)` / `cache.set(bucket, key, data, meta)`.

### 3.4 Handlers de componente

Patrón común:

```python
def process_drillholes(
    params: PreviewParams,
    extractor: Any,
    service: Any,
    cache: DataCache,
    cache_meta: dict,
) -> list[DrillholeProjection] | None: ...
```

- Devuelven datos o `None`; **no** construyen mensajes de UI.
- Señalizan errores con excepciones internas de `profile/errors.py`
  (`ProfileInputError`, `ProfileServiceError`, `ProfileDataError`), sin texto
  traducible.
- Mantienen el logging de cache hit/miss en el módulo del componente.
- No conocen `ProfileController` ni Qt.

### 3.5 Mensajes (wrappers)

Ejemplo de wrapper:

```python
def _process_drillholes(self, params, cache_meta, messages):
    if not params.collar_layer:
        return None
    try:
        return process_drillholes(
            params, self.drillhole_extractor, self.drillhole_service,
            self.data_cache, cache_meta,
        )
    except ProfileServiceError:
        messages.append(self.tr("Drillholes: Service failed to load"))
        return None
```

Así se preservan:

- el contexto `ProfileController` de las traducciones;
- el orden y el texto de los mensajes actuales;
- la posibilidad de que los tests sigan inyectando mocks en
  `controller.profile_extractor`, etc. (los wrappers leen los atributos en cada
  llamada; no se capturan referencias obsoletas).

### 3.6 Por qué no mover los mensajes a los handlers

Mover `self.tr("...")` a una función libre haría que `pylupdate5` registre la
cadena bajo otro contexto (módulo/clase), mientras en runtime `ProfileController.tr`
busca bajo `ProfileController`. Los handlers puros + wrappers traductores evitan
una migración de contexto y mantienen `make i18n-check` sin cambios.

---

## 4. Fases de implementación

### Fase 0 — Baseline y tests de caracterización

- Añadir tests que fijen el comportamiento actual de mensajes/errores de los
  cuatro componentes (orden, `None`, mensajes de servicio ausente) y de
  `generate_profile_data`.
- Ejecutar baseline: 778 tests, analyzer, `wc -l`.
- **Aceptación**: tests nuevos verdes contra el código actual.

### Fase 1 — Extraer caché y claves

- Crear `profile/cache.py` con las funciones de clave.
- `get_cached_data`/`cache_data` usan las funciones de “main”.
- `_component_cache_key` se elimina del controlador; los `_process_*` siguen
  dentro y llaman a `cache.py`.
- **Aceptación**: `test_controller_cache_keys.py` verde sin cambios;
  `controller.py` ~395 líneas; sin cambios de comportamiento.

### Fase 2 — Extraer sondajes y estructuras (mínimo para <300)

- Crear `profile/errors.py`, `profile/drillholes.py`, `profile/structures.py`.
- Mover la lógica de `_process_drillholes` y `_process_structures` a handlers.
- Los `_process_*` quedan como wrappers que traducen mensajes.
- **Aceptación**: `controller.py` <300 líneas; tests de orquestación/caché
  verdes; `module_size_gate` deja de marcar `controller.py` (5 → 4 módulos >400).

### Fase 3 — Extraer topografía y geología (recomendada)

- Crear `profile/topography.py` y `profile/geology.py` con el mismo patrón.
- **Aceptación**: `controller.py` ~180–220 líneas; cada nuevo módulo <200;
  comportamiento idéntico.

### Fase 4 — Cierre

- `ruff check` / `ruff format --check`, `mypy`, `check_docs`.
- `pylupdate5` + `make i18n-check` (0 `unfinished`, contexto intacto).
- `qgis-analyzer analyze . --max-cc 10` (CC PASS; module size de controller OK).
- `sync_metrics.py` + `forge validate`; actualizar `task.md`/métricas.
- Commit por fase (atómicos) y close-session al final.

---

## 5. Tests

| Test | Cobertura |
|---|---|
| `tests/core/test_controller_cache_keys.py` | Sin cambios; garantiza que los wrappers siguen usando todas las claves |
| `tests/core/test_controller_orchestration.py` | Sin cambios; garantiza que los wrappers leen los mocks actuales |
| `tests/core/test_controller_di.py` | Sin cambios; DI y lazy load |
| `tests/core/services/profile/test_cache.py` (nuevo) | Claves incluyen capa/línea/banda/campos/suavizado; main key |
| `tests/core/services/profile/test_drillholes.py` (nuevo) | Cache hit/miss, servicio ausente, extracción nula |
| `tests/core/services/profile/test_structures.py` (nuevo) | Proyección, buffer vacío, servicio ausente |
| `tests/core/services/profile/test_topography.py` (nuevo) | Capas ausentes, extractor ausente, perfil vacío, cache |
| `tests/core/services/profile/test_geology.py` (nuevo) | Contexto, segmentos vacíos, suavizado, servicio ausente |
| `tests/core/test_architecture_boundary.py` | Los nuevos módulos no importan QGIS/Qt |

Objetivo: +12–18 tests unitarios; la suite total no debe bajar de 778.

---

## 6. Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| Cambiar el contexto/orden de los mensajes i18n | Wrappers conservan `self.tr`; tests de caracterización + `make i18n-check` |
| Tests que inyectan mocks después de `__init__` | Wrappers pasan `self.<extractor>` en cada llamada; no se cachean procesadores con dependencias fijas |
| Romper `controller.data_cache.clear()` de GUI | Se conserva `self.data_cache` como `DataCache`; los handlers lo reciben |
| Diferencias de semántica en `None`/errores | Tests de caracterización antes de mover y comparación de mensajes/valores |
| Crecimiento de un nuevo “god module” | Cada handler en su archivo, <200 líneas, sin estado compartido salvo la caché |
| `GOD_OBJECT` sigue en 22 atributos | Fuera de alcance; documentado como deuda posterior (posible `ControllerServices` en otra iteración) |
| Duplicar lógica de claves | Una sola función por componente en `cache.py`; tests de claves |

---

## 7. Criterios de aceptación

- `wc -l core/controller.py` **<300** (objetivo 180–220).
- Cada módulo nuevo **<200 líneas**.
- `module_size_gate` deja de listar `core/controller.py`; el resto de módulos
  >400 queda como deuda (4 restantes).
- `qgis-analyzer analyze . --max-cc 10`: CC **PASS**, sin nuevos issues.
- `PYTHONPATH=.. .venv/bin/python -m unittest discover tests`: **OK**, ≥778.
- `ruff`, `format`, `mypy`, `check_docs`, `forge validate`, `sync_metrics --validate`:
  PASS.
- `make i18n-check`: 0 `unfinished`; los `.ts` no pierden mensajes.
- `test_architecture_boundary`: PASS sin ampliar la allowlist.

---

## 8. Rollback

Cada fase es un commit independiente. Si una fase rompe tests o i18n:

1. `git revert <commit>` de esa fase.
2. Mantener las fases anteriores (caché y handlers ya extraídos).
3. Reabrir el plan con el test/riesgo concreto antes de reintentar.

---

## 9. Deuda diferida — `GOD_OBJECT` de `ProfileController`

El analyzer marca:

```
core/controller.py:30  [GOD_OBJECT]  LOW
Class 'ProfileController' holds 22 instance attributes (> 15)
```

**Decisión (usuario, 2026-10-23)**: no abordarlo en esta refactorización; queda
como deuda posterior. El plan de tamaño de módulo **no** promete eliminar este
issue: tras las fases 1–3 el controlador bajará de líneas, pero conservará los
mismos atributos de dependencia.

Disparador futuro (sesión aparte):

- Agrupar los lazy services (`collar_processor`, `survey_processor`,
  `interval_processor`, `trajectory_engine`, `geology_service`,
  `structure_service`, `drillhole_service`) en un `ControllerServices` o
  dataclass interno.
- Exponer propiedades de compatibilidad para los tests/DI que hoy acceden a
  `controller.collar_processor`, etc.
- Criterio de aceptación futuro: `ProfileController` ≤15 atributos, sin romper
  `test_controller_di.py` ni el contrato de `generate_profile_data`.

---

**Aprobación requerida**: confirmar alcance (fases 0–3) y objetivo <300 antes de
tocar código. La implementación empezará por la Fase 0 (tests de caracterización).
