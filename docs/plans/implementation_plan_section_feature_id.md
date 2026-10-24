# Implementation Plan — Fix `section_feature_id` in the sampled section

**Status**: PROPUESTO — pendiente de aprobación
**Created**: 2026-10-24
**Scope**: selección de feature en `SectionPage`, propagación a preview/export y LOD
**Branch propuesta**: `fix/section-feature-id` (desde `main`)

---

## 1. Resumen ejecutivo

`PreviewParams.section_feature_id` existe, se persiste, entra en el hash de preview y
en las claves de caché, pero **no cambia la sección muestreada**:

1. `SectionPage` no tiene selector: `section_feature_id` es siempre `None` (comentario
   “future multi-line selector” en `section_page.py:90`). El primer feature siempre gana.
2. Aunque se fije por código o se restaure de un proyecto, los callers de extracción
   llaman a los extractores **sin** `feature_id`. Los extractores ya lo soportan; el
   plan es conectarlo de extremo a extremo.

**Resultado esperado**: con una capa de línea multi-feature, seleccionar el feature B
produce topografía, geología, estructuras, sondajes, estadísticas DEM, validación y
export basados en B; el LOD se calcula con la longitud de B; el feature A y B no
comparten caché.

---

## 2. Ground truth

### 2.1 Lo que ya funciona

| Pieza | Estado |
|---|---|
| `PreviewParams.section_feature_id: int \| None` | Existe (`core/domain/dtos.py`) |
| `resolve_section_feature/geometry(layer, feature_id)` | Implementado; `None` = primer feature |
| `ProfileExtractor.extract_profile(..., feature_id=...)` | Acepta `feature_id` |
| `ProfileExtractor.calculate_lod_interval(..., feature_id=...)` | Acepta `feature_id` |
| `GeologyExtractor.extract_context(..., feature_id=...)` | Acepta `feature_id` |
| `StructureExtractor.extract_section_and_structures(..., feature_id=...)` | Acepta `feature_id` |
| `DrillholeExtractor.extract_context(..., feature_id=...)` | Acepta `feature_id` |
| Hash de preview | Incluye `section_feature_id` (`preview_param_hasher.py:112`) |
| Claves de caché de componentes | Incluyen `section_feature_id` (`profile/cache.py`) |
| Validación / stats DEM / invalidación geométrica | Ya pasan el id |

### 2.2 Callers que lo omiten

| Archivo:línea | Llamada actual | Falta |
|---|---|---|
| `core/services/profile/topography.py:55` | `extract_profile(line, raster, band)` | `feature_id=params.section_feature_id` |
| `core/services/profile/geology.py:57` | `extract_context(..., smoothing_window_m=...)` | `feature_id=params.section_feature_id` |
| `core/services/profile/structures.py:55` | `extract_section_and_structures(line, struct, buffer)` | `feature_id=params.section_feature_id` |
| `core/services/profile/drillholes.py:60` | `extract_context(..., band_num)` | `feature_id=params.section_feature_id` |
| `core/services/preview_service.py:125` | `calculate_lod_interval(line, canvas_width)` | `params.section_feature_id` |
| `core/services/preview_service.py:129` | `extract_profile(..., interval=...)` | `feature_id=params.section_feature_id` |
| `core/services/preview_service.py:154` | `extract_section_and_structures(line, struct, buffer)` | `params.section_feature_id` |
| `gui/preview_task_orchestrator.py:74` | `extract_context(...)` geología | `feature_id=params.section_feature_id` |
| `gui/preview_task_orchestrator.py:126` | `extract_context(...)` sondajes | `feature_id=params.section_feature_id` |

### 2.3 UI

`gui/ui/pages/section_page.py` (269 líneas):

- `section_feature_id` se declara en `_setup_ui` (línea 92) pero no hay widget.
- `get_data`/`dump` lo publican (líneas 184/192).
- `load`/`reset` lo restauran/limpian (203/209).
- `update_dem_stats` y `validate` ya usan `resolve_section_geometry(..., id)`.

No existe ningún `QComboBox` de features en `gui/`.

