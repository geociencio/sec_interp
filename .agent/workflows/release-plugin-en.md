---
description: Unified Release Workflow (QGIS Release Flow) based on IA Guide
---

Follow this 5-phase workflow to perform an official release of the SecInterp plugin.

### Phase 1: Quality & Readiness
1. **Analyze Quality**: Run `uv run qgis-analyzer . -o analysis_results`.
2. **Update Badges**: Update `Code Quality` and `QGIS Compliance` in `README.md` based on results.

### Phase 2: Versioning & Documentation
1. **Sync Version**:
   - Update `version` and `changelog` in `metadata.txt`.
   - Update `version` in `pyproject.toml`.
   - Update the version badge in `README.md`.
2. **Technical Changelog**: Move `[Unreleased]` to the new version in `docs/CHANGELOG.md`.
3. **Release Notes**:
   ```bash
   sed -e "s/{version}/X.Y.Z/g" -e "s/{date}/$(date +%F)/g" .github/release_template.md > /tmp/release_notes.md
   ```

### Phase 3: Verification
1. **Linting**: `uv run ruff check --fix . && uv run ruff format .`
2. **Tests**: `PYTHONPATH=.. uv run python3 -m unittest discover tests` (319+ tests).

### Phase 4: Git & Tagging
1. **Preparation Commit**:
   `git add metadata.txt pyproject.toml docs/CHANGELOG.md README.md docs/source/MAINTENANCE_LOG.md`
   `git commit -m "chore(release): prepare vX.Y.Z"`
2. **Tag**: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
3. **Push**: `git push origin main && git push origin vX.Y.Z`

### Phase 5: Build & Distribution
1. **Build ZIP**: `make package VERSION=main` (Verify in `dist/`).
2. **GitHub Release**:
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z" --notes-file /tmp/release_notes.md dist/*.zip dist/*.sha256 --draft
   ```
3. **QGIS Portal**: Upload the ZIP to [plugins.qgis.org](https://plugins.qgis.org/).
