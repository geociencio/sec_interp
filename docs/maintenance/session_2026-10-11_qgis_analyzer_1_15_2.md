# Maintenance Session: 2026-10-11 - qgis-plugin-analyzer 1.15.2 Upgrade

## Technical Summary

Adopted `qgis-plugin-analyzer` **1.15.2**, the upstream fix for the `B102`/`B307`
false positives flagged during the 1.15.1 adoption. Pinning SecInterp to 1.15.2 removes the
two false positives on Qt `QDialog.exec()` and restores the Security Score to 100.0. This
step also closes the upstream release loop: the same session fixed and released
qgis-plugin-analyzer 1.15.2 (including a CI fix so releases auto-publish to PyPI).

## Changes Made

### Phase 1 — Dependency bump
- `pyproject.toml`: `qgis-plugin-analyzer>=1.15.1` → `>=1.15.2` (deps + dev).
- `uv.lock`: upgraded via `uv lock --upgrade-package qgis-plugin-analyzer --no-cache
  --refresh` (the plain `--refresh` still saw `<=1.15.1` through the stale simple-index
  cache, per the documented "freshly published release" lesson) + `uv sync`.
  Verified `qgis-analyzer version` → `1.15.2`.

### Phase 2 — Re-analysis
- `uv run qgis-analyzer analyze . --max-cc 10` (175 files / 135 modules).

| Metric | 1.15.1 | 1.15.2 | Delta |
| :--- | :--- | :--- | :--- |
| Module Stability | 57.9 | 57.9 | = |
| Maintainability | 99.9 | 99.9 | = |
| Security (Bandit) | 80.0 | **100.0** | +20.0 |
| Type Hint (Params/Returns) | 95.2 / 99.5 | 95.2 / 99.5 | = |
| Docstring Coverage | 98.5 | 98.5 | = |
| Total issues | 34 | **32** | −2 |
| `SECURITY:B102` | 2 | **0** | −2 |
| CC gate | PASS | PASS | = |
| Module Size gate | FAIL (1) | FAIL (1) | = |

`security.findings` is now empty (`count: 0`). The two previous findings
(`gui/dialog_interpretation_manager.py:83`, `plugin/lifecycle.py:105`, both
`QDialog.exec()`) are gone.

### Phase 3 — Metrics sync
- `uv run python scripts/sync_metrics.py` refreshed `agent_metrics.json`: `security_score`
  80.0 → 100.0, `total_issues` 34 → 32, `issue_breakdown` (B102 removed),
  `ground_truth_sources`. `meta.tools.qgis-plugin-analyzer` → `1.15.2` (manual).

### Phase 4 — Documentation
- Added this session note; `DEVELOPMENT_LOG.md` + `CHANGELOG.md` (`[Unreleased]`).
- `.agent-state/task.md` / `next_steps.md` updated.
- `AI_CONTEXT.md` regenerated fresh via `make context`.

## Verification Results

- `ruff check` / `ruff format --check`: clean.
- `PYTHONPATH=.. uv run python3 -m unittest discover tests`: **714 OK**.
- `python .agent/tools/forge.py metrics validate`: **PASS**.
- `uv run python scripts/sync_metrics.py --validate`: **PASS**.
- `make context`: fresh (`2,639 / 8,000` tokens, 33 %).

## Related upstream work (same session)

- **qgis-plugin-analyzer 1.15.2 released** from the analyzer repo:
  - `fix(security)`: `check_exec_eval` now flags only bare-name `exec(...)`/`eval(...)`,
    ignoring attribute/method calls (Qt `QDialog.exec()`); +2 regression tests.
  - `ci(release)`: `publish-pypi` no longer `needs` the tag-push draft job (which is skipped
    on `release` events), so releases now auto-publish to PyPI — the reason 1.15.0/1.15.1
    had to be uploaded manually.
  - Tag `v1.15.2`, GitHub release and **PyPI** (`qgis_plugin_analyzer-1.15.2`) are live.

## Backlog

- `module_size_gate` FAIL (`core/controller.py` 428 > 400); 15 `GOD_OBJECT`, 1
  `SPAGHETTI_CODE`, 10 `MISSING_DOCSTRING`, 4 `NON_PYTHONIC_LOOP`, 2 `POTENTIAL_MISSING_SLOT`.
- Optional upstream hardening (not requested): `B602` matches any `.run(..., shell=True)`
  and `B608` any `.execute(...)` without validating the receiver object.
