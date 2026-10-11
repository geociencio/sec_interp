# Active Task Board (Updated 2026-10-11)

### Completed this session (2026-10-11 — QGIS MCP integration: fork + `qgis_driver`)

- [x] **Fork vendorizado** `tools/qgis_mcp/` (`nkarasiak/qgis-mcp` v0.15.1, `55519eb`); puerto por defecto **9876 → 9877**; `PROVENANCE.md`.
- [x] **Extensión SecInterp**: `handlers/secinterp.py` + 6 tools `secinterp_*` (`src/qgis_mcp/server.py`) + grupo compound `secinterp`; sin `execute_code`. Paridad handler↔tool verificada por los tests del fork.
- [x] **opencode**: `mcp.secinterp_qgis` (compound, 9877) deshabilitado globalmente + subagente **`qgis_driver`**; workflow `.agent-state/workflows/smoke-qgis4.md` (+ fila en `AGENTS.md`).
- [x] **Scope**: `tools/` fuera del ZIP (verificado), de `.analyzerignore` y de `ruff`.
- [x] **Smoke en vivo QGIS 4.2.1** verde (`ping`→`open`→`preview`→`ready`→`results`→`export`); PNG 2286×900. Fork suite **429 passed / 2 skipped**.
- Ref: `docs/maintenance/session_2026-10-11_qgis_mcp_integration.md`.
- [ ] **Mantener el fork sincronizado** con upstream (`PROVENANCE.md`); correr `diagnose` tras cada update.

### Completed this session (2026-10-11 — Type-check gate: mypy wired)

- [x] **`make mypy`** target (runs from `$(CURDIR)/..` con `--explicit-package-bases sec_interp/core sec_interp/exporters`); añadido a `pre-release`.
- [x] **CI**: job `typecheck` en `.github/workflows/test.yml` (`UV_FROZEN=1 make mypy`).
- [x] **32 → 0 errores** en `core` + `exporters` (anotaciones, guards `None`, tipos precisos, quirks de qgis-stubs, contrato `BaseExporter.export`, attrs del mixin).
- [x] Gates verdes: `make mypy` **Success (89 files)** · ruff · **763 OK** (Docker).
- [ ] **Futuro**: extender el gate a `gui` (338 hallazgos) módulo a módulo; opcional `mypy-baseline`.

### Completed this session (2026-10-11 — Toolchain modernization: ruff 0.17 + mypy 2.4)

- [x] **ruff** 0.15.2 → **0.17.0** (`ruff>=0.17.0`; `.pre-commit-config.yaml` rev `v0.8.4` → `v0.17.0`).
- [x] **New rules fixed**: `ISC004` (3 mensajes con paréntesis explícitos en `validation_helpers.py`); `PLR0917` (`# noqa` ampliado en `drillhole_extractor.py`).
- [x] **Markdown**: excluded `**/*.md` from `[tool.ruff]` (0.17 formatea bloques Markdown → doc/churn evitados).
- [x] **mypy** 1.19.1 → **2.4.0** (`mypy>=2.4.0`): sin hallazgos nuevos en el plugin.
- [x] **black** eliminado (no se usa).
- [x] Gates verdes: ruff `--frozen` (CI parity) · pre-commit · **763 OK** (Docker).
- [ ] Opcional: cablear `mypy` a un target acotado; `uv self update` (0.12.10 → 0.13.0).

### Completed this session (2026-10-11 — Dependency refresh, uv "safe batch")

- [x] **Ecosystem**: `qgis-manage` 0.9.0 → **0.9.2** (build/release CI); `qgis-stubs` 0.2.0.post1 → 0.5.0.
- [x] **Dev tools**: `bandit` 1.9.4 · `flake8` 7.4.1 · `pre-commit` 4.6.2 · `pytest` 9.1.1 · `pytest-mock` 3.16.0 · `networkx` 3.7 · `setuptools` 84.0.0 · `sphinx-intl` 2.4.0 · `sphinxcontrib-mermaid` 2.1.1 · `myst-parser` 5.1.0 · `linkify-it-py` 2.2.0.
- [x] **Method**: `uv lock --upgrade-package …` + `uv sync`; `agent_metrics.json` unchanged.
- [x] **Held back (deliberate)**: `ruff` 0.15.2 → 0.17.0 (lint rules + pre-commit/CI sync) and `mypy` 1.19.1 → 2.4.0 (major). `black` unused → removal candidate.
- [x] Gates verdes: ruff · 763 OK (Docker) · `qgis-manage 0.9.2` packaging smoke (exit 0) · `forge metrics validate` PASS.
- [ ] **Opcional**: `uv self update` (0.12.10 → 0.13.0).

### Completed this session (2026-10-11 — qgis-plugin-analyzer 1.16.0, coverage fix + triage)

- [x] **Dependency**: `qgis-plugin-analyzer>=1.15.2` → `>=1.16.0` (`pyproject.toml` deps+dev; `uv.lock`).
- [x] **Root cause found**: 1.15.2 analysed **135** modules whole-project vs the true **171**; 1.16.0 fixes the discovery bug (verified: `core/validation` alone showed 12 in 1.15.2, but only 5 whole-project).
- [x] **i18n triage**: 167 `MISSING_I18N` → **0** (`extra_ignore_calls` for `_stats_edit`/`_check_field` + 129 `# no-i18n`).
- [x] **CC remediation**: 3 functions > 10 refactored (`implausible_crs_reason` 14→7, `export_topography` 12→5, `export_structures` 11→7) → `cc_gate` PASS.
- [x] **Metrics**: `agent_metrics.json` re-synced (quality 56.2, maintainability 99.9, security 100.0, issues 35, i18n 0, tool 1.16.0). Gates verdes (ruff · forge · sync validate · 763 OK · `make context` fresco).
- Ref: `docs/maintenance/session_2026-10-11_qgis_analyzer_1_16_0.md`.
- [ ] **Backlog (aflorado)**: `module_size_gate` FAIL **4** módulos (+3 nuevos); `GOD_OBJECT` 18; i18n de core (mensajes user-facing en inglés).