---

## 3. Diseño propuesto

### 3.1 Nuevo selector de feature

Crear `gui/ui/pages/section_feature_selector.py`:

```python
class SectionFeatureSelector(QComboBox):
    featureChanged = pyqtSignal()

    def set_layer(self, layer) -> None: ...
    def selected_feature_id(self) -> int | None: ...
    def select_feature(self, feature_id: int | None) -> bool: ...
```

Comportamiento:

- `set_layer(None|inválida|sin features)` → combo vacío, deshabilitado,
  `selected_feature_id() -> None`; el consumidor conserva el fallback “primer feature”.
- Una feature → seleccionarla, combo visible/deshabilitado (o texto único) para dejar
  claro que no hay elección.
- Varias features → entradas con `fid` y, si existe un campo de nombre/display,
  `"{fid} — {label}"`; sin campo, `"{fid}"`.
- Cap de seguridad: máximo 500 features listados (las capas de sección no deberían
  acercarse); si se supera, listar las primeras y dejar el resto fuera con un warning.
- `select_feature(fid)` devuelve `False` si el fid no existe (para `load`).
- No bloquea señales al usuario; `set_layer` sí debe hacerlo para evitar emisiones en
  cascada.

`SectionPage` solo añade el widget en la fila 2 y llama a su API; la lógica de poblado
queda fuera de la página para no superar 300 líneas.

### 3.2 `SectionPage`

- Importar `QComboBox`/selector; añadir `self.feature_selector` en `_setup_ui`
  (fila 2, debajo de la línea).
- `self.section_feature_id` pasa a ser el valor de `feature_selector.selected_feature_id()`.
- `_on_line_layer_changed()`:
  - `feature_selector.set_layer(line_combo.currentLayer())`;
  - `section_feature_id = feature_selector.selected_feature_id()`;
  - `update_dem_stats()`;
  - `dataChanged.emit()`.
- `connect_signals`: conectar `line_combo.layerChanged` a `_on_line_layer_changed` y
  `feature_selector.featureChanged` a un slot que actualice id, stats y `dataChanged`.
  `disconnect_signals` debe desconectar ambos (hoy hay un patrón duplicado; limpiar sin
  romper el contrato de la página).
- `load`: tras restaurar la capa, `select_feature(data.get("section_feature_id"))`; si el
  fid ya no existe, seleccionar la primera y persistir `None`/primer fid.
- `reset`: `feature_selector.set_layer(None)` y `section_feature_id = None`.
- `get_data`/`dump`: sin cambios de esquema (siguen publicando `int|None`).
- `validate`: si hay capa con features y el fid seleccionado no existe, devolver error
  explícito; si no hay selección (`None`), validar el primer feature como hoy.
- `update_dem_stats` no cambia: ya usa `self.section_feature_id`.

### 3.3 Propagación core/preview/export

Sin cambios de firma en extractores; solo pasar el argumento:

- `core/services/profile/topography.py`
- `core/services/profile/geology.py`
- `core/services/profile/structures.py`
- `core/services/profile/drillholes.py`
- `core/services/preview_service.py` (LOD, topo, structures)
- `gui/preview_task_orchestrator.py` (geología, sondajes)

El path de **export** (`ProfileController.generate_profile_data` → handlers) queda
cubierto por los cuatro handlers. El path de **preview interactivo** queda cubierto por
`PreviewService` + los dos tasks asíncronos.

### 3.4 LOD

`calculate_lod_interval(line_lyr, canvas_width, feature_id)` ya calcula la longitud con
`resolve_section_geometry`; solo falta pasar el id desde `PreviewService`. Con eso, una
línea de 100 m y otra de 200 m generan intervalos distintos aunque compartan capa.

### 3.5 Caché / invalidación

No se toca la clave: ya incluye `section_feature_id` en topo/geol/struct/drill. El bug
era que el id no llegaba al extractor; una vez conectado, A y B tendrán claves distintas
y no habrá datos cruzados.

`preview_param_hasher` ya incluye el id; el selector debe emitir `dataChanged` para que
el preview se regenere al cambiar de feature.

