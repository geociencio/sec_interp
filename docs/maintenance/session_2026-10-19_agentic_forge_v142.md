# Session 2026-10-19 — Agentic Forge v1.4.1 → v1.4.2 Upgrade

## Context

Follow-up to the reliability-hardening session: update the `.agent` framework from
`f15d44a` (v1.2.0-4) to the latest release and keep the project adapters, tests and docs
compatible. No plugin-runtime changes.

## What was done

### v1.4.1 (`811997a0`)

- Fast-forwarded `.agent` `f15d44a` → `537f9fd`. The project's memory, overlay-validation
  and unittest commits were ancestors of the release, so no work was lost.
- `scripts/sync_metrics.py` now imports checks from `forge_metrics_checks` and reporting
  from `forge_metrics_report` (the framework split `forge_metrics.py`).
- `memory prune` is dry-run by default: tests call `prune_lessons(apply=True)` /
  `prune_next_steps_snapshots(apply=True)`; `release-plugin` uses `memory prune --apply`.
- Validator tests migrated to `workflow_graph` (`workflow_files`, `scan_workflows`) and
  `skill_conflicts.find_conflicts`; `validate_memory_limits` → `validate_memory_budget`.
- Removed two obsolete `_check_i18n_consistency` tests (the check no longer exists):
  **778 tests** (827 static).
- Replaced the deprecated `qa-docker` alias with `testing-standards` in active workflows
  and `AGENTS.md`. The alias remains for backward compatibility.

### v1.4.2 (`eff33d1a`)

- Fast-forwarded `.agent` `537f9fd` → `b264e35` (quality-gate hotfix).
- Framework metric scans now skip cache directories (`.mypy_cache`, `.ruff_cache`,
  `.pytest_cache`, `__pycache__`); TOML config errors are caught via `ValueError`.
- No project adapter changes were required.

### Tooling

- Added the v1.4.2 `[project]` commands to `forge.toml`: `test_command_full`,
  `lint_command`, `format_command` and `type_command`, so
  `forge.py project lint|format|test-full|type` works out of the box.

## Quality

- **778 tests OK** (827 static), 122 test files.
- Framework pytest suite: **36 passed, 1 deselected**. The deselected
  `test_workflow_graph_has_no_broken_refs` assumes every workflow uses one of the three
  canonical agents; SecInterp legitimately adds `qgis_driver` for the QGIS-MCP smoke test
  (registered in `opencode.json`). The validator accepts it; the framework test does not.
- `forge validate`: 17 skills, 18 workflows, 3 templates.
- `sync_metrics --validate` and `forge metrics validate`: PASS.
- `memory check`: 328/350 lines.
- `ruff`, `format`, `mypy`, `check_docs`: PASS.
- `.agent` clean at `b264e35` (v1.4.2).

## Pending

1. ~~Portal QGIS~~ — **v3.11.0 approved in the QGIS plugin repository** (2026-10-23).
2. `module_size_gate`: 5 modules > 400 lines.
3. `uv` 0.12.10 → 0.13.0 (blocked by pacman).
4. Interop plan §9: start with **B1**.
5. Optional: native review of machine-assisted translations; refresh `help/html`.
6. Known separate bug: `section_feature_id` is cached but not passed to profile sampling.
