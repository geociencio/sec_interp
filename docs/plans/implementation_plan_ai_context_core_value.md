# Implementation Plan — Maximize ai-context-core Value (Context as a First-Class Session Input)

**Status**: ✅ IMPLEMENTED (2026-10-10) — F0–F6 executed; newly-surfaced gate findings deferred to backlog (after the release train)
**Created**: 2026-10-10
**Owner**: @architect (+ @qa_engineer for verification, @auditor for scope discipline)
**Relates to**: `implementation_plan_ai_context_core_context_only_v5.md`, `session_2026-10-10_ai_context_core_v500.md`, `session_2026-10-10_agentic_forge_v120_migration.md`
**Scope**: agentic tooling / session context; **no plugin runtime code** is expected to change (except Makefile + tooling config + docs)

---

## 0. Why

`ai-context-core` (CLI `ai-ctx`) v5.0.1 is a **context-only compiler**: it *extracts* (provider: `external` = `qgis-plugin-analyzer` output, or `builtin` = its own AST), *transforms* (structure, git evolution, curated manual notes, token budget), *renders* (`AI_CONTEXT.md`, `project_context.json`, `context_manifest.json`) and *verifies* staleness.

Today its value is **close to zero**:

- `start-session` **reads** `AI_CONTEXT.md` but nothing regenerates it on start → the agent reads a stale bundle.
- The framework v1.2.0 removed every `ai-ctx` invocation (framework became tool-agnostic); only the project overlay `release-plugin` still regenerates it.
- The genuinely differentiated commands (`deps`, `git`, `roadmap`, `graph`) are **unused**.
- Its metrics duplicate `qgis-plugin-analyzer` (the declared single source of truth) into `agent_metrics.json`.

This plan turns ai-ctx into a **first-class, always-fresh, curated session input**, and wires its unique capabilities where they pay off.

---

## 1. Evidence (ground truth, measured 2026-10-10)

| # | Finding | Evidence |
| :-- | :--- | :--- |
| F-A | **Scope is wrong: the analyzer is blind to `core/` and `exporters/`.** `.analyzerignore` says *"Focus: gui/ and sec_interp_plugin.py"* and excludes `core/`, `exporters/`, `tests/`, `scripts/`, `docs/`. | `analysis_results/project_context.json` modules = 71 = `gui` 65 + `plugin` 4 + `__init__` 1 + `sec_interp_plugin` 1. Repo has 173 plugin `.py` (core 76, gui 80, exporters 13). |
| F-B | ai-ctx inherits the same wrong scope (it reads `.analyzerignore`). | `ai-ctx stats` = 76 modules; top-complex all `gui/*`; `ai-ctx deps` nodes = 76. |
| F-C | The rendered bundle is **stale and self-contradictory**. | `AI_CONTEXT.md`/`PROJECT_SUMMARY.md` (git_sha `8fd69c25`): 71 modules / 8,699 SLOC / CC 8.8 / MI 99.9 vs live `ai-ctx stats`: 76 modules / 6,962 SLOC / CC 11.6 / MI 43.8. |
| F-D | The structure tree **leaks a dead path** (`antigravity-framerepo/`, gitignored, 1.8 MB) and is truncated (`+38 more`). | `ai-ctx graph/…`; `fs_tree.generate_tree_optimized` ignores `.analyzerignore`/`.gitignore` (fixed `tree -I` list upstream). |
| F-E | Bundle sections are empty: `entry_points`, `primary dependencies`. | `AI_CONTEXT.md` headers present, no rows. |
| F-F | `ai-ctx verify` only hashes **`.py` inputs** → a docs-only session never goes stale. | `context/verify.py: compute_content_hash → scan.python_files`. |
| F-G | Config `.ai-context/config.toml` uses **dead v4 keys** (`[patterns.*]`, `[analysis].exclude_patterns`). v5 reads `[sources]`, `[context]`, `context_docs`, `[context.budget]`. | `config_loader.py:9-11` resolution order; v5 pipeline. |
| F-H | The **curated-notes channel exists but is unused**: `.ai-context/architecture_notes.md` / `project_brain.md`, config `context_docs`, CLI `--include-md`. | `context_fields.read_manual_notes`. |
| F-I | **44 legacy files tracked** in `.ai-context/` (dead per our own v5.0.0 doc), excluded in `.bandit`/`.analyzerignore`/`.qgisignore`/`pyproject.toml`. | `git ls-files .ai-context` = 44. |
| F-J | Docs mislead: `README_DEV.md:43` calls ai-ctx "hygiene metrics"; `session_2026-10-10_ai_context_core_v500.md:68` says framework workflows still call `ai-ctx` (no longer true). | grep. |

> **F-A is the root issue.** Fixing it makes ai-ctx cover the real codebase *and* closes a latent blind spot in the project's own quality gates (which currently never score `core/`/`exporters/`).

---

## 2. Decisions Required (User Review)

> [!IMPORTANT]
> These must be approved before coding.

