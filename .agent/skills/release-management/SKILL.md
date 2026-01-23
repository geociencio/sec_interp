---
name: release-management
description: Standards for QGIS plugin release process with quality validation
trigger: when preparing releases, updating versions, or using /release-plugin workflow
scope: root
---

# Release Management Skill

## Overview

This skill centralizes the complete release process for the SecInterp QGIS plugin, ensuring quality, consistency, and compliance with QGIS Plugin Repository standards.

## Release Process (5 Phases)

### Phase 1: Quality & Preparation

#### 1.1 Quality Analysis
```bash
uv run qgis-analyzer analyze . -o analysis_results
```

**Validation Checklist**:
- [ ] Overall Plugin Score > 25/100
- [ ] No critical violations (CC > 20)
- [ ] All public functions have docstrings
- [ ] No deprecated PyQt5 imports
- [ ] No QVariant legacy usage

#### 1.2 Update Quality Badges
Update `README.md` badges with current metrics:
- Code Quality badge
- QGIS Compliance badge
- Test coverage badge

---

### Phase 2: Versioning & Documentation

#### 2.1 Version Synchronization

**Files to update** (use semantic versioning):
1. **`metadata.txt`**:
   ```ini
   version=X.Y.Z
   changelog=
       X.Y.Z (YYYY-MM-DD)
       * Category: Description
         - Detail 1
         - Detail 2
   ```

2. **`pyproject.toml`**:
   ```toml
   version = "X.Y.Z"
   ```

3. **`README.md`**:
   ```markdown
   ![Version](https://img.shields.io/badge/version-X.Y.Z-blue)
   ```

**Semantic Versioning Rules**:
- **MAJOR (X)**: Breaking changes, incompatible API changes
- **MINOR (Y)**: New features, backward-compatible
- **PATCH (Z)**: Bug fixes, backward-compatible

#### 2.2 Changelog Update

Move `[Unreleased]` section to new version in `docs/CHANGELOG.md`:
```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature descriptions

### Changed
- Modified functionality

### Fixed
- Bug fixes

### Deprecated
- Features to be removed
```

#### 2.3 Release Notes Generation

Create release notes in `docs/releases/RELEASE_NOTES_vX.Y.Z.md`:

```markdown
# Release vX.Y.Z - [Title]

Short Summary
-------------
[1-2 sentence overview]

Highlights
----------
- **Category**: Brief description
- **Category**: Brief description

Notable Changes (Detailed)
----------------------------
- **feat**: Feature description
- **refactor**: Refactoring description
- **fix**: Bug fix description

Security Fixes
-------------------------
- [List security fixes or "N/A"]

Breaking Changes
----------------------------------------------------
- [List breaking changes or "N/A"]

Installation / Update Instructions
--------------------------------------------
[Standard installation instructions]

Published Artifacts
---------------------
- Plugin ZIP: `sec_interp.X.Y.Z.zip`
- Checksum: `sec_interp.X.Y.Z.zip.sha256`

Verifications Performed (CI)
------------------------------
- [x] Tests passed (361 tests)
- [x] Linter passed
- [x] Manual verification in QGIS
```

---

### Phase 3: Verification

#### 3.1 Code Quality
```bash
# Linting & Formatting
uv run ruff check --fix .
uv run ruff format .
uv run black .
```

#### 3.2 Tests
```bash
# Unit tests
PYTHONPATH=.. uv run python3 -m unittest discover tests

# Docker tests (full suite)
make docker-test
```

**Expected**: 361+ tests passing, 0 failures

#### 3.3 AI Context Update
```bash
uv run ai-ctx analyze --path .
```

Verify metrics in `project_brain.md`:
- Code Maintainability Score: 100/100
- No new architectural violations

---

### Phase 4: Git & Tagging

#### 4.1 Commit Preparation

**Use skill `commit-standards` for message**:
```bash
git add metadata.txt pyproject.toml docs/CHANGELOG.md README.md docs/releases/RELEASE_NOTES_vX.Y.Z.md
git commit -m "chore(release): prepare vX.Y.Z"
```

#### 4.2 Create Tag
```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z - [Title]"
```

**Tag naming**: Always prefix with `v` (e.g., `v2.7.0`)

#### 4.3 Push to Remote
```bash
git push origin main
git push origin vX.Y.Z
```

---

### Phase 5: Packaging & Distribution

#### 5.1 Build Plugin ZIP
```bash
make package VERSION=main
```

**Verify artifacts** in `dist/`:
- `sec_interp.X.Y.Z.zip`
- `sec_interp.X.Y.Z.zip.sha256`

**ZIP Contents Validation**:
- [ ] `metadata.txt` has correct version
- [ ] No `__pycache__` directories
- [ ] No `.pyc` files
- [ ] No test files
- [ ] No development scripts

#### 5.2 GitHub Release (Draft)
```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z - [Title]" \
  --notes-file docs/releases/RELEASE_NOTES_vX.Y.Z.md \
  --draft \
  dist/*.zip dist/*.sha256
```

**Review draft** at: `https://github.com/geociencio/sec_interp/releases`

#### 5.3 QGIS Plugin Repository

1. Login to [plugins.qgis.org](https://plugins.qgis.org/)
2. Navigate to "My Plugins" → "Sec Interp"
3. Click "Upload new version"
4. Upload `sec_interp.X.Y.Z.zip`
5. Verify metadata is parsed correctly
6. Click "Publish"

**Post-publish validation**:
- [ ] Plugin appears in QGIS Plugin Manager
- [ ] Version number is correct
- [ ] Changelog is visible
- [ ] Download link works

---

## Release Checklist (Complete)

### Pre-Release
- [ ] All tests passing (361+)
- [ ] Quality score > 25/100
- [ ] No critical violations
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Release notes created

### Versioning
- [ ] `metadata.txt` version updated
- [ ] `pyproject.toml` version updated
- [ ] `README.md` badge updated
- [ ] Version follows semver

### Verification
- [ ] Linting passed
- [ ] Formatting applied
- [ ] AI context updated
- [ ] Manual testing in QGIS

### Git
- [ ] Commit created with proper message
- [ ] Tag created (vX.Y.Z)
- [ ] Pushed to remote

### Distribution
- [ ] ZIP built successfully
- [ ] SHA256 checksum generated
- [ ] GitHub draft release created
- [ ] QGIS Plugin Repository updated

---

## Common Issues & Solutions

### Issue: ZIP contains test files
**Solution**: Update `.gitattributes` to exclude tests:
```
tests/ export-ignore
```

### Issue: Version mismatch between files
**Solution**: Use search & replace:
```bash
grep -r "2.7.0" metadata.txt pyproject.toml README.md
```

### Issue: QGIS Plugin Repository rejects ZIP
**Solution**: Validate `metadata.txt` format:
- Check all mandatory fields are present
- Verify `qgisMinimumVersion` is valid
- Ensure no syntax errors in changelog

### Issue: Tests fail before release
**Solution**: Run Docker tests to isolate environment:
```bash
make docker-test
```

---

## Integration with Other Skills

- **commit-standards**: Use for release commit messages
- **qa-docker**: Use for pre-release testing
- **qgis-core**: Reference for QGIS compliance validation

---

## References

- QGIS Plugin Repository: https://plugins.qgis.org/
- Semantic Versioning: https://semver.org/
- Plugin Metadata Spec: https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/plugins/plugins.html#plugin-metadata
