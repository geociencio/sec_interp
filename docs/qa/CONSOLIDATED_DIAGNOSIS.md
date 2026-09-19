# 🕵️ Diagnóstico Consolidado — Arquitectura SecInterp

> Análisis exhaustivo del acoplamiento Core/GUI, el God Object en `main_dialog.py` y el subsistema de preview. Cada afirmación verificada contra el código con referencia `archivo:línea`.
> Fecha: 2026-09-18 · Rama: `refactor/core-gui-decoupling` · Plan asociado: `docs/plans/implementation_plan_architecture_refactor_v3.8.0.md`

---

## Resumen Ejecutivo

| Dimensión | Severidad | Hallazgo clave |
|---|---|---|
| Acoplamiento QGIS en `core/` | 🔴 Crítico | 36 archivos violan `core/AGENTS.md`; `QgsProject.instance()` y `from qgis.core import *` presentes pese a estar "FORBIDDEN" |
| God Object en GUI | 🔴 Crítico | 9 managers reciben `self` (el diálogo entero); ciclos de acoplamiento bidireccionales |
| Subsistema de preview | 🟡 Alto | LOD x3, doble pipeline drillhole, doble filtrado, 3 cachés, ~600 líneas muertas |
| Infraestructura de tests | 🟡 Alto | Mock-First enmascara el acoplamiento real a QGIS |

---

## Dimensión 1 — Acoplamiento QGIS en `/core` (violación arquitectónica real)

**Alcance:** 72 archivos `.py`. Clasificación:

| Categoría | Cantidad | Contenido |
|---|---|---|
| 🔴 GEOM_LAYER | 30 | `QgsGeometry`, `QgsVectorLayer`, `QgsFeature`, `QgsProject`, `QgsDistanceArea`, `QgsPointXY` |
| 🟡 QT_SHIM | 3 | `data_cache.py`, `i18n.py`, `qt6_compat.py` (solo `qgis.PyQt` para `tr()`/enums) |
| 🟡 QgsSettings | 2 | `config.py`, `access_control_service.py` (store de settings, no geometría) |
| 🟢 AGNOSTIC | 37 | lógica pura (patrón de referencia) |

La detección precisa del gate (`tests/core/test_architecture_boundary.py`) arroja **36 archivos** con violaciones (unión de las 4 categorías de patrón).

### 1.1 Fugas críticas

- **`core/utils/qgis.py` (`LayerResolver`)** — mayor fuga transitiva. `resolve()` llama `QgsProject.instance()` (línea 54). Contamina `preview_service.py`, `validation_helpers.py` y `controller.py`, que parecen agnosticos pero no lo son.
- **`core/controller.py:111-158`** — `connect_layer_notifications()` recibe `QgsMapLayer` y hace `layer.dataChanged.connect(callback)`: cableado de señales Qt/QGIS dentro del core.
- **`core/controller.py:388-393`** — construye `QgsDistanceArea()` inline con `QgsProject.instance().transformContext()` y `.ellipsoid()`; duplica el helper `spatial.create_distance_area`.
- **`core/utils/spatial.py:11-17,135-136`** — importa `QgsProject`, `QgsGeometry`, etc.; `create_distance_area` usa `QgsProject.instance().transformContext()`.
- **`core/services/drillhole/data_fetcher.py:7,28`** — `QgsFeatureRequest` sobre `QgsVectorLayer` (lectura de features en el core).
- **`core/domain/entities.py:9,21`** — `TYPE_CHECKING: from qgis.core import QgsVectorLayer` + `LayerDict = dict[str, "QgsVectorLayer"]`: fuga de tipo (no runtime, pero rompe el agnosticismo de tipos).
- **`core/domain/dtos.py`** — sin import QGIS directo, pero `PreviewParams.validate()` llama lazy a `ProjectValidator` (cadena QGIS-coupled).

### 1.2 Superficie de frontera (funciones públicas con tipos QGIS)

