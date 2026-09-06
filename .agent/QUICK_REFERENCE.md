# Quick Reference: Workflows + Skills System

**Created Date**: 2026-03-09
**Version**: 1.6 (Updated 2026-05-26 — Generation 6)

---

## 📋 Executive Summary

The SecInterp project features a complete system of **13 skills** and **16 workflows** integrated to automate the invocation of specialized agents and contextual knowledge. As of **Phase v3.5.0**, the system has reached **Generation 6** maturity.

---

## 🛠️ Available Skills (13)

| Skill | Description | When to Use |
|:------|:------------|:------------|
| [agentic-memory](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/agentic-memory/SKILL.md) | Lessons and patterns management | Extracting meta-lessons, preferences |
| [coding-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/coding-standards/SKILL.md) | Project coding standards | Writing Python code, refactoring |
| [commit-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/commit-standards/SKILL.md) | Conventional Commits standards | Creating commits, validating messages |
| [documentation-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/documentation-standards/SKILL.md) | Logs and project history standards | Updating development/maintenance logs |
| [geological-logic](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/geological-logic/SKILL.md) | Geological logic and 3-level validation | Working with drillholes, interpolation |
| [i18n-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/i18n-standards/SKILL.md) | Internationalization standards | Adding translations, UI strings |
| [project-context](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/project-context/SKILL.md) | Project purpose and architecture | Starting tasks, requesting overviews |
| [qa-docker](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/qa-docker/SKILL.md) | Docker testing and QGIS mocks | Writing/executing tests, using mocks |
| [qgis-core](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/qgis-core/SKILL.md) | QGIS API and plugin structure | Working with PyQGIS, QgsTask |
| [qgis-migration-4x](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/qgis-migration-4x/SKILL.md) | QGIS 4.x migration guide | Checking for deprecated APIs |
| [release-management](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/release-management/SKILL.md) | QGIS release process | Preparing releases, versioning |
| [ui-framework](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/ui-framework/SKILL.md) | Programmatic UI and premium aesthetics | Modifying GUI, layouts, CSS |
| [changelog-generator](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/skills/changelog-generator/SKILL.md) | Automated changelog from git commits | Writing release notes, CHANGELOG updates |

---

## 🔄 Available Workflows (16)

### Daily Development

| Workflow | Agent | Skills | Purpose |
|:---------|:------|:-------|:----------|
| [/start-session](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/start-session.md) | Senior Architect | qgis-core, qa-docker | Start session with semantic skill injection |
| [/create-commit](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/create-commit.md) | QA Engineer | qa-docker, commit-standards | Commit with quality validation |
| [/run-tests](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/run-tests.md) | QA Engineer | qa-docker | Run tests with intelligent interpretation |
| [/close-session](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/close-session.md) | QA Engineer | qa-docker, commit-standards | Close session with auto-metrics and pruning |

### Refactoring and Quality

| Workflow | Agent | Skills | Purpose |
|:---------|:------|:-------|:----------|
| [/refactor-code](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/refactor-code.md) | Senior Architect | qgis-core, geological-logic | Refactor code with CC validation |
| [/run-tests-in-qgis](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/run-tests-in-qgis.md) | QA Engineer | qa-docker | Integration tests in real QGIS |
| [/audit-plugin](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/audit-plugin.md) | Agent Auditor | project-context, i18n-standards | Full quality and security audit |
| [/fix-linting](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/fix-linting.md) | QA Engineer | coding-standards | Automatically fix style issues |

### Features and i18n

| Workflow | Agent | Skills | Purpose |
|:---------|:------|:-------|:----------|
| [/build-feature](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/build-feature.md) | Architect | qgis-core, qa-docker | Autonomous pipeline for new features |
| [/i18n-maintenance](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/i18n-maintenance.md) | QA Engineer | i18n-standards | Add or update translations |

### Release and Planning

