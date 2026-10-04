# Agentic Forge — Quick Reference

**Version**: 1.0 (extracted from SecInterp Gen 8)
**Reference implementation**: SecInterp (QGIS plugin)

---

## 📋 Executive Summary

Agentic Forge is a **runtime-agnostic** agentic development framework. The core ships
**11 skills** and **15 workflows**; a project may add its own skills as an **overlay**
without touching the framework.

The reference implementation is **SecInterp**, which adds 2 project-overlay skills
(`project-context`, `geological-logic`) under `.agent-state/skills/`.

---

## 🛠️ Core Skills (11)

Paths are relative to this file (framework root).

| Skill | Description | When to Use |
|:------|:------------|:------------|
| [agentic-memory](skills/agentic-memory/SKILL.md) | Lessons and patterns management | Extracting meta-lessons, preferences |
| [coding-standards](skills/coding-standards/SKILL.md) | Project coding standards | Writing Python code, refactoring |
| [commit-standards](skills/commit-standards/SKILL.md) | Conventional Commits standards | Creating commits, validating messages |
| [documentation-standards](skills/documentation-standards/SKILL.md) | Logs and project history standards | Updating development/maintenance logs |
| [i18n-standards](skills/i18n-standards/SKILL.md) | Internationalization standards | Adding translations, UI strings |
| [qa-docker](skills/qa-docker/SKILL.md) | Docker testing and QGIS mocks | Writing/executing tests, using mocks |
| [qgis-core](skills/qgis-core/SKILL.md) | QGIS API and plugin structure | Working with PyQGIS, QgsTask |
| [qgis-migration-4x](skills/qgis-migration-4x/SKILL.md) | QGIS 4.x migration guide | Checking for deprecated APIs |
| [release-management](skills/release-management/SKILL.md) | QGIS release process | Preparing releases, versioning |
| [ui-framework](skills/ui-framework/SKILL.md) | Programmatic UI and premium aesthetics | Modifying GUI, layouts, CSS |
| [changelog-generator](skills/changelog-generator/SKILL.md) | Automated changelog from git commits | Writing release notes, CHANGELOG updates |

> Domain/technology skills (QGIS, UI, release) can be grouped as `scaffold/<domain>/`
> so the neutral core stays small. The reference project adds `project-context` and
> `geological-logic` in its overlay.

---

## 🔄 Workflows (15)

### Daily Development

| Workflow | Agent | Skills | Purpose |
|:---------|:------|:-------|:----------|
| [/start-session](workflows/start-session.md) | architect | qgis-core, qa-docker | Start session with semantic skill injection |
| [/create-commit](workflows/create-commit.md) | qa_engineer | qa-docker, commit-standards | Commit with quality validation |
| [/run-tests](workflows/run-tests.md) | qa_engineer | qa-docker | Run tests with intelligent interpretation |
| [/close-session](workflows/close-session.md) | qa_engineer | qa-docker, commit-standards | Close session with auto-metrics and pruning |

### Refactoring and Quality

| Workflow | Agent | Skills | Purpose |
|:---------|:------|:-------|:----------|
| [/refactor-code](workflows/refactor-code.md) | architect | qgis-core, geological-logic | Refactor code with CC validation |
| [/run-tests-in-qgis](workflows/run-tests-in-qgis.md) | qa_engineer | qa-docker | Integration tests in real QGIS |
| [/audit-plugin](workflows/audit-plugin.md) | auditor | project-context, i18n-standards | Full quality and security audit |
| [/fix-linting](workflows/fix-linting.md) | qa_engineer | coding-standards | Automatically fix style issues |

### Features and i18n

| Workflow | Agent | Skills | Purpose |
|:---------|:------|:-------|:----------|
| [/build-feature](workflows/build-feature.md) | architect | qgis-core, qa-docker | Autonomous pipeline for new features |
| [/i18n-maintenance](workflows/i18n-maintenance.md) | qa_engineer | i18n-standards | Add or update translations |

### Release and Planning

| Workflow | Agent | Skills | Purpose |
|:---------|:------|:-------|:----------|
| [/release-plugin](workflows/release-plugin.md) | qa_engineer | release-management | Full release process |
| [/start-phase](workflows/start-phase.md) | architect | project-context | Start major phase with planning |
| [/close-phase](workflows/close-phase.md) | architect | project-context | Close phase with metrics and retro |
| [/ia-critic](workflows/ia-critic.md) | auditor | project-context | Implementation plan audit |
| [/verify-standards](workflows/verify-standards.md) | architect | coding-standards | Audit agent system consistency |

---

## ⚡ Tooling

The framework ships generic agentic tooling. In the reference implementation it lives
in `scripts/` and resolves paths from `forge.toml` via `forge_paths.py`:

| Tool | Purpose | Command |
|:-----|:--------|:--------|
| **System Validator** | Validate framework structure + overlay | `uv run python scripts/validate_agent_system.py` |
| **Workflow Graph** | Dependency graph & broken-reference validator | `uv run python scripts/validate_agent_system.py --graph` |
| **Skill Conflicts** | Cross-skill overlap detection | `uv run python scripts/validate_agent_system.py --conflicts` |
| **Metric Validator** | Cross-file consistency check | `uv run python scripts/sync_metrics.py --validate` |
| **Metrics Sync** | Ground-truth metric extraction | `uv run python scripts/sync_metrics.py` |
| **Memory Pruning** | Auto-prune consolidated lessons | `uv run python scripts/memory_prune.py` |
| **Lesson Extractor** | Propose `AGENT_LESSONS` candidates | `uv run python scripts/lesson_extractor.py --propose` |
| **Session Index** | Chronological index of session logs | `uv run python scripts/session_index.py` |

> F5 of the extraction plan consolidates these into a `agentic-forge/tools/forge.py`
> CLI (`forge validate`, `forge metrics …`).

---

## 📊 Quality Gates (generic)

The framework enforces these gates; **project values** live in
`.agent-state/memory/agent_metrics.json`:

- **Cyclomatic complexity** ≤ 10 per function
- **Docstrings** on public APIs + strict type hints
- **Mock-first** unit tests (no live service required)
- **i18n hygiene** (no untranslated user-facing strings)
- **Module size** limit
- **Security** scan

---

## 🛡️ Pre-push Quality Gate

The reference implementation wires a `.git/hooks/pre-push` gate that blocks a push if
the analyzer fails or any function exceeds **CC > 10**.

---

## 📚 References

- [README.md](README.md) — framework overview
- [AGENTS.md](AGENTS.md) — runtime/role configuration (canonical file lives at repo root in the reference implementation)
- [workflows/index.md](workflows/index.md) — workflow quick reference

> Project-specific state (memory, task board, `next_steps.md`, metrics) lives in
> `.agent-state/`, never in the framework.

---

**System Version**: 1.0 (extracted from SecInterp Gen 8 — opencode-native)
