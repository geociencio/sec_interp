# Maintenance Session: 2026-10-10 - ai-context-core Value Leverage (Context as a First-Class Session Input)

## Technical Summary

`ai-context-core` (CLI `ai-ctx`, v5.0.1) was a **context-only compiler** that
SecInterp barely used: `start-session` read a stale `AI_CONTEXT.md`, nothing
regenerated it on start, and its unique commands were unused. An audit revealed
the **root cause**: `.analyzerignore` — shared by `ai-ctx` **and**
`qgis-plugin-analyzer` — was scoped to `gui/` only (*"Focus: gui/ and
sec_interp_plugin.py"*), excluding `core/` and `exporters/`. As a result the
context bundle **and the project's own quality gates were blind to the business
logic**.

This session turns ai-ctx into an always-fresh, curated session input and fixes
the analysis scope so both the context and the gates cover the whole plugin.
Plan: `docs/plans/implementation_plan_ai_context_core_value.md`.

## Changes Made

- **Scope (keystone)**: `.analyzerignore` rewritten — analyze `core/`, `gui/`,
  `exporters/`, `sec_interp_plugin.py`; exclude only dev tooling (`tests/`,
  `scripts/`, `docs/`), agent state (`.agent/`, `.agent-state/`, `.ai-context/`),
  generated artifacts and non-code files. **Coverage 71 → 135 modules.**
- **Config v5**: `.ai-context/config.toml` rewritten to the v5 schema
  (`[sources] source="external"`, `[context] sections`, `[context.budget]`,
  `context_docs`); the dead v4 keys (`[patterns.*]`, `[analysis]`) were removed.
- **Curated context**: new `.ai-context/architecture_notes.md` (always embedded as
  *manual architecture notes*) + `docs/CORE_DISTINCTION_GUIDE_EN.md` via
  `context_docs`. Rendered `AI_CONTEXT.md` = **2,639 / 6,000 tokens**, 135 modules,
  no `antigravity-framerepo` leak.
- **Freshness**: `Makefile` gains `context` (qgis-analyzer + `ai-ctx context
  --source external --check`), plus `context-deps`, `context-git`,
  `context-roadmap`, `context-graph`, `context-health`. Root `AGENTS.md` gains a
  **"Context & Architecture Tooling"** section (regenerate at `/start-session`).
- **Wiring**: `make context-graph` renders `docs/structure/architecture.mmd`
  (Mermaid dependency graph).
- **Hygiene**: `README_DEV.md` and `session_2026-10-10_ai_context_core_v500.md`
  corrected (ai-ctx is context-only; the framework no longer calls it); removed
  **44 dead legacy `.ai-context/` files** (kept `config.toml` + notes); deleted the
  local gitignored `antigravity-framerepo/` (1.8 MB).
- **Metrics**: `agent_metrics.json` re-synced (quality 56.9 → **57.9**, issues
  4 → 16).

## Verification Results

- `uv run ruff check .` → clean · `uv run ruff format --check .` → 179 formatted.
- `python .agent/tools/forge.py metrics validate` → all agentic files consistent.
- `uv run python scripts/check_docs.py` → passed (36 active docs).
- `uv run ai-ctx context --path . --source external --check` → fresh.
- CC gate **PASS**; i18n **PASS**.

## Newly Surfaced Findings (backlog — deferred)

The corrected scope revealed pre-existing issues in `core/`/`exporters/` that had
never been gated. Per decision, these are **not fixed now** (to be triaged after
the release train v3.10.0 / v3.11.0):

- 🔴 `module_size_gate = FAIL`: `core/controller.py` = **428 lines** (> 400).
- 10 × `MISSING_DOCSTRING` (mostly `__init__.py` in `core/`/`exporters/`).
- 4 × `NON_PYTHONIC_LOOP`, 2 × `POTENTIAL_MISSING_SLOT`, +6 signal-leak heuristics.

## Notes / Follow-ups

- Release train (`release/v3.10.0`, `release/v3.11.0`) is unaffected (branches
  predate this change); when merging it into `main` later, watch for conflicts in
  `.ai-context/` and doc references.
- `ai-ctx verify` hashes only `.py` inputs, so a docs-only session never reads as
  stale; run `make context` at session start for a guaranteed-fresh bundle.
- The `antigravity-framerepo/` tree leak in `AI_CONTEXT.md` was an upstream
  `ai-ctx` limitation (`generate_tree_optimized` ignores `.analyzerignore`); it is
  now resolved locally by removing the dead directory.
