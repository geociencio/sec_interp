# Workflow Index — CodeWhale Runtime

> Maps each `.agent/workflows/*.md` to concrete CodeWhale actions.
> For humans: "I want to run X, what do I tell the agent?"
> For agents: "User said /X, what do I actually do?"

---

## Daily Development

### `/start-session`
**Tell the agent**: "Ejecuta /start-session"
**What happens**:
```
uv run python scripts/sync_metrics.py
uv run ai-ctx analyze --path .
cat .agent/next_steps.md
cat .agent/task.md
uv sync
```
**Expected output**: Métricas actualizadas, tareas activas visibles, dependencias OK.

### `/close-session`
**Tell the agent**: "Ejecuta /close-session con topic [nombre]"
**What happens**:
```
uv run python scripts/sync_metrics.py
# Update AGENT_LESSONS.md with 3 lessons
uv run python scripts/memory_prune.py
uv run python scripts/metrics_report.py
# Update next_steps.md
git add . && git commit -m "chore(docs): close session [topic]"
```

### `/create-commit`
**Tell the agent**: "Ejecuta /create-commit con mensaje [msg]"
**What happens**:
```
uv run ruff check --fix . && uv run ruff format .
uv run python scripts/check_cc.py
git add . && git commit -m "[msg]"
```

### `/run-tests`
**Tell the agent**: "Ejecuta /run-tests"
**What happens**: `make docker-test` (completo) o `uv run python -m unittest discover tests -q` (local parcial)

---

## Refactoring & Quality

### `/refactor-code`
**Tell the agent**: "Ejecuta /refactor-code en [archivo/modulo]"
**What happens**: Lee coding-standards, aplica cambios, valida CC, ejecuta ruff.

### `/audit-plugin`
**Tell the agent**: "Ejecuta /audit-plugin"
**What happens**: `uv run qgis-analyzer analyze .` → revisa `analysis_results/`

### `/fix-linting`
**Tell the agent**: "Ejecuta /fix-linting"
**What happens**: `uv run ruff check --fix . && uv run ruff format .`

---

## Features & i18n

### `/build-feature`
**Tell the agent**: "Ejecuta /build-feature [descripcion]"
**What happens**: Lee geological-logic skill → implementa → /ia-critic review → /create-commit

### `/i18n-maintenance`
**Tell the agent**: "Ejecuta /i18n-maintenance [idioma]"
**What happens**: Lee i18n-standards skill → edita JSON/TS → `verify_i18n_hygiene.py`

### `/ia-critic`
**Tell the agent**: "Ejecuta /ia-critic sobre [plan]"
**What happens**: Lee AGENT_LESSONS.md → contrasta contra core/gui AGENTS.md → emite veredicto

---

## Release & Planning

### `/release-plugin`
**Tell the agent**: "Ejecuta /release-plugin"
**What happens**: Lee release-management skill → `make zip` → `unzip -l` verificación

### `/start-phase`
**Tell the agent**: "Ejecuta /start-phase [nombre]"
**What happens**: Lee next_steps.md → crea plan → /ia-critic → inicia implementación

### `/close-phase`
**Tell the agent**: "Ejecuta /close-phase [nombre]"
**What happens**: Crea `docs/maintenance/phase_closure_[nombre].md` → actualiza DEVELOPMENT_LOG.md → sync_metrics

### `/verify-standards`
**Tell the agent**: "Ejecuta /verify-standards"
**What happens**:
```
uv run python scripts/check_cc.py
uv run python scripts/verify_i18n_hygiene.py
uv run python scripts/skill_sync.py
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

---

## Quick Reference Card

```
Inicio de sesión:         /start-session
Cierre de sesión:         /close-session [topic]
Commit con calidad:       /create-commit [mensaje]
Tests:                    /run-tests

Refactor seguro:          /refactor-code [archivo]
Auditoría completa:       /audit-plugin
Linting automático:       /fix-linting

Nueva feature:            /build-feature [desc]
Traducciones:             /i18n-maintenance [lang]
Revisión de plan:         /ia-critic

Release:                  /release-plugin
Inicio de fase:           /start-phase [nombre]
Cierre de fase:           /close-phase [nombre]
Verificar estándares:     /verify-standards
```
