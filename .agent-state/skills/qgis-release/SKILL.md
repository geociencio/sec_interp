---
name: qgis-release
description: QGIS plugin repository validation and submission. Use before uploading a ZIP to plugins.qgis.org or when preparing a release.
---

# Skill: QGIS Plugin Repository Release

Authoritative references:

- <https://plugins.qgis.org/docs/publish>
- <https://plugins.qgis.org/docs/approval>
- <https://plugins.qgis.org/docs/security-scanning>
- <https://plugins.qgis.org/docs/security-scanning/config-files>
- <https://plugins.qgis.org/docs/migrate-qgis4>
- <https://docs.qgis.org/3.40/en/docs/pyqgis_developer_cookbook/plugins/plugins.html>
- Project audit: `docs/research/qgis_plugin_repository_requirements.md`
- Upstream split: `docs/research/upstream_gate_integration.md`

## Hard requirements (a violation blocks or rejects the upload)

- `metadata.txt` with `name`, `qgisMinimumVersion`, `description`, `about`,
  `version`, `author`, `email`, **`repository`**.
- `LICENSE` at the plugin root, **no extension** (`LICENSE`, not `LICENSE.txt`).
- One plugin folder at the ZIP root (ASCII letters/digits/`_`/`-`, no leading digit)
  containing `metadata.txt`, `__init__.py` (with `classFactory`) and `LICENSE`.
- Numeric, unique `X.Y.Z` version; the portal orders versions by string comparison.
- ZIP ≤ **25 MB**; no binaries; no development files.
- Bandit and detect-secrets findings at CRITICAL level block the version.
- QGIS 4 listing: `qgisMaximumVersion` ≥ 4.0 (SecInterp uses `4.99`).
  `supportsQt6=True` is deprecated.

## Security rules

| Tool | Severity | Blocks? |
| :--- | :--- | :---: |
| Bandit | CRITICAL | **Yes** |
| detect-secrets | CRITICAL | **Yes** |
| Flake8 | INFO | No |
| File analysis (permissions, suspicious files) | WARNING | No |

Config files are recognized only at the ZIP root: `.bandit`, `.secrets.baseline`,
`.flake8`. Their presence yields `Validated (configured)`; they suppress findings,
they do not lower the bar. Do not bundle them unless a real false positive requires it.

## How the project gates map to the tools

| Layer | Tool / command | Covers |
| :--- | :--- | :--- |
| Static quality | `qgis-analyzer analyze . --max-cc 10` | CC, docstrings, i18n, architecture, module size, analyzer security rules |
| Metadata/structure | `make qgis-validate` (`qgis-manage validate --strict --repo`) | required metadata, slug, structure, LICENSE, binaries, `about`/`repository` |
| Source packaging | `qgis-manage package --repo-check` (inside `make zip`) | same metadata/compliance checks before building the ZIP |
| Style | `make flake8` | portal-compatible flake8 on the packaged plugin scope |
| Security (portal) | `make security-scan` (`scripts/security_scan.py`) | Bandit + detect-secrets (CRITICAL), flake8 (INFO) |
| Artifact | `make portal-check` | ZIP root, embedded metadata, LICENSE, ≤25 MB, binaries/dev files, version, permissions, icon |
| QGIS 4 | `qgisMaximumVersion` ≥ 4.0 + Qt6 checker | QGIS 4 Ready listing and Qt 6 enum/import issues |

`qgis-manage` and `qgis-analyzer` **do not** check the final ZIP permissions, size,
icon, README or flake8, and `qgis-manage security` wraps the analyzer's own security
rules rather than the portal's Bandit/detect-secrets pair. That is why the project
keeps `make flake8` and `make portal-check` as separate gates.

## Pre-upload workflow

```bash
make pre-release      # ruff, flake8, mypy, analyzer, i18n, Qt6, security, Docker
make zip              # docs + compile + package --repo-check + portal-check
make portal-check     # explicit re-run; validates the built ZIP
```

`make portal-check` must pass before uploading. It checks the ZIP root folder,
required metadata, LICENSE, size, prohibited binaries/dev files, version and file
permissions; warnings (e.g. restrictive modes, small icon) are reported but do not
block, matching the portal.

## Upload flow

1. Upload at <https://plugins.qgis.org/plugins/sec_interp/>.
2. Status `Validating` → results email → `Validated`/`Validated (configured)` or
   `Blocked`.
3. `Blocked` means a critical Bandit/detect-secrets finding; fix it and upload a **new**
   version — never reuse the version string.
4. Trusted users are auto-approved after validation; otherwise staff review (minutes to
   days).
5. After approval, publish the GitHub release if it is still a draft and update the
   README version badge.

## Common rejection causes

- Broken or irrelevant `homepage`/`tracker`/`repository` links.
- Missing or misnamed `LICENSE`.
- Binaries or dev folders in the ZIP.
- Version not numeric or not unique.
- External dependencies not declared in `about`.
- A plugin that crashes QGIS during the random install/run test.
- Weak `about` (it must describe the plugin, not repeat `description`).
