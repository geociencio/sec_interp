# Active Task Board (Updated 2026-10-28)

> Historial detallado: `.agent-state/history/tasks/` y `docs/maintenance/`.
> Este tablero solo refleja el estado activo; las sesiones cerradas no se acumulan aquí.

## 🎯 Foco actual: post-release 3.12.0 / polish 3.12.1

- [x] **`qgis-manage` 0.10.0 → 0.15.0** — lock/sync; el análisis histórico está en `docs/research/qgis_manage_0.12.0_analysis.md`. 0.15 añade `validate --zip`, auditoría del ZIP, normalización de permisos y `security --portal` (native + Bandit + detect-secrets + Flake8).
- [x] **Makefile/CI** — `compile` con `--type` repetible y `--jobs` (recursos solo si cambian); `clean` propio que preserva `resources.py` y `examples/sample_data/*.cpg`; `zip --repo-check`; `docker-test` usa `uv run python` en el post-paso. La automatización de release por cola fue retirada.
- [x] **Config** — `[tool.qgis-manager]` (`qgis_version=4`, `max_backups=1`, `auto_compile=false`); `.qgis-manage/` ignorado en Git y `.qgisignore`.
- [x] **Gates 2026-10-25** — 839 tests locales OK; Docker OK; ruff/format/mypy/check_docs/i18n/security PASS; Qt6 0; CC PASS; 37 issues; docstring 99.1 %.
- [x] **Icono actualizado** — `icon.png` 128×128 desde `docs/source/images/sec_interp_icon.svg`; paquete nuevo valida sin warnings.
- [x] **Sistema agéntico** — skill `qgis-release`, `make flake8` bloqueante (perímetro del portal), `make portal-check` delegado en `qgis-manage validate --zip` (0.15) e integrado en `make zip`; `make security-scan` usa `qgis-manage security --portal`; `qgis-analyzer` 1.18 con `--exclude`/`--flake8`/`security --tools`.
- [x] **Automatización de cola retirada** — eliminados `.release-queue.json`, `scripts/next_scheduled_release.py` y `.github/workflows/scheduled-release.yml`; 3.12.0 en adelante se publican a mano desde `main`.
- [x] **Release 3.12.0 publicado en GitHub** — bump/changelog/notas/README, gates verdes, ZIP 3.12.0, commit `4f7cb048`, tag `v3.12.0`, GitHub Release *Latest*.
- [x] **v3.12.0 activo en el portal QGIS (2026-10-28)** — <https://plugins.qgis.org/plugins/sec_interp/>, marcado **QGIS 4 Ready**. El artefacto publicado aún tiene F811/E402 y el icono 23×24; Flake8 es informativo, así que fue aceptado. 3.12.1 queda como polish (lint limpio + icono 128×128).
- [x] **Capturas USER_GUIDE 3.12.0** — 22 figuras integradas (sidebar de 6 entradas, Symbology/Interpretation), `ui_main_dialog_v26` y los `workflow_*` retirados, catálogo es al 100 %; staging en `docs/source/images_v3.12.0/` (ignorado).

## 📌 Pendientes del proyecto

- [ ] **`uv` 0.12.10 → 0.13.0** — bloqueado por pacman (Manjaro stable sirve 0.12.10).
- [ ] **Interop §9** — empezar por **B1** (estilos 3D de sondeo) → B3 → B2 → B4 → Fase A.
- [ ] **Opcional** — revisión nativa de traducciones; refrescar `help/html` con `make docs`.

## ✅ Cerrado recientemente (2026-10-24/25)

- [x] **Tooling: `qgis-manage` 0.15.0** — ver arriba; 3.12.0 ya está publicado en GitHub y en el portal.
- [x] **Core QGIS-agnostic** — `core/` sin imports QGIS/PyQt; puertos de i18n/settings y factory de map settings inyectados; allowlist vacía; mergeado en `main` (`af0bfbbb`).
- [x] **Documentación** — walkthrough v2 consolidada, arquitectura pública reconstruida y análisis técnico v3.11.0 publicado.
- [x] **Interpretation settings tab** — `InterpretationPage` movida a `SettingsPage`; sidebar 7 → 6; alias `page_interpretation` conservado; mergeada en `main` (`1cc2c105`).
- [x] **Validación manual QGIS 4** — selector desplegado y probado: `secc1.shp` muestra 4 de 7 líneas; preview, LOD, export y persistencia OK.
- [x] **`section_feature_id` fix** — selector `fid — label` con filtro de 2 vértices; propagación a topo/geología/estructuras/sondajes, LOD y tasks async; mergeado en `main` (`83e86a2c`).
- [x] **`module_size_gate` PASS** — controller 465→295, geometry 598→69, preview factory 535→202, 3D exporter 472→155, preview renderer 438→335; 0 módulos >400.
- [x] **Portal QGIS** — v3.12.0 activa (2026-10-28), **QGIS 4 Ready**; v3.11.0 fue la anterior (2026-10-23).
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
