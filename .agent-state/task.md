# Active Task Board (Updated 2026-10-19)

> Historial detallado: `.agent-state/history/tasks/` y `docs/maintenance/`.
> Este tablero solo refleja el estado activo; las sesiones cerradas no se acumulan aquí.

## 🎯 Foco actual: fiabilidad del sistema agéntico (P0)

- [ ] **Memoria** — consolidar las 24 lecciones >90 días, marcar `consolidated_in`, arreglar `prune_lessons` y aplicar el límite de 350 líneas. Ver `docs/qa/AGENT_AUDIT_2026-10-18.md` §3.1.
- [ ] **Validador** — incluir los 4 workflows de `.agent-state/workflows/` en `forge validate`, `--graph` y `--conflicts`; añadir test de regresión.
- [ ] **Workflows** — sustituir el `pytest` genérico por el comando real del proyecto (unittest) y parametrizarlo en `forge.toml`.

## 📌 Pendientes del proyecto

- [ ] **Portal QGIS** — confirmar aprobación de v3.11.0 (la página aún lista 3.10.0).
- [ ] **`module_size_gate`** — 5 módulos > 400 líneas (detalle en `.agent-state/memory/agent_metrics.json`).
- [ ] **`uv` 0.12.10 → 0.13.0** — bloqueado por pacman (Manjaro stable sirve 0.12.10).
- [ ] **Interop §9** — empezar por **B1** (estilos 3D de sondeo) → B3 → B2 → B4 → Fase A.
- [ ] **Opcional** — borrar la rama `backup/main-pre-v3.11.0` cuando se valide `main`.

## ✅ Cerrado recientemente (2026-10-18/19)

- [x] **v3.11.0** — release publicada, ZIP verificado (311 archivos, 2,28 MiB, ayuda en 14 idiomas) y subido al portal; merge del tren en `main`.
- [x] **Auditorías** — `docs/qa/REPO_AUDIT_2026-10-18.md` y `docs/qa/AGENT_AUDIT_2026-10-18.md`.
- [x] **Métricas** — `agent_metrics.json` reconciliado: 37 issues (incluye `UNPRECISE_LAYER`), 49 sesiones y `tests_static=797` / `tests_executed=748` separados del baseline legacy 792; `sync_metrics.py --validate` comprueba frescura contra `project_context.json`.
- [x] **Handoff** — `task.md` reescrito; el tablero anterior quedó archivado en `.agent-state/history/tasks/tasks_2026-10-18_pre_metrics_reconciliation.md`.
- [x] **Release** — gate de docstrings alineado con el baseline real (99,0 %) y conteos de tests manuales eliminados de `release-plugin.md`.

## 🧹 Deuda no bloqueante

- 7 archivos de `core/` en la allowlist de QGIS: `config.py`, `data_cache.py`, `access_control_service.py`, `export/map_settings_factory.py`, `export/orchestrator.py`, `utils/i18n.py`, `utils/io.py`.
- Traducciones de documentación: `USER_GUIDE` fr (28 %) / de (18 %).
- i18n del plugin: catálogos `.ts` desincronizados respecto a v3.9–v3.11 (ver auditoría del repositorio, §6).

## 🏁 Cerrado

- **Goal 1.1** — symbology/legend styling (v3.11.0).
- **Divergencia `legend_widget.py`** — resuelta por el merge de v3.11.0.
- **Adaptive VE (Goal 1.2)** — completo.
- **Goal 2 (tech debt)** — analyzer 0 issues en su momento; el estado actual es 37 hallazgos conocidos.
