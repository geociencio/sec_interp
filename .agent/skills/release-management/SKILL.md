---
name: release-management
description: Standards for the QGIS plugin release process with quality validation.
trigger: when preparing releases, updating versions, or using the /release-plugin workflow.
---

# Release Management (Full Version)

Controls the plugin's version lifecycle, ensuring that each delivery meets the standards of the QGIS repository and the project.

## When to use this skill
- When finishing a development phase and preparing a new version.
- When updating `metadata.txt` or `pyproject.toml`.
- When generating release notes or updating the changelog.
- When using the `/release-plugin` workflow.

## Degree of Freedom
- **Strict**: The 5-phase process and quality score requirements are non-negotiable.

## Detailed Workflow

### Phase 1: Quality and Preparation
1. **Quality and Security Analysis**:
   ```bash
   uv run qgis-analyzer analyze . -o analysis_results
   uv run qgis-analyzer security --deep .
   ```
   - Validate: Score > 25, zero High-Severity security issues, no critical violations (CC > 20).
2. **Update Badges**: Reflect metrics in `README.md`.

### Phase 2: Versioning and Documentation

> [!IMPORTANT]
> **FULL CHECKLIST OF DOCUMENTS TO UPDATE** (each file in this order):
>
> | # | File | What to update |
> |:--|:-----|:--------------|
> | 1 | `metadata.txt` | `version` + `changelog` (escape `%%`) |
> | 2 | `pyproject.toml` | `version` |
> | 3 | `README.md` | Badges: `Version`, `Code Quality`, `QGIS Compliance`, `i18n`, "What's New" section |
> | 4 | `docs/CHANGELOG.md` | Move `[Unreleased]` to `[X.Y.Z]` with date |
> | 5 | `docs/docsec/CHANGELOG.md` | Same for Spanish documentation |
> | 6 | `docs/releases/RELEASE_NOTES_vX.Y.Z.md` | Create new file with highlights |
> | 7 | `docs/DEVELOPMENT_LOG.md` | Add version closing entry |
> | 8 | `.agent/QUICK_REFERENCE.md` | Update test count and metrics |

1. **Synchronization**: Update `metadata.txt` (including changelog), `pyproject.toml`, and `README.md`.
2. **Versioning and Registration Standards (CRITICAL)**:
   - **[Semantic Versioning (SemVer)](https://semver.org/spec/v2.0.0.html)**:
     - MAJOR (X): Breaking changes.
     - MINOR (Y): Backward-compatible new features.
     - PATCH (Z): Backward-compatible bug fixes.
   - **[Keep a Changelog](https://keepachangelog.com/en/1.0.0/)**:
     - Keep `docs/CHANGELOG.md` and `docs/docsec/CHANGELOG.md` strictly aligned with this standard.
     - Group changes logically (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`).
3. **Release Notes**: Generate detailed release notes in `docs/releases/RELEASE_NOTES_vX.Y.Z.md`.

### Phase 3: Technical Verification
1. Achieve 535+ passing tests.
2. Run `make docker-test` for an isolated environment.
3. Update `AI_CONTEXT.md` via `uv run ai-ctx analyze`.

### Phase 4: Git and Tagging
1. Release commit: `chore(release): prepare vX.Y.Z`.
2. Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.
3. Push: `git push origin main --tags`.

### Phase 5: Packaging and Distribution
1. Build: `make package VERSION=main`.
2. Validate ZIP in `dist/`: No `__pycache__`, no test files.
3. Upload: Upload to [plugins.qgis.org](https://plugins.qgis.org/) and create a draft on GitHub.

## Instructions and Rules

### Critical Files Detail
- **metadata.txt**: Must contain `version`, `qgisMinimumVersion`, and formatted `changelog`.
- **pyproject.toml**: The `version` field must match exactly.

### Release Notes Template
```markdown
# Release vX.Y.Z - [Title]
Highlights:
- **feat**: ...
- **fix**: ...
Published Artifacts: `sec_interp.X.Y.Z.zip`
```

## Quality Checklist
- [ ] Is the Quality Score above 25/100?
- [ ] Have all version references been updated?
- [ ] Has the ZIP file been verified (no technical garbage)?
- [ ] Have Git Tagging rules been followed?
- [ ] Did the 535+ tests pass successfully?