| Archivo | Funciones/métodos con tipos QGIS |
|---|---|
| `controller.py` | `connect_layer_notifications(layers: dict[str, Any])`, `_process_topography/_geology/_structures` (vía `LayerResolver`) |
| `utils/spatial.py` | `calculate_line_azimuth(QgsGeometry)`, `calculate_step_size(QgsGeometry, ...)`, `get_line_start_point(QgsGeometry) -> QgsPointXY`, `create_distance_area(QgsCoordinateReferenceSystem) -> QgsDistanceArea` |
| `utils/sampling.py` | `sample_elevation_along_line(...)`, `prepare_profile_context(QgsVectorLayer)`, `sample_point_elevation(QgsRasterLayer, QgsPointXY, ...)` |
| `utils/drillhole.py` | `project_trajectory_to_section(...)` |
| `utils/io.py` | `create_vector_writer(..., QgsCoordinateReferenceSystem, QgsFields, ...) -> QgsVectorFileWriter` |
| `utils/resource_manager.py` | `temporary_memory_layer(...) -> QgsVectorLayer`, `ResourceManager.cleanup_layer(QgsMapLayer)` |
| `utils/geometry_utils/*` | `processing.create_buffer_geometry/create_memory_layer/densify_line_by_interval/calculate_segment_range`; `filtering.filter_features_by_buffer`; `extraction.extract_*`; `optimization.PreviewOptimizer.decimate`; `measurement.calculate_polyline_metrics` |
| `interfaces/structure_interface.py` | `detach_structures(QgsVectorLayer, QgsGeometry, ...)`, `project_structures(...)` |
| `interfaces/profile_interface.py` | `generate_topographic_profile(QgsVectorLayer, QgsRasterLayer, ...)` |
| `services/structure_service.py` | `detach_structures`, `project_structures`, `_create_buffer_zone`, `_filter_structures -> list[QgsFeature]` |
| `services/geology_service.py` | `generate_geological_profile(...)`; `process_task_data` reconstruye `QgsCoordinateReferenceSystem`/`QgsGeometry.fromWkt` |
| `services/profile_service.py` | `generate_topographic_profile(QgsVectorLayer, QgsRasterLayer, ...)` |
| `services/drillhole_service.py` | `project_collars`, `process_intervals`, `_build_collar_coordinate_map`, `_extract_point_from_attrs` |
| `services/export_service.py` | `get_map_settings(...) -> QgsMapSettings`, `_resolve_layers` (`QgsProject.instance()`) |
| `services/drillhole/*` | `projection_engine.project_point_to_line`; `data_fetcher.fetch_bulk_data`; `drillhole_orchestrator.prepare_task_input/process_task_data`; `collar_processor.detach_features/pre_sample_z`; `trajectory_engine.process_single_hole` |
| `services/geology/*` | `profile_sampler.generate_master_profile`; `outcrop_processor.extract_outcrop_data` |
| `validation/project_validators.py` | `SectionValidator`, `DEMValidator`, etc. (rutean por `LayerResolver` + `QgsWkbTypes`) |
| `validation/layer_validator.py` | `validate_layer_exists -> QgsMapLayer`, `validate_layer_geometry(QgsWkbTypes.GeometryType)`, `validate_crs_compatibility(list[QgsMapLayer])` |
| `validation/field_validator.py` | `validate_field_exists(QgsVectorLayer, ...)`, `validate_field_type(QgsVectorLayer, ...)` |

### 1.3 Archivos ya AGNOSTIC (patrón a imitar)

**Puros:** `exceptions.py`, `performance_metrics.py`, `models/settings_model.py`, `domain/enums.py`, `domain/spatial_meta.py`, `domain/task_inputs.py` (DTO ideal), `utils/geology.py`, `utils/parsing.py`, `utils/rendering.py`, `utils/metadata_reader.py`, `utils/safe_loader.py`, `interfaces/cache_interface.py`, `interfaces/drillhole_interface.py`, `interfaces/geology_interface.py`, `interfaces/i_renderer_3d.py`, `interfaces/preview_interface.py`, `validation/base_validator.py`, `validation/pipeline.py`, `validation/path_validator.py`, `validation/validators.py`, `services/drillhole/survey_processor.py`, `services/drillhole/interval_processor.py`.

**Transitivamente acoplados (cuidado):** `services/preview_service.py` (importa `LayerResolver`), `validation/validation_helpers.py` (re-exporta `LayerResolver`), `utils/geometry.py` (fachada de `geometry_utils/*`), `utils/__init__.py`, `services/__init__.py`.

**Mejores prácticas detectadas:** `domain/task_inputs.py` (DTOs), `services/drillhole/data_fetcher.py` (capa in → tuplas out), `services/drillhole/interval_processor.py` y `survey_processor.py`.

---

## Dimensión 2 — God Object en GUI

### 2.1 Estructura

`SecInterpDialog(SecInterpMainWindow)` (`gui/main_dialog.py:46`) hereda de `SecInterpMainWindow(QDialog)` (`gui/ui/main_window.py:32`), que construye toda la UI programática (sidebar, páginas, preview, output, botones). `main_dialog.py` añade 9 managers + lógica encima.

`_init_managers()` (`main_dialog.py:114-127`) instancia **todos** los managers pasando `self`:

| Línea | Manager | Arg |
|---|---|---|
| 118 | `InputManager` | `self` |
| 119 | `StateManager` | `self` (spawnea `DialogSettingsPersistence` + `UIStatusManager`) |
| 120 | `PreviewManager` | `self`, `PreviewService(...)` |
| 121 | `ExportManager` | `self` |
| 123 | `InterpretationManager` | `self` |
| 125 | `ToolManager` | `self` |
| 126 | `NavigationManager` | `self` |
| 104 | `SignalManager` | `self` |
| 127 | `PreviewLayerFactory()` | *(sin dialog — único desacoplado)* |

