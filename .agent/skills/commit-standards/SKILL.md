---
name: commit-standards
description: Standards for creating clean, conventional commits with quality validation
trigger: when creating commits, writing commit messages, or using /crea-commit workflow
scope: root
---

# Commit Standards Skill

## Language Rule
> [!IMPORTANT]
> All commit messages MUST be written in **English**.

## Conventional Commits Format

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Usage | Example |
|:-----|:------|:--------|
| `feat` | New user-facing feature | `feat(ui): add legend visibility toggle` |
| `fix` | Bug fix for the user | `fix(drillhole): correct azimuth calculation for vertical holes` |
| `refactor` | Code change (no bug fix, no feature) | `refactor(core): reduce complexity in GeologyService.prepare_task_input` |
| `docs` | Documentation only | `docs(api): update drillhole service docstrings` |
| `style` | Formatting, whitespace | `style: apply black formatting to core module` |
| `test` | Adding/correcting tests | `test(integration): add 3D projection coverage` |
| `perf` | Performance improvement | `perf(export): optimize polygon rendering` |
| `chore` | Build process, tools | `chore: update uv dependencies` |
| `build` | Build system, dependencies | `build: add sphinx to dev dependencies` |
| `ci` | CI configuration | `ci: add Docker test workflow` |

### Commit Message Rules

1. **Lowercase summary**: Start description with lowercase letter
2. **Imperative mood**: Use present tense ("add" not "added" or "adds")
3. **No period**: Don't end description with a period
4. **Length**: Keep first line under 50 characters if possible
5. **Detailed body**: Explain "what" and "why" for complex changes

## Pre-Commit Quality Checklist

Before committing, validate:

### Code Quality
- [ ] `ruff` passes without errors
- [ ] `black` formatting applied
- [ ] No new linting violations introduced

### Metrics Validation
- [ ] `ai-ctx analyze` executed successfully
- [ ] Complexity didn't increase significantly
- [ ] Docstring coverage didn't decrease

### Testing
- [ ] Relevant tests pass (`make docker-test` for full suite)
- [ ] New features have corresponding tests
- [ ] No test coverage regression

### QGIS Compliance (for plugin code)
- [ ] No new PyQt5 legacy imports
- [ ] No deprecated QVariant usage
- [ ] Follows QGIS plugin standards

## Commit Message Templates

### Feature with Breaking Change
```text
feat(core)!: migrate to QgsTask for async processing

BREAKING CHANGE: GeologyService.process_data() now returns QgsTask instead of direct result.
Update all callers to use task.waitForFinished() or connect to task.taskCompleted signal.
```

### Refactoring for Technical Debt
```text
refactor(gui): reduce complexity in MainDialog.apply_attribute_inheritance

- Extract validation logic to _validate_inputs (CC: 21 → 8)
- Extract data collection to _extract_outcrop_data (CC: 21 → 6)
- Add type hints and docstrings
```

### Bug Fix with Context
```text
fix(export): correct legend rendering in PDF export

Legend was not respecting show_legend setting in PDF exports.
Root cause: PreviewSettings.show_legend not passed to QPainter context.
```

### Documentation Update
```text
docs(architecture): update validation architecture diagram

Reflect 3-level validation implementation from v2.7.0
```

## Integration with Project Tools

### Ruff/Black Issues
- **Style changes**: `style: apply black formatting to <module>`
- **Refactoring**: `refactor(<scope>): fix ruff violations in <module>`

### qgis-analyzer Improvements
- **Complexity reduction**: `refactor(<scope>): reduce complexity in <method>`
- **Docstring additions**: `docs(<scope>): add docstrings to <module>`
- **Type hints**: `refactor(<scope>): add type hints to <module>`

### ai-ctx Quality Improvements
- **Metrics improvement**: `refactor: improve code maintainability score`
- **Architecture fixes**: `refactor: resolve architectural violations in <component>`

## Scope Guidelines

Use scopes to indicate the affected component:

| Scope | Component |
|:------|:----------|
| `core` | Core services (drillhole, geology, validation) |
| `gui` | GUI components (dialogs, widgets) |
| `export` | Export functionality (PNG, PDF, SVG) |
| `ui` | User interface (layouts, styles) |
| `tests` | Test infrastructure |
| `docs` | Documentation |
| `build` | Build system, scripts |

## Examples from SecInterp Project

### Good Commits ✅
```text
feat(export): add SVG export support with custom DPI
refactor(core): extract validation logic from GeologyService
fix(gui): prevent crash when no drillholes selected
docs(api): update sphinx configuration for QGIS mocks
test(integration): add 3D projection validation tests
```

### Bad Commits ❌
```text
Fixed stuff                          # Too vague, no type
feat(core): Added new feature.       # Period at end, past tense
FEAT: BIG CHANGE                     # Uppercase, no scope
refactor: cambios en el servicio     # Spanish (must be English)
```

## Validation Command

Before committing, run:
```bash
# Format code
uv run black .
uv run ruff check --fix .

# Update metrics
uv run ai-ctx analyze --path .

# Verify tests
make docker-test
```

## Reference
- Full guidelines: [COMMIT_GUIDELINES.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/docsec/COMMIT_GUIDELINES.md)
- Conventional Commits spec: https://www.conventionalcommits.org/
