# Technical Specification — Module Size Gate Remediation (<300 lines)

**Branch:** `refactor/module-size-gate`
**Goal:** `module_size_gate FAIL (6 modules >400l) → PASS (<300l cada uno)` ✅ **COMPLETADO**
**Priority:** `export_service.py:645` primero, luego descomposición lógica incremental
**Author:** @architect · 2026-09-20 · Aprobado por usuario
**Skills:** `coding-standards`, `qgis-core`, `project-context`

---

## ✅ Resultado final (2026-09-20)

`module_size_gate: PASS` · CC gate PASS · i18n PASS · 564 tests OK (612 static) · analyzer issues 3 (sin cambios).

| Módulo original | Antes | Después | Commit |
|---|---|---|---|
| `core/services/export_service.py` | 645 | **13** (shim) | `c3116a6` |
| `gui/ui/pages/drillhole_page.py` | 451 | **130** | `39e1168` |
| `gui/ui/pages/settings_page.py` | 417 | **124** | `78bcb45` |
| `sec_interp_plugin.py` | 508 | **129** | `900afb8` |
| `gui/main_dialog.py` | 481 | **193** | `ac58143` |
| `gui/dialog_interpretation_manager.py` | 445 | **107** | `85cbbb5` |
| `gui/dialog_preview_manager.py` | 435 | **231** | `77f193d` |

Nuevos módulos por fase: `core/services/export/` (orchestrator + 7 handlers + 2 factories + compat),
`plugin/` (lifecycle/input_validator/render_pipeline), `gui/ui/pages/drillhole/` (3 tabs),
`gui/ui/pages/settings/` (3 tabs + persistence), mixins `gui/dialog_*_mixin.py`,
`gui/interpretation_*_mixin.py`, `gui/preview_*_mixin.py`.

**Patrón aplicado:** fachada + mixins/handlers, con `connect`/`disconnect` y slots co-localizados
por archivo para satisfacer las reglas del analyzer (signal leaks / missing slot), y patch targets
de tests preservados moviendo sólo lo no parcheado a nivel de módulo.

---

## 1. Ground Truth Actual

```bash
wc -l sec_interp_plugin.py gui/main_dialog.py gui/ui/pages/drillhole_page.py \
      gui/dialog_interpretation_manager.py gui/dialog_preview_manager.py \
      gui/ui/pages/settings_page.py core/services/export_service.py
# 507 480 451 444 434 416 645
uv run qgis-analyzer summary  # 52.4/100, 99.9/100, 100/100, 3 issues (2 NON_PYTHONIC_LOOP, 1 SPATIAL_INDEX)
PYTHONPATH=/home/jmbernales/qgispluginsdev uv run python -m unittest discover -s tests  # 558 OK (606 static)
```

Allowlist `core/AGENTS.md:8` — `core/services/export_service.py` es gris permitido (`qgis.core.QgsMapSettings`).

## 2. Target <300 (óptimo <250)

Cada módulo descomponer para dejar **colchón 100 líneas** ante futuros features. No sólo pasar 400.

Fases priorizadas por ROI/riesgo:

| Fase | Módulo | Actual | Target | Estrategia |
|------|--------|--------|--------|------------|
| **1** | `core/services/export_service.py` | 645 | orchestrator 150 + 7 handlers 60-90 + 2 factories 40 | Paquete `core/services/export/` con delegación |
| 2 | `gui/ui/pages/drillhole_page.py` | 451 | coordinator 100 + 3 tabs 110c/u | Tabs independientes `drillhole/collar_tab.py` etc. |
| 3 | `gui/ui/pages/settings_page.py` | 416 | coordinator 100 + 3 tabs | `settings/default_tab.py` etc. |
| 4 | `sec_interp_plugin.py` | 507 | facade 120 + 3 helpers 120c/u | `plugin/lifecycle.py`, `input_validator.py`, `render_pipeline.py` |
| 5 | `gui/main_dialog.py` | 480 | root 150 + mixins 80c/u | `main_dialog/lifecycle_mixin.py`, `message_mixin.py` |
| 6 | `gui/dialog_interpretation_manager.py` | 444 | facade 180 + 2 helpers 140c/u | `interpretation/persistence.py`, `inheritance.py` |
| 7 | `gui/dialog_preview_manager.py` | 434 | orchestrator 250 + callbacks 120 | `preview/callbacks.py` (ya hay orchestrator/hasher/reporter) |

**Esta especificación implementa Fase 1 completa; fases 2-7 quedan planificadas y se ejecutan en PRs atómicos sucesivos sobre la misma rama.**

## 3. Diseño Fase 1 — `core/services/export/`

### 3.1 Estructura propuesta

```
core/services/export/
  __init__.py                # re-export ExportService para compatibilidad
  orchestrator.py            # ExportService (fachada <150l)
  path_resolver.py           # resolve_export_path + get_profile_name (40l, puro pathlib)
  map_settings_factory.py    # create_map_settings (30l, único import qgis.core)
  handlers/
    __init__.py
    topography.py            # export_topography (70l)
    geology.py               # export_geology (60l)
    structures.py            # export_structures (80l)
    drillholes.py            # export_drillholes 2D (75l)
    drillholes_3d.py         # export_drillholes_3d declarativo (90l)
    interpretations.py       # export_interpretations 2D+3D (100l)
    axes.py                  # export_axes (40l)
```

