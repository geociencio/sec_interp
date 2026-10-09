# Implementation Plan: Unify Agentic Systems on agentic-forge

**Status**: 🚧 IN PROGRESS — Part A (upstream genericization) started
**Created**: 2026-10-08
**Owner**: @architect (+ @qa_engineer for verification)
**Scope**: `qgis-plugin-analyzer`, `qgis-plugin-manager`, `ai-context-core` — adopt
the `agentic-forge` framework (Codeberg) as the canonical agentic system.

---

## 0. Context

A reevaluation of the SecInterp agentic system (2026-10-04) extracted the reusable
framework into **`agentic-forge`** (https://codeberg.org/geociencio/agentic-forge,
MIT), mounted as a git submodule at `.agent/`, with project-owned state under
`.agent-state/` and a `forge.toml` path/config contract.

The three sibling projects (`qgis-plugin-analyzer`, `qgis-plugin-manager`,
`ai-context-core`) share the same lineage but sit in different generations
(Gen 5 vs Gen 8) with duplicated, drifting agentic systems. This plan unifies them
on the `agentic-forge` pattern.

**Canonical target model**:

```
<project>/
├── .agent/           ← git submodule → codeberg.org/geociencio/agentic-forge
│   ├── skills/       (generic)   ├── workflows/ (generic)
│   ├── tools/        (forge.py CLI + forge_paths + validate + memory_prune
│   │                  + lesson_extractor + forge_metrics)
│   ├── scaffold/<domain>/        (qgis, ...)
│   └── AGENTS.md     (default config)
├── .agent-state/     ← project-owned (never overwritten by framework updates)
│   ├── memory/  task.md  next_steps.md  history/
│   └── skills/       (overlay: project-context, domain-logic, ...)
├── forge.toml        ← [forge].framework/.state + [project] thresholds
├── opencode.json     ← native subagents (allow/ask/deny) + skills.paths
└── AGENTS.md         ← canonical root override (what opencode loads)
```

---

## 1. Decisions (confirmed)

1. **Framework consumption = git submodule** (single source of truth, explicit
   version pinning via gitlink, `submodules: recursive` in CI).
2. **`qa-standards` → `testing-standards`**, promoted to the framework as a generic skill.
3. **`release-management` → generic (PyPI)** upstream; QGIS variant lives in `scaffold/qgis`.
4. **Thresholds** extracted to `forge.toml` from the analyzer's own rules:
   `max_cc = 15` (HIGH_COMPLEXITY rule in `RULES.md`), `module_size_limit = 400`
   (framework default).

Minor (locked): `i18n-standards` genericized upstream (visitor notes folded into
`domain-logic` overlay); workflow overlay support deferred; `module_size_limit` uses
the framework default.

---

## 2. Skill taxonomy (target)

### Framework — generic skills (`.agent/skills/`)
`agentic-memory`, `changelog-generator`, `coding-standards`, `commit-standards`,
`documentation-standards`, `testing-standards` (renamed), `release-management`
(generic PyPI), `qa-docker`, `i18n-standards` (genericized).

### Framework — domain scaffolds (`scaffold/qgis/`)
`qgis-core`, `qgis-migration-4x`, `ui-framework`, QGIS `release-plugin` + QGIS
`audit-plugin` + `run-tests-in-qgis` workflows.

### Project overlay (`.agent-state/skills/`)
- analyzer: `domain-logic`, `project-context`
- manager: `domain-logic`, `project-context`
- ai-context-core: `domain-logic`, `project-context`, `skill-authoring`,
  `debug-specialist`, `tech-stack`, `testing-standards` (if project-specific)

---

## 3. Part A — Upstream genericization (agentic-forge, Codeberg)

- **A1**: Genericize `release-management`, `i18n-standards`, `qa-docker` (remove
  QGIS-specific bias; move specifics to `scaffold/qgis`).
- **A2**: Move `qgis-core`, `qgis-migration-4x`, `ui-framework` → `scaffold/qgis/skills/`.
- **A3**: Promote `testing-standards` (from analyzer `qa-standards`), genericized.
- **A4**: Add generic workflows `release-package` (PyPI) and `audit-package`
  (self-audit), from the analyzer's `release-package`/`audit-plugin`.
- **A6**: Tag `v1.2.0`.

---

## 4. Part B — Migrate qgis-plugin-analyzer (F1–F5)

- **F1** state/path split: `git mv .agent/{memory,history,task.md,next_steps.md}`
  → `.agent-state/`; add `forge.toml` (`max_cc=15`, `module_size_limit=400`).
- **F2** content split: move `domain-logic`, `project-context` → `.agent-state/skills/`.
- **F3** submodule: `git submodule add https://codeberg.org/geociencio/agentic-forge.git
  .agent` pinned at `v1.2.0`; CI `submodules: recursive`.
- **F4** tooling: drop `scripts/{validate_agent_system,memory_prune,sync_metrics,
  mcp_server,security_scan,run_tests_in_qgis}.py` + `upstream/`; use `forge.py`;
  keep `sync_metrics.py` as a collector/adapter.
- **F5** cleanup: remove `.ai-context/`, `scaffold/`, `ai-context-core` dev-dep,
  `.ai-context` ruff exclude; fix `opencode.json` `skills.paths` to include
  `.agent-state/skills`; rewrite root `AGENTS.md`.

Verification: `forge.py validate --graph --conflicts`, `git submodule status`,
`qgis-analyzer analyze . --profile release --strict`, `ruff`/`mypy`/`pytest`.

---

## 5. Part C/D — Replicate to ai-context-core and qgis-plugin-manager

After the analyzer is migrated and validated, replicate the template on
`ai-context-core` (Gen 8) and `qgis-plugin-manager` (Gen 5, biggest lift), then add a
cross-repo gate confirming all three pin the same framework version.

---

*Plan adopted 2026-10-08 — framework `agentic-forge`, submodule consumption,
generalization-first (Part A) then analyzer pilot (Part B).*