### 2.2 Grafo de acoplamiento (calls cruzadas vía `self.dialog`)

| Desde | Hacia | Ref |
|---|---|---|
| `ExportManager` | `StateManager` | `dialog_export_manager.py:161` |
| `InterpretationManager` | `PreviewManager` | `dialog_interpretation_manager.py:302,354` |
| `InterpretationManager` | `PreviewLayerFactory` | `dialog_interpretation_manager.py:284` |
| `UIStatusManager` | `InputManager` | `ui_status_manager.py:40,52,65,78` |
| `PreviewManager` | `InterpretationManager` | `dialog_preview_manager.py:214-215` |
| `StateManager` | `ToolManager` / `InterpretationManager` | `dialog_state_manager.py:108,111-113` |
| `SignalManager` | `ToolManager`/`ExportManager`/`PreviewManager` | `dialog_signal_manager.py:172,215-217,231,304,319,323-324` |
| `PreviewTaskOrchestrator` | `PreviewManager` | `preview_task_orchestrator.py:92-94,152-154` |

### 2.3 Ciclos detectados

1. **`PreviewManager ↔ InterpretationManager`**: `PreviewManager` limpia interpretaciones (`dialog_preview_manager.py:214-215`) ↔ `InterpretationManager` lee `preview_manager.cached_data` (`dialog_interpretation_manager.py:302,354`) y llama `update_preview_from_checkboxes` (`:253`).
2. **`SecInterpPlugin ↔ diálogo`**: `draw_preview()` escribe `dlg.current_canvas/current_layers/current_topo_data` (`sec_interp_plugin.py:433-454`) que `ExportManager` lee (`dialog_export_manager.py:52,58,122`); y managers llaman `plugin_instance.draw_preview()`. `_get_and_validate_inputs()` (`sec_interp_plugin.py:261-335`) llama `dlg.get_selected_values()`.

### 2.4 Otros hallazgos

- `DialogSettingsPersistence` (401 líneas) pokea widgets por nombre de atributo en 7 páginas (`:62-96,116-303`) y llama a `page_settings._reset_export_defaults()` (método privado).
- `gui/services/` está **vacío** (solo `__init__.py`); su responsabilidad declarada vive en `tasks/` + `PreviewTaskOrchestrator`.
- `SignalManager` es un **registro de cableado**, no event bus: conecta widgets → métodos del diálogo → re-despacho a managers vía `self.dialog.*_manager`.
- `ProfileSnapper` duplicado: `tools/measure_tool.py:37` vs `tools/interpretation_tool.py:38`.

### 2.5 Líneas de código (GUI total ~7,951)

| Archivo | Líneas | Nota |
|---|---|---|
| `dialog_preview_manager.py` | 483 | orquestación + render + async |
| `main_dialog.py` | 449 | God Object (> stop-condition 300) |
| `dialog_interpretation_manager.py` | 423 | lógica espacial que debería ir a core |
| `dialog_settings_persistence.py` | 401 | acoplamiento más profundo |
| `dialog_signal_manager.py` | 324 | registro de cableado |
| `dialog_export_manager.py` | 218 | imagen + datos (2 concerns) |
| `main_dialog_config.py` | 219 | constantes (bien) |
| `dialog_tool_manager.py` | 195 | 2 clases (ToolManager + NavigationManager) |
| `dialog_input_manager.py` | 194 | el más limpio (delega a `ProjectValidator`) |
| `dialog_state_manager.py` | 117 | thin |
| `ui_status_manager.py` | 85 | small |
| `settings_page.py` | 416 | página más grande |
| `drillhole_page.py` | 378 | |

---

## Dimensión 3 — Subsistema de preview (redundancia real)

### 3.1 Inventario

| Archivo | Líneas | Responsabilidad |
|---|---|---|
| `dialog_preview_manager.py` | 483 | orquestador central |
| `preview_task_orchestrator.py` | 157 | envuelve 2 `QgsTask` (geology + drillhole) |
| `preview_layer_factory.py` | 495 | construye/styling de capas memoria |
| `preview_renderer.py` | 350 | render a canvas + cleanup + (muerto) export imagen |
| `preview_param_hasher.py` | 71 | hash SHA256 de `PreviewParams` |
| `preview_reporter.py` | 145 | formatea resultados |
| `preview_axes_manager.py` | 207 | grilla y etiquetas de ejes |
| `preview_legend_renderer.py` | 178 | leyenda sobre `QPainter` |
| `lod_calculator.py` | 48 | **muerto** (solo tests) |
| `renderers/*` (6 + base + color) | ~280 | estilos de capa |
| `core/services/preview_service.py` | 363 | orquesta generación sync |