**Compatibilidad:** `core/services/export_service.py` se mantiene como **shim** 12 líneas: `from sec_interp.core.services.export.orchestrator import ExportService; __all__ = ["ExportService"]`. Así `sec_interp_plugin.py:117` y `tests/core/test_export_service.py` no rompen.

### 3.2 Orchestrator (150l)

```python
class ExportService:
    def __init__(self, controller=None): ...
    def tr(self, message: str) -> str: ...
    def export_data(self, output_folder: Path, params: PreviewParams, ...) -> list[str]: ...
    def _resolve_layers(self, params) -> tuple: ...
    def _orchestrate_exports(self, folder, params, ...) -> None:  # routing dict
```

- Mantiene validación `export_options`, `profile_data` check, `result_msg`, resolución `format_ext` (.shp/.gpkg/.dxf) desde `settings.export.default_format`.
- Handlers invocados via `handlers = {"exp_topo": lambda: topography.export(...), ...}` — mismo contrato actual.
- Única interacción QGIS: delega a `map_settings_factory.create_map_settings` para `get_map_settings` público.

### 3.3 Factories

**`path_resolver.py`**
```python
def get_profile_name(controller) -> str: ...
def resolve_export_path(folder: Path, base_name: str, profile_name: str, naming_pattern: str|None, ext: str) -> tuple[Path, str]: ...
```
Lógica extraída de `ExportService._get_export_path:593` (mkdir, naming_pattern, gpkg vs container_folder). Sin imports QGIS.

**`map_settings_factory.py`**
```python
from qgis.core import QgsMapSettings, QgsRectangle
def create_map_settings(layers, extent, size, background_color) -> QgsMapSettings: ...
```
Aísla único `from qgis.core import QgsMapSettings` permitido en allowlist. Testeable con mock.

### 3.4 Handlers

Cada handler patrón uniforme:

```python
from __future__ import annotations
import logging
from pathlib import Path
from typing import Any
from sec_interp.core.exceptions import DataMissingError, ExportError
from sec_interp.logger_config import get_logger
logger = get_logger(__name__)

def export_topography(folder: Path, data: list[tuple], crs: Any, csv_exporter: Any, msg: list[str], settings: Any|None, ext: str) -> None:
    logger.info("✓ Saving topographic profile...")
    try:
        vec_path, vec_layer = path_resolver.resolve_export_path(...)
        ...
    except (OSError, ValueError, TypeError, DataMissingError) as e:
        raise ExportError(...) from e
```

- Lazy import `from sec_interp.exporters import XVectorExporter` DENTRO de cada función (preserva testabilidad con patch).
- Mensajería `msg.append(f"  - {path.relative_to(folder)}")` idéntica.
- `drillholes_3d.py` mantiene tabla declarativa `tasks:449` (4 tuplas) + loop `if options.get(type_flag) and options.get(proj_flag)`.
- `interpretations.py` encapsula `can_export_3d()` + `_export_interpretations_3d` (QgsGeometry via `line_layer.getFeatures()`).

### 3.5 Flujo de datos (Extract-then-Compute intacto)

`gui/dialog_export_manager.py:1` → `ExportService.export_data(Path, PreviewParams, ...)` → handlers → `exporters/*Exporter.export(Path|str, data, layer_name)` → filesystem. Sin cambios en `PreviewParams` DTO.

## 4. Testing & Validación

- **Existentes:** `tests/core/test_export_service.py` (13 tests) debe seguir verde sin modificación. Si falla, shim no re-exportó bien.
- **Nuevos (opcional Fase 1):** `tests/core/services/export/test_path_resolver.py` (profile_name sanitization, gpkg vs shapefile branching) — 6 tests.
- **Gate:** `uv run qgis-analyzer analyze . --max-cc 10` CC ≤10, `uv run ruff check .` + `uv run ruff format --check .`, `PYTHONPATH=/home/jmbernales/qgispluginsdev uv run python -m unittest discover -s tests` 558+ OK.
- **Métrica:** `wc -l core/services/export_service.py` (shim) 12 + `orchestrator.py` <150 + cada handler <100. `core/services/export_service.py` deja de contar como >400.

## 5. Riesgos y Mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| Expandir allowlist QGIS en core | Solo `map_settings_factory.py` importa `qgis.core`; resto `Any`. CI grep `from qgis` en handlers |
| Romper `sec_interp_plugin.py:117` `SafeLoader` | Shim mantiene import path idéntico |
| Duplicar try/except logger boilerplate | Extraer helper `_wrap_export_error` si handler CC >10 |
| Paths GPKG vs Shp regresión | `path_resolver` cubierto con 6 tests paramétricos |

## 6. Próximos pasos (Fases 2-7)

Tras Fase 1 merge parcial, continuar sobre misma rama `refactor/module-size-gate` con commits atómicos por módulo, cada uno con `wc -l` verificación + tests. Final `uv run python scripts/sync_metrics.py` + `agent_metrics.json` update.

---
**Aprobación:** Usuario 2026-09-20 — "menor a 300 o la más óptima, export_service.py primero"
