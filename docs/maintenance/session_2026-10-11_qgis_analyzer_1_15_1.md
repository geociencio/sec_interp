# Maintenance Session: 2026-10-11 - qgis-plugin-analyzer 1.15.1 Upgrade

## Technical Summary

Adopted `qgis-plugin-analyzer` **1.15.1** ("Security Scanning Restored"). This patch
immediately follows the 1.15.0 adoption in the same session and is the upstream fix for the
**disconnected security registry** reported in the deep-analysis report
(`qgis-plugin-analyzer/docs/reports/DEEP_ANALYSIS_v1.15.0_DEAD_CODE_DUPLICATION.md`). The
release also lands the recommended hardening: shared `rules/scopes.py`, dead-code removal
and complexity reductions.

## Changes Made

### Phase 1 — Dependency bump
- `pyproject.toml`: `qgis-plugin-analyzer>=1.15.0` → `>=1.15.1` (deps + dev).
- `uv.lock` via `uv lock --upgrade-package qgis-plugin-analyzer --refresh`
  (1.15.0 → 1.15.1) + `uv sync`. Verified `qgis-analyzer version` → `1.15.1`.

### Phase 2 — Re-analysis
- `uv run qgis-analyzer analyze . --max-cc 10` (175 files / 135 modules).

| Metric | 1.15.0 | 1.15.1 | Delta |
| :--- | :--- | :--- | :--- |
| Module Stability | 57.9 | 57.9 | = |
| Maintainability | 99.9 | 99.9 | = |
| Security (Bandit) | 100.0 | **80.0** | −20.0 |
| Type Hint (Params/Returns) | 95.2 / 99.5 | 95.2 / 99.5 | = |
| Docstring Coverage | 98.5 | 98.5 | = |
| Total issues | 32 | 34 | +2 |
| `SECURITY:B102` | – | 2 | +2 |
| CC gate | PASS | PASS | = |
| Module Size gate | FAIL (1) | FAIL (1) | = |

The Security Score drop is **not a plugin regression** — it is the scanner finally running.
The analyzer's own release notes state: *"expect real findings now"*.

### Phase 3 — Triage of the new findings (2 × `SECURITY:B102`)

Both findings are **false positives** of the restored `check_exec_eval` rule (B102 = `exec`):

| Location | Code | Reality |
| :--- | :--- | :--- |
| `gui/dialog_interpretation_manager.py:83` | `dlg.exec()` | `QDialog.exec()` (Qt event loop) |
| `plugin/lifecycle.py:105` | `self.dlg.exec()` | `QDialog.exec()` (Qt event loop) |

The rule matches any call whose callee name is `exec`, including attribute calls
(`ast.Attribute.attr`), because `SecurityContext.call_function_name` returns the attribute
name (`security_checker.py`). Verified with a probe: `exec(code)` (true positive) and
`dlg.exec()` (false positive) are both flagged, and `# noqa: B102` does **not** suppress
the finding. SecInterp has **no** real builtin `exec`/`eval` usage.

→ Upstream fix recommended (analyzer 1.15.2): restrict B102/B307 to `ast.Name`
builtins only, or allowlist well-known QDialog `.exec()`. Not suppressed in SecInterp
(kept as honest metrics + backlog), pending the upstream fix.

### Phase 4 — Metrics parser fix (side effect of the new rule-id format)

The new rule-id `SECURITY:B102` (contains a colon) broke `scripts/sync_metrics.py`'s
issue-statistics parser, which split on the **first** colon and silently dropped the entry
(`total_issues` 32 instead of 34). Fixed by splitting on the **last** colon
(`rsplit(":", 1)`).

### Phase 5 — Metrics sync
- `uv run python scripts/sync_metrics.py` refreshed `agent_metrics.json`:
  `security_score` 100.0 → 80.0, `total_issues` 32 → 34, `issue_breakdown`
  (+ `SECURITY:B102: 2`), `ground_truth_sources`. `meta.tools.qgis-plugin-analyzer` →
  `1.15.1` (manual; not touched by the sync script).

### Phase 6 — Documentation
- Added this session note; `DEVELOPMENT_LOG.md` + `CHANGELOG.md` (`[Unreleased]`).
- `.agent-state/task.md` / `next_steps.md` updated (B102 false-positive backlog).
- `AI_CONTEXT.md` regenerated fresh via `make context`.

## Verification Results

- `ruff check` / `ruff format --check`: clean (179 files formatted).
- `PYTHONPATH=.. uv run python3 -m unittest discover tests`: **714 OK**.
- `python .agent/tools/forge.py metrics validate`: **PASS**.
- `uv run python scripts/sync_metrics.py --validate`: **PASS**.
- `make context`: fresh (`2,639 / 8,000` tokens, 33 %).

## Impact

- Security scanning is functional again (analyzer + `qgis-plugin-manager`, which delegates
  to it). Real B-codes now fire; SecInterp's only hits are the two Qt `.exec()` false
  positives.
- The deep-analysis report recommendations are now largely shipped upstream: shared
  `rules/scopes.py`, `models/` + `modernization_rules` + `get_all_handlers` +
  `setup_output_dir` removed, and `ProjectAnalyzer.run` / `visit_For` / `visit_Constant`
  complexity reduced; upstream coverage 75 % → 86 %.

## Backlog

- **Upstream (analyzer)**: B102/B307 false positives on attribute `.exec()`/`.eval()`
  (Qt dialogs); also make `# noqa: <RULE>` effective for security findings.
- **SecInterp**: `module_size_gate` FAIL (`core/controller.py` 428 > 400); 15
  `GOD_OBJECT`, 1 `SPAGHETTI_CODE` (from the 1.15.0 adoption).
