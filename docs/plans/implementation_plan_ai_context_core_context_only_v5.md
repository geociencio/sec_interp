# Implementation Plan: ai-context-core as a Context-Only Tool (v5.0.0)

**Status**: ✅ IMPLEMENTED — shipped upstream as `ai-context-core` v5.0.0 on PyPI (2026-10-10); adopted (scoped) by SecInterp the same day
**Created**: 2026-10-08
**Owner**: @architect (+ @auditor for scope discipline, @qa_engineer for verification)
**Target repo**: `~/qgispluginsdev/ai-context-core` (PyPI `ai-context-core`)
**Consumer impacted**: `sec_interp` (and, as dev-dep, `qgis-plugin-analyzer`)
**Relates to**: `implementation_plan_unify_agentic_systems.md`, session `2026-10-08_ai_context_core_v411.md`

---

## 0. Context

`ai-context-core` (CLI `ai-ctx`, v4.1.1) advertises itself as *"the central nervous
system for your AI-assisted coding workflow"* with **Context Management** as its core
capability. In practice it has grown into a **full static-analysis engine** that
duplicates `qgis-plugin-analyzer` almost line by line.

This plan restores coherence: `ai-context-core` becomes a **context compiler** that
*consumes* analysis (rather than owning it) and produces token-efficient, versioned,
verifiable context artifacts for AI agents.

### Decisions already taken (2026-10-08)

| Decision | Choice |
| :--- | :--- |
| Target identity | **Context-only estricto** (breaking, v5.0.0) |
| Quality Score / `audit` gate | **Renamed to `context health`**, no quality gate |
| First-iteration additions | **Provider del analyzer · Token budget · verify/staleness · Symbol index** (MCP deferred) |

### Non-goals (owned by siblings)

- QGIS compliance, metadata, Qt6 rules, Processing detection → `qgis-plugin-analyzer`
- i18n AST audit (`MISSING_I18N`) → `qgis-plugin-analyzer`
- Security scanning (Bandit-style, secrets, injection) → `qgis-plugin-analyzer` + `bandit`/`detect-secrets`
- Code-quality scoring / CC gate / module stability → `qgis-plugin-analyzer`
- Lint/format → `ruff`
- Packaging / deploy → `qgis-plugin-manager`
- Code scaffolding → `agentic-forge` / `qgis-plugin-analyzer`

---

## 1. Evidence — what ai-context-core is today

| Signal | Finding |
| :--- | :--- |
| Name / tagline | "AI context" + "Context Management" |
| Actual weight | `analyzer/visitors/` ≈ **55 modules**: security (`injection*`, `secrets`, `insecure_calls`), QGIS (`qgis_*`), i18n (`i18n*`), design patterns (`singleton/factory/observer/strategy/decorator`), anti-patterns (`god_object`, `spaghetti_code`, `magic_number`), metrics (`halstead`, `complexity_visitor`), plus 26 builders including `aggregator_qgis`, `qgis*`, `security_severity`, `issues`, `patterns`. |
| Context layer | `context/` = **~194 LOC** (`manager.py` 59 + `components/` 135), and it is **legacy/unused**: it builds GPT/DeepSeek/Claude *prompts*, disconnected from `AI_CONTEXT.md` generation. |
| Runtime deps | `click`, `rich` only → fully self-contained ⇒ re-implements the analyzer instead of consuming it. |
| Overlap | i18n, Qt6, metadata, security, CC gate, graph/coupling, `serve`, `fix`, `init`, `project_context.json` all duplicated from `qgis-plugin-analyzer`. |
| Root cause | ADR-0002 ("13 improvements") doubled down on *adding analysis* rather than sharpening the context promise. |

---

## 2. Target contract

> **ai-context-core compiles context.** `extract` (providers) → `transform`
> (context / symbol index / budget) → `render` (artifacts) → `verify`.

It is a **consumer** of analysis. Its artifacts are:
**token-efficient**, **versioned**, **verifiable**, and carry **provenance**.

```
src/ai_context_core/
├── providers/          # NEW: external (qgis-analyzer) + builtin (minimal AST)
├── model/              # NEW: AnalysisResult, SymbolIndex (versioned schema)
├── context/            # transform, budget, verify, store
├── render/             # AI_CONTEXT.md, project_context.json, *.mmd, symbols.json
└── cli/commands/       # slimmed
```

---

## 3. REMOVE (v5.0.0, one deprecation cycle)

### 3.1 CLI commands (`src/ai_context_core/cli/commands/`)