`dialog_preview_manager._handle_geometric_changes` ya resuelve la geometría con el id;
no requiere cambios.

---

## 4. Tests

### Unitarios

| Test | Cobertura |
|---|---|
| `tests/gui/test_section_feature_selector.py` | poblado 0/1/N features, labels, `selected_feature_id`, `select_feature` inválido, cap, señales |
| `tests/gui/test_section_page.py` | cambio de capa repuebla, cambio de feature actualiza id/stats/dataChanged, load/reset, validate fid inválido |
| `tests/gui/test_preview_task_orchestrator.py` | geología y sondajes reciben `feature_id` |
| `tests/core/test_preview_service.py` | LOD, topo y structures reciben `feature_id` |
| `tests/core/test_controller_characterization.py` o nuevo `test_profile_feature_id.py` | los cuatro handlers pasan el id al extractor |
| `tests/core/test_profile_cache.py` | ya cubre que el id cambia la clave; añadir caso feature A/B |

### Integración

- Capa con dos líneas (`fid=7`, longitud 100; `fid=9`, longitud 200):
  - `extract_profile(..., feature_id=9)` devuelve ~200 m, no 100.
  - `calculate_lod_interval(..., feature_id=9)` usa 200.
  - geología/estructuras/sondajes usan la línea 9.
  - `generate_profile_data` con `section_feature_id=9` produce datos distintos de 7.
  - export usa la línea 9.
- Regresión: `feature_id=None` sigue usando el primer feature.

### Gates

- `PYTHONPATH=.. .venv/bin/python -m unittest discover tests` ≥808 OK.
- `ruff`, `format`, `mypy`, `check_docs`, `forge validate`.
- `make i18n-check` si el selector añade textos nuevos.
- `qgis-analyzer --max-cc 10`: CC/module size/i18n PASS.

---

## 5. Fases

1. **Fase 0 — Caracterización**: fixture multi-feature y tests que demuestren que hoy
   `feature_id` no llega al extractor (fallan antes del fix).
2. **Fase 1 — Propagación**: conectar los 9 callers de §2.2; sin UI. Tests de
   preview/export/LOD. Debe verse el cambio fijando `section_feature_id` por código.
3. **Fase 2 — Selector UI**: `SectionFeatureSelector` + integración en `SectionPage`,
   persistencia, señales y validación. Mantener `section_page.py` <300 líneas.
4. **Fase 3 — Integración/cierre**: test multi-feature end-to-end, docs, analyzer,
   métricas y commit.

Cada fase es un commit atómico; la rama se mergea solo con todos los gates verdes.

---

## 6. Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| Capas con miles de features | Cap de 500 + fallback al primer feature; no cargar todo en el combo |
| FIDs cambian al editar la capa | `load`/`validate` detectan fid ausente y vuelven al primero |
| Regresión del comportamiento actual | `None` sigue significando “primer feature”; tests de regresión |
| Preview no se refresca | `featureChanged` → `dataChanged`; hash ya incluye el id |
| Tasks asíncronos con datos viejos | Pasar el id al construir el contexto antes de lanzar el task |
| `SectionPage` >300 líneas | Selector en módulo aparte; solo +10 líneas en la página |
| Textos nuevos sin i18n | Usar `self.tr` en el selector y ejecutar `i18n-check` |
| Caché cruzada A/B | Claves ya incluyen el id; test explícito de dos features |

---

## 7. Criterios de aceptación

- Seleccionar el feature B cambia topografía, geología, estructuras, sondajes, stats
  DEM, validación y export.
- El LOD usa la longitud del feature seleccionado.
- A y B tienen cachés separadas; no hay datos de A en B.
- `section_feature_id` se persiste/restaura; un fid inválido no rompe la UI.
- `None` mantiene el comportamiento histórico (primer feature).
- 808+ tests OK, `section_page.py` <300 líneas, analyzer PASS.

---

**Aprobación requerida**: confirmar el alcance (propagación + selector UI) antes de
crear la rama y empezar por la Fase 0.
