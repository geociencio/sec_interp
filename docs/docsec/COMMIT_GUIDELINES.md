# Commit Guidelines

This project follows the **Conventional Commits** specification for all version control messages. This ensures a consistent, readable, and machine-parsable history.

## Language Rule
> [!IMPORTANT]
> All commit messages MUST be written in **English**.

## Format
The commit message should be structured as follows:

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- **feat**: A new feature for the user (not a new feature for the build script).
- **fix**: A bug fix for the user.
- **refactor**: A code change that neither fixes a bug nor adds a feature.
- **docs**: Documentation only changes.
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc).
- **test**: Adding missing tests or correcting existing tests.
- **perf**: A code change that improves performance.
- **chore**: Changes to the build process or auxiliary tools and libraries such as documentation generation.
- **build**: Changes that affect the build system or external dependencies.
- **ci**: Changes to CI configuration files and scripts.

### Examples

#### Feature
```text
feat(ui): add multi-point measurement tool to profile preview
```

#### Bug Fix
```text
fix(drillhole): correct azimuth calculation for vertical holes
```

#### Refactoring
```text
refactor(core): modularize geometry intersection logic
```

## Rules
1. **Lowercase summary**: The description should start with a lowercase letter.
2. **Imperative mood**: Use the imperative, present tense ("add" not "added" or "adds").
3. **No period**: Do not end the description with a period.
4. **Length**: Keep the first line under 50 characters if possible.
5. **Detailed body**: Use the body to explain "what" and "why" if the change is complex.

## Integration with Tools
- **Ruff**: Formatting and linting issues found by Ruff should be committed as `style` or `refactor` depending on context.
- **QA**: Quality improvements suggested by `qgis-analyzer` should be committed as `refactor`.
