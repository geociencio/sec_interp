---
description: Unified Release Workflow (QGIS Release Flow) based on IA Guide
agent: QA Engineer
skills: [release-management, qa-docker, commit-standards, i18n-standards]
validation: |
  - Verify that 455+ tests pass in Docker
  - Confirm that qgis-analyzer score > 25/100
  - Validate that versions are synchronized in 3 files
  - Verify that ZIP was generated correctly
---

Follow this 5-phase workflow to perform an official release of the SecInterp plugin.

### Phase 1: Quality & Readiness

🤖 **Agent Action**: Use skill **release-management** to validate complete pre-release checklist.

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

### Phase 2: Versioning & Documentation

🤖 **Agent Action**: Use skill **release-management** to synchronize versions automatically.

1. **Sync Version**:
   - Update `version` and `changelog` in `metadata.txt`.
     - ⚠️ **CRÍTICO**: Escape all `%` as `%%` in changelog (e.g., `100%%` not `100%`).
   - Update `version` in `pyproject.toml`.
   - Update the version badge in `README.md`.

   🤖 **Agent Action**: Validate that all 3 versions match exactly.

2. **Technical Changelog**: Move `[Unreleased]` to the new version in `docs/CHANGELOG.md` and sync `docs/docsec/CHANGELOG.md` (Spanish).

3. **Release Notes**:
   // turbo
   ```bash
   sed -e "s/{version}/X.Y.Z/g" -e "s/{date}/$(date +%F)/g" .github/release_template.md > /tmp/release_notes.md
   ```

   🤖 **Agent Action**: Generate structured release notes following **release-management** skill template.

### Phase 3: Verification

🤖 **Agent Action**: Use skill **qa-docker** to validate tests and skill **commit-standards** for linting.

1. **Security Scan** (Deep Audit):
   // turbo
   ```bash
   uv run qgis-analyzer security --deep .
   ```

   🤖 **Agent Action**: Review security reports. No HIGH severity findings allowed.

2. **Linting & Formatting**:
   // turbo
   ```bash
   uv run ruff check --fix . && uv run ruff format . && uv run black .
   ```
   **Note**: Document minor linting issues (like F821/W503 in external reports) for later fix if not blocking.

3. **Tests**:
   // turbo
   ```bash
   make docker-test
   ```
   (455+ tests must pass).

### Phase 4: Git & Tagging

🤖 **Agent Action**: Use skill **commit-standards** for commit message.

1. **Preparation Commit**:
   Ensure `.qgisignore` is updated and optimized.
   ```bash
   git add metadata.txt pyproject.toml docs/CHANGELOG.md docs/docsec/CHANGELOG.md README.md docs/releases/RELEASE_NOTES_vX.Y.Z.md .qgisignore
   git commit -m "chore(release): prepare vX.Y.Z"
   ```

2. **Tag**: `git tag -a vX.Y.Z -m "Release vX.Y.Z - Title"`
3. **Push**: `git push origin main && git push origin vX.Y.Z`

### Phase 5: Build & Distribution

🤖 **Agent Action**: Use skill **release-management** to validate artifacts and publication process.

1. **Build Optimized ZIP**:
   // turbo
   ```bash
   make package VERSION=main
   ```
   (Verify in `dist/`).

   🤖 **Agent Action**: Validate ZIP contents:
   - metadata.txt has correct version
   - No logs, no `sample_data`, no caches.
   - **Key Metric**: Package size should be < 500KB (Ideally ~220KB).
   - Check `sha256` checksum.

2. **GitHub Release**:
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z - Title" --notes-file docs/releases/RELEASE_NOTES_vX.Y.Z.md dist/*.zip dist/*.sha256 --draft
   ```

3. **QGIS Portal**: Upload the ZIP to [plugins.qgis.org](https://plugins.qgis.org/).

   🤖 **Agent Action**: Remember to validate post-publication:
   - Plugin appears in QGIS Plugin Manager
   - Version is correct
   - Changelog is visible