### 3.2 Redundancias confirmadas

1. **LOD x3**: `PreviewService.calculate_max_points` (usado, `preview_service.py:63-94`), `LODCalculator.calculate_max_points` (**muerto**, `lod_calculator.py:23-48`), `PreviewOptimizer.decimate/adaptive_sample` (simplificación real).
2. **Doble pipeline drillhole**: sync (`preview_service._generate_drillholes` + 4 helpers, solo tests) vs async (`drillhole_orchestrator`, producción). `skip_drillholes=True` siempre (`dialog_preview_manager.py:156`).
3. **Doble filtrado de visibilidad**: `dialog_preview_manager.py:268-277` y `sec_interp_plugin.py:456-480`.
4. **3 call sites de `draw_preview`** casi idénticos (`dialog_preview_manager.py:243,298,355`).
5. **3 mecanismos de cache**: `PreviewParamHasher` + `_handle_geometric_changes` (`:197`) + `controller.data_cache` (`main_dialog.py:405`). `ENABLE_CACHE`/`CACHE_EXPIRY_SECONDS` definidos pero nunca usados.
6. **Doble cálculo de `calculate_max_points`** por ciclo de render (`dialog_preview_manager.py:237` y `preview_service.py:152`).
7. **Styling categorized duplicado**: `geology_renderer.py:28-45` vs `drillhole_renderer.py:_apply_interval_style:60-75`.
8. **Boilerplate memory-layer+CRS** en 3 sitios (`preview_layer_factory.py:116-128`, `preview_axes_manager.py:69-74,131-140`).
9. **Leyenda con 3 callers**: `legend_widget.py:79`, `preview_renderer.py:238-242`, `exporters/*_exporter.py`.

### 3.3 Código muerto

- `gui/lod_calculator.py` (solo `tests/gui/test_lod_calculator.py`).
- `PreviewRenderer.export_to_image` (`preview_renderer.py:244-282`).
- `PreviewLayerFactory.interpolate_elevation` (`preview_layer_factory.py:481-495`) — dup de `core/utils/sampling.py:127-164`.
- Pipeline drillhole sync de `PreviewService` (`preview_service.py:203-363`).
- `self.active_drill_task` (`dialog_preview_manager.py:436`).
- `show_legend`/`**kwargs` sin uso en `PreviewRenderer.render` (`preview_renderer.py:85-86`).
- `TYPE_CHECKING: pass` vacíos (`dialog_preview_manager.py:36-37`, `preview_param_hasher.py:8-9`).
- Import stale `from .main_dialog_preview import PreviewManager` (`preview_task_orchestrator.py:18`).
- 7 constantes `DialogConfig` muertas (`main_dialog_config.py:47-48,66,68,72-73,77`).
- `_cleanup_rubber_bands` nunca ejecuta (no se agregan rubbers).

### 3.4 Acoplamiento de `preview_service.py`

Sin `import qgis.core` directo, pero runtime-coupled vía `LayerResolver.resolve` (`preview_service.py:23,139,176,259,294-295`), `prepare_profile_context` (retorna `QgsGeometry`/`QgsPointXY`/`QgsDistanceArea`) y `QgsCoordinateTransformContext` (`:99,117`).

---

## Dimensión 4 — Infraestructura de pruebas

- **663 métodos `test_*`** en el árbol; `unittest discover tests` ejecuta **592 casos** (baseline OK, 11.15s).
- `tests/base_test.py` inyecta `mock_core`/`mock_gui` vía `ModuleProxy` (Mock-First). Consecuencia: los tests de core **no detectan** el acoplamiento real a QGIS (por eso 36 archivos lo violan sin fallar).
- Comando canónico: `PYTHONPATH=.. uv run python3 -m unittest discover tests` (el `make test` lo hace implícito tras `compile`+`transcompile`). `pytest` falla por `pytest-qt` sin Qt.

---

## Recomendaciones (consolidadas)

1. **DTO real** en `core/`: mover la extracción a `gui/adapters/`, `LayerResolver` y `connect_layer_notifications` a GUI.
2. **Event bus / interfaces estrechas** en GUI para eliminar `self.dialog`.
3. **Contrato `RenderState`** para romper el ciclo plugin↔diálogo.
4. **Unificar LOD, pipeline drillhole, filtrado y cache** del preview.
5. **Eliminar código muerto** (Fase 1) antes de refactorizar en profundidad.
6. **Clasificar Extract vs Compute** antes de migrar cada `geometry_utils` (buffer/CRS → GUI; decimate/densify/project → core con `math`).

Véase el plan por fases en `docs/plans/implementation_plan_architecture_refactor_v3.8.0.md`.
