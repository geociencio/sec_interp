---
description: Unified Release Workflow (QGIS Release Flow) based on IA Guide
agent: QA Engineer
skills: [release-management, qa-docker, commit-standards, i18n-standards, changelog-generator]
validation: |
  - Verify that 535+ tests pass in Docker
  - Confirm that qgis-analyzer score > 25/100
  - Ensure Zero High-Severity Security Findings (`security --deep`)
  - Validate that versions are synchronized in 3 files
  - Verify that ZIP was generated correctly
---

# Workflow: Release Plugin

Follow this 5-phase workflow to perform an official release of the SecInterp plugin.

### Phase 1: Quality and Preparation

🤖 **Agent Action**: Use **release-management** skill to validate complete pre-release checklist.

1. **Analyze Quality**:
   // turbo
   ```bash
   uv run qgis-analyzer analyze . -o analysis_results
   ```

   🤖 **Agent Action**: Verify that:
   - Overall Plugin Score > 25/100
   - No critical QGIS compliance violations
   - **Note**: Discard i18n false positives in docstrings if `core/` has 100% coverage.

2. **Update Badges**: Update `Code Quality` and `QGIS Compliance` in `README.md` based on results.

### Phase 2: Versioning and Documentation

🤖 **Agent Action**: Use **release-management** skill to synchronize versions automatically.

1. **Synchronize Version (Semantic Versioning)**:
   - Abide by `X.Y.Z` (Major.Minor.Patch).
   - Update `version` and `changelog` explicitly in `metadata.txt`.
     - ⚠️ **CRITICAL**: Escape all `%` as `%%` in the changelog (e.g., `100%%` not `100%`).
   - Update `version` in `pyproject.toml`.
   - Update the version badge in `README.md`.

2. **Update `README.md` (MANDATORY)**:
   🤖 **Agent Action**: Verify and update all badges and version references in `README.md`.
   - `Version` badge: `X.Y.Z`
   - `Code Quality` badge: Update with current `ai-ctx analyze` score.
   - `QGIS Compliance` badge: Update with `qgis-analyzer` result.
   - `i18n Languages` badge: Update if new languages were added.
   - "What's New" section: Summarize the main changes of this version.

   🤖 **Agent Action**: Validate that all 3 versions match exactly (`metadata.txt`, `pyproject.toml`, `README.md`).

3. **Technical Changelog (Keep A Changelog)**: Use **changelog-generator** to move `[Unreleased]` to the new version in `docs/CHANGELOG.md` and sync `docs/docsec/CHANGELOG.md` (Spanish) if applicable, using valid types (`Added`, `Changed`, `Fixed`, etc.).

4. **Release Notes**:
   // turbo
   ```bash
   sed -e "s/{version}/X.Y.Z/g" -e "s/{date}/$(date +%F)/g" .github/release_template.md > /tmp/release_notes.md
   ```

   🤖 **Agent Action**: Generate structured release notes using **changelog-generator** following **release-management** skill template.

### Phase 3: Verification

🤖 **Agent Action**: Use **qa-docker** skill to validate tests and skill **commit-standards** for linting.

1. **Security Scan** (Deep Audit):
   // turbo
   ```bash
   uv run qgis-analyzer security --deep .
   ```

   🤖 **Agent Action**: Review security reports. No HIGH severity findings allowed to proceed.

2. **Linting & Formatting**:
   // turbo
   ```bash
   uv run ruff check --fix . && uv run ruff format . && uv run black .
   ```
   **Note**: Document minor linting issues (like F821/W503 in external reports) for later fix if they don't block functionality.

3. **Tests**:
   // turbo
   ```bash
   make docker-test
   ```
   (535+ tests must pass).

   🤖 **Agent Action**: Alert if any test fails or if there is a coverage regression.

### Phase 4: Git and Tagging

🤖 **Agent Action**: Use **commit-standards** skill for commit message.

1. **Preparation Commit**:
   Ensure `.qgisignore` is updated and optimized.
   ```bash
   git add metadata.txt pyproject.toml docs/CHANGELOG.md docs/docsec/CHANGELOG.md README.md docs/releases/RELEASE_NOTES_vX.Y.Z.md .qgisignore
   git commit -m "chore(release): prepare vX.Y.Z"
   ```

2. **Tag**: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
3. **Push**: `git push origin main && git push origin vX.Y.Z`

### Phase 5: Packaging and Distribution

🤖 **Agent Action**: Use **release-management** skill to validate artifacts and publication process.

1. **Validate `metadata.txt`**:
   // turbo
   ```bash
   uv run qgis-analyzer metadata .
   ```

2. **Validate `pyproject.toml`**:
   // turbo
   ```bash
   uv run qgis-analyzer pyproject .
   ```

3. **Quick Scan (Linting & Security)**:
   // turbo
   ```bash
   uv run qgis-analyzer analyze . --strict
   ```

4. **Build Optimized ZIP**:
   // turbo
   ```bash
   make package VERSION=main
   ```
   (Verify in `dist/`).

   🤖 **Agent Action**:
   - Validate ZIP contents (no logs, no `sample_data`, no caches).
   - **Key Metric**: Package size should be < 500KB (Ideally ~220KB).
   - Check `sha256` checksum.

2. **GitHub Release**:
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z" --notes-file docs/releases/RELEASE_NOTES_vX.Y.Z.md dist/*.zip dist/*.sha256 --draft
   ```

3. **QGIS Portal**: Upload the ZIP to [plugins.qgis.org](https://plugins.qgis.org/).

   🤖 **Agent Action**: Remember to validate post-publication:
   - Plugin appears in QGIS Plugin Manager
   - Version is correct
   - Changelog is visible

## Expected Result
- Official version published on QGIS repository and GitHub.
- Documentation and Git tags synchronized.
- Technically validated plugin with visible metrics.
