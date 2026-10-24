# Active Task Board (Updated 2026-10-23)

> Historial detallado: `.agent-state/history/tasks/` y `docs/maintenance/`.
> Este tablero solo refleja el estado activo; las sesiones cerradas no se acumulan aquí.

## 🎯 Foco actual: deuda del proyecto (post-hardening)

- [x] **Memoria** — `AGENT_LESSONS.md` compactado de 98 a 27 lecciones (318 líneas, límite 350); las 71 restantes quedan archivadas en `.agent-state/history/memory/AGENT_LESSONS_2026-10-19_full.md` y destiladas en `project-context`. `prune_lessons` probado y `forge.py memory check` + gate de `validate` añadidos.
- [x] **Validador** — `forge validate` y `--graph` recorren framework + `.agent-state/workflows/` (18 workflows); detección de nombres duplicados y test de regresión para skills/scripts/frontmatter del overlay.
- [x] **Workflows/deps** — workflows genéricos migrados a `unittest` (`run-tests`, `start-session`, `close-session`, `release-package`, index); `forge.toml` declara `test_command`/`test_command_docker`; eliminadas las deps `pytest`, `pytest-qt` y `pytest-mock` y regenerado `uv.lock`; `tests/README.md` reescrito.

## 📌 Pendientes del proyecto

- [ ] **`module_size_gate`** — 4 módulos > 400 líneas restantes (`core/controller.py` resuelto: 465 → 295).
- [ ] **`uv` 0.12.10 → 0.13.0** — bloqueado por pacman (Manjaro stable sirve 0.12.10).
- [ ] **Interop §9** — empezar por **B1** (estilos 3D de sondeo) → B3 → B2 → B4 → Fase A.
- [ ] **Opcional** — borrar la rama `backup/main-pre-v3.11.0` cuando se valide `main`.

## ✅ Cerrado recientemente (2026-10-18/24)

- [x] **Refactor `core/controller.py`** — 465 → **295 líneas**; caché y procesadores movidos a `core/services/profile/`; 21 tests nuevos; suite **807 OK** (856 static); module-size gate 5 → 4 módulos. Rama local `refactor/module-size-controller`.

- [x] **Portal QGIS** — v3.11.0 aprobada/en verde en el repositorio de plugins (2026-10-23); el badge de versión del README se actualizó de 3.9.1 a 3.11.0 y enlaza a la ficha.

- [x] **Release gate** — `scheduled-release.yml` ejecuta ruff, mypy, docs, security, i18n y analyzer antes de empaquetar; `make pre-release` incluye analyzer + i18n-check y 5 tests guardan el orden.
- [x] **i18n** — los 13 catálogos se regeneraron a 363 mensajes, se completaron las cadenas v3.9–v3.11 (0 `unfinished`), se recompilaron los `.qm` y se añadió el gate `make i18n-check` (`tests/core/test_i18n_catalogs.py`).
- [x] **Compatibilidad QGIS 3.28 / Python 3.9** — eliminados `isinstance(x, A | B)` y `zip(strict=...)`; `from __future__ import annotations` en `safe_loader`; ruff con `target-version=py39`; gate estático `tests/core/test_python_compat.py`; README/README_DEV alineados.
- [x] **Caché de exportación** — las claves de `ProfileController` incluyen línea, ráster, `section_feature_id`, suavizado/ventana, banda y todos los mapeos de campos de sondaje; 4 tests de regresión.
- [x] **v3.11.0** — release publicada, ZIP verificado (311 archivos, 2,28 MiB, ayuda en 14 idiomas) y subido al portal; merge del tren en `main`.
- [x] **Auditorías** — `docs/qa/REPO_AUDIT_2026-10-18.md` y `docs/qa/AGENT_AUDIT_2026-10-18.md`.
- [x] **Agentic Forge v1.4.2** — submódulo actualizado (`b264e35`, hotfix de v1.4.1); adaptados `sync_metrics.py` a `forge_metrics_checks`/`forge_metrics_report`, los tests de memoria al modo dry-run (`--apply`) y los tests del validador a `workflow_graph`/`skill_conflicts`; `qa-docker` sustituido por `testing-standards`.
- [x] **Métricas** — `agent_metrics.json` reconciliado: 37 issues (incluye `UNPRECISE_LAYER`), 50 sesiones y `tests_static=827` / `tests_executed=778` separados del baseline legacy 792; `sync_metrics.py --validate` comprueba frescura contra `project_context.json`.
- [x] **Handoff** — `task.md` reescrito; el tablero anterior quedó archivado en `.agent-state/history/tasks/tasks_2026-10-18_pre_metrics_reconciliation.md`.
- [x] **Release** — gate de docstrings alineado con el baseline real (99,0 %) y conteos de tests manuales eliminados de `release-plugin.md`.

## 🧹 Deuda no bloqueante

- 7 archivos de `core/` en la allowlist de QGIS: `config.py`, `data_cache.py`, `access_control_service.py`, `export/map_settings_factory.py`, `export/orchestrator.py`, `utils/i18n.py`, `utils/io.py`.
- `ProfileController` `GOD_OBJECT` (22 atributos, `core/controller.py:30`) — **diferido** tras el refactor de tamaño; agrupar lazy services en una sesión aparte.
- Traducciones de documentación: `USER_GUIDE` fr (28 %) / de (18 %).

## 🏁 Cerrado

- **Goal 1.1** — symbology/legend styling (v3.11.0).
- **Divergencia `legend_widget.py`** — resuelta por el merge de v3.11.0.
- **Adaptive VE (Goal 1.2)** — completo.
- **Goal 2 (tech debt)** — analyzer 0 issues en su momento; el estado actual es 37 hallazgos conocidos.
