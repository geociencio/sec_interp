# SecInterp Agentic System (Generation 6)

Welcome to the **SecInterp Agentic Intelligence Core**. This directory contains the complete brain, tools, and protocols that empower the AI agent to act as a Senior Architect, QA Engineer, and Auditor for the SecInterp QGIS plugin.

> **⚠️ Obsolete**: The `antigravity-framerepo/` directory (former Antigravity framework starter kit, Gen 2/3) is **deprecated**. It is superseded by this `.agent/` system and is no longer tracked by git (see `.gitignore`). Do not sync or update it — use the skills and workflows in `.agent/` instead.

## 🚀 Overview: The Generation 6 Architecture

SecInterp has evolved into a **Generation 6 Agentic System**, moving beyond simple script execution into a state-governed, self-pruning, and metric-aware cognitive architecture.

### Key Innovations in Gen 6:
1.  **Semantic Context Injection**: No more token bloat. The root `AGENTS.md` skills table lists each skill with a "when to use" description; the agent reads only the relevant `SKILL.md` files on demand.
2.  **Autonomous Memory Pruning**: The `memory_prune.py` utility automatically maintains the lesson log, moving consolidated knowledge to long-term archives.
3.  **Zero-Regression Quality Gates**: A mandatory `pre-push` hook enforces Cyclomatic Complexity (CC <= 10) and quality standards before any code reaches the repository.
4.  **Observability Engine**: `sync_metrics.py --report` provides visual Markdown trends of the agent's effectiveness and technical debt evolution.
5.  **Unified Metric Sync**: `sync_metrics.py` runs the qgis-analyzer quality gates (CC via `--max-cc`, i18n via `MISSING_I18N`) and writes a single coherent snapshot to `agent_metrics.json`.

---

## 📁 Directory Structure

```bash
.agent/
├── AGENTS.md               # ➡️ Compatibility pointer (canonical config is root AGENTS.md)
├── QUICK_REFERENCE.md      # 📋 Fast lookup for skills and workflows
├── next_steps.md           # 🎯 Active goals and handoff state
├── architecture/           # 🏗️ System design and optimization plans
│   └── IMPROVEMENT_PLAN.md  # Gen 6→7 improvement plan (2026-05-24)
├── memory/                 # 🧠 Cognitive history and lessons
│   ├── AGENT_LESSONS.md    # Structured technical lessons (YAML)
│   ├── agent_metrics.json  # Operational metrics (schema v2.0)
│   └── memory_policy.md    # Memory lifecycle policy (3-tier rules)
├── skills/                 # 🛠️ On-demand capabilities (13)
│   ├── geological-logic/   # Specialized geological processing
│   ├── qgis-core/          # PyQGIS and async tasks expertise
│   └── ... (see QUICK_REFERENCE.md)
├── workflows/              # 🔄 Standardized operational procedures (15)
│   ├── index.md            # Workflow quick reference
│   ├── start-session.md    # Initializing with context
│   ├── close-session.md    # Closing with metric sync + memory prune
│   └── ... (see QUICK_REFERENCE.md)
└── history/                # 📜 Archived task boards and next_steps snapshots
    ├── tasks/              # Phase task archives (tasks_vX.Y.Z.md)
    └── next_steps/         # Session handoff snapshots (90-day retention, pruned monthly)
```

---

## 🧠 Memory & Observability

The system maintains a **3-Tier Memory Model**:
-   **Episodic Memory**: Session logs and task records in `docs/maintenance/` (100+ files, dated). Archived task boards and next_steps snapshots in `.agent/history/`.
-   **Semantic Memory**: Distilled lessons in `AGENT_LESSONS.md` (~29 active + 12 pruned index).
-   **Long-Term Archive**: Pruned lessons moved to the `[PRUNED]` index once consolidated into `SKILL.md` files.

### Session Archive
Full session summaries are stored in **`docs/maintenance/`** with the naming convention `session_YYYY-MM-DD_[topic].md`. Phase closures use `phase_closure_vX.Y.Z.md`. This is the canonical episodic memory store — see `memory_policy.md` for the full lifecycle policy.

