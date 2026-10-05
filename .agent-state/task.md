# Active Task Board (Updated 2026-10-04)

### Completed this session (2026-10-04 — Offline Help: User Guide only)

- [x] **Help button → User Guide only**: offline manual reduced to a single `USER_GUIDE`
  document in all 14 languages (clean nav), via `docs/source/help_index.rst` + `conf.py`
  (`SECINTERP_DOCS_HELP=1`) + `build_docs.sh` web/help split (renames `help_index.html` →
  `index.html`). Plugin code and published website untouched.
- [x] `.gitignore`: ignore `graphify-out/` (local code graph / Obsidian vault).
- [ ] Optional: `make docs-i18n-update` to translate the “SecInterp Help” title.
- Commits: `92e5eabd`, `81d1f39d`. Reference: `docs/maintenance/session_2026-10-04_help_userguide_only.md`.

### Completed this session (2026-10-04 — Agentic Forge extraction F1–F5)

- [x] **F1–F5**: framework agéntico extraído y publicado en **Codeberg** (`agentic-forge`, MIT),
  consumido como **submódulo** en `.agent/`; estado del proyecto en `.agent-state/`; CLI
  `.agent/tools/forge.py`; `sync_metrics` partido (core genérico + colector). Plan:
  `docs/plans/implementation_plan_agentic_forge_extraction.md`.
- [x] Commits: `be5baa9f`, `a0241127`, `1a0290e4`, `a5a6a281`, `43a4aa64`, `2e7940c7`, `3ee51a5c`.
- [ ] Pendiente Codeberg: **description + topics** del repo `agentic-forge` (UI).

### Completed this session (2026-10-04 — v3.9.1, v2-first docs, ZIP/CI fixes)

- [x] **v3.9.1 published** (the cron never fired → published via `workflow_dispatch`; tag +
  GitHub release + ZIP). ZIP asset later **replaced** with the corrected/optimized build.
- [x] **v3.9.1 uploaded to the QGIS plugin repository** (portal) — `dist/sec_interp.3.9.1.zip`
  (2.38 MiB, offline help in 14 languages) is live.
- [x] **Merged `release/v3.9.1` → `main`** (`11806511`): `main` now has the smoothed profile;
  4 conflicts resolved (metadata/CHANGELOG/DEVELOPMENT_LOG/agent_metrics); tests 745 → **763**.
- [x] **Docs v2-first**: README + 3 canonical architecture/report docs → v3.9.1; **v1 vault
  frozen** (removed from `sync_vault_mirrors.sh`); v2 mirrors + structure docs regenerated;
  vault footers (356 notes + Index) → v3.9.1.
- [x] **`.agent/` quick wins**: `black`→`ruff format`, phantom refs, stale counts (763/15),
  Gen 8 marked done, `qgis-migration-4x` referenced, validator count fixed.
- [x] **Version bump** `metadata`/`pyproject` → 3.9.1 + `make docs-version` (7 docs) + CHANGELOG.
- [x] **Offline help / ZIP**: CI shipped the ZIP **without `help/`**; fixed the workflow +
  `build_docs.sh`; optimized help (dedup `_static` + lossless PNG) → ZIP **3.76 → 2.38 MiB**;
  excluded `.release-queue.json` from the package.

### ⚠️ Pending — `legend_widget.py` divergence (block for the train merge)

The release-train branches **removed** `gui/legend_widget.py` (`1d82db0f`, legend side panel);
`main` **keeps** it. When merging the train (`v3.11.0`) into `main`: drop the `legend_widget.py`
references in `docs/ARCHITECTURE_EN.md` and `docs/structure/project_structure*.md` and resolve
the conflict. (This also blocked the direct `build_docs.sh` backport via the pre-push doc gate.)

### Completed this session (2026-09-27 — release train + CI + vault)

- [x] **v3.9.0 released** (tag `v3.9.0`, GitHub release live; portal skipped by decision).
  Fixed a release-blocking mock-isolation bug in `tests/gui`; gates green (696 local /
  681 Docker, analyzer 0, security PASS); ZIP audited. Commits `e00604e`, `664d775`.
- [x] **Release train v3.9.1 / v3.10.0 / v3.11.0** prepared on cumulative branches and
  **scheduled** (Sundays Oct 4 / 11 / 18) via `.github/workflows/scheduled-release.yml`;
  validated with a `dry_run`.
- [x] **CI repaired on `main`** (ruff pin, Qt6 detection, Docker test job, docs token guard,
  legacy `release.yml` removed) — `main` all green, no more failed-run notifications.
