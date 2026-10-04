# Implementation Plan: Agentic Forge — Framework Extraction

**Status**: 🚧 IN PROGRESS — **F1 COMPLETED (2026-10-04)**; F2–F5 pending
**Created**: 2026-10-04
**Owner**: @architect
**Framework repo name**: `agentic-forge` (Codeberg)
**References**: `AGENTS.md`, `scripts/forge_paths.py`, `forge.toml`, `docs/maintainer/FRAMEWORK_SYNC_GUIDE.md`

---

## 0. Executive Summary

Separate the **re-usable agentic framework** (skills, workflows, tooling) from the
**project-owned state** (memory, task board, metrics), so the framework can be reused
across projects and versioned independently, hosted on **Codeberg**.

The framework is **vendor-neutral** by design (works with any agent runtime: opencode,
Claude Code, Cursor…). It is split into a generic core plus domain scaffolds
(`scaffold/qgis`, `scaffold/web`, …), which is why the neutral name `agentic-forge`
was chosen over the previous Antigravity-branded naming.

Target model (**Option D**): the generic framework becomes a **git submodule** at
`.agent/`; project state lives in `.agent-state/` and is never overwritten by a
framework update.

---

## 1. Target Architecture

```
SecInterp/
├── .agent/                     ← git submodule → Codeberg (agentic-forge)
│   ├── skills/  workflows/  resources/  architecture/
│   ├── tools/                  ← generic CLI (`forge`), extracted in F5
│   ├── scaffold/<domain>/      ← qgis, web, ...
│   └── README.md  QUICK_REFERENCE.md  AGENTS.template.md
├── .agent-state/               ← versioned in SecInterp (project-owned state)
│   ├── memory/  (agent_metrics.json, AGENT_LESSONS.md, memory_policy.md)
│   ├── skills/  (project-context, geological-logic)   ← project overlay
│   ├── task.md  next_steps.md  history/
├── forge.toml                  ← path/config contract (framework + state)
└── AGENTS.md                   ← canonical root config
```

**Why state must leave `.agent/`**: a git submodule cannot mix local files inside its
own directory, and framework updates must never clobber project history/metrics.

---

## 2. Classification: framework vs project

### Framework (→ `agentic-forge`)

| Item | Notes |
| :--- | :--- |
| `skills/` (generic: coding-standards, commit-standards, qa-docker, qgis-core, qgis-migration-4x, ui-framework, release-management, i18n-standards, documentation-standards, changelog-generator, agentic-memory) | Re-usable; some are QGIS-flavored, packaged under `scaffold/qgis` |
| `workflows/` (16) | Generic operational procedures |
| `resources/`, `architecture/`, `README`, `QUICK_REFERENCE` | Framework docs |
| `validate_agent_system.py`, `mcp_server.py`, `lesson_extractor.py`, `memory_prune.py`, `session_index.py`, `security_scan.py` | Generic agentic tooling |
| `sync_metrics.py` | **Hybrid** → split into generic core + project adapter |

### Project (stays in SecInterp)

| Item | Notes |
| :--- | :--- |
| `skills/project-context`, `skills/geological-logic` | Project overlay → `.agent-state/skills/` |
| `memory/`, `history/`, `task.md`, `next_steps.md` | Already moved to `.agent-state/` (F1) |
| `generate_vault_v2.py`, `check_notes.py`, `generate_structure_links.py` | Code-walkthrough vault |
| `check_docs.py`, `sync_docs_*`, `sync_vault_mirrors.sh`, `docs_i18n_status.py`, `build_docs.sh` | SecInterp docs/Sphinx |
| `i18n/*`, `update-strings.sh` | Plugin translations |
| `next_scheduled_release.py`, `package-for-qgis.sh`, `run_in_qgis.py`, `setup_venv.sh` | QGIS release/env |

---

## 3. Tooling Integration

### Path contract
`forge.toml` (repo root) declares `[forge].framework` and `[forge].state`.
`scripts/forge_paths.py` resolves them (walks up to find `forge.toml`), so the tooling
keeps working after it is moved under `.agent/tools/`.

### `sync_metrics.py` split (F5)
- **Generic core**: `agent_metrics.json` schema, session rotation, `--validate`
  cross-file/internal consistency, doc metric scanning.
- **Project adapter**: `qgis-analyzer` invocation, `tests/` discovery,
  `TESTING_STATUS.md`, `CC_THRESHOLD`/`MODULE_SIZE_LIMIT`, docs scanners.

### Execution modes
- **A. Vendored in the submodule (now)**: `uv run python .agent/tools/forge.py <cmd>`;
  tooling deps declared in the project `pyproject.toml`. Zero publish overhead.
- **B. Published package (later)**: `uv add --dev "agentic-forge @ git+https://codeberg.org/<user>/agentic-forge"`
  → `uv run forge <cmd>`. Recommended only if reuse across many projects grows.

> Skills/workflows must be physically present (agents read them), so the `.agent/`
> submodule is required even if the CLI is packaged.

---

## 4. Phased Rollout

