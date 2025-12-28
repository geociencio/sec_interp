---
description: Process to create a clean release of the QGIS plugin
---

This workflow guides the preparation, packaging, and publishing of a new version.

### 1. Metadata Preparation
// turbo
1. Update `metadata.txt` with the new version and changelog.
2. Update `docs/CHANGELOG.md` with technical details.
3. Run `python analyze_project_optfixed.py` to synchronize metrics.

### 2. Exclusion Configuration
1. Review `.gitattributes` to ensure new development files have `export-ignore`.
   - Must ignore: `.ai-context/`, `.git/`, `tests/`, `Makefile`, `scripts/`, `.pylintrc`, `.flake8`, `.analyzerignore`.

### 3. ZIP Generation (Clean Build)
// turbo
1. Commit all preparation changes: `git commit -am "chore(release): prepare version X.Y.Z"`.
2. Run the package command: `make package VERSION=main`.
3. Rename the file: `mv sec_interp.zip sec_interp_vX.Y.Z.zip`.

### 4. Verification and Tagging
1. Verify ZIP contents: `unzip -l sec_interp_vX.Y.Z.zip`.
2. Create and push the tag:
   ```bash
   git tag vX.Y.Z -m "Release description"
   git push origin main && git push origin vX.Y.Z
   ```

### 5. Repository Publishing
1. Upload to GitHub Releases attaching the ZIP.
2. Upload to [plugins.qgis.org](https://plugins.qgis.org/) for general distribution.
