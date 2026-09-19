# Session Report: Core/GUI Decoupling Refactor — Completion

**Date:** 2026-09-19
**Branch:** `refactor/core-gui-decoupling`
**Phase:** v3.8.0 — Fase 4 & 5 (Core QGIS-agnostic migration + Validation DTO)
**Responsible:** jmbernales

---

## 1. Executive Summary

Se completó el refactor de arquitectura **Extract-then-Compute** del plugin, eliminando
el acoplamiento directo de `core/` con QGIS. La allowlist de violaciones de arquitectura
se redujo de **36 → 6 archivos**, migrando todos los servicios de negocio a un núcleo
100% agnóstico y concentrando la interacción QGIS en una nueva capa de adapters
(`gui/adapters/`). El trabajo quedó en la rama `refactor/core-gui-decoupling`, **34 commits**
por delante de `main` (fast-forward limpio disponible, sin mergear).

Verificación: **558/558 tests OK**, `ruff check` PASS, gate de arquitectura 3/3, y pruebas
manuales en QGIS 4.x confirmando preview, exportación 2D/3D y el fix de Qt6.

---

## 2. Qué se realizó

### 2.1 Servicios migrados a QGIS-agnostic (patrón Extract-then-Compute)

| Commit | Servicio/Capa | Resultado |
|---|---|---|
| `e00419d5` | `export_service` | desacoplado de `QgsProject.instance()` |
| `49de4b03` | `StructureService` | puro (proyección en `math` + `StructureExtractor`) |
| `4b4a129a` | `GeologyService` | puro (`build_segments` + `GeologyExtractor`) |
| `5d47fe9f` | `ProfileService` | eliminado (100% Extract) → `ProfileExtractor` |
| `69e8a84f` | dominio `drillhole` | puro (`process_context` + `DrillholeExtractor`) |
| `9b1bcee9` | capa de validación | DTO `LayerMetadata` + `ValidationExtractor` |

### 2.2 Helpers de geometría y utilidades

- `aa9f53d4`: helpers Extract movidos a `gui/adapters/geometry.py`
  (`create_distance_area`, `densify`, `get_line_vertices`, `calculate_segment_range`,
  `sample_elevation_*`, `prepare_profile_context`); `spatial/sampling/processing` quedaron puros.
- `project_point_onto_polyline` reimplementado en math puro (stdlib).
- `calculate_drillhole_trajectory` / `interpolate_intervals_on_trajectory` ya eran puros.

### 2.3 Adapters creados (`gui/adapters/`)

`layer_resolver.py`, `feature_fetcher.py`, `geometry.py`, `structure_extractor.py`,
`geology_extractor.py`, `profile_extractor.py`, `drillhole_extractor.py`,
`validation_extractor.py`.

### 2.4 Archivos eliminados (dead code / lógica absorbida)

`profile_service.py`, `profile_interface.py`, `drillhole_orchestrator.py`,
`geology/outcrop_processor.py`, `geology/profile_sampler.py`, `utils/geometry.py`,
`utils/geometry_utils/{extraction,filtering}.py`, `utils/qt6_compat.py`,
`utils/resource_manager.py`, `gui/lod_calculator.py` (+ test).

### 2.5 DTOs nuevos

`GeologyContext`, `OutcropSegments`, `DrillholeContext`, `LayerMetadata`.

### 2.6 Bugs corregidos durante pruebas manuales (QGIS 4.x / Qt6)

- `0bc44e92` — `QEvent.Resize` → `QEvent.Type.Resize` (`legend_widget.py`).
- `4671ac6` — `AccessControlService`: exportación 3D habilitada por defecto
  (antes `SecInterp/enable_3d` default `False`).

---

## 3. Verificación

| Métrica | Valor |
|---|---|
| Tests (unittest) | 558/558 OK |
| `ruff check .` | PASS |
| Gate de arquitectura | 3/3 OK |
| Allowlist `core/` | 36 → **6** |
| Manual QGIS 4.x | preview (4 servicios), export 2D/3D, fix Qt6 confirmados |

---

## 4. Deuda restante

### 4.1 Áreas grises (6 archivos aún acoplados a QGIS)

Estos **no son acoplamientos accidentales** sino integración QGIS genuina. Migrarlos
exigiría decisiones de diseño, no solo mover código:

| Archivo | Acoplamiento | Posible abordaje |
|---|---|---|
| `utils/i18n.py` | `QCoreApplication` (`TranslatableMixin`) | mecanismo `tr()` sin QGIS (o aceptar como shim) |
| `config.py` | `QgsSettings` | `SettingsStore` inyectable |
| `data_cache.py` | `qgis.PyQt` (tr) | ídem i18n |
| `services/access_control_service.py` | `QgsSettings` | `SettingsStore` inyectable |
| `services/export_service.py` | `QgsMapSettings`/`QgsRectangle` | mover render a GUI/adapter |
| `utils/io.py` | `QgsVectorFileWriter` | abstracción de escritor de vectores |

### 4.2 Deuda técnica (de fases previas, pendiente)

- `module_size_gate` FAIL: 7 módulos > 400 líneas (`sec_interp_plugin.py`,
  `dialog_preview_manager.py`, `dialog_settings_persistence.py`, `main_dialog.py`,
  `dialog_interpretation_manager.py`, `measure_tool.py`, `settings_page.py`).
- 2 `NON_PYTHONIC_LOOP` (qgis-analyzer).
- 1 `SPATIAL_INDEX` warning en `dialog_interpretation_manager.py`.

### 4.3 Metas v3.8.0 no iniciadas

- **Goal 1 (3D/Simbología)**: live symbology preview, `VerticalExaggerationService`,
  toggle Auto/Manual, integración render, tests de proyección cartesiana.
- **Goal 2 (deuda)**: retirar `qt6_compat` (✅ hecho), `NON_PYTHONIC_LOOP`,
  `SPATIAL_INDEX`, `module_size_gate`.

---

## 5. Recomendaciones

1. **Mergear** `refactor/core-gui-decoupling` → `main` (`--ff-only`) tras validar
   `make docker-test` + `make qt6-check`.
2. **Documentar las 6 áreas grises** como deuda aceptada (no forzar el patrón
   Extract-then-Compute en integración QGIS genuina).
3. **Release v3.8.0** tras el merge (ciclo cerrado, refactor capitalizado).

---

**Filosofía**: una fase no termina cuando el código funciona, sino cuando el
conocimiento queda documentado y la visión del siguiente ciclo es clara.
