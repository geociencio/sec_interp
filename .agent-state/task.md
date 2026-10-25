# Active Task Board (Updated 2026-10-25)

> Historial detallado: `.agent-state/history/tasks/` y `docs/maintenance/`.
> Este tablero solo refleja el estado activo; las sesiones cerradas no se acumulan aquí.

## 🎯 Foco actual: preparación del release 3.12.0

- [x] **`qgis-manage` 0.10.0 → 0.12.0** — lock/sync; análisis en `docs/research/qgis_manage_0.12.0_analysis.md`. 0.10.1/0.11/0.12 corrigieron backups, `--type`, guard de versión, `clean`, poda de `--repo-check` (3.2 s → 0.67 s) y añadieron manifiesto, `deploy --dry-run`, `ignore check`, `--json`.
- [x] **Makefile/CI** — `compile` con `--type` repetible y `--jobs` (recursos solo si cambian); `clean` propio que preserva `resources.py` y `examples/sample_data/*.cpg`; `zip --repo-check`; `docker-test` usa `uv run python` en el post-paso. La automatización de release por cola fue retirada.
- [x] **Config** — `[tool.qgis-manager]` (`qgis_version=4`, `max_backups=1`, `auto_compile=false`); `.qgis-manage/` ignorado en Git y `.qgisignore`.
- [x] **Gates 2026-10-25** — 839 tests locales OK / 888 static; Docker OK; ruff/format/mypy/check_docs/i18n/security PASS; Qt6 0; CC PASS; 37 issues; docstring 99.1 %.
- [x] **Automatización de cola retirada** — eliminados `.release-queue.json`, `scripts/next_scheduled_release.py` y `.github/workflows/scheduled-release.yml`; 3.12.0 en adelante se publican a mano desde `main`.
- [x] **Release 3.12.0 publicado en GitHub** — bump/changelog/notas/README, gates verdes, ZIP 3.12.0, commit `4f7cb048`, tag `v3.12.0`, push y GitHub Release publicado como *Latest*. **Pendiente**: subir el ZIP al portal QGIS.
- [x] **Capturas USER_GUIDE 3.12.0** — 22 figuras integradas (sidebar de 6 entradas, Symbology/Interpretation), `ui_main_dialog_v26` y los `workflow_*` retirados, catálogo es al 100 %; staging en `docs/source/images_v3.12.0/` (ignorado).

## 📌 Pendientes del proyecto

- [ ] **`uv` 0.12.10 → 0.13.0** — bloqueado por pacman (Manjaro stable sirve 0.12.10).
- [ ] **Interop §9** — empezar por **B1** (estilos 3D de sondeo) → B3 → B2 → B4 → Fase A.
- [ ] **Opcional** — revisión nativa de traducciones; refrescar `help/html` con `make docs`.

## ✅ Cerrado recientemente (2026-10-24/25)

- [x] **Tooling: `qgis-manage` 0.12.0** — ver arriba; release 3.12.0 queda como único trabajo grande pendiente.
- [x] **Core QGIS-agnostic** — `core/` sin imports QGIS/PyQt; puertos de i18n/settings y factory de map settings inyectados; allowlist vacía; mergeado en `main` (`af0bfbbb`).
- [x] **Documentación** — walkthrough v2 consolidada, arquitectura pública reconstruida y análisis técnico v3.11.0 publicado.
- [x] **Interpretation settings tab** — `InterpretationPage` movida a `SettingsPage`; sidebar 7 → 6; alias `page_interpretation` conservado; mergeada en `main` (`1cc2c105`).
- [x] **Validación manual QGIS 4** — selector desplegado y probado: `secc1.shp` muestra 4 de 7 líneas; preview, LOD, export y persistencia OK.
- [x] **`section_feature_id` fix** — selector `fid — label` con filtro de 2 vértices; propagación a topo/geología/estructuras/sondajes, LOD y tasks async; mergeado en `main` (`83e86a2c`).
- [x] **`module_size_gate` PASS** — controller 465→295, geometry 598→69, preview factory 535→202, 3D exporter 472→155, preview renderer 438→335; 0 módulos >400.
- [x] **Portal QGIS** — v3.11.0 aprobada/en verde (2026-10-23); badge del README actualizado.
- [x] **i18n** — 13 catálogos a 363 mensajes, 0 `unfinished`, `.qm` recompilados y gate `make i18n-check`.
- [x] **Compatibilidad QGIS 3.28 / Python 3.9** — sin `isinstance(x, A | B)` ni `zip(strict=...)`; gates estáticos y ruff `py39`.

## 🧹 Deuda no bloqueante

- `ProfileController` `GOD_OBJECT` (21 atributos) — diferido.
- Traducciones de documentación: `USER_GUIDE` fr (28 %) / de (18 %).
- Upstream `qgis-manage`: `--require-docs` asume `help/html/index.html`; `clean` borra `*.cpg` versionados; `profiles list` solo lista QGIS 3; manifiesto neutro en plugins pequeños.
- `.agent/tests` no se puede ejecutar (pytest eliminado del entorno).

## 🏁 Cerrado

- **Goal 1.1** — symbology/legend styling (v3.11.0).
- **Divergencia `legend_widget.py`** — resuelta por el merge de v3.11.0.
- **Adaptive VE (Goal 1.2)** — completo.
- **Goal 2 (tech debt)** — el estado actual es 37 hallazgos conocidos, CC PASS.