| Delete | Lives in | Rationale |
| :--- | :--- | :--- |
| `audit` | `analysis.py` | Quality gate → analyzer; replaced by `health` |
| `inspect` | `analysis.py` | Single-file deep analysis → analyzer |
| `patterns` | `reports.py` | Design-pattern detection, not context |
| `security` | `reports.py` | → analyzer + bandit |
| `qgis` | `specialized.py` | QGIS compliance/i18n/Qt6 → analyzer |
| `fix` | `maintenance.py` | Auto-remediation → analyzer |
| `scaffold` | `maintenance.py` | Code generation → agentic-forge |
| `doctor` | `maintenance.py` | Generic env diagnostics (or reduce to context-health) |
| `interactive` | `interactive.py` | Not context |
| `serve` | `base.py` | Keep **only** if it serves the *context* report; drop the analysis dashboard |

**Keep**: `init`, `profiles`, `stats`, `clean`, `analyze`, `context`, `full-scan`,
`help-me`, `deps`, `git`, `graph`, `compare`, `roadmap`, **+ new** `verify`, `symbols`, `health`.

### 3.2 Visitors (`analyzer/visitors/`)

Delete: `qgis_api`, `qgis_base`, `qgis_visitor`, `framework_rules`, `frameworks`,
`i18n`, `i18n_components`, `injection`, `injection_os`, `injection_sql`,
`insecure_calls`, `secrets`, `security_base`, `singleton*`, `factory`,
`observer*`, `strategy*`, `decorator*`, `halstead`, `checker_base`
(if only used by removed passes).

Keep: `imports`, `imports_visitor`, `import_export`, `sloc*`, `complexity_visitor`,
`classes`, `functions`, `ast_utils`, `ast_metrics`, `visitors_base`, `dead_code`.
Anti-patterns (`god_object`, `spaghetti_code`, `magic_number`): **demote to context
warnings** (no score) or delete — decide in F2.

### 3.3 Builders (`analyzer/builders/`)

Delete: `aggregator_qgis`, `qgis.py`, `qgis_processing`, `qgis_scope`,
`qgis_summarizer`, `security_severity`, `issues`, `patterns`, `git_patterns`.
Keep: `ai_context_generator`, `context_metrics`, `context_base`, `structure`,
`dependencies`, `cycle_detector`, `formatter`, `reporting`, `metrics_summarizer`,
`calculator`, `git_tech`, `metric_keys`, `parser`, `classifier`, `algorithms`.

### 3.4 Config

- Delete `config/profiles/qgis.toml`; keep `python-generic` (+ new `providers`/`budget` keys).
- `deprecations.py`: `REMOVAL_VERSION = "5.0.0"`; add facades for removed imports for one cycle.

---

## 4. ADD (first iteration)

### A. Provider layer (keystone)
- `providers/base.py`: `AnalysisProvider` protocol → normalized `model/AnalysisResult`.
- `providers/external/qgis_analyzer.py`: run `qgis-analyzer analyze . --json` or read
  `analysis_results/project_context.json`.
- `providers/builtin/`: minimal `python-generic` AST extraction (structure, imports,
  complexity) as a standalone fallback.
- Config `[providers] source = "auto|external|builtin"`; `--source` flag on `analyze`/`context`.
- Default `auto`: external if analyzer output/dep present, else builtin.

### B. Token budget
- `context/budget.py`: estimator (heuristic `chars/4`; `tiktoken` as optional extra).
- `[context.budget]` per-section limits; `--max-tokens`.
- Render a summary: `context: 3,412 / 8,000 tokens (43%)`; per-section counts in the manifest.

### C. verify / staleness
- `context/verify.py` + command `verify`.
- Every artifact carries `_meta` = `{schema, tool_version, git_sha, content_hash}` — reuse
  the 4.1.1 cache-versioning pattern.
- `ai-ctx verify` exits `1` on drift; `ai-ctx context --check` for CI.

### D. Symbol index
- `context/symbol_index.py` + command `symbols`.
- AST extraction of definitions (module/class/function/method) + references with `file:line`.
- Emits versioned `symbols.json`; query via `--grep`.

### E. context health (ex-Quality Score)
- Command `health`: freshness + symbol coverage + token size + provenance.
- **No quality gate.** Exit code non-zero only for staleness failures.

---

## 5. Phased execution

### F0 — Contract & freeze
- Write `docs/adr/0008-context-only-contract.md` (accepted decision).
- Bump `REMOVAL_VERSION` to `5.0.0`; freeze new analysis features.
- Rename score surface to "context health" in docs.
- **Exit**: ADR merged; no code removal yet.

### F1 — Provider layer
- Implement `providers/` + `model/`; wire `--source`; make `context` the primary path.
- **Exit**: `ai-ctx context` on `sec_interp` produces equivalent sections via external
  provider vs. builtin (regression snapshot diff); `pytest` green.

