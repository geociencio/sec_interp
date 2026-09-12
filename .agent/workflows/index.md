# Workflow Index — CodeWhale Runtime

> Maps each `.agent/workflows/*.md` to concrete CodeWhale actions.
> For humans: "I want to run X, what do I tell the agent?"
> For agents: "User said /X, what do I actually do?"

---

## Daily Development

### `/start-session`
**Tell the agent**: "Run /start-session"
**What happens**:
```
uv run python scripts/sync_metrics.py
uv run ai-ctx analyze --path .
cat .agent/next_steps.md
cat .agent/task.md
uv sync
```
**Expected output**: Updated metrics, visible active tasks, dependencies OK.

### `/close-session`
**Tell the agent**: "Run /close-session with topic [name]"
**What happens**:
```
uv run python scripts/sync_metrics.py --close-session --topic [name]
# Update AGENT_LESSONS.md with 3 lessons
uv run python scripts/memory_prune.py
uv run python scripts/metrics_report.py
# Update next_steps.md
git add . && git commit -m "chore(docs): close session [topic]"
```

### `/create-commit`
**Tell the agent**: "Run /create-commit with message [msg]"
**What happens**:
```
uv run ruff check --fix . && uv run ruff format .
uv run python scripts/check_cc.py
git add . && git commit -m "[msg]"
```

### `/run-tests`
**Tell the agent**: "Run /run-tests"
**What happens**: `make docker-test` (full) or `uv run python -m unittest discover tests -q` (partial, local)

---

## Refactoring & Quality

### `/refactor-code`
**Tell the agent**: "Run /refactor-code on [file/module]"
**What happens**: Reads coding-standards, applies changes, validates CC, runs ruff.

### `/audit-plugin`
**Tell the agent**: "Run /audit-plugin"
**What happens**: `uv run qgis-analyzer analyze .` → review `analysis_results/`

### `/fix-linting`
**Tell the agent**: "Run /fix-linting"
**What happens**: `uv run ruff check --fix . && uv run ruff format .`

---

## Features & i18n

### `/build-feature`
**Tell the agent**: "Run /build-feature [description]"
**What happens**: Reads geological-logic skill → implement → /ia-critic review → /create-commit

### `/i18n-maintenance`
**Tell the agent**: "Run /i18n-maintenance [language]"
**What happens**: Reads i18n-standards skill → edit JSON/TS → `verify_i18n_hygiene.py`

### `/ia-critic`
**Tell the agent**: "Run /ia-critic on [plan]"
**What happens**: Reads AGENT_LESSONS.md → contrast against core/gui AGENTS.md → issue verdict

---

## Release & Planning

### `/release-plugin`
**Tell the agent**: "Run /release-plugin"
**What happens**: Reads release-management skill → `make zip` → `unzip -l` verification

### `/start-phase`
**Tell the agent**: "Run /start-phase [name]"
**What happens**: Reads next_steps.md → create plan → /ia-critic → start implementation

### `/close-phase`
**Tell the agent**: "Run /close-phase [name]"
**What happens**: Creates `docs/maintenance/phase_closure_[name].md` → update DEVELOPMENT_LOG.md → sync_metrics

### `/verify-standards`
**Tell the agent**: "Run /verify-standards"
**What happens**:
```
uv run python scripts/check_cc.py
uv run python scripts/verify_i18n_hygiene.py
uv run python scripts/skill_sync.py
uv run python scripts/validate_agent_system.py
uv run python scripts/workflow_graph.py --validate
```

---

## Quality Gate Scripts (Direct)

| Script | Command |
|--------|---------|
| Full metric sync | `uv run python scripts/sync_metrics.py` |
| AI Context | `uv run ai-ctx analyze --path .` |
| CC validation | `uv run python scripts/check_cc.py` |
| i18n hygiene | `uv run python scripts/verify_i18n_hygiene.py` |
| Memory prune | `uv run python scripts/memory_prune.py` |
| Metrics report | `uv run python scripts/metrics_report.py` |
| Skill sync | `uv run python scripts/skill_sync.py` |
| Context selector | `uv run python scripts/context_selector.py` |
| Agent system validation | `uv run python scripts/validate_agent_system.py` |
| Workflow graph validation | `uv run python scripts/workflow_graph.py --validate` |

---

## Quick Reference Card

```
Start session:             /start-session
Close session:             /close-session [topic]
Commit with quality:       /create-commit [message]
Tests:                     /run-tests

Safe refactor:             /refactor-code [file]
Full audit:                /audit-plugin
Automatic linting:         /fix-linting

New feature:               /build-feature [desc]
Translations:              /i18n-maintenance [lang]
Plan review:               /ia-critic

Release:                   /release-plugin
Start phase:               /start-phase [name]
Close phase:               /close-phase [name]
Verify standards:          /verify-standards
```
