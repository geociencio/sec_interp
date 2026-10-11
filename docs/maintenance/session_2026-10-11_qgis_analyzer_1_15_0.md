# Maintenance Session: 2026-10-11 - qgis-plugin-analyzer 1.15.0 Upgrade

## Technical Summary

Adopted the newly published `qgis-plugin-analyzer` **1.15.0** ("Repo Hygiene &
Hardening") and re-ran the full static analysis to refresh ground-truth metrics in
`agent_metrics.json`. The bump is **tooling-only** (no plugin runtime code touched). The
1.15.0 release adds design-pattern / anti-pattern detection (`GOD_OBJECT`,
`SPAGHETTI_CODE`, `MAGIC_NUMBER`, `DEAD_CODE`), Halstead metrics and module-level
optimization suggestions, a transversal `# noqa`, configurable `--workers N`, and a
reliable ruff audit — which surfaced **new findings** without changing any score.

## Changes Made

### Phase 1 — Dependency bump
- `pyproject.toml`: `qgis-plugin-analyzer>=1.14.0` → `>=1.15.0` (both `dependencies` and
  `[dependency-groups].dev`).
- `uv.lock`: upgraded via `uv lock --upgrade-package qgis-plugin-analyzer --refresh`
  (`1.14.0` → `1.15.0`, resolved 74 packages) + `uv sync`. Verified with
  `qgis-analyzer version` → `1.15.0`.

### Phase 2 — Re-analysis
- `uv run qgis-analyzer analyze . --max-cc 10` (scope: all, **175 files / 135 modules**).

| Metric | 1.14.0 | 1.15.0 | Delta |
| :--- | :--- | :--- | :--- |
| Module Stability | 57.9 | 57.9 | = |
| Maintainability | 99.9 | 99.9 | = |
| Security (Bandit) | 100.0 | 100.0 | = |
| Type Hint (Params) | 95.2% | 95.2% | = |
| Type Hint (Returns) | 99.5% | 99.5% | = |
| Docstring Coverage | 98.5% | 98.5% | = |
| Total issues | 16 | 32 | **+16** |
| `GOD_OBJECT` | – | 15 | +15 |
| `SPAGHETTI_CODE` | – | 1 | +1 |
| `MISSING_DOCSTRING` | 10 | 10 | = |
| `NON_PYTHONIC_LOOP` | 4 | 4 | = |
| `POTENTIAL_MISSING_SLOT` | 2 | 2 | = |
| CC gate | PASS | PASS | = |
| Module Size gate | FAIL (1) | FAIL (1) | = |

The score is **unchanged**: the new anti-pattern rules are additive detectors, not
re-weighted. `GOD_OBJECT` flags classes with > 15 instance attributes (or > 20 methods);
`SPAGHETTI_CODE` flags deeply nested logic.

### Phase 3 — Metrics sync
- `uv run python scripts/sync_metrics.py` refreshed `agent_metrics.json`:
  `total_issues` 16 → 32, `issue_breakdown` (+ `GOD_OBJECT` 15, `SPAGHETTI_CODE` 1),
  `ground_truth_sources.qgis_analyzer` (date/command/scores/issues), `meta.last_updated`.
- Manual bump of `meta.tools.qgis-plugin-analyzer` → `1.15.0` and the `i18n_note` string
  (both reference the analyzer version and are not updated by the sync script).
- `python .agent/tools/forge.py metrics validate` and
  `uv run python scripts/sync_metrics.py --validate`: **PASS** (47 agentic files).

### Phase 4 — Documentation
- Added this session note.
- `docs/DEVELOPMENT_LOG.md` + `docs/CHANGELOG.md` (`[Unreleased]`) entries.
- `.agent-state/task.md` / `next_steps.md` updated (new anti-pattern backlog).
- `AI_CONTEXT.md` regenerated fresh via `make context`.

## Verification Results

- `ruff check` / `ruff format --check`: clean (179 files formatted).
- `PYTHONPATH=.. uv run python3 -m unittest discover tests`: **714 OK**.
- `python .agent/tools/forge.py metrics validate`: **PASS**.
- `uv run python scripts/sync_metrics.py --validate`: **PASS**.
- `make context`: fresh (`2,639 / 8,000` tokens, 33%).

## Impact

### New Findings (backlog, non-blocking)
- **15 × `GOD_OBJECT`** — classes exceeding the attribute/method heuristic, mainly GUI
  orchestrators (`gui/ui/pages/preview_page.py` 39 attrs, `gui/main_dialog.py` 33,
  `gui/dialog_preview_manager.py` 30) plus `core/controller.py` and
  `core/services/vertical_exaggeration_service.py`. These overlap the documented
  `module_size_gate` debt.
- **1 × `SPAGHETTI_CODE`** — `exporters/drillhole_exporters.py::_write_traces`
  (complexity 9, depth 5).
- **Optimizations** — `complexity_refactoring` / `module_too_large` suggestions for
  `core/controller.py` (428 lines) and several exporters.
- Design patterns detected (informational): `decorator` × 3, `factory` × 5.

The plugin runtime is unaffected; `GOD_OBJECT` and `SPAGHETTI_CODE` are **new
heuristics**, not regressions. They feed the existing post-release backlog.

## Lessons

- A tool upgrade can add findings without moving a single score: 1.15.0 kept Module
  Stability at 57.9 yet raised `total_issues` 16 → 32 purely via new anti-pattern rules.
  Always re-run `analyze .` (never `summary`) after a version bump and read the issue
  *breakdown*, not just the score.
