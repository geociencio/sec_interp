# Agentic Forge

A **runtime-agnostic** agentic development framework: skills, workflows, roles, memory
and quality gates that let an AI coding agent operate as a disciplined senior engineer.

> **Reference implementation**: **SecInterp** (a QGIS plugin). Project-specific state
> and skills live **outside** the framework, under `.agent-state/`, so a framework
> update never overwrites project history or metrics.

---

## 🚀 Principles

1. **Semantic context injection** — the root `AGENTS.md` lists each skill with a
   "when to use" description; the agent loads only the relevant `SKILL.md` on demand.
2. **Autonomous memory pruning** — consolidated lessons are moved to a `[PRUNED]` index.
3. **Zero-regression quality gates** — a `pre-push` hook enforces complexity and style
   standards before code reaches the repository.
4. **Observability** — metric sync/report tooling tracks quality over time.
5. **Runtime-agnostic** — verified with opencode; works with any agent that reads
   `AGENTS.md` + `SKILL.md`.

---

## 📁 Directory Structure

```bash
# Framework (this repository)
├── AGENTS.md               # ➡️ Compatibility pointer (canonical config lives at project root)
├── QUICK_REFERENCE.md      # 📋 Fast lookup for skills and workflows
├── architecture/           # 🏗️ System design and optimization plans
├── skills/                 # 🛠️ Re-usable capabilities
├── workflows/              # 🔄 Standardized operational procedures
└── scaffold/<domain>/      # 🧩 Optional domain packs (qgis, web, ...)

# Project-owned (lives at the project root, NOT in this repository)
.agent-state/
├── next_steps.md           # 🎯 Active goals and handoff state
├── task.md                 # 📌 Active task board
├── skills/                 # 🧩 Project-specific skill overlay
├── memory/                 # 🧠 Lessons, metrics, memory policy
└── history/                # 📜 Archived task boards and next_steps snapshots
```

---

## 🧩 Path Model

A `forge.toml` at the project root declares two directories:

```toml
[forge]
framework = ".agent"        # this framework (candidate git submodule)
state = ".agent-state"      # project-owned state
```

The tooling resolves them through a small helper (`forge_paths.py`) that walks up to
find `forge.toml`, so it keeps working regardless of where the tools live. The skill
scanner validates the **framework skills plus the project overlay**.

---

## 🧠 Memory Model (3 tiers)

- **Short-term**: current session context (`AI_CONTEXT.md`), reset each session.
- **Episodic**: session logs + archived task boards / `next_steps` snapshots.
- **Semantic**: distilled lessons (`AGENT_LESSONS.md`) and `SKILL.md` procedures.

The project owns this state under `.agent-state/`; the framework only defines the rules.

---

## 🛠️ How to Use

1. Clone this framework at `.agent/` (or add it as a git submodule).
2. Add a root `AGENTS.md` with your roles + skills table.
3. Add `forge.toml` declaring `framework` and `state` directories.
4. Put project state and project-specific skills under `.agent-state/`.
5. Start a session with `/start-session` and close it with `/close-session`.

---

## 🛡️ Quality Standards (generic)

- **Cyclomatic complexity** ≤ 10 per function.
- **Docstrings** on public APIs, strict type hints.
- **Mock-first** unit tests (no live service required).
- **i18n hygiene**: no untranslated user-facing strings.
- **Module size** limit and **security** scan.

Only the **rules** ship here. Each project records its own scores in
`.agent-state/memory/agent_metrics.json`.

---

## 📄 License

Released under the [MIT License](LICENSE).

---

**System Version**: 1.0 (extracted from SecInterp Gen 8 — opencode-native)
