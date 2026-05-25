# SecInterp Agentic System (Generation 6)

Welcome to the **SecInterp Agentic Intelligence Core**. This directory contains the complete brain, tools, and protocols that empower the AI agent to act as a Senior Architect, QA Engineer, and Auditor for the SecInterp QGIS plugin.

## 🚀 Overview: The Generation 6 Architecture

SecInterp has evolved into a **Generation 6 Agentic System**, moving beyond simple script execution into a state-governed, self-pruning, and metric-aware cognitive architecture.

### Key Innovations in Gen 6:
1.  **Semantic Context Injection**: No more token bloat. The system uses `context_selector.py` to pre-load only the most relevant skills for the current task.
2.  **Autonomous Memory Pruning**: The `memory_prune.py` utility automatically maintains the lesson log, moving consolidated knowledge to long-term archives.
3.  **Zero-Regression Quality Gates**: A mandatory `pre-push` hook enforces Cyclomatic Complexity (CC <= 10) and quality standards before any code reaches the repository.
4.  **Observability Engine**: `metrics_report.py` provides visual Markdown trends of the agent's effectiveness and technical debt evolution.
5.  **Unified Metric Sync**: `sync_metrics.py` runs all quality gates (qgis-analyzer + check_cc + verify_i18n) and writes a single coherent snapshot to `agent_metrics.json`.

---

## 📁 Directory Structure

```bash
.agent/
├── AGENTS.md               # 🧠 Primary role definitions & skill mappings
├── QUICK_REFERENCE.md      # 📋 Fast lookup for skills and workflows
├── next_steps.md           # 🎯 Active goals and handoff state
├── task.md                 # 📋 Active task board
├── architecture/           # 🏗️ System design and optimization plans
│   ├── OPTIMIZATION_PLAN.md # Gen 5→6 roadmap
│   ├── IMPROVEMENT_PLAN.md  # Gen 6→7 improvement plan (2026-05-24)
│   └── memory_policy.md     # 3-tier memory management rules
├── memory/                 # 🧠 Cognitive history and lessons
│   ├── AGENT_LESSONS.md    # Structured technical lessons (YAML)
│   ├── agent_metrics.json  # Operational metrics (schema v2.0)
│   └── memory_policy.md    # Memory lifecycle policy
├── skills/                 # 🛠️ On-demand capabilities (13)
│   ├── geological-logic/   # Specialized geological processing
│   ├── qgis-core/          # PyQGIS and async tasks expertise
│   └── ... (see QUICK_REFERENCE.md)
├── workflows/              # 🔄 Standardized operational procedures (15)
│   ├── index.md            # CodeWhale runtime quick reference
│   ├── start-session.md    # Initializing with context
│   ├── close-session.md    # Closing with metric sync + memory prune
│   └── ... (see QUICK_REFERENCE.md)
└── history/                # 📜 Archived task boards and next_steps snapshots
    ├── tasks/              # Phase task archives (8 files)
    └── next_steps/         # Session handoff snapshots (43 files)
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
-   **`uv run python scripts/metrics_report.py`**: Generates a Markdown performance report.
-   **`uv run python scripts/memory_prune.py`**: Prunes old consolidated lessons.
-   **`uv run python scripts/check_cc.py`**: Validates complexity thresholds.
-   **`uv run python scripts/verify_i18n_hygiene.py`**: AST-based i18n hygiene scanner.

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
This system was designed for Antigravity/Gemini but is fully operational in CodeWhale/DeepSeek V4. See **`.codewhale/instructions.md`** for the runtime bridge and **`workflows/index.md`** for workflow quick reference.

---

## 🛡️ Quality Standards

This project enforces:
-   **CC <= 10**: No function should be overly complex (verified by `check_cc.py`).
-   **100% Docstrings**: All public APIs must follow Google Style (verified by qgis-analyzer).
-   **100% Return Types**: Strict typing for all function returns.
-   **94.2% Param Types**: Type hints on all function parameters.
-   **Mock-First Testing**: Isolated unit tests that do not require a live QGIS instance.
-   **Dual-Scope i18n**: AST gate (`verify_i18n_hygiene.py`) + qgis-analyzer i18n check.

### Current Scores (2026-05-24)
| Metric | Score |
|--------|-------|
| Module Stability | 52.3/100 |
| Maintainability | 90.7/100 |
| Security (Bandit) | 100.0/100 |
| Tests | 620 passing |
| CC Gate | PASS (all ≤ 10) |
| i18n AST Gate | PASS (0 violations) |

---

**System Version**: 1.6 (Gen 6 — Phase 1 Complete)
**Last Audit**: 2026-05-24 (ground-truth audit)
**Status**: 🟢 Operational — Metric Integrity Verified
