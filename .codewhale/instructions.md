# CodeWhale — SecInterp Agentic Bridge

> This document bridges the `.agent/` system (designed for Antigravity/Gemini)
> to the current CodeWhale/DeepSeek V4 runtime. It is Tier 5 (Local Law) in
> the CodeWhale Constitution hierarchy — subordinate to user directives and
> Constitutional Articles, but above memory and personality.

---

## How This Works

The `.agent/` directory contains 13 skills, 15 workflows, a 3-tier memory
system, and quality gates. These were designed for a runtime where `/commands`
dispatch workflows. In CodeWhale, **there is no command dispatcher**.
Workflows are executed by the agent reading the workflow doc and performing
the equivalent actions using CodeWhale tools.

**Golden rule**: When a user says "run /start-session" or references a
workflow, read the corresponding `.agent/workflows/*.md` and execute its
steps using available tools (`exec_shell`, `read_file`, `write_file`, etc.).

---

## Skill Mapping: `.agent/skills/` → CodeWhale

CodeWhale loads skills natively from `~/.codewhale/skills/` and
`~/.agents/skills/`. The project's `.agent/skills/` are **embedded
knowledge** — the agent reads them on demand via `read_file`.

| .agent Skill | CodeWhale Equivalent | How to Activate |
|---|---|---|
| `coding-standards` | AGENTS.md + Constitution | Always active (root AGENTS.md) |
| `commit-standards` | AGENTS.md commit section | On demand: `read_file .agent/skills/commit-standards/SKILL.md` |
| `qa-docker` | `exec_shell` + `make docker-test` | Run: `read_file .agent/skills/qa-docker/SKILL.md` then `make docker-test` |
| `geological-logic` | AGENTS.md Core/GUI rules | Always active (core/AGENTS.md) |
| `qgis-core` | AGENTS.md QGIS rules | Always active |
| `qgis-migration-4x` | On demand | Read when working with Qt5/Qt6 compat |
| `ui-framework` | AGENTS.md GUI rules | Always active (gui/AGENTS.md) |
| `i18n-standards` | On demand | Read when doing translations |
| `project-context` | Constitution context pack | Auto-loaded at session start |
| `documentation-standards` | On demand | Read when updating docs/logs |
| `release-management` | On demand | Read during release workflow |
| `changelog-generator` | `git log` + manual | Interpretive (no script) |
| `agentic-memory` | `read_file` + `edit_file` | Manual: update AGENT_LESSONS.md |

**CodeWhale-native skills** (from `~/.codewhale/skills/`) that overlap:
- `delegate` → replaces sub-agent spawning in build-feature workflow
- `v4-best-practices` → replaces context_selector.py semantic injection
- `pdf`, `spreadsheets`, `documents`, `presentations` → for exporters work

---

## Workflow Mapping: `.agent/workflows/` → CodeWhale Actions

### Daily Development

| Workflow | CodeWhale Equivalent |
|---|---|
| `/start-session` | 1. `uv run python scripts/sync_metrics.py` 2. `read_file .agent/next_steps.md` 3. `read_file .agent/task.md` 4. `uv sync` |
| `/close-session` | 1. `uv run python scripts/sync_metrics.py` 2. Update `AGENT_LESSONS.md` 3. `uv run python scripts/memory_prune.py` 4. `uv run python scripts/metrics_report.py` 5. Update `next_steps.md` 6. `git add . && git commit -m "chore(docs): close session [topic]"` |
| `/create-commit` | 1. `uv run ruff check --fix . && uv run ruff format .` 2. `uv run python scripts/check_cc.py` 3. `git add . && git commit -m "..."` |
| `/run-tests` | `make docker-test` (full) or `uv run python -m unittest discover tests -q` (local) |

### Refactoring & Quality

| Workflow | CodeWhale Equivalent |
|---|---|
| `/refactor-code` | 1. `read_file .agent/skills/coding-standards/SKILL.md` 2. Make changes 3. `uv run python scripts/check_cc.py` 4. `uv run ruff check --fix .` |
| `/audit-plugin` | `uv run qgis-analyzer analyze .` then inspect `analysis_results/` |
| `/fix-linting` | `uv run ruff check --fix . && uv run ruff format .` |

### Features & i18n

| Workflow | CodeWhale Equivalent |
|---|---|
| `/build-feature` | 1. `read_file .agent/skills/geological-logic/SKILL.md` 2. Implement 3. `/ia-critic` review 4. `/create-commit` |
| `/i18n-maintenance` | 1. `read_file .agent/skills/i18n-standards/SKILL.md` 2. Edit JSON/TS files 3. `uv run python scripts/verify_i18n_hygiene.py` |
| `/ia-critic` | 1. `read_file .agent/memory/AGENT_LESSONS.md` 2. Cross-check plan against core/gui AGENTS.md constraints |