| Workflow | Agent | Skills | Purpose |
|:---------|:------|:-------|:----------|
| [/release-plugin](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/release-plugin.md) | QA Engineer | release-management | Full release process |
| [/start-phase](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/start-phase.md) | Senior Architect | project-context | Start major phase with planning |
| [/close-phase](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/close-phase.md) | Senior Architect | project-context | Close phase with metrics and retro |
| [/ia-critic](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/ia-critic.md) | Agent Auditor | project-context | Implementation plan audit |
| [/verify-standards](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/verify-standards.md) | Senior Architect | coding-standards | Audit agent system consistency |

---

## ⚡ Gen 6 Automation Scripts

| Script | Purpose | Command |
|:-------|:--------|:--------|
| **Memory Pruning** | Auto-prune consolidated lessons | `uv run python scripts/memory_prune.py` |
| **Context Selector**| Semantic skill selection | `uv run python scripts/context_selector.py` |
| **Metrics Report** | Markdown trend report | `uv run python scripts/metrics_report.py` |
| **CC Checker** | Validate complexity thresholds | `uv run python scripts/check_cc.py` |
| **Metrics Sync** | Unified ground-truth metric extraction | `uv run python scripts/sync_metrics.py` |
| **Metric Validator** | Cross-file consistency check | `uv run python scripts/validate_agent_metrics.py` |
| **Workflow Graph** | Dependency graph & ref validator | `uv run python scripts/workflow_graph.py` |
| **Metrics Trends** | Trend report with ASCII sparklines | `uv run python scripts/metrics_report.py` |
| **Lesson Extractor** | Auto-propose AGENT_LESSONS candidates | `uv run python scripts/lesson_extractor.py --propose` |
| **Session Index** | Chronological index of maintenance logs | `uv run python scripts/session_index.py` |
| **Workflow Executor** | Runtime-agnostic workflow translator | `uv run python scripts/workflow_executor.py <name>` |
| **System Validator** | Validate .agent/ structure integrity | `uv run python scripts/validate_agent_system.py` |

---

## 📊 System Metrics

**Current Status** *(updated 2026-05-24 — ground-truth audit)*:
- ✅ **Generation 6 Enabled**: Automated memory, context, and quality gates.
- ✅ **Security Score**: **100.0/100** (Bandit).
- ✅ **Maintainability**: **90.7/100** (qgis-analyzer).
- ✅ **Module Stability**: **52.3/100** (qgis-analyzer).
- ✅ **Docstring Coverage**: **100.0%** (Project-wide compliance).
- ✅ **Return Type Coverage**: **100.0%**.
- ✅ **Param Type Coverage**: **94.2%**.
- ✅ **Complexity Gate**: **CC <= 10** (verified 2026-05-24 by check_cc.py).
- ✅ **i18n Hygiene Gate**: **0 violations** (verified by verify_i18n_hygiene.py).
- ⚠️ **qgis-analyzer i18n**: 72 MISSING_I18N flagged (all false positives after triage).
- ✅ **Tests**: **620 passing** (confirmed 2026-05-24 via `make docker-test`).

---

## 🛡️ Pre-push Quality Gate

The system includes a mandatory `.git/hooks/pre-push` gate that blocks any push if:
1. `qgis-analyzer` analysis fails.
2. Any function has a **Cyclomatic Complexity > 10**.

---

## 🔧 Maintenance

### Sync Skills and Workflows
```bash
uv run python scripts/skill_sync.py
```

### Run Metrics Report
```bash
uv run python scripts/metrics_report.py
```

---

## 📚 References

- [.agent/README.md](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/README.md) - **Full System Documentation**
- [AGENTS.md](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/AGENTS.md) - Full agents and skills definition
- [.codewhale/instructions.md](file:///home/jmbernales/qgispluginsdev/sec_interp/.codewhale/instructions.md) - **CodeWhale Runtime Bridge**
- [workflows/index.md](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/index.md) - **Workflow Quick Reference**
- [DEVELOPMENT_LOG.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/DEVELOPMENT_LOG.md) - Project history

---

**Last update**: 2026-05-26
**System Version**: 1.6 (Generation 6 — Operational Excellence)
