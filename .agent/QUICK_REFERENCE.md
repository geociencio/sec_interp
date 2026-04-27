# Quick Reference: Workflows + Skills System

**Created Date**: 2026-03-09
**Version**: 1.2 (Updated 2026-04-27)

---

## 📋 Executive Summary

The SecInterp project features a complete system of **13 skills** and **16 workflows** integrated to automate the invocation of specialized agents and contextual knowledge.

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
| [/start-session](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/start-session.md) | Senior Architect | qgis-core, qa-docker | Start session with synchronized context |
| [/create-commit](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/create-commit.md) | QA Engineer | qa-docker, commit-standards | Commit with quality validation |
| [/run-tests](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/run-tests.md) | QA Engineer | qa-docker | Run tests with intelligent interpretation |
| [/close-session](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/close-session.md) | QA Engineer | qa-docker, commit-standards | Close session with updated logs |

### Refactoring and Quality

| Workflow | Agent | Skills | Purpose |
|:---------|:------|:-------|:----------|
| [/refactor-code](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/workflows/refactor-code.md) | Senior Architect | qgis-core, geological-logic | Refactor code with complexity validation |
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

## 🎯 Common Use Cases

### Start Development Session
```bash
/start-session
```
**What it does**:
- Activates "Senior Architect Agent"
- Loads skills: qgis-core, qa-docker, project-context
- Syncs context (AI_CONTEXT.md, next_steps.md)
- Runs `make test` or `make docker-test` (571 tests)
- Validates quality metrics

### Create Commit with Validation
```bash
/create-commit
```
**What it does**:
- Activates "QA Engineer Agent"
- Loads skills: qa-docker, commit-standards
- Runs ruff/black
- Analyzes metrics (ai-ctx analyze)
- Generates Conventional Commits message options

---

## 📊 System Metrics

**Current Status** *(updated 2026-04-27)*:
- ✅ 13 skills synchronized
- ✅ 16 workflows with full metadata (100%)
- ✅ Zero legacy or duplicate workflows
- ✅ All referenced skills validated (0 warnings)

**Tests**:
- 571 tests total
- 100% success rate (local `make test`)
- Complete QGIS mocking coverage

**Quality** *(qgis-plugin-analyzer v1.13.1)*:
- HIGH_COMPLEXITY issues: 0
- Overall Plugin Score: 41.7/100 (pending i18n/docstring work)

---

## 🔧 Maintenance

### Sync Skills and Workflows
```bash
uv run python3 scripts/skill_sync.py
```

### Add New Skill
1. Create directory: `.agent/skills/[skill-name]/`
2. Create `SKILL.md` with YAML frontmatter.
3. Run `skill_sync.py`.

### Add New Workflow
1. Create file: `.agent/workflows/[name].md`
2. Add YAML frontmatter.
3. Run `skill_sync.py`.

---

## 📚 References

- [AGENTS.md](file:///home/jmbernales/qgispluginsdev/sec_interp/.agent/AGENTS.md) - Full agents and skills definition
- [DEVELOPMENT_LOG.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/DEVELOPMENT_LOG.md) - Project history

---

**Last update**: 2026-04-27
**System Version**: 1.2 (Deduplication + Metrics Refresh)