### Release & Planning

| Workflow | CodeWhale Equivalent |
|---|---|
| `/release-plugin` | 1. `read_file .agent/skills/release-management/SKILL.md` 2. `make zip` 3. Verify with `unzip -l` |
| `/start-phase` | 1. `read_file .agent/next_steps.md` 2. Create implementation plan 3. `/ia-critic` |
| `/close-phase` | 1. Update docs/maintenance/phase_closure 2. Update DEVELOPMENT_LOG.md 3. `uv run python scripts/sync_metrics.py` |
| `/verify-standards` | 1. `uv run python scripts/check_cc.py` 2. `uv run python scripts/verify_i18n_hygiene.py` 3. `uv run python scripts/skill_sync.py` |

---

## Gen 6 Automation Scripts — All Verified

All scripts tested and working in this runtime (2026-05-24):

| Script | Command | Status |
|---|---|---|
| `sync_metrics.py` | `uv run python scripts/sync_metrics.py` | ✅ |
| `check_cc.py` | `uv run python scripts/check_cc.py` | ✅ |
| `verify_i18n_hygiene.py` | `uv run python scripts/verify_i18n_hygiene.py` | ✅ |
| `memory_prune.py` | `uv run python scripts/memory_prune.py` | ✅ |
| `metrics_report.py` | `uv run python scripts/metrics_report.py` | ✅ |
| `context_selector.py` | `uv run python scripts/context_selector.py` | ✅ |
| `skill_sync.py` | `uv run python scripts/skill_sync.py` | ✅ |

---

## ⚠️ Known Skill Conflicts (Resolved)

When two `.agent/skills/` give contradictory guidance, these resolutions take precedence. Registered: 2026-05-24.

| Domain | Skill A says | Skill B says | Resolution |
|--------|-------------|-------------|------------|
| **Path handling** | `coding-standards`: ALWAYS `pathlib`, NEVER string concatenation | `qgis-core`: QGIS APIs return `str` paths | Use `Path` objects internally; accept `str` at QGIS boundary, convert with `Path(...)`. Never concatenate with `+` or `os.path.join`. |
| **Geometries** | `geological-logic`: Core MUST NEVER import `QgsGeometry`; use WKT | `qgis-core`: References `QgsGeometry` in GUI examples | WKT strings in `core/`; `QgsGeometry` only in `gui/`. Convert at the bridge: `QgsGeometry.fromWkt()` / `.asWkt()`. |
| **Type strictness** | `coding-standards`: Google Docstrings + return types mandatory | `qgis-core`: QGIS examples often untyped | All new code fully typed. Legacy QGIS patterns tolerated but not emulated. |
| **i18n method** | `i18n-standards`: f-strings with `tr()` for word reordering | `coding-standards`: `.format()` preferred for complex strings | f-strings for simple; `.format()` / `%` for complex/multi-lingual. |

**Rule**: If two skills conflict on a domain not listed here, prefer the *more restrictive* skill until the conflict is explicitly resolved and added to this table.

## What's Different in This Runtime

### Available (CodeWhale-native)
- ✅ `exec_shell` — all scripts, builds, tests
- ✅ `read_file` / `write_file` / `edit_file` — file I/O bypassing shell sandbox
- ✅ `grep_files` / `file_search` — faster than find/grep
- ✅ `task_shell_start` / `task_shell_wait` — long-running commands
- ✅ `agent_open` — sub-agents (parallel work, faster than sequential)
- ✅ `checklist_write` / `update_plan` — task tracking (replaces task.md)
- ✅ Constitution hierarchy — truth, verification, user agency built-in
- ✅ `load_skill` — native skill loading from `~/.codewhale/skills/`

### NOT Available (workflow differences)
- ❌ `/command` dispatch — workflows are documents, not executable triggers. The agent reads them and performs equivalent actions.
- ⚠️ `uv run ai-ctx analyze` — generates AI_CONTEXT.md (architecture, dependencies, patterns). Different from sync_metrics.py (quality gates). Both should run at session start.
- ❌ `make docker-test` — requires Docker daemon. Available in dev environment but not guaranteed.
- ❌ `// turbo` annotations — ignored. Use `task_shell_start` for background work.

### Recommendations
- Use `checklist_write` instead of `.agent/task.md` for active task tracking
- Use `agent_open` for parallel investigations (replaces sequential sub-agent spawning)
- Use `sync_metrics.py` at session start/end instead of manual metric updates
- Read skill files on demand with `read_file`; don't pre-load all 13
