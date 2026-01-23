---
description: Unified Release Workflow (QGIS Release Flow) based on IA Guide
agent: QA Engineer
skills: [release-management, qa-docker, commit-standards]
validation: |
  - Verify that 361 tests pass in Docker
  - Confirm that qgis-analyzer score > 25/100
  - Validate that versions are synchronized in 3 files
  - Verify that ZIP was generated correctly
---

Follow this 5-phase workflow to perform an official release of the SecInterp plugin.

### Phase 1: Quality & Readiness

🤖 **Agent Action**: Use skill **release-management** to validate complete pre-release checklist.

1. **Analyze Quality**: Run `uv run qgis-analyzer . -o analysis_results`.

   🤖 **Agent Action**: Verify that:
   - Overall Plugin Score > 25/100
   - No methods with CC > 20
   - No critical QGIS compliance violations

2. **Update Badges**: Update `Code Quality` and `QGIS Compliance` in `README.md` based on results.

### Phase 2: Versioning & Documentation

🤖 **Agent Action**: Use skill **release-management** to synchronize versions automatically.

1. **Sync Version**:
   - Update `version` and `changelog` in `metadata.txt`.
   - Update `version` in `pyproject.toml`.
   - Update the version badge in `README.md`.

   🤖 **Agent Action**: Validate that all 3 versions match exactly.

2. **Technical Changelog**: Move `[Unreleased]` to the new version in `docs/CHANGELOG.md`. **Format: `[vX.Y.Z] - Title`**.

3. **Release Notes**:
   ```bash
   sed -e "s/{version}/X.Y.Z/g" -e "s/{date}/$(date +%F)/g" .github/release_template.md > /tmp/release_notes.md
   # EDIT manually to add " - Title" to the Header
   ```

   🤖 **Agent Action**: Generate structured release notes following **release-management** skill template.

### Phase 3: Verification

🤖 **Agent Action**: Use skill **qa-docker** to validate tests and skill **commit-standards** for linting.

1. **Linting & Formatting**: `uv run ruff check --fix . && uv run ruff format . && uv run black .`
2. **Tests**: `make docker-test` (361+ tests must pass).

   🤖 **Agent Action**: Alert if any test fails or if there's coverage regression.

### Phase 4: Git & Tagging

🤖 **Agent Action**: Use skill **commit-standards** for commit message.

1. **Preparation Commit**:
   ```bash
   git add metadata.txt pyproject.toml docs/CHANGELOG.md README.md docs/releases/RELEASE_NOTES_vX.Y.Z.md
   git commit -m "chore(release): prepare vX.Y.Z"
   ```

2. **Tag**: `git tag -a vX.Y.Z -m "Release vX.Y.Z - Title"`
3. **Push**: `git push origin main && git push origin vX.Y.Z`

### Phase 5: Build & Distribution

🤖 **Agent Action**: Use skill **release-management** to validate artifacts and publication process.

1. **Build ZIP**: `make package VERSION=main` (Verify in `dist/`).

   🤖 **Agent Action**: Validate ZIP contents:
   - metadata.txt has correct version
   - No __pycache__ or .pyc files
   - No test files

2. **GitHub Release**:
   ```bash
   # Add Title to the release title
   gh release create vX.Y.Z --title "vX.Y.Z - Title" --notes-file docs/releases/RELEASE_NOTES_vX.Y.Z.md dist/*.zip dist/*.sha256 --draft
   ```

3. **QGIS Portal**: Upload the ZIP to [plugins.qgis.org](https://plugins.qgis.org/).

   🤖 **Agent Action**: Remember to validate post-publication:
   - Plugin appears in QGIS Plugin Manager
   - Version is correct
   - Changelog is visible
