# 2. Conventional Commits and English Standardization

Date: 2024-07 (v1.0)

## Status

Accepted

## Context

Collaborative development requires a clear, parseable history. Inconsistent commit messages ("fix bug", "changes", "update") make it impossible to:
- Automatically generate Changelogs.
- Determine semantic version bumps (Major/Minor/Patch).
- Understand the scope of changes without reading the diff.

Additionally, mixing languages (Spanish/English) in code and commits creates friction for international contributors.

## Decision

We enforce **Conventional Commits** and **English-Only** for all version control operations.

### 1. Format
All commits must follow the pattern:
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```
Types:
- `feat`: New feature (minor release).
- `fix`: Bug fix (patch release).
- `docs`: Documentation only.
- `style`: Formatting, missing semi colons, etc.
- `refactor`: Code change that neither fixes a bug nor adds a feature.
- `perf`: A code change that improves performance.
- `test`: Adding missing tests or correcting existing tests.
- `build`: Changes that affect the build system or external dependencies.
- `chore`: Other changes that don't modify src or test files.

### 2. Enforcement
- **Pre-commit Hook**: A git hook validates the message against a regex pattern before allowing the commit.
- **Language**: The description and body MUST be in English.

## Consequences

### Positive
- **Automation**: We can use tools like `semantic-release` or standard changelog generators.
- **Clarity**: The history becomes a readable log of "what" and "why".
- **Discipline**: Forces developers to think about the nature of their change before committing.

### Negative
- **Friction**: New contributors might be blocked by the hook if they don't know the format.

## Compliance
- All PRs must be squashed or rebased to ensure every commit on `main` follows the valid format.
- `docs/docsec/COMMIT_GUIDELINES.md` serves as the reference manual.
