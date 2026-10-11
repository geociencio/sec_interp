# Maintenance Session: 2026-10-11 - qgis-plugin-analyzer 1.16.0 Upgrade

## Technical Summary

Adopted `qgis-plugin-analyzer` **1.16.0**. Beyond the documented release notes, the
adoption exposed a **latent module-coverage bug in 1.15.2**: whole-project analysis
reported **135** modules while the plugin actually contains **171** (its real `.py`
count minus the two ignored root scripts). 1.16.0 fixes discovery, so code that had
never been gated — `core/validation/*`, `exporters/*`, `gui/adapters/*`,
`gui/ui/pages/*` — is now analysed. Every finding surfaced by the corrected coverage
was triaged in the same cycle so the quality gates stay green.

## Root cause: 1.15.2 under-reported coverage

| | 1.15.2 | 1.16.0 | Truth |
| :--- | :--- | :--- | :--- |
| Modules analysed | 135 | **171** | **171** |
| Physical lines | 15,832 | 22,703 | — |

Evidence it was a 1.15.2 bug (not a 1.16.0 over-reach):

- `find core gui exporters plugin *.py` → 173; minus the two ignored root scripts
  (`logger_config.py`, `run_qgis_manage.py`) → **171** = the 1.16.0 count exactly.
- `1.15.2 analyze core/validation` (sub-directory) listed all **12** modules; the
  *whole-project* run listed only **5** — so 1.15.2 could see the files, but its
  whole-project aggregation dropped 36 modules (`core` 53/74, `exporters` 5/13,
  `gui` 71/78).
- Consequence: every historical metric (quality 57.9, maintainability 99.9, **0**
  `MISSING_I18N`, 32 issues) was computed over ~79 % of the codebase.

## Changes Made

### Phase 1 — Dependency bump
- `pyproject.toml`: `qgis-plugin-analyzer>=1.15.2` → `>=1.16.0` (deps + dev).
- `uv.lock` via `uv lock --upgrade-package qgis-plugin-analyzer --no-cache --refresh`
  + `uv sync`; `qgis-analyzer --version` → `1.16.0`.

### Phase 2 — Re-analysis (corrected baseline)

| Metric | 1.15.2 | 1.16.0 (initial) | 1.16.0 (after triage) |
| :--- | :--- | :--- | :--- |
| Modules | 135 | 171 | 171 |
| Module Stability | 57.9 | 56.3 | **56.2** |
| Maintainability | 99.9 | 95.5 | **99.9** |
| Security (Bandit) | 100.0 | 100.0 | 100.0 |
| Total issues | 33 | 203 | **35** |
| `MISSING_I18N` | 0 | 167 | **0** |
| `GOD_OBJECT` | 15 | 18 | 18 |
| CC gate | PASS | **FAIL (3)** | **PASS** |
| Module Size gate | FAIL (1) | FAIL (4) | FAIL (4) |

### Phase 3 — i18n triage (167 → 0)
- All 167 findings were in the **36 newly-covered** modules (0 in previously-covered
  ones) → the rule did not change; coverage did.
- `[tool.qgis-analyzer.profiles.default.rules.MISSING_I18N] extra_ignore_calls`:
  added `_stats_edit` and `_check_field`, whose text arguments are translated
  internally via `self.tr(...)` (the rule cannot follow that indirection).
- **129 inline `# no-i18n`** tags for the remainder. `core/` is deliberately
  Qt-free, so its user-facing messages are English by design; translating them
  requires injecting the GUI translator (`QCoreApplication.translate` is
  forbidden in `core/`). This is recorded as **core i18n debt**.

### Phase 4 — Cyclomatic-complexity remediation (3 functions → 0)
- `core/validation/crs_plausibility.py::implausible_crs_reason` **14 → 7**
  (split into `_geographic_out_of_bounds` / `_projected_maybe_geographic`).
- `core/services/export/handlers/topography.py::export_topography` **12 → 5**
  (extracted `_export_profile_pair`, `_smoothed_topography`, `_record_written`).
- `core/services/export/handlers/structures.py::export_structures` **11 → 7**
  (extracted `_resolve_raster_resolution`, `_record_written`).
- Behaviours and messages preserved (53 targeted unit tests green).

### Phase 5 — Metrics sync
- `uv run python scripts/sync_metrics.py` refreshed `agent_metrics.json`
  (scores, `issue_breakdown`, ground truth, `module_size_gate`);
  `meta.tools.qgis-plugin-analyzer` → `1.16.0` (manual).

### Phase 6 — Documentation
- Added this session note; `DEVELOPMENT_LOG.md` + `CHANGELOG.md` (`[Unreleased]`).
- `.agent-state/task.md` / `next_steps.md` updated. `AI_CONTEXT.md` regenerated
  via `make context`.

## Verification Results

- `ruff check` / `ruff format --check`: clean (179 files).
- `make docker-test`: **763 tests OK** (23 / 301 / 323 / 40 / 76).
- `python .agent/tools/forge.py metrics validate`: **PASS**.
- `uv run python scripts/sync_metrics.py --validate`: **PASS**.
- `make context`: fresh (**2,650 / 8,000** tokens, 33 %, **171 modules**).

## Backlog (surfaced by the coverage fix, non-blocking)

- `module_size_gate` FAIL grows 1 → **4**: `core/controller.py` 428,
  `exporters/interpretation_3d_exporter.py` 466, `gui/adapters/geometry.py` 598,
  `gui/preview_layer_factory.py` 511.
- `GOD_OBJECT` 15 → 18 (the rule now also flags classes with > 20 methods).
- `MISSING_DOCSTRING` 10, `NON_PYTHONIC_LOOP` 4, `POTENTIAL_MISSING_SLOT` 2,
  `SPAGHETTI_CODE` 1, `UNPRECISE_LAYER` 1.
- Core i18n debt: user-facing core-sourced messages are English (Qt-free core).
- Optional upstream improvement: `MISSING_I18N` flags strings already translated
  via helper indirection and attribute docstrings (only the first module string is
  recognised as a docstring).
