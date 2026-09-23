# Implementation Plan: Geology on the Smoothed Profile (v3.9.1)

**Phase**: v3.9.1 — follow-up to the smoothed topography profile (v3.9.0 extra)
**Status**: ✅ IMPLEMENTADO 2026-09-23 (Opción A; `PreviewParams.smooth/smooth_window` +
hash; perfil maestro de geología suavizado en `_generate_master_profile`; callers
controller/orchestrator; Smooth invalida S2). Tests: extractor + hash + assemble.
**Created**: 2026-09-23
**Referencias**: `gui/adapters/geology_extractor.py` (`_generate_master_profile`),
`core/services/geology_service.py` (`build_segments`),
`core/controller.py` (`_process_geology`), `gui/preview_task_orchestrator.py`
(`start_geology_task`), `core/utils/sampling.py` (`smooth_profile_by_distance`),
`gui/preview_param_hasher.py`, `core/domain/dtos.py` (`PreviewParams`),
`gui/dialog_signal_manager.py`.

---

## 0. Resumen ejecutivo

Hacer que **la geología siga el perfil suavizado** cuando la opción **Smooth** está
activa, de forma consistente en preview y export. Hoy la geología tiene su propio
perfil maestro (`GeologyExtractor._generate_master_profile`) que se muestrea del DEM
con vecino más cercano y se interpola a los segmentos; el suavizado actual solo afecta
al dibujo de la topografía (Present).

**Decisión tomada**: **Opción A** — suavizar el **perfil maestro de geología al
extraer** (dato), no en Present. Estructuras y collares **no se tocan** (son datos de
interpretación y siguen con su muestreo crudo).

**Consecuencia**: `Smooth` pasa de ser solo-visual a ser un **dato del perfil**; cambia
la firma de vigencia del preview (S2) y se aplica al pulsar **Preview** (se regenera
geología). El export de geología también sale suavizado.

---

## 1. Contexto técnico verificado

| Hecho | Fuente |
|---|---|
| Geología tiene perfil maestro propio (muestreo DEM) independiente del topo | `gui/adapters/geology_extractor.py:149` `_generate_master_profile` |
| Segmentos interpolan elevación del perfil maestro | `core/services/geology_service.py:67` `interpolate_segment_points` |
| Extracción llamada en export (controller) y preview (orchestrator async) | `core/controller.py:262`, `gui/preview_task_orchestrator.py:74` |
| Filtro de suavizado ya existe (puro, stdlib) | `core/utils/sampling.py` `smooth_profile_by_distance` |
| `Smooth`/`smooth_window` ya viven en los controles y en `get_preview_options()` | `gui/ui/pages/preview_page.py`, `gui/dialog_facade_mixin.py` |
| Hoy `Smooth` no está en `PreviewParams`/hash (solo re-render) | `gui/preview_param_hasher.py` |

---

## 2. Cambios por archivo

### 2.1 Parámetros (data) — pasar a PreviewParams + hash
- `core/domain/dtos.py`: `PreviewParams` `+smooth: bool = False`, `+smooth_window: int = 30` (+ docstring).
- `gui/preview_param_hasher.py`:
  - `assemble_preview_params`: `smooth=bool(preview_options.get("smooth", False))`,
    `smooth_window=preview_options.get("smooth_window", 30)`.
  - `PreviewParamHasher.calculate_hash`: incluir ambos (`smooth`, `smooth_window`) ⇒
    `is_preview_current()` detecta el cambio.

### 2.2 Extracción de geología
- `gui/adapters/geology_extractor.py`:
  - `extract_context(..., smoothing_window_m: float = 0.0)`.
  - `_generate_master_profile(..., smoothing_window_m: float = 0.0)`: tras el bucle,
    si `smoothing_window_m > 0`:
    ```python
    smoothed = smooth_profile_by_distance(master_profile_data, smoothing_window_m)
    master_profile_data = smoothed
    master_grid_dists = [
        (d, pt, e)
        for (d, pt, _old), (_d, e) in zip(master_grid_dists, smoothed, strict=True)
    ]
    ```
  - Import de `smooth_profile_by_distance` (`sec_interp.core.utils.sampling`).

### 2.3 Callers (pasar la ventana desde params)
- `core/controller._process_geology` (export):
  `smoothing_window_m = float(params.smooth_window) if params.smooth else 0.0`.
- `gui/preview_task_orchestrator.start_geology_task` (preview): idem desde `params`.
- Topografía: sin cambios (ya suaviza en `draw_preview` con `options["smooth"]`).

### 2.4 Señales (Controls)
- `gui/dialog_signal_manager`:
  - `chk_smooth.toggled` y `spin_smooth_window.valueChanged` pasan de
    `preview_manager.update_from_checkboxes` a `state_manager.update_button_state`
    (invalidan S2).
  - El resto de opciones de preview (legend, max points, auto LOD, adaptive) sin
    cambios.
- **UX**: al marcar/ajustar Smooth, el preview queda obsoleto; se aplica al pulsar
  **Preview** (regenera geología + dibuja topografía suavizada). Export deshabilitado
  hasta re-Preview.

### 2.5 Docs
- `CHANGELOG [Unreleased]`: "la geología (y su export) siguen el perfil suavizado
  cuando Smooth está activo".
- `DEVELOPMENT_LOG` + `docs/maintenance/` al cerrar la sesión.

---

## 3. Tests

- `tests/gui/test_geology_extractor*.py` (o el existente de geología):
  - `_generate_master_profile` con `smoothing_window_m>0` atenúa un pico y
    `master_grid_dists` queda consistente (mismas distancias, mismas elevaciones que
    `master_profile_data`); `=0` no-op.
  - `extract_context(..., smoothing_window_m=0)` comportamiento idéntico al actual.
- `tests/gui/test_preview_param_hasher*` (o `test_ui_gating`): el hash cambia con
  `smooth`/`smooth_window`; `assemble_preview_params` mapea las claves.
- Callers: `controller` y `orchestrator` propagan la ventana (mock).
- Gates: `ruff`/format, suite completa, `qgis-analyzer --max-cc 10`, gates
  CC/Module Size/i18n.

---

## 4. Alcance explícito

- **No** se tocan: estructuras, collares, stats perfil-vs-DEM (siguen crudas),
  relleno topográfico.
- El overlay rojo suave de la topografía se mantiene.
- Un solo perfil de geología (no se exporta una versión cruda adicional).

## 5. Riesgos

- Ventana grande ⇒ puede aplanar picos geológicos; la controla el usuario (10–500 m).
- Consistencia geología↔topografía: ambas se suavizan con el mismo filtro y la misma
  resolución de muestreo (`resolve_sampling_interval`); validar en smoke que coinciden.
- Cambio de comportamiento de `Smooth` (de instantáneo a aplicar en Preview); documentar
  en el CHANGELOG y en el tooltip del control si procede.