| Phase | Scope | Status |
| :--- | :--- | :--- |
| **F1** | Create `.agent-state/`, migrate state, make tooling path-aware via `forge.toml` + `forge_paths.py` (no submodule yet) | ✅ **DONE 2026-10-04** |
| **F2** | Extract generic content + tooling, publish `agentic-forge` on Codeberg (`git subtree split` preserves history). Source of truth is the evolved `.agent/` (`antigravity-framerepo` is deprecated) | ✅ **DONE 2026-10-04** — published (fresh, no history) at `codeberg.org/geociencio/agentic-forge` |
| **F3** | Convert `.agent/` to a git submodule; CI with `submodules: recursive`; document cloning | ⬜ Pending |
| **F4** | Governance: framework issues/PRs on Codeberg; bump the gitlink on updates; update `/start-session` etc. | ⬜ Pending |
| **F5** | **Tooling extraction** (separate/last): `agentic-forge/tools/forge.py` CLI + `sync_metrics` split; repoint `pre-push`, `Makefile`, workflows | ⬜ Pending |

**Sequencing rationale**: F1–F4 change structure/content; F5 refactors working tooling.
Keeping F5 last means every earlier phase is independently verifiable and reversible,
and a red gate is never ambiguous between "structure" and "refactor" causes.

---

## 5. Codeberg Setup (F2/F3 sketch)

```bash
# F2 — curate the framework (merge SecInterp generic skills/workflows with framerepo)
#      and publish, preserving history:
git subtree split -P .agent -b agent-history            # or per-subfolder
git remote add codeberg git@codeberg.org:<user>/agentic-forge.git
git push codeberg agent-history:main

# F3 — convert .agent into a submodule
git rm -r --cached .agent && rm -rf .agent
git submodule add git@codeberg.org:<user>/agentic-forge.git .agent
```

---

## 6. Risks & Guardrails

- **Private repo**: `AGENT_LESSONS` and session notes are internal.
- **Windows**: symlink approach discarded; submodule is safe.
- **CI**: GitHub CI does not reference `.agent` today; add `submodules: recursive` when F3 lands.
- **Packaging**: `.qgisignore` excludes both `.agent/` and `.agent-state/` from the ZIP.
- **Dirty-submodule**: F1 keeps state out of `.agent/`, so `sync_metrics.py` no longer
  dirties the future submodule each session.

---

## 7. F1 — Change Log (COMPLETED)
- New `.agent-state/` (moved with `git mv`): `memory/`, `history/`, `task.md`, `next_steps.md`.
- New `forge.toml` + `scripts/forge_paths.py` (path contract; `forge_paths` exposes
  `PROJECT_ROOT`, `FRAMEWORK_DIR`, `STATE_DIR`, `*_FILE` constants).
- Path-aware tooling: `sync_metrics.py`, `validate_agent_system.py`, `lesson_extractor.py`,
  `memory_prune.py`, `mcp_server.py` (consistency scan now covers framework **+** state).
- Active references updated (`.agent/workflows/*`, `agentic-memory/SKILL.md`,
  `.agent/README.md`, `architecture/IMPROVEMENT_PLAN.md`, `AGENTS.md`, `scripts/README.md`,
  `.qgisignore`). Historical docs left untouched.
- **Gates green**: `sync_metrics --validate`, `validate_agent_system`, `check_docs`,
  `pre-commit`, `make docker-test` (763 tests), `tests/agentic` (23).

---

## 8. F2 — Change Log

### F2a — Content split (DONE 2026-10-04)
- Moved project-specific skills to the overlay with `git mv`:
  `.agent/skills/project-context` + `.agent/skills/geological-logic` → `.agent-state/skills/`.
- `forge_paths.py`: added `OVERLAY_SKILLS_DIR`, `skill_dirs()`, `agent_roots()`.
- `validate_agent_system.py`: skill validation/conflicts/graph now scan
  **framework + overlay** (`skill_dirs()`); robust relative-path rendering across roots.
- References updated (root `AGENTS.md`, `.agent/QUICK_REFERENCE.md`, `.agent/README.md`,
  `core/AGENTS.md`). Framework now has 11 skills; 2 live in the project overlay (13 total).
- **Gates green**: `validate_agent_system` (13 skills, 15 workflows; `--conflicts`,
  `--graph` OK), `sync_metrics --validate`, `check_docs`.

### F2b — Publish on Codeberg (DONE 2026-10-04)
Published (fresh export, **no history** — public-safe) via `scripts/export_agentic_forge.sh`
→ **https://codeberg.org/geociencio/agentic-forge** (`main`, 35 files: `skills/`, `workflows/`,
`resources/`, `architecture/`, `README.md`, `QUICK_REFERENCE.md`). No `.agent-state/`, no
`/home/*` paths. The repo is **public**.

> **Published repo**: **MIT licensed** (`.agent/LICENSE`, exported). Still pending: set the
> repository description/topics (UI/API). Tooling (`tools/forge`) arrives in F5.

### F2 follow-up (genericization)
**Public-ready pass (DONE 2026-10-04)**: `.agent/README.md` and `.agent/QUICK_REFERENCE.md`
rewritten as framework-neutral docs (Agentic Forge; SecInterp as *reference implementation*);
absolute `/home/...` paths removed (`QUICK_REFERENCE.md`, `qa-docker/SKILL.md`); project
metrics moved out of framework docs; `scripts/export_agentic_forge.sh` added (fresh/no-history
export for **public**; `--with-history` for **private**; safety gate rejects `/home/` leaks).

Residual `SecInterp` mentions inside individual skills/workflows are non-sensitive and can be
templatized later; `geological-logic` may be promoted to `scaffold/geology`. The framework repo
still needs a **LICENSE** decision and, in F5, its own `tools/`.

---

*Plan approved 2026-10-04 — Option D, framework name `agentic-forge`, tooling extraction deferred to F5.*
