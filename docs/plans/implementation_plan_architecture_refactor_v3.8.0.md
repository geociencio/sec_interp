# Plan de Implementación — Refactor de Arquitectura Core/GUI (v3.8.0)

## Objetivo General
Eliminar el acoplamiento de la capa `core/` con QGIS (patrón **Extract-then-Compute**) y descomponer el **God Object** `gui/main_dialog.py` + sus 9 managers. Resultado: un core 100% QGIS-agnostic, testeable sin QGIS, y una GUI desacoplada por interfaces estrechas.

## Decisiones de Arquitectura (confirmadas)

| Decisión | Elección | Justificación |
|---|---|---|
| Ambigüedad del core | **100% agnostic** (WKT / tuplas de coordenadas) | Cumple `core/AGENTS.md` al pie de la letra |
| Dependencias de geometría | **Stdlib only** (`math`, sin shapely/pyproj) | Lo que queda en core tras Extract es matemática trivial; lo duro (buffer/CRS/topología) es Extract y vive en GUI |
| Orden de ataque | **GUI primero** (Fase 2-3), core después (Fase 4) | Menor riesgo, mayor visibilidad; el core se migra con la UI estable |
| Moneda de geometría | `list[tuple[float, float]]` + WKT opcional | Evita escribir un parser WKT en stdlib; GUI hace `QgsGeometry ↔ tuplas` |

### Clasificación Extract vs Compute
| Operación actual | Naturaleza | Destino |
|---|---|---|
| `densify`, Douglas-Peucker (`decimate`/`adaptive_sample`), `project_point_to_line`, `calculate_line_azimuth`, `calculate_polyline_metrics`, `interpolate_elevation` | **Compute** (trig/interpolación) | `core` con `math` |
| `create_buffer_geometry`, `filter_features_by_buffer` | **Extract** (buffer de polígono) | `gui/adapters` (`QgsGeometry.buffer`) |
| CRS transform (`QgsCoordinateTransform`) | **Extract** | `gui/adapters` |
| Distancia elipsoidal (`QgsDistanceArea.setEllipsoid`) | Compute (planar/haversine) | `core` con `math` |
| Lectura de features (`getFeatures`, `QgsFeatureRequest`) | **Extract** | `gui/adapters` |

---

## Diagnóstico Consolidado (resumen)

- **`core/`**: 72 archivos → 30 GEOM_LAYER (violación real) + 5 grises (Qt-shim / `QgsSettings`) + 37 AGNOSTIC.
- **Fuga clave**: `core/utils/qgis.py` (`LayerResolver` → `QgsProject.instance()`) contamina `preview_service.py`, `validation_helpers.py`, `controller.py`.
- **`core/controller.py:111-158`**: `connect_layer_notifications()` cablea `layer.dataChanged` (señal QGIS) dentro del core.
- **GUI**: `SecInterpDialog` (449 líneas) + 9 managers reciben `self` (el diálogo entero). Ciclo `PreviewManager ↔ InterpretationManager`; ciclo `SecInterpPlugin ↔ diálogo`.
- **Preview**: LOD implementado 3 veces (una muerta); dos pipelines de drillhole; doble filtrado de visibilidad; 3 mecanismos de cache; ~600 líneas de código muerto.

## Guardarraíles

- **Test-gate de arquitectura** (`tests/core/test_architecture_boundary.py`): escanea `core/`, falla ante `qgis.core`/`qgis.gui`/`qgis.PyQt`/`QgsProject.instance()` no allowlistados, y fuerza a encoger la allowlist (entradas stale → fail).
- **Allowlist inicial**: 36 archivos. Meta final: allowlist vacía.
- **Baseline**: `uv run python3 -m unittest discover tests` → **592 tests, OK** (11.15s).

---

## Fases

### Fase 0 — Baseline + guardarraíles ✅ (completada)
- [x] Rama `refactor/core-gui-decoupling`.
- [x] Baseline: 592 tests OK.
- [x] Test-gate de arquitectura con allowlist de 36 archivos.
- [x] Plan guardado en `docs/plans/implementation_plan_architecture_refactor_v3.8.0.md`.

**Salida:** línea base verde + ratchet de arquitectura funcionando.

### Fase 1 — Limpieza de código muerto (bajo riesgo)
- Eliminar: `gui/lod_calculator.py`, `PreviewRenderer.export_to_image`, `PreviewLayerFactory.interpolate_elevation` (dup), pipeline drillhole sync (`preview_service._generate_drillholes` + 4 helpers), 7 constantes `DialogConfig` muertas, `active_drill_task`, import stale `main_dialog_preview`, `TYPE_CHECKING: pass`.
- Consolidar: styling categorized (1 helper), boilerplate memory-layer+CRS, `ProfileSnapper` (1 clase).
- Actualizar tests afectados.

**Salida:** ~600 líneas menos, suite verde, allowlist sin cambios.

### Fase 2 — Desacoplar God Object (GUI)
1. Interfaces estrechas (ports/ViewModels) en lugar de `self.dialog`.
2. Romper ciclo `PreviewManager ↔ InterpretationManager` con `PreviewState`/`PreviewCache`.
3. Contrato `RenderState` para `ExportManager`.
4. Protocolo `load()/dump()` en páginas.
5. `SignalManager` → event bus real (widgets → métodos de manager).
6. Split `ExportManager`; `main_dialog.py` < 300 líneas.

**Salida:** sin `self.dialog` universal; stop-condition de 300 líneas cumplido.

### Fase 3 — Consolidar preview
1. Único LOD. 2. Único pipeline drillhole (async). 3. Único filtrado de visibilidad. 4. 1 helper de render. 5. Unificar cache.

**Salida:** una fuente de verdad por responsabilidad.

### Fase 4 — Migración core → agnostic (strangler fig)
1. Crear `gui/adapters/` (Extract). 2. Mover `LayerResolver` y `connect_layer_notifications` a GUI. 3. Reimplementar `geometry_utils/*` con `math`; mover buffer/CRS arriba. 4. Migrar servicio por servicio: `data_fetcher` → `structure_service` → `geology_service` → `profile_service` → `drillhole` → `export_service`. 5. Encoger allowlist a 0.

**Salida:** `core/` libre de `qgis.*`; tests core 100% sin QGIS.

### Fase 5 — Validación DTO + settings
- `ValidationParams`/validadores aceptan layer-metadata DTO. 2. Extraer `QgsSettings` del core (`SettingsStore` inyectable).

**Salida:** validación 100% DTO-driven.

### Fase 6 — Documentación + release
- Actualizar docs, `CHANGELOG.md`, `DEVELOPMENT_LOG.md`, `/verify-standards`, `/release-plugin`.

---

## Riesgos
1. **Tests enmascaran el acoplamiento** (Mock-First): mitigado por el gate de Fase 0.
2. **Buffer/CRS mal clasificados**: revisar cada `geometry_utils` antes de migrar.
3. **Regresión numérica** al pasar de `QgsDistanceArea` a `math`: golden tests capturados en Fase 0.
4. **Ciclo plugin↔diálogo** es el acoplamiento más resistente: requiere contrato `RenderState` primero.
