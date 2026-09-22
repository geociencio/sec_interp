# Next Steps (Updated 2026-09-21)

## ✅ Session 2026-09-21 — Adaptive Vertical Exaggeration + Preview fixes (COMPLETADO)

- **Adaptive VE (Goal 1.2) end-to-end** — 7 commits (`38c1c651..8f50994a`):
  - **Fase 1 (Core)**: `core/services/vertical_exaggeration_service.py` (stdlib-only, thread-safe).
    Algoritmo: base por aspect-ratio (elev/dist → 1/2/5/10) × densidad estructural (0.7/1.0/1.3),
    clamp `[0.5, 20.0]`, round 1-dec. `calculate_from_result` usa **solo topo+struct** (§5.1 decidido:
    excluye geol/drillhole async para evitar flicker). 9 tests core.
  - **Fase 2 (GUI)**: toggle `Auto` (default `True`) en `dem_page.py` que deshabilita el spin manual;
    `DialogDefaults.AUTO_VERTICAL_EXAGGERATION`, `DemSettings.auto_vert_exag`, `ConfigService`. 7 tests.
  - **Fase 3 (Integración)**: `PreviewRenderMixin._resolve_vertical_exaggeration()` resuelve
    auto=service vs manual=spin; `draw_preview` recibe `vert_exag` (ya no lee el spin); DI de
    `VerticalExaggerationService` en `PreviewManager`; VE excluido de `PreviewParams`/hasher. 3 tests.
  - **Fase 4 (Persistencia)**: tests de persistencia (`config`/`settings_model`/`integration`) +
    docs (`ARCHITECTURE_EN.md`, vault note + Index, mirrors). 5 tests.
- **VE visible**: `PreviewReporter` muestra `Vertical exaggeration: 2.6× (auto)` / `(manual)` y
  footer condicional; etiqueta de solo lectura `auto_ve_value` junto al checkbox Auto en `dem_page.py`;
  `logger.info` del VE resuelto.
- **Fix scratch layers**: los layers de memoria del preview quedaban en `QgsProject` al cerrar →
  aviso "temporary scratch layers". Causa raíz: el botón OK usa `accept_handler` → `self.accept()`
  que NO dispara `closeEvent`. Fix: `PreviewRenderer.cleanup()` + limpieza en `closeEvent`,
  `accept_handler` (OK/Save) y `unload()`.
- **Verificación**: 643 tests (594 local + Docker 5/5 shards OK), analyzer 0 issues, CC≤10 PASS,
  quality 53.8, ruff PASS.

## 🎯 Goals pendientes (post v3.8.0)

### Goal 1: 3D Interpretation & Symbology Enhancements
- [ ] **1.1** Live symbology/legend styling preview bajo el sidebar de Settings. <!-- id: 1.1 -->
- [x] **1.2** Adaptive VE (Fase 1-4) — COMPLETO 2026-09-21 ✅
- [ ] **1.5** Expandir tests de integración de proyección vertical cartesiana (sondajes muy desviados). <!-- id: 1.5 -->

## 🧾 Deuda restante (documentada, no bloqueante)

- **6 áreas grises** (integración QGIS genuina): `i18n.py`, `config.py`, `data_cache.py`,
  `access_control_service.py`, `export/map_settings_factory.py`, `export/orchestrator.py`, `io.py`.
- **Analyzer**: 0 issues.
- **Docs i18n opcional**: traducir `USER_GUIDE` fr (28%) / de (18%); `make docs` para publicar.

## 🚀 How to Resume
1. Run `/start-session`.
2. Continuar con **Goal 1.1** (symbology preview) o **1.5** (tests proyección cartesiana).
3. Plan de referencia adaptive VE (completado): `docs/plans/implementation_plan_adaptive_ve_v3.8.0.md`.

## Referencia
- `docs/maintenance/session_2026-09-21_adaptive_ve_and_preview_fixes.md`
