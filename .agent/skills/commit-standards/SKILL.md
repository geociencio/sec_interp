---
name: commit-standards
description: Standards for creating clean and conventional commits with quality validation.
trigger: when creating commits, writing commit messages, or using the /create-commit workflow.
---

# Commit Standards

Standardizes the Git history ensuring each change is traceable, readable, and meets quality standards before being integrated.

## When to use this skill
- When writing commit messages for changes in code or documentation.
- Before performing a `git commit` to ensure quality steps have been met.
- When using the `/create-commit` workflow.

## Degree of Freedom
- **Strict**: Conventional Commits format and language rules (EN for the message) must be followed strictly.

## Workflow
1. **Pre-Validation**: Run linters (`ruff`, `black`) and metric validation (`ai-ctx analyze`).
2. **Testing**: Confirm that tests pass (`make docker-test`).
3. **Formatting**: Write the message following the Conventional Commits specification.
4. **Review**: Verify that the message uses imperative mood and a lowercase description.

## Instructions and Rules

### Language Rule
> [!IMPORTANT]
> All commit messages MUST be written in **English**.

### Conventional Commits Format
```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Commit Types
| Type | Usage | Example |
|:-----|:------|:--------|
| `feat` | New functionality | `feat(ui): add legend visibility toggle` |
| `fix` | Bug fix | `fix(drillhole): correct azimuth calculation` |
| `refactor` | Code change (neither fix nor feat) | `refactor(core): reduce complexity in service` |
| `docs` | Documentation only | `docs(api): update docstrings` |
| `style` | Formatting, whitespace | `style: apply black formatting` |
| `test` | Add/fix tests | `test(integration): add coverage` |
| `chore` | Maintenance tasks | `chore: update uv dependencies` |

## Quality Checklist
- [ ] Is the message in English and imperative?
- [ ] Have `ruff` and `black` been executed?
- [ ] Do tests pass successfully?
- [ ] Has the quality score not decreased critically?
