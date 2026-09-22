# Implementation Plan: Adaptive Vertical Exaggeration (Revisado Post-Refactor)

**Phase**: v3.8.0+ — Goal 1 (3D/simbología) Fase 1-3 (hereda v3.7.0 Goal 2.2)
**Status**: En ejecución — Fase 1 (Core) ✅ · Fase 2 (GUI) ✅ · Fase 3 (Integración) ✅ 2026-09-21 · Fase 4 pendiente
**Created**: 2026-07-20 · **Revisado**: 2026-09-20
**Supersedes**: `implementation_plan_adaptive_ve_v3.7.0.md` (mantiene algoritmo, reubica integración)
**Referencias**: `phase_report_v3.8.0.md:122` (Goal 1 no iniciado), `session_2026-07-20b_adaptive_ve_plan.md` (15 archivos trazados), `AGENTS.md` Extract-then-Compute, `tests/core/test_architecture_boundary.py:46` (allowlist 6)

---

## 0. Resumen Ejecutivo

Reemplazar el `vertexag_spin` estático `[0.1, 100] default 1.0` por un sistema que calcule la exageración óptima desde la geometría del perfil (`elev_range/dist_range`) y la densidad estructural, con override manual. El plan v3.7.0 sigue válido en algoritmo, pero su **punto de inserción, persistencia y tipos** deben migrarse al nuevo **Extract-then-Compute**: el service permanece `stdlib`-only en `core/services/` y el cómputo se consume en `gui/dialog_preview_manager.py` (no en `sec_interp_plugin.py` raw), usando `PreviewResult.get_elevation_range()` / `get_distance_range()` ya existentes.

**Objetivo cuantitativo**: `adaptive_ve = clamp(base_aspect * density_mult, 0.5, 20.0)` redondeado 1-dec; 7 tests core; 0 violaciones `qgis` en `core/` (gate `uv run qgis-analyzer analyze . --max-cc 10` PASS).

---

## 1. Algoritmo Adaptivo (Core) — Sin Cambios Funcionales

**Archivo nuevo**: `core/services/vertical_exaggeration_service.py` — `from __future__ import annotations`, sin `qgis.*` (respeta `core/AGENTS.md`), thread-safe, puro `math`.

### 1.1 Base por relación de aspecto

```
aspect_ratio = elevation_range / distance_range   # ambos desde PreviewResult
Si aspect_ratio > 0.5:   → 1.0   (ya expresivo)
Si aspect_ratio > 0.1:   → 2.0
Si aspect_ratio > 0.02:  → 5.0
Si aspect_ratio <=0.02:  → 10.0
```

Intuición: 1000m largo / 20m relieve (0.02) → 10× para visibilizar estructuras; 200m/100m (0.5) → 1×.

### 1.2 Factor densidad estructural

```
structural_density = len(struct_data) / distance_range
>0.1 (1/10m): 0.7  (reducir, ya denso)
>0.01:        1.0
<=0.01:       1.3  (aumentar, disperso)
```

Si `struct_data is None or empty` → `mult=1.0`.

### 1.3 Fórmula final

```
adaptive_ve = clamp(base * mult, 0.5, 20.0)  # round(..., 1)
Si topo vacío → 1.0 (DEFAULT_VERT_EXAG)
```

**Firma (implementada 2026-09-21)**:

```python
class VerticalExaggerationService:
    def calculate(self, topo: ProfileData | None, struct: StructureData | None) -> float: ...
    def calculate_from_result(self, result: PreviewResult) -> float:
        return self.calculate(result.topo, result.struct)  # topo+struct ONLY (§5.1)
```

**Desviación §5.1 (implementada)**: `calculate_from_result` NO usa
`PreviewResult.get_elevation_range()` (`dtos.py:133`), porque ese método incluye
geol+drillhole (async) y produciría flicker al re-renderizar tras los callbacks.
El servicio extrae elevaciones solo de `result.topo` + `result.struct`; la
distancia se deriva de `topo` (equivalente a `get_distance_range()`).

---

## 2. Cambios en la Interfaz (GUI) — Adaptados a `DemPage` Protocol

**Archivo**: `gui/ui/pages/dem_page.py:93` `_setup_profile_settings` (actual `vertexag_spin` Q `10..100.0` `DialogDefaults.VERTICAL_EXAGGERATION="1.0"`).

### 2.1 Toggle Auto/Manual

```python
self.auto_ve_check = QCheckBox(self.tr("Auto"))
self.auto_ve_check.setChecked(True)
self.auto_ve_check.toggled.connect(self._on_auto_ve_toggled)
def _on_auto_ve_toggled(self, checked: bool) -> None:
    self.vertexag_spin.setEnabled(not checked)
```

Layout: `Vert. Exag.  [Auto ✓]  [1.0]` — spin deshabilitado si Auto. Tooltip en Auto: `self.tr("Calculated automatically")`.

### 2.2 Protocolo `BasePage` (revisado)

Anterior v3.7.0 asumía `config.set` directo. Ahora `gui/dialog_settings_persistence.py:42` itera `_data_pages()` y llama `page.dump()` / `page.load()`:

```python
# gui/ui/pages/dem_page.py
def get_data(self) -> dict: return {"raster_layer":..., "scale":..., "vertexag": self.vertexag_spin.value(), "auto_vert_exag": self.auto_ve_check.isChecked()}
def dump(self) -> dict: return {"dem_layer": self.raster_combo.currentLayer(), "dem_band": ..., "scale":..., "vert_exag":..., "auto_vert_exag": self.auto_ve_check.isChecked()}
def load(self, data: dict) -> None: # restaura ambos
def reset(self) -> None: # DialogDefaults.AUTO_VERTICAL_EXAGGERATION
def connect_signals(self) -> None: ...
```

No se toca `DialogSettingsPersistence` per-se.

### 2.3 Config / Model

- `gui/main_dialog_config.py:14` `class DialogDefaults`: añadir `AUTO_VERTICAL_EXAGGERATION: bool = True` (bool, no string — corrige inconsistencia `SCALE="50000"`).
- `core/models/settings_model.py:30` `DemSettings`: añadir `auto_vert_exag: bool = True`, `vert_exag: float = 1.0` con `validate_and_clamp(0.1, float("inf"))` (mantiene manual [0.1,100] UI clamp separado de auto [0.5,20]).
- `core/config.py:67` `ConfigService._load_from_qgs_settings` → `data["dem"]["auto_vert_exag"] = self.get("auto_vert_exag", True)`; `reset_defaults` y `get_all_settings` análogos. `config.py` es allowlist gris (`qgis.core` legítimo) — añadir constante no ensancha violación.

### 2.4 Persistencia y Validación

- `core/validation/validation_helpers.py:144` `_validate_vert_exag` — mantener hard error `<0.1`, warnings `>10`; auto clamp es warning separado vía `validate_reasonable_ranges`.
- `core/validation/project_validators.py:215` — no bloquea auto `[0.5,20]` (más restrictivo que manual).

---

## 3. Flujo de Datos (Revisado Post-Refactor)

**Antes (v3.7.0 §3)**: `PreviewService.generate_all() → PreviewResult(topo,struct,geol) → VerticalExaggerationService → render` en `sec_interp_plugin.py`.

**Ahora (v3.8.0, 2 etapas por async)**:

```
1. Usuario Preview → PreviewManager.generate_preview():109
   → plugin._get_and_validate_inputs():296 → PreviewParams (SIN vert_exag, render-only)
2. _process_preview_data():148 → preview_service.generate_all(params, ctx):158 → PreviewResult(topo, struct) ; geol=None (async)
   → _update_cache_and_metrics ; _trigger_async_updates(geology_task, drillhole_task):186
3. _update_ui_state():136 → _run_render_pipeline() → _render_cached_data():245
   → NUEVO: auto = page_dem.auto_ve_check.isChecked()
     ve = VerticalExaggerationService().calculate_from_result(cached PreviewResult) if auto else page_dem.vertexag_spin.value()
   → plugin.draw_preview(..., vert_exag=ve):426 (ya no lee spin directo)
   → preview_renderer.render(vert_exag=ve) → PreviewLayerFactory._apply_exaggeration:86 (y*ve) + PreviewAxesManager._compute_grid:64
4. Async callbacks _on_geology_finished():317 / _on_drillhole_finished():386
   → cached_data["geol"]=results ; update_from_checkboxes() → re-render
   → si auto y elev_range incluye geol → recalcular ve (decision: ver §5.1)
```

**Decisión clave**: `PreviewParams` y `PreviewParamHasher:13` **excluyen** VE (evita miss de cache por VE y loop VE↔hash). VE se resuelve solo en render.

---

## 4. Matriz de Cambios por Archivo (Revisada)

| Archivo | Cambio | Capa | Gate |
|---|---|---|---|
| `core/services/vertical_exaggeration_service.py` | **Nuevo** `VerticalExaggerationService` `calculate` + `calculate_from_result` → `float` (stdlib, `core/domain` deps only) | Core | `test_architecture_boundary` PASS (sin `qgis`) |
| `core/models/settings_model.py` | `DemSettings.auto_vert_exag: bool = True` | Core | allowlist gris OK |
| `core/config.py` | `data["dem"]["auto_vert_exag"]` load/reset | Core | gris OK |
| `core/validation/validation_helpers.py` | Ajuste warnings clamp auto [0.5,20] vs manual [0.1,100] | Core | — |
| `gui/ui/pages/dem_page.py` | `auto_ve_check` QCheckBox, handler, `get_data`/`dump`/`load`/`reset`/`connect_signals`, `layer_keys` incluye `auto_vert_exag` si aplica | GUI | `qgis.PyQt` OK (GUI) |
| `gui/main_dialog_config.py` | `AUTO_VERTICAL_EXAGGERATION = True` | GUI | — |
| `gui/dialog_preview_manager.py` | Resolver VE en `_render_cached_data` y callbacks; inyectar `VerticalExaggerationService` vía DI | GUI | — |
| `sec_interp_plugin.py` | Migrar `draw_preview:426` de lectura directa spin a param `vert_exag` pasado por PreviewManager | GUI | reduce God-Object |
| `gui/dialog_input_manager.py` | Opcional `get_auto_vert_exag()` si se requiere validación | GUI | — |
| `i18n/master_data/*.json` + `i18n/SecInterp_*.ts` | `self.tr("Auto")`, tooltip | i18n | `MISSING_I18N` 0 |
| `tests/core/test_vertical_exaggeration_service.py` | **Nuevo** 7 tests (ver §6) `BaseTestCase` mock-first | Test | `allowlist` PASS |
| `tests/gui/test_dem_page.py` | Nuevos `test_auto_toggle_disables_spin`, `dump_load_auto` | Test | — |