### Observability Tools:
-   **`uv run python scripts/sync_metrics.py`**: Unified ground-truth extraction (qgis-analyzer + CC + i18n)
-   **`uv run python scripts/sync_metrics.py --report`**: Generates a Markdown performance report.
-   **`uv run python scripts/memory_prune.py`**: Prunes old consolidated lessons.
-   **`uv run qgis-analyzer analyze . --max-cc 10`**: Validates complexity thresholds.
-   **`uv run qgis-analyzer analyze .`**: AST-based i18n hygiene scanner (`MISSING_I18N` rule).

---

## 🛠️ How to use the System

### 1. Starting a Session
Always start with `/start-session`. This runs `sync_metrics.py` + `ai-ctx analyze`, reads `next_steps.md` and `task.md`, and synchronizes the project state.

### 2. Developing and Testing
Use specialized workflows like `/build-feature` or `/refactor-code`. These ensure that the **Agent Auditor** reviews your plans before implementation.

### 3. Committing and Pushing
Use `/create-commit`. The system will validate your message, check the quality metrics, and run ruff. The `pre-push` hook will block any push that exceeds CC standards.

### 4. Closing a Session
Always use `/close-session`. This runs `sync_metrics.py`, updates `AGENT_LESSONS.md`, prunes memory, generates metrics report, updates `next_steps.md`, and commits.

### Runtime Adaptation
This system is runtime-agnostic and currently operates under opencode. See **`workflows/index.md`** for the workflow quick reference.

---

## 🛡️ Quality Standards

This project enforces:
-   **CC <= 10**: No function should be overly complex (verified by `qgis-analyzer --max-cc 10`).
-   **100% Docstrings**: All public APIs must follow Google Style (verified by qgis-analyzer).
-   **100% Return Types**: Strict typing for all function returns.
-   **93.1% Param Types**: Type hints on all function parameters.
-   **Mock-First Testing**: Isolated unit tests that do not require a live QGIS instance.
-   **i18n hygiene**: AST-based `MISSING_I18N` rule in qgis-analyzer.
-   **Module Size**: No source module exceeds 400 lines (verified by qgis-analyzer).

### Current Scores (2026-09-20)
| Metric | Score |
|--------|-------|
| Module Stability | 54.0/100 |
| Maintainability | 99.9/100 |
| Security (Bandit) | 100.0/100 |
| Tests | 615 passing |
| CC Gate | PASS (all ≤ 10) |
| i18n AST Gate | PASS (0 violations) |
| Module Size Gate | PASS |

### Canonical Metric Sources

Multiple analyzers produce overlapping numbers. To avoid metric staleness, each dimension has a **single authoritative source**:

| Metric | Authoritative tool | Stored in |
| :--- | :--- | :--- |
| Module Stability | `qgis-analyzer` (`qgis-analyzer analyze .`) | `agent_metrics.json` → `quality_score_latest` |
| Maintainability | `qgis-analyzer` | `agent_metrics.json` → `maintainability_score` |
| Security | `qgis-analyzer` (Bandit) | `agent_metrics.json` → `security_score` |
| Cyclomatic Complexity | `qgis-analyzer analyze . --max-cc 10` | `agent_metrics.json` → `cyclomatic_complexity_gate` |
| i18n hygiene | `qgis-analyzer` `MISSING_I18N` rule (AST) | `agent_metrics.json` → `i18n_hygiene_gate` |
| i18n analyzer scope | `qgis-analyzer` MISSING_I18N | `agent_metrics.json` → `i18n_issues_qgis_analyzer` |
| Test count | `make docker-test` → `sync_metrics.py --testing-status` | `agent_metrics.json` → `tests_ok` |
| Type hints / Docstrings | `qgis-analyzer` research metrics | `agent_metrics.json` summary |

> `ai-ctx` (`AI_CONTEXT.md`, `PROJECT_SUMMARY.md`) measures a **different** "quality score" (aggregate heuristic) and is **not** canonical. Ignore it when reporting project metrics.

---

**System Version**: 1.8 (Gen 6 — Phase 1 complete, Gen 7 tooling wired + tested)
**Last Audit**: 2026-09-12 (metric reconciliation, phase v3.7.0 closure, agentic tooling hardening)
**Status**: 🟢 Operational — Metric Integrity Verified