1. **Scope (F-A/F-B).** Change `.analyzerignore` to cover `core/` + `exporters/` + `gui/` (recommended), keeping `tests/`, `docs/`, `scripts/`, `.agent*`, `antigravity-framerepo/` excluded? ⚠️ This also changes `qgis-plugin-analyzer` output (shared file) → gates may surface new pre-existing findings in `core/`/`exporters/`. Alternative: keep scope as-is and accept a gui-focused context (low value).
2. **Freshness point.** Regenerate at **session start** (recommended, self-healing) and optionally again at close, vs. rely only on close-session.
3. **Metric source.** `--source external` (metrics from `qgis-plugin-analyzer`, single source of truth — recommended) vs `builtin` (ai-ctx's own AST; no analyzer dependency).
4. **Curated guidance.** Create `.ai-context/architecture_notes.md` (short, curated) and/or embed existing docs via `context_docs` (e.g. `docs/CORE_DISTINCTION_GUIDE_EN.md`)? (recommended: curated notes + one or two globs with a token budget).
5. **Legacy cleanup.** Remove the dead `.ai-context/` files (keep only `config.toml` + `architecture_notes.md`) and delete local `antigravity-framerepo/` (1.8 MB)? (recommended: yes, separate commit).
6. **Wiring surface.** Project-owned `make` targets + a root `AGENTS.md` "Context & Architecture Tooling" section (recommended, no framework fork) vs. new overlay workflows.

---

## 3. Target architecture

```
qgis-plugin-analyzer ──► analysis_results/project_context.json   (single-source metrics)
        │
        ▼
ai-ctx context --source external ──► AI_CONTEXT.md (fresh + curated + budgeted)
                                     project_context.json
                                     context_manifest.json
        ▲
        │  make context  (run by the agent at /start-session)
        │
agent reads AI_CONTEXT.md + next_steps.md + AGENT_LESSONS.md
        │
        └─ on demand:  ai-ctx deps (cycles/coupling) · git (hotspots) · roadmap (debt) · graph (Mermaid)
```

Division of labour: **qgis-analyzer** owns metrics/gates; **ai-ctx** compiles/renders/verifies context; **forge** (`forge metrics validate`) owns doc/ground-truth coherence.

---

## 4. Goals and Components

### G1 — Correct the analysis scope (keystone)
- `[MODIFY] .analyzerignore` — regroup into "always exclude noise" vs "analyze": include `core/`, `exporters/`, `gui/`, `sec_interp_plugin.py`; exclude `tests/`, `scripts/`, `docs/`, `.agent/`, `.agent-state/`, `.ai-context/`, `antigravity-framerepo/`, `build/`, `dist/`, generated artifacts.
- **Verify** the resulting module set (expect ≈ 173) and that `./sec_interp_plugin.py` entry is detected.
- Assess gate impact (CC ≤ 10, module size ≤ 400, i18n, docstrings) on the newly included `core/`/`exporters/`; log any new findings as backlog (do **not** silently expand the gate without a decision).

### G2 — Curated context (turn facts into guidance)
- `[NEW] .ai-context/architecture_notes.md` — purpose, Core/UI boundary, Extract-then-Compute, thread-safety rules, key directories, tech stack, known gotchas. Target ~120–150 lines (token-aware).
- `[MODIFY] .ai-context/config.toml` — `context_docs = ["docs/CORE_DISTINCTION_GUIDE_EN.md"]` (optional); `[context.budget]` cap.
- This feeds `manual_notes`, the highest-leverage section (`help-me` explicitly recommends it).

### G3 — v5 configuration hygiene
- `[MODIFY] .ai-context/config.toml` — replace dead v4 keys with v5: `[sources] source="external"`, optional `external_path`; `[context] sections`, `[context.budget]`; `context_docs`.
- Keep the file minimal and self-documenting.

### G4 — Freshness at session start
- `[MODIFY] Makefile` — add:
  - `context:` → `uv run qgis-analyzer analyze . --max-cc 10` (refresh ground truth) `&& uv run ai-ctx context --path . --source external --check`.
  - `context-deps:`, `context-git:`, `context-roadmap:`, `context-graph:`, `context-health:`.
- `[MODIFY] AGENTS.md` — add a short "Context & Architecture Tooling" section instructing the agent to run `make context` before reading `AI_CONTEXT.md` at `/start-session`, and to use the other targets in review/planning.
- `[MODIFY] .agent-state/next_steps.md` / session notes as needed.

### G5 — Wire the differentiated commands
- `deps` → run during architecture/refactor work (`/refactor-code` guidance in AGENTS.md); its circular-dependency output is directly relevant to the known `legend_widget.py` cycle.
- `git` → inform refactor prioritization (hotspots) — already covered by `forge`, but cheap to expose.
- `roadmap` → feed planning (`/close-session`, `/start-phase`) to refresh debt priorities in `next_steps.md`.
- `graph` → `ai-ctx graph -o docs/structure/architecture.mmd` (Mermaid) for docs (optional).
- `symbols` → **skip** (overlaps grep/LSP).

### G6 — Gates, docs and legacy hygiene
- `[MODIFY] .agent/workflows` usage guidance (via AGENTS.md) — `ai-ctx verify --path .` as a close-time freshness gate (exits 1 when `.py` changed since last render).
- `[MODIFY] README_DEV.md` — correct ai-ctx description (context-only, not "hygiene metrics").
- `[MODIFY] session_2026-10-10_ai_context_core_v500.md:68` — fix the now-wrong statement about framework workflows.
- `[DELETE]` legacy `.ai-context/` dead files (keep `config.toml` + `architecture_notes.md`); update `.bandit`, `.analyzerignore`, `.qgisignore`, `.gitattributes`, `pyproject.toml`.
- `[DELETE] antigravity-framerepo/` (local, gitignored) OR file an upstream ai-ctx issue for the tree exclusion.

---

## 5. Phased Execution

| Phase | Deliverable | Exit criteria |
| :-- | :--- | :--- |
| **F0 — Scope audit (read-only)** | Inventory of what `.analyzerignore` excludes today; dry-run module set with the proposed scope | Documented list of newly-covered files; explicit gate-impact list |
| **F1 — Scope fix (G1)** | Updated `.analyzerignore` | `analysis_results/project_context.json` covers `core/`+`exporters/`; gates status recorded |
| **F2 — Config v5 (G3)** | `[MODIFY] .ai-context/config.toml` | `ai-ctx context --source external` renders with `[sources]`/`[context]` honored |
| **F3 — Curated notes + budget (G2)** | `.ai-context/architecture_notes.md` + budget | `AI_CONTEXT.md` shows a non-empty manual-notes section within budget |
| **F4 — Freshness (G4)** | `make context*` + AGENTS.md section | `make context` renders fresh bundle; `ai-ctx verify` exits 0 right after |
| **F5 — Command wiring (G5)** | AGENTS.md mapping + `graph` doc artifact | `make context-deps/-roadmap/-graph` produce output (or artifact) |
| **F6 — Hygiene & gates (G6)** | Doc fixes, legacy cleanup, verify gate | `forge metrics validate` green; tree/vault gates green; `ruff`/pre-commit pass |

---

## 6. Verification Plan

1. **Scope**: `uv run python -c "import json;d=json.load(open('analysis_results/project_context.json'));print(len(d['modules']))"` → expect ≈ 173 (was 71). Spot-check `core/services/*` and `exporters/*` present.
2. **Context freshness**: `uv run ai-ctx context --path . --source external --check` → prints token count, exits 0.
3. **Curated notes**: `rg "Architecture" AI_CONTEXT.md` (or manual-notes heading) non-empty.
4. **Gates**: `uv run qgis-analyzer analyze . --max-cc 10`; `forge metrics validate`; `make docs-check`; `pre-commit run --all-files`.
5. **Regression**: full `make docker-test` (unchanged — no runtime code touched).
6. **Coherence**: after F4, `python .agent/tools/forge.py metrics validate` stays green and `for agent_metrics.json` reflects the new scope deliberately.

---

## 7. Effort Estimation

| Phase | Effort | Risk |
| :-- | :-- | :-- |
| F0 | 1 h | low |
| F1 | 1–2 h | **high** (gate impact) |
| F2 | 0.5 h | low |
| F3 | 2–3 h | medium (content quality) |
| F4 | 1 h | low |
| F5 | 1–2 h | low |
| F6 | 2–3 h | medium (legacy cleanup breadth) |
| **Total** | **~9–13 h** | |

---

## 8. Risks & Mitigations

| Risk | Mitigation |
| :-- | :--- |
| **F-A fix surfaces many new gate findings in `core/`/`exporters/`** | F0 dry-run first; treat new findings as an explicit backlog decision, not a silent gate change; ship scope fix in its own commit. |
| `.analyzerignore` is shared with `qgis-plugin-analyzer` → changes metrics score | Decide in §2.1; re-run analyzer and record the delta in `agent_metrics.json` deliberately. |
| Curated notes drift from reality | Keep them short, high-level, and reviewed at close-session; link to canonical docs. |
| Context bundle grows past budget | `[context.budget]` + `--max-tokens`; keep notes concise. |
| `antigravity-framerepo/` tree leak is upstream | Delete the local dir (recommended) and/or file an upstream issue in `ai-context-core`. |
| Legacy `.ai-context/` deletion breaks an unknown consumer | `rg` confirmed no external references besides ignore-lists; delete in an isolated commit and re-verify gates. |

---

## 9. Out of Scope

- Rewriting the framework's generic workflows (no `ai-ctx` there by design).
- Any change to plugin runtime code (`core/`, `gui/`, `exporters/`).
- Replacing `qgis-plugin-analyzer` as the metrics source.
- Upstream changes to `ai-context-core` (tracked separately; only local workarounds here).
