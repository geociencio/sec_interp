# Maintenance Session: 2026-10-10 - ai-context-core v5.0.0 Adoption (Scoped)

## Technical Summary

Adopted `ai-context-core` **v5.0.0** (`ai-ctx`) once published on PyPI. This is a
**breaking major** that repositions the tool as a **context-only compiler**
(`sources → transform → render → verify`): it *consumes* analysis instead of owning
it. The adoption is deliberately **scoped**: `ai-ctx` is used only as a context
compiler (`context` / `git` / `roadmap` / `verify` / `symbols`); all quality gates
(CC, i18n, module size, security, QGIS compliance) remain **single-sourced** in
`qgis-plugin-analyzer`.

## What changed in v5.0.0

- **Removed commands**: `audit`, `qgis`, `security`, `patterns`, `inspect`, `fix`,
  `scaffold`, `doctor`, `interactive`, `serve`, **`full-scan`**.
- **New commands**: `health` (context health), `verify` (staleness, exit 1 on drift),
  `symbols` (index, `--grep` for `file:line`).
- **Kept**: `analyze`, `context` (primary), `deps`, `git`, `graph`, `roadmap`,
  `stats`, `compare`, `clean`, `init`, `profiles`, `help-me`.
- **Analysis source**: `--source auto|external|builtin`; default `auto` consumes
  `qgis-plugin-analyzer`'s `analysis_results/project_context.json` when present.
- **New artifact**: `context_manifest.json` (per-section token counts + `_meta`
  provenance: schema, tool_version, git_sha, content_hash).

## Changes Made

- **Dependency**: `ai-context-core>=4.1.1` → `>=5.0.0` in `pyproject.toml`
  (`project.dependencies` and `dependency-groups.dev`); `uv.lock` updated via
  `uv lock` + `uv sync`.
- **`.gitignore`**: added `context_manifest.json` and `symbols.json` (new v5.0.0
  artifacts).
- **Artifacts regenerated** with `uv run ai-ctx analyze --path . --no-cache`:
  `AI_CONTEXT.md`, `PROJECT_SUMMARY.md`, `project_context.json`,
  `context_manifest.json` (all git-ignored).
- **Metrics**: `agent_metrics.json` tool version `4.1.1` → `5.0.0`; replaced the
  obsolete `ground_truth_sources.ai_context` block (its `qgis_compliance` /
  `i18n_coverage_pct` came from the removed `ai-ctx qgis`) with a context-only block.

## Verification Results

- **Tooling**: `uv run ai-ctx --version` → `5.0.0`; `uv run ai-ctx verify --path .`
  → **`Context is fresh.` (exit 0)**.
- **Analysis**: `analyze --path .` reported `source: external` (consuming
  qgis-analyzer), SLOC **8,699**, Quality Score (heuristic, now external)
  **56.9/100**.
- **Context bundle**: `context_manifest.json` → **619 tokens total** (structure 311,
  metrics 90, dependencies 40, git 160); `_meta.schema: 1`, `git_sha: 2bdac133…`,
  deterministic `content_hash`.
- **`AI_CONTEXT.md`** is now context-only (structure, complexity, coupling, git
  churn) — the former design-pattern / anti-pattern / QGIS-compliance / i18n
  sections are gone by design.
- **No runtime impact**: no `ai_context_core` imports in `core/`, `gui/`, or
  `exporters/` (CLI-only consumption).

## Impact

`ai-ctx` no longer competes with `qgis-plugin-analyzer` on quality metrics, removing
the documented "Multi-Tool Scope Mismatch". SecInterp gains a token-efficient,
verifiable context bundle plus unique git churn / roadmap capabilities. Historical
references to `ai-ctx full-scan` remain valid as history but are superseded by
`ai-ctx analyze` / `ai-ctx context` (both still render `AI_CONTEXT.md`).

## Out of Scope (deferred)

- The legacy tracked `.ai-context/` subsystem (dead: nothing imports
  `ai_workflow.py` / `context_manager.py`).
- The `.agent/` framework workflows still invoke `ai-ctx analyze --path .`, which
  remains valid in v5.0.0.
- `AI_CONTEXT.md` still lists the gitignored `antigravity-framerepo/` in its
  structure section (exclusion handling upstream in ai-context-core).
