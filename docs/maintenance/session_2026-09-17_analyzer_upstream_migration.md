# Session 2026-09-17 — Analyzer Upstream Migration

## 🎯 Objective
Reconcile the `docs/plans/upstreaming_qgis_analyzer.md` plan with the shipped qgis-plugin-analyzer 1.14.0 and complete the SecInterp-side migration: retire the now-redundant `check_cc.py` / `verify_i18n_hygiene.py` scripts and drive the CC and i18n gates directly from the analyzer.

## ✅ Actions Taken

### Phase 1 — Reconnaissance
Verified against the installed analyzer source (`.venv/.../site-packages/analyzer/`) that the upstreaming plan (sections 2–7) was **already fully implemented in 1.14.0**:

| Plan item | 1.14.0 location | Status |
| :--- | :--- | :--- |
| AST i18n rule (`MISSING_I18N`) | `visitors/i18n_visitor.py` (port of `i18n_ast_rule.py`) | DONE |
| Per-project config | `[tool.qgis-analyzer.profiles.<p>.rules.MISSING_I18N]` | DONE |
| `--max-cc` gate | `analyzer/cli/commands/analyze.py` + `commands.py::_enforce_max_cc` | DONE |
| `--json` / `--include-content` / `schema_version` | `analyzer/cli/commands/analyze.py`, output JSON | DONE |

### Phase 2 — Config
- `pyproject.toml`: added `[tool.qgis-analyzer.profiles.default.rules.MISSING_I18N]` with `extra_ignore_calls = ["PerformanceTimer"]`, suppressing the 2 remaining false positives (`Total Preview Generation`, `Total Preview Export Time`).

### Phase 3 — Migration (code)
- Retired `scripts/check_cc.py`, `scripts/verify_i18n_hygiene.py` and the already-merged `scripts/upstream/i18n_ast_rule.py`.
- Refactored `scripts/sync_metrics.py`:
  - `run_qgis_analyzer()` now invokes `analyze . --max-cc 10` and exposes `cc_gate` from the exit code.
  - Removed `run_check_cc()` / `run_verify_i18n()`.
  - `sync_main()` derives `cc` (exit code) and `i18n` (`MISSING_I18N == 0`); `update_metrics_json()` reads `cc`/`i18n` keys.
  - Report/`--json`/print output renamed `i18n_ast_gate` → `i18n_gate`.
- Fixed the **pre-push hook** (`.git/hooks/pre-push`): the legacy `analyze . --output json` (where `--output` was a filename) was broken under 1.14.0 (now a directory); replaced with `analyze . --max-cc 10`.

### Phase 4 — Documentation & references
- Rewrote `docs/plans/upstreaming_qgis_analyzer.md` (upstreaming COMPLETE + migration checklist).
- Updated `scripts/README.md`, `scripts/lesson_extractor.py`, 6 `.agent/workflows/*`, `.agent/skills/i18n-standards/SKILL.md`, `.agent/README.md`, `.agent/QUICK_REFERENCE.md`, and `agent_metrics.json` (`ground_truth_sources`, `i18n_note`, `issue_breakdown`).

## 📊 Operational Metrics
- `qgis-analyzer analyze . --max-cc 10`: exit 0; `MISSING_I18N` **2 → 0**; total issues **5 → 3** (2 `NON_PYTHONIC_LOOP`, 1 `SPATIAL_INDEX`).
- `sync_metrics.py --validate`: PASS (37 `.agent/` files coherent).
- `ruff check .`: PASS (scripts/ excluded by design).
- Tests: 640/640 (Docker) + 13 agentic unit tests OK.

## 📦 Commit
- `61de59f2` `refactor(scripts): migrate CC and i18n gates to qgis-plugin-analyzer` — pushed to `origin/main` (12 commits total, `7962a7c6..61de59f2`).

## ⚠️ Pending
- Pre-existing uncommitted working-tree changes left as-is (not part of this session): `examples/sample_data/MURALLA.qgs`, `MURALLA.qgs~`, `resources/resources.py`.
- Real technical debt unchanged: 2 `NON_PYTHONIC_LOOP` (2.2), 1 `SPATIAL_INDEX` (2.3), `module_size_gate` FAIL (7 modules > 400 lines, 2.4).
- The `.git/hooks/pre-push` fix is local-only (hooks are not tracked by git).

## 📝 Lessons
- Before writing an upstreaming plan against a dependency, check the *installed* source: the analyzer 1.14.0 had already implemented the entire plan, so the correct action was migration, not implementation.
- A CLI flag contract change (`--output` from filename to directory) can silently break an untracked hook; verify local hooks against the current CLI when bumping a tool version.