- [x] **Qt6 / QGIS 4 fixes**: `QgsRasterBandStats` scope + `Qgis.RasterBandStatistic` fallback.
- [x] **Code Walkthrough v2 vault refreshed to v3.9.0**: 308 notes, `check_notes --strict` PASS.

## 🎯 Current Focus: Goal 1 — 3D Interpretation & Symbology Enhancements

**Status**: IN PROGRESS — Adaptive VE (Goal 1.2 umbrella) COMPLETE ✅
**Reference plan**: `docs/plans/implementation_plan_adaptive_ve_v3.8.0.md` (COMPLETADO)

### Pending Tasks

- [ ] **1.1** Implement a live symbology/legend styling preview under the Settings sidebar
- [x] **1.2** Adaptive VE — Fases 1-4 COMPLETE ✅ 2026-09-21 (service + toggle + integration + persistence; 24 tests; VE visible en Results + etiqueta junto al checkbox)
- [ ] **1.5** Expand Cartesian vertical projection integration tests (highly deviated drillhole surveys)

### Also completed this session (beyond the plan)

- [x] VE visible en el panel Results (`2.6× (auto)` / `3.5× (manual)`) + etiqueta de solo lectura junto al checkbox Auto
- [x] Fix: layers temporales de preview ya no persisten al cerrar (OK/Save, Cancel/X y unload)
- [x] **Code Walkthrough Vault v2** (docs-only, 2026-09-22): bóveda bilingüe **COMPLETA** —
  Core 56/56 + GUI 73/73 + Fase 3 22/22 + Fase 4 (23 hubs `layer_*` + Index final)
  (302 notas, `check_notes.py --strict` PASS, 0 enlaces rotos). Tooling + `project_structure_table.md`.
  Ver `.agent-state/next_steps.md`.

### Also completed this session (2026-09-23, beyond the plan)

- [x] **CRS Sampling Hardening + Structure/Section fixes** (6 commits
  `baf11d8c..eb9ffa20`): anti-cuelgue DEM/CRS, detección bloqueante de CRS mal
  etiquetado, sampler CRS-aware (geología/estructuras/collares), fix de combos
  estructurales. Suite verde (unittest 666), smoke QGIS 4 OK. Ver `.agent-state/next_steps.md`.

### Also completed this session (2026-09-23, smoothed profile)

- [x] **Optional smoothed topography profile** (`3094a1f1`, `76fc6206`):
  Smooth control + window in Controls, soft-red overlay, extra smoothed export
  files. Suite green, analyzer 0 issues. Ver `.agent-state/next_steps.md`.

### Also completed this session (2026-09-23, DEM/Section v3.9.0)

- [x] **Fases 1.5 + 1.6 + 2 + 3** completadas (`2a14767b..6d342189`): resolver
  central de la sección, stats de banda del DEM, modo de color topo, stats
  perfil-vs-DEM. Suite verde, analyzer 0 issues, smoke QGIS 4 OK. Ver
  `.agent-state/next_steps.md`.

### Resume Point

**Agentic Forge (F1–F5) COMPLETO**: framework en `codeberg.org/geociencio/agentic-forge`
(MIT, `main` `a77548b`, tags `v1.0.0`/`v1.1.0`), consumido como submódulo en `.agent/`
(gobernanza vía `scripts/update_agentic_forge.sh`). Solo queda poner **description + topics**
en Codeberg.

**Plugin**: v3.9.0 y v3.9.1 publicados (v3.9.1 en el portal QGIS); `main` con v3.9.1. Quedan
**v3.10.0 (11 oct)** y **v3.11.0 (18 oct)** programados. Siguiente: resolver la **divergencia
`legend_widget.py`** al mergear el tren, **refresco de la bóveda a v3.11.0**, y deuda funcional
(**Goal 1.1 Fase 4** presets, **selector multi-línea**, **Goal 1.5**).

### Non-blocking Documented Debt

- 6 gray areas (genuine QGIS integration): `i18n.py`, `config.py`, `data_cache.py`,
  `access_control_service.py`, `export/map_settings_factory.py`, `export/orchestrator.py`, `io.py`.
- Optional docs: translate `USER_GUIDE` fr (28%) / de (18%); run `make docs` to publish.

### Closed

- Goal 2 (tech debt): analyzer 0 issues, module_size PASS, CC PASS, i18n PASS ✅
- Adaptive VE (Goal 1.2): full end-to-end ✅