*No toca* `gui/dialog_settings_persistence.py` directo (hereda via `dump`).

---

## 5. Decisiones y Riesgos (Requieren Confirmación Pre-Fase 1)

**5.1 Alcance de `elev_range`**: ¿Incluir `geol`/`drillhole` además de `topo+struct`? Recomendado **solo topo+struct sincrónico** para estabilidad; si se incluye geol, requiere recálculo en `_on_geology_finished` y flicker potencial. **✅ DECIDIDO (2026-09-21, usuario): topo+struct only** — implementado en `calculate_from_result` (ver §1).

**5.2 Clamp manual vs auto**: Mantener validación dura `vert_exag >=0.1` (`project_validators.py:215`) y auto clamp `[0.5,20]` como warning; `DemSettings` no fuerza clamp auto.

**5.3 Migración de settings existentes**: `auto_vert_exag` default `True` — usuarios con `vert_exag` previo verán auto-override; ¿notificar o preservar manual si clave existe? **✅ DECIDIDO (2026-09-21, usuario): `auto_vert_exag = True` por defecto** (propuesta original del plan).

**5.4 Almacenamiento en `PreviewResult`**: ¿Guardar `applied_vert_exag: float | None` para `PreviewReporter`? Opcional, no bloquea.

---

## 6. Tests Requeridos (Actualizados Mock-First)

Hereda `tests/base_test.py::BaseTestCase`, `mock_core/mock_gui`, `WKT`/`tuple`, `self.assert*`.

| Test | Descripción |
|---|---|
| `test_calculate_flat_profile` | 5000m/20m → `>5.0` |
| `test_calculate_steep_profile` | 200m/100m → `≈1.0` |
| `test_dense_structures_reduce_ve` | `density>0.1` → `×0.7` |
| `test_sparse_structures_increase_ve` | `density<=0.01` → `×1.3` |
| `test_empty_struct_data` | `None/[]` → mult 1.0 |
| `test_empty_topo_data` | `[]` → `1.0` |
| `test_clamp_bounds` | extremos → `[0.5,20.0]` |
| `test_calculate_from_result` | usa `PreviewResult.get_*_range()` DRY |
| `test_no_qgis_import` | `assert "qgis" not in service_imports` (gate) |

---

## 7. Orden de Implementación (4 fases, ~2-3 días)

1. **Fase 1 Core** (0.5d): `VerticalExaggerationService` + tests core. Gate `ruff` + `qgis-analyzer --max-cc 10` PASS. **Bloqueante** para resto.
2. **Fase 2 GUI** (0.5d): `dem_page.py` checkbox + `DialogDefaults`/`DemSettings`/`ConfigService`. Tests gui `dem_page` mock.
3. **Fase 3 Integración** (0.5d): `dialog_preview_manager.py` resolver + `sec_interp_plugin.draw_preview` param. Manual QGIS visual.
4. **Fase 4 Persistencia + Verificación** (0.5d): `dump/load` validated, `validation_helpers` warnings, `docker-test` 613 tests, `sync_metrics --validate` PASS, `ARCHITECTURE_EN.md` + vault notas actualizadas.

No-Fase 5 separada (verificación integrada); bloque `pre-release` (`qt6-check` + `security-scan` + `docker-test`) en Fase 4.

---

## 8. No-Alcance (Hereda v3.7.0 §8)

- VE non-uniform por zonas, `dip_scale_factor` auto, ML/heuristicas geológicas complejas, `PreviewResult` cached por VE.

---

## 9. Checklist de Salida por Fase

- [x] Fase1 PASS (2026-09-21): `core/services/vertical_exaggeration_service.py` sin `qgis`, `tests/core/test_vertical_exaggeration_service.py` 9/9, `make pep8` PASS
- [x] Fase2 PASS (2026-09-21): `DemPage` toggle funciona, `dump/load/reset` round-trip, `i18n` 0
- [x] Fase3 PASS (2026-09-21): `draw_preview` recibe `vert_exag` calculado, preview re-renderiza en Auto y Manual, async geol no rompe
- [ ] Fase4 PASS: settings persisten tras reinicio QGIS, `docker-test` 613/613, `agent_metrics.json` + `ARCHITECTURE_EN.md` + vault sync

---

*Plan listo para `/build-feature` Fase 1. Esperar aprobación de §5.1 antes de codificar.*