### Completed this session (2026-10-11 — qgis-plugin-analyzer 1.15.2, B102 fix)

- [x] **Dependency**: `qgis-plugin-analyzer>=1.15.1` → `>=1.15.2` (`pyproject.toml` deps+dev; `uv.lock` vía `--no-cache --refresh`).
- [x] **Re-analysis**: `analyze . --max-cc 10` (175 files / 135 modules). **Security 80.0 → 100.0**; issues 34 → 32 (`SECURITY:B102` eliminado); `security.findings` vacío.
- [x] **Upstream (misma sesión)**: release **1.15.2** del analyzer (fix `check_exec_eval` + CI `publish-pypi`); GitHub release + PyPI vivos.
- [x] **Metrics**: `agent_metrics.json` re-sincronizado (security 100.0, breakdown, tool 1.15.2). Gates verdes (ruff · forge · sync validate · 714 OK · `make context` fresco).
- Ref: `docs/maintenance/session_2026-10-11_qgis_analyzer_1_15_2.md`.

### Completed this session (2026-10-11 — qgis-plugin-analyzer 1.15.1, Security Scanning Restored)

- [x] **Dependency**: `qgis-plugin-analyzer>=1.15.0` → `>=1.15.1` (`pyproject.toml` deps+dev; `uv.lock`).
- [x] **Re-analysis**: `analyze . --max-cc 10` (175 files / 135 modules). **Security Score 100.0 → 80.0** (scanner restaurado); issues 32 → 34 (+2 `SECURITY:B102`).
- [x] **Triage**: los 2 `B102` son **falsos positivos** sobre `QDialog.exec()` (`gui/dialog_interpretation_manager.py:83`, `plugin/lifecycle.py:105`); `# noqa: B102` no los suprime → fix upstream pendiente (1.15.2).
- [x] **Fix parser**: `scripts/sync_metrics.py` divide por el **último** `:` para no perder `SECURITY:B102` (subcontaba 32 vs 34).
- [x] **Metrics**: `agent_metrics.json` re-sincronizado (security 80.0, breakdown, ground truth); tool → 1.15.1. Gates verdes (ruff · forge · sync validate · 714 OK · `make context` fresco).
- Ref: `docs/maintenance/session_2026-10-11_qgis_analyzer_1_15_1.md`.

### Completed this session (2026-10-11 — qgis-plugin-analyzer 1.15.0 Adoption)

- [x] **Dependency**: `qgis-plugin-analyzer>=1.14.0` → `>=1.15.0` (`pyproject.toml` deps+dev; `uv.lock` 1.14.0 → 1.15.0).
- [x] **Re-analysis**: `analyze . --max-cc 10` (175 files / 135 modules). Scores unchanged (57.9 / 99.9 / 100.0); **issues 16 → 32** (+15 `GOD_OBJECT`, +1 `SPAGHETTI_CODE`).
- [x] **Metrics**: `sync_metrics.py` refreshed `agent_metrics.json`; tool → 1.15.0. Gates verdes (ruff · `forge metrics validate` · `sync_metrics --validate` · 714 OK · `make context` fresco).
- Ref: `docs/maintenance/session_2026-10-11_qgis_analyzer_1_15_0.md`.
- [ ] **Backlog (nuevo, no bloqueante)**: 15 `GOD_OBJECT` (orquestadores GUI), 1 `SPAGHETTI_CODE` (`drillhole_exporters.py::_write_traces`).


### Completed this session (2026-10-10 — ai-context-core v5.1.0 Adoption)

- [x] **Dependency**: `ai-context-core>=5.1.0` (`pyproject.toml` deps+dev, `uv.lock` 5.0.1 → 5.1.0).
- [x] **Config**: `.ai-context/config.toml` `max_tokens` 6000 → 8000 + `mermaid_style=false` (default v5.1.0).
- [x] **Metrics**: `agent_metrics.json` tool → 5.1.0; `context_tokens` 619 → 2639 (stale fix).
- [x] Gates verdes: ruff · `forge metrics validate` · suite local OK (unittest discover) · `make context` fresco.
- Commit: `ff6f5cfe`. Ref: `docs/maintenance/session_2026-10-10_ai_context_core_v510.md`.

### Completed this session (2026-10-10 — ai-context-core Value Leverage)

- [x] **Scope fix** `.analyzerignore` (**71 → 135 módulos**; cubre `core/`+`gui/`+`exporters/`).
- [x] **Config v5** `.ai-context/config.toml` + **notas curadas** `.ai-context/architecture_notes.md`.
- [x] **Frescura**: `make context` + `context-{deps,git,roadmap,graph,health}`; sección "Context & Architecture Tooling" en `AGENTS.md`.
- [x] **Higiene**: `README_DEV.md`/v500 corregidos; 44 legacy `.ai-context/` y `antigravity-framerepo/` eliminados. Gates verdes (ruff/forge/docs/CC/i18n).
- [ ] **Backlog (tras los releases)**: `module_size_gate=FAIL` (`core/controller.py` 428 > 400), 10 `MISSING_DOCSTRING`, 4 `NON_PYTHONIC_LOOP`, 2 `POTENTIAL_MISSING_SLOT`, +6 signal leaks.
- Plan: `docs/plans/implementation_plan_ai_context_core_value.md`. Ref: `docs/maintenance/session_2026-10-10_ai_context_core_value.md`.

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
