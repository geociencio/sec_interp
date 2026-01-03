---
description: Unified Release Workflow for SecInterp (Quality + Automation)
---

# Release Workflow for SecInterp

This document is the master guide for performing a project release. It combines rigorous Quality Assurance steps with automated CLI tools (`uv`, `make`, `gh`) to ensure a robust and efficient process.

## Phase 1: Quality & Readiness
Before touching version numbers, validate the project state.

1. **Run QGIS Plugin Analyzer**:
   // turbo
   `uv run qgis-analyzer . -o analysis_results`
   > [!NOTE]
   > Scores are the primary indicator of release readiness. Target 100/100 in QGIS Compliance.

2. **Update Quality Badges**:
   - Check `analysis_results/PROJECT_SUMMARY.md`.
   - Update **Code Quality** and **QGIS Compliance** badges in `README.md`.

## Phase 2: Versioning & Documentation
1. **Determine Version**:
   - Check `metadata.txt`, `pyproject.toml` and `docs/source/MAINTENANCE_LOG.md`.
   - Decide next SemVer (Major/Minor/Patch).

2. **Bump Version (Synchronized)**:
   - **metadata.txt**: Update `version` and the top entry in `changelog`.
   - **pyproject.toml**: Update `version = "X.Y.Z"`.
   - **README.md**: Update the Version badge.

3. **Update docs/CHANGELOG.md**:
   - Move `[Unreleased]` content to `[X.Y.Z] - YYYY-MM-DD`.
   - Ensure specific sections (`Major Features`, `Stability`) are correct.

4. **Generate Release Notes**:
   ```bash
   VERSION=2.5.0
   DATE=$(date +%F)
   sed -e "s/{version}/$VERSION/g" -e "s/{date}/$DATE/g" .github/release_template.md > /tmp/release_notes.md
   ```
   > **Review**: Check `/tmp/release_notes.md` and fill in any SecInterp-specific highlights.

## Phase 3: Verification
Ensure the codebase is clean and functional before tagging.

1. **Run Linting & Formatting**:
   // turbo
   `uv run ruff check --fix . && uv run ruff format .`
   - Ensure all automated fixes are applied.

2. **Run Tests**:
   // turbo
   `PYTHONPATH=.. uv run python3 -m unittest discover tests`
   - **Requirement**: 100% Pass Rate (319+ tests).

## Phase 4: Git Operations
1. **Commit Changes**:
   ```bash
   git add metadata.txt pyproject.toml docs/CHANGELOG.md README.md docs/source/MAINTENANCE_LOG.md
   git commit -m "chore(release): prepare v$VERSION"
   ```

2. **Create Tag**:
   ```bash
   git tag -a "v$VERSION" -m "Release v$VERSION"
   ```

3. **Push to Origin**:
   ```bash
   git push origin main
   git push origin "v$VERSION"
   ```

## Installation / Update Instructions
--------------------------------------------
- Installation from QGIS Repository:
  1. Search for `SecInterp` in Plugins Manager.
  2. Click Install.
- Installation from ZIP:
  1. Download `sec_interp.{version}.zip` from GitHub.
  2. In QGIS: Plugins > Manage and Install Plugins > Install from ZIP.

## Phase 5: Build & Distribution
1. **Build Artifacts (ZIP)**:
   // turbo
   `make package VERSION=main`
   - Verify output: `dist/sec_interp.X.Y.Z.zip`.

2. **Create GitHub Release**:
   ```bash
   # Build artifacts (SecInterp ZIP)
   make package VERSION=main

   # Create release using GitHub CLI
   gh release create v{version} --title "v{version}" --notes-file /tmp/release_notes.md dist/*.zip dist/*.sha256 --draft
   ```

3. **Publish to QGIS Repository**:
   - Log in to [plugins.qgis.org](https://plugins.qgis.org/).
   - Upload the generated ZIP.

---

## ✅ Quick Checklist
- [ ] Quality Analysis run & Badges updated.
- [ ] Version bumped in `metadata.txt` and `pyproject.toml`.
- [ ] `docs/CHANGELOG.md` finalized.
- [ ] Tests and Linter passed.
- [ ] Git Tag created and pushed.
- [ ] Build created via `make package`.
- [ ] GitHub Draft Release created with ZIP.
- [ ] Uploaded to QGIS Plugin Repository.
