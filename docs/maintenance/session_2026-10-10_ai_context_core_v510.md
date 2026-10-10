# Maintenance Session: 2026-10-10 - ai-context-core v5.1.0 Adoption

## Technical Summary

Adopted `ai-context-core` **v5.1.0** ("Context Alignment & Hardening"), a
**backward-compatible** release: no command or artifact contract was removed.
It makes the flagship artifact token-efficient by default and aligns the tool
with the v5.0.0 context-only contract. The adoption is a dependency bump plus a
config alignment; no SecInterp source code changed.

## What changed in v5.1.0

- **Mermaid styling is opt-in**: new `[context].mermaid_style` (default `false`)
  drops the token-heavy `classDef`/`class … module;` block from the dependency
  diagram. `generate_dependency_diagram(deps, include_style=...)` and the builders
  (which now receive the config: `BaseAnalysesBuilder(analyses, config=None)`)
  honor it. Measured upstream: `AI_CONTEXT.md` −23%, `dependencies` −30%.
- **Default token budget**: `config/defaults.toml` now ships `max_tokens = 8000`
  and `[context.budget.sections] dependencies = 2500` (previously commented out).
- **Contract fidelity**: `project_context.json` (builtin pipeline and the external
  qgis-analyzer mapping) no longer exposes the retired `security`,
  `qgis_compliance`, `patterns` and `antipatterns` keys — those domains belong to
  `qgis-plugin-analyzer` (ADR-0008).
- **Unused-import fix**: the detector now honors `# noqa` / `# noqa: F401`
  (new tokenize-based `visitors/noqa.py`; per-import line spans; the worker passes
  the raw `content` to detectors).
- **`ai-ctx init` no longer scaffolds workflows** (template files removed); it
  prints a pointer to the agentic-forge framework.

## Changes Made

- **Dependency**: `ai-context-core>=5.0.1` → `>=5.1.0` in `pyproject.toml`
  (`project.dependencies` and `dependency-groups.dev`); `uv.lock` updated.
- **Config**: `.ai-context/config.toml` aligned with the new defaults —
  `max_tokens` `6000` → `8000` and explicit `mermaid_style = false`.
- **Metrics**: `agent_metrics.json` tool version `5.0.1` → `5.1.0` and
  `context_tokens` `619` → `2639` (was stale after the value-leverage session).
- **Commit**: `chore(deps): adopt ai-context-core 5.1.0` (`ff6f5cfe`).

## Verification Results

- **Tooling**: `uv run ai-ctx --version` → `5.1.0`; `make context` →
  `2,639 / 8,000 tokens (33%)`, **Context check: fresh**.
- **Contract**: root `project_context.json` no longer carries `security`,
  `qgis_compliance`, `patterns`, `antipatterns`; SecInterp does not consume them.
  `scripts/sync_metrics.py` reads the analyzer output
  (`analysis_results/project_context.json`, which keeps `security`), so gates are
  unaffected.
- **Quality**: `ruff check`/`format` clean · `forge metrics validate` PASS ·
  `unittest discover tests` **714 OK**.
- **No runtime impact**: `ai-context-core` remains a CLI-only dev dependency.

## Note

The local index cache can report only `<=5.0.1`; use
`uv lock --upgrade-package ai-context-core --refresh` (as done here) or
`--no-cache` until the cache refreshes. The v5.1.0 token reduction did not apply
to SecInterp (2,639 → 2,639) because its diagram already rendered compact.