### F2 — Removal (v5.0.0)
- Delete §3 files/commands; add deprecation facades; update `README.md`, `CONFIGURATION.md`,
  `.analyzerignore` semantics; prune tests.
- **Exit**: `ai-ctx --help` shows only the context surface; `pytest` green (expected count
  reduced from 333); `ruff check` clean.

### F3 — Token budget + manifest
- Implement §4B; add manifest (`context_manifest.json`) with per-section token counts.
- **Exit**: `context --max-tokens` truncates deterministically; manifest matches rendered sizes.

### F4 — verify + symbol index + health
- Implement §4C/§4D/§4E.
- **Exit**: `verify` returns 0 after fresh `context`, 1 after editing a tracked file;
  `symbols --grep` returns `file:line`.

### F5 — Ecosystem alignment
- Cross-link READMEs (`qgis-plugin-analyzer` ↔ `ai-context-core`).
- Update `agentic-forge` skill `project-context` references.
- Update SecInterp workflows (`/start-session`, `/close-session`) and docs referencing
  `ai-ctx qgis`/`audit` → `qgis-analyzer` + `ai-ctx context`.

---

## 6. Migration & deprecation

- **Major bump** `4.x → 5.0.0`; one deprecation cycle for removed imports (warn, don't break).
- Removed CLI commands: keep hidden no-op stubs that print a redirect pointer to the
  owner (`qgis-analyzer …` / `agentic-forge …`) for one release.
- Changelog: `### Removed` + `### Changed` with the identity contract.

## 7. Ecosystem impact

| Consumer | Impact |
| :--- | :--- |
| `sec_interp` | No runtime breakage. Already uses `qgis-analyzer` for i18n/CC gates. Workflows referencing `ai-ctx qgis`/`audit` must switch to `qgis-analyzer` + `ai-ctx context`; `pyproject` stays (uses `context`/`roadmap`/`git`). Resolves the i18n inconsistency (F6) by single-sourcing. |
| `qgis-plugin-analyzer` | Becomes sole owner of hygiene; uses `ai-context-core` as dev-dep → must follow the deprecation cycle. Publish a stable `project_context.json` schema contract. |
| `agentic-forge` | Update `project-context` skill to describe the new division. |

## 8. Risks & mitigations

| Risk | Mitigation |
| :--- | :--- |
| `roadmap` needs complexity + churn | **Do not** prune `complexity_visitor`, `sloc`, `git_tech`. |
| `tiktoken` adds a dependency | Optional extra with heuristic fallback. |
| Breaking API for the analyzer (dev-dep) | Mandatory one-cycle deprecation + redirect stubs. |
| Loss of standalone (non-QGIS) use | Keep minimal `builtin` provider for `python-generic`. |
| Scope creep during F2 | @auditor gate: any re-added analysis feature is rejected. |

## 9. Verification

- **Per phase**: `uv run pytest -q` + `uv run ruff check .` in `ai-context-core`.
- **Regression**: snapshot `AI_CONTEXT.md` / `project_context.json` on `sec_interp`
  with `--source external` vs `builtin`; sections must match modulo provider provenance.
- **Staleness**: `ai-ctx verify` → 0 fresh, 1 stale.
- **Budget**: `--max-tokens N` never exceeds `N`; manifest sums equal rendered counts.
- **Cross-repo**: after F5, `forge validate` green in the three sibling repos.

## 10. Open questions

1. Anti-patterns: demote to context warnings or delete entirely in F2?
2. `compare`: keep as *context delta* tool, or delegate diffing to CI snapshots?
3. `serve`: keep a context-only HTML view, or drop HTML entirely (analyzer owns dashboards)?
4. Should `dependency graph` (`deps`) stay in ai-context-core, or delegate to
   `qgis-analyzer graph` and keep only the Mermaid render for context?

---

## Appendix A — CLI surface before/after

| Command | 4.1.1 | 5.0.0 |
| :--- | :---: | :---: |
| `analyze` / `full-scan` | ✅ | ✅ (provider-backed) |
| `context` | ✅ | ✅ (primary) |
| `deps` / `graph` | ✅ | ✅ (see Q4) |
| `git` / `roadmap` | ✅ | ✅ |
| `stats` / `compare` | ✅ | ✅ |
| `help-me` | ✅ | ✅ |
| `init` / `profiles` / `clean` | ✅ | ✅ |
| `verify` / `symbols` / `health` | ❌ | ✅ **new** |
| `audit` / `inspect` | ✅ | ❌ (→ analyzer / `health`) |
| `qgis` / `security` / `patterns` | ✅ | ❌ (→ analyzer) |
| `fix` / `scaffold` / `doctor` | ✅ | ❌ (→ analyzer / agentic-forge) |
| `interactive` / `serve` | ✅ | ❌ (see Q3) |
