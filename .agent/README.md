# SecInterp Agentic System (Generation 6)

Welcome to the **SecInterp Agentic Intelligence Core**. This directory contains the complete brain, tools, and protocols that empower the AI agent to act as a Senior Architect, QA Engineer, and Auditor for the SecInterp QGIS plugin.

## 🚀 Overview: The Generation 6 Architecture

SecInterp has evolved into a **Generation 6 Agentic System**, moving beyond simple script execution into a state-governed, self-pruning, and metric-aware cognitive architecture.

### Key Innovations in Gen 6:
1.  **Semantic Context Injection**: No more token bloat. The system uses `context_selector.py` to pre-load only the most relevant skills for the current task.
2.  **Autonomous Memory Pruning**: The `memory_prune.py` utility automatically maintains the lesson log, moving consolidated knowledge to long-term archives.
3.  **Zero-Regression Quality Gates**: A mandatory `pre-push` hook enforces Cyclomatic Complexity (CC <= 10) and quality standards before any code reaches the repository.
4.  **Observability Engine**: `metrics_report.py` provides visual Markdown trends of the agent's effectiveness and technical debt evolution.

---

## 📁 Directory Structure

```bash
.agent/
├── AGENTS.md               # 🧠 Primary role definitions & skill mappings
├── QUICK_REFERENCE.md      # 📋 Fast lookup for skills and workflows
├── architecture/           # 🏗️ System design and optimization plans
│   ├── OPTIMIZATION_PLAN.md # Roadmap for system evolution
│   └── memory_policy.md     # 3-tier memory management rules
├── memory/                 # 🧠 Cognitive history and lessons
│   ├── AGENT_LESSONS.md    # Structured technical lessons (YAML)
│   ├── agent_metrics.json  # Operational metrics (schema v2.0)
│   └── history/            # Session and task logs
├── skills/                 # 🛠️ On-demand capabilities (13)
│   ├── geological-logic/   # Specialized geological processing
│   ├── qgis-core/          # PyQGIS and async tasks expertise
│   └── ... (see QUICK_REFERENCE.md)
└── workflows/              # 🔄 Standardized operational procedures (16)
    ├── start-session.md    # Initializing with context
    ├── create-commit.md    # Quality-validated commits
    └── ... (see QUICK_REFERENCE.md)
```

---

## 🧠 Memory & Observability

The system maintains a **3-Tier Memory Model**:
-   **Episodic Memory**: Raw session logs and task records in `memory/history/`.
-   **Semantic Memory**: Distilled lessons in `AGENT_LESSONS.md`.
-   **Long-Term Archive**: Pruned lessons moved to the `[PRUNED]` index once consolidated into `SKILL.md` files.

### Observability Tools:
-   **`uv run python scripts/metrics_report.py`**: Generates a performance report.
-   **`uv run python scripts/memory_prune.py`**: Prunes old consolidated lessons.
-   **`uv run python scripts/check_cc.py`**: Validates complexity thresholds.

---

## 🛠️ How to use the System

### 1. Starting a Session
Always start with `/start-session`. This triggers the `context_selector.py` to inject the right skills and synchronizes the project state.

### 2. Developing and Testing
Use specialized workflows like `/build-feature` or `/refactor-code`. These ensure that the **Agent Auditor** reviews your plans before implementation.

### 3. Committing and Pushing
Use `/create-commit`. The system will validate your message, check the quality metrics, and run ruff/black. The `pre-push` hook will block any push that exceeds CC standards.

### 4. Closing a Session
Always use `/close-session`. This updates the `DEVELOPMENT_LOG.md`, prunes the memory, and records metrics for the session.

---

## 🛡️ Quality Standards

This project enforces:
-   **CC <= 10**: No function should be overly complex.
-   **100% Docstrings**: All public APIs must follow Google Style.
-   **100% Return Types**: Strict typing for all function returns.
-   **Mock-First Testing**: Isolated unit tests that do not require a live QGIS instance.

---

**System Version**: 1.5 (Gen 6 Initialized)
**Last Audit**: 2026-04-29
**Status**: 🟢 Operational Excellence Mode
