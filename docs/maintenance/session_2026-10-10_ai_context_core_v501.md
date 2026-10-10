# Maintenance Session: 2026-10-10 - ai-context-core v5.0.1 Adoption

## Technical Summary

Adopted `ai-context-core` **v5.0.1** ("Post-Release Cleanup"), a **patch release**
that follows the `v5.0.0` context-only contract. It is an internal consolidation
and hygiene release: **no command or artifact contract changed**, so the adoption
is a dependency bump plus artifact regeneration. `ai-ctx` remains scoped as a
context-only compiler; all quality gates stay single-sourced in
`qgis-plugin-analyzer`.

## What changed in v5.0.1

- **Single render path**: `ai-ctx analyze` now runs `compile_context ->
  render_context` for every source (builtin and external); the legacy engine
  render (`ProjectAnalyzer.analyze()` / `_generate_outputs()`) and dead HTML
  branches were removed, so all artifacts share one provenance/schema path.
- `ai-ctx analyze --format` is `markdown|json`.
- **Removed residue**: `ContextAggregator` compatibility alias and the
  `deprecations` module, `graph_engine`, an unused `maintenance_group`, duplicate
  calculator Halstead helpers, the `extra_data` parameter, unused `get_category`
  methods and the `SummaryGenerator` alias.
- **Repository hygiene** (upstream): shared `cli/console.py`, orphan fixtures and
  scratch files removed.

## Changes Made

- **Dependency**: `ai-context-core>=5.0.0` → `>=5.0.1` in `pyproject.toml`
  (`project.dependencies` and `dependency-groups.dev`); `uv.lock` updated via
  `uv lock --no-cache` + `uv sync --no-cache`.
- **Artifacts regenerated** with `uv run ai-ctx analyze --path . --no-cache`:
  `AI_CONTEXT.md`, `PROJECT_SUMMARY.md`, `project_context.json`,
  `context_manifest.json` (all git-ignored).
- **Metrics**: `agent_metrics.json` tool version `5.0.0` → `5.0.1` (tool block +
  `ai_context` ground-truth source/notes).

## Verification Results

- **Tooling**: `uv run ai-ctx --version` → `5.0.1`; `uv run ai-ctx verify --path .`
  → **`Context is fresh.` (exit 0)**.
- **Analysis**: `analyze --path .` reported `source: external` (consuming
  qgis-analyzer), SLOC **8,699**, Quality Score (heuristic, external) **56.9/100**.
- **Context bundle**: `context_manifest.json` → **619 tokens total** (structure 311,
  metrics 90, dependencies 40, git 160), unchanged from v5.0.0; `_meta.schema: 1`,
  `source: external`, deterministic `content_hash`.
- **No runtime impact**: no `ai_context_core` imports in `core/`, `gui/`, or
  `exporters/` (CLI-only consumption).

## Impact

Patch-level maintenance with no behavioral change to SecInterp. It keeps the
toolchain current with the post-`v5.0.0` consolidation (single render path) while
preserving the token-efficient, verifiable context bundle and the single-sourced
quality-gate model.

## Note

`uv lock` may replay a stale cached simple index that reports only `<=5.0.0`;
use `uv lock --no-cache` (and `uv sync --no-cache`) until the local index cache
refreshes.
