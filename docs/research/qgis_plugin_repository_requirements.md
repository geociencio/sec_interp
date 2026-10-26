# QGIS Plugin Repository — Requirements Research

> **Date**: 2026-10-25
> **Target**: plugins.qgis.org (QGIS Plugins Website, 2026), QGIS 3.x/4.x
> **Scope**: what the official repository validates, what blocks approval, and how
> SecInterp 3.12.x measures against it.
> **Status**: research/hand-off note (not part of the audited docs set).

---

## 1. Sources

Official documentation consulted:

- Publish a plugin: <https://plugins.qgis.org/docs/publish>
- Approval process: <https://plugins.qgis.org/docs/approval>
- QGIS 4 migration: <https://plugins.qgis.org/docs/migrate-qgis4>
- Security scanning overview: <https://plugins.qgis.org/docs/security-scanning>
- Security tools and severities: <https://plugins.qgis.org/docs/security-scanning/tools>
- Security config files: <https://plugins.qgis.org/docs/security-scanning/config-files>
- Rule reference (205 rules): <https://plugins.qgis.org/docs/security-scanning/rules>
- FAQ (version ordering): <https://plugins.qgis.org/docs/faq>
- PyQGIS Cookbook, *Structuring Python Plugins*: <https://docs.qgis.org/3.40/en/docs/pyqgis_developer_cookbook/plugins/plugins.html>
- PyQGIS Cookbook, *Releasing your plugin*: <https://docs.qgis.org/3.40/en/docs/pyqgis_developer_cookbook/plugins/releasing.html>

---

## 2. Two different gates

1. **Automated validation** on upload: metadata/package structure, required fields,
   LICENSE, unique version, size limit, then Bandit and detect-secrets (blocking) plus
   Flake8 and file analysis (informational).
2. **Human approval** by volunteers: metadata links, documentation, license, random
   install/run tests, cross-platform sanity, no binaries, no duplicate functionality.

A version is downloadable only after it reaches `Validated` (or
`Validated (configured)` when a security config file is bundled). `Blocked` versions
cannot be downloaded or approved.

---

## 3. Mandatory and recommended metadata

From the PyQGIS Cookbook metadata table:

| Field | Required | Notes | SecInterp 3.12.0 |
| :--- | :---: | :--- | :--- |
| `name` | ✅ | Short name; unique/recognizable | `Sec Interp` |
| `qgisMinimumVersion` | ✅ | `X.Y` | `3.28` |
| `qgisMaximumVersion` | — | `X.Y`; auto `major.99` if empty | `4.99` (QGIS 4 Ready) |
| `description` | ✅ | One line, no HTML | ✅ |
| `about` | ✅ | Detailed, no HTML | ⚠️ short (see §9) |
| `version` | ✅ | Numeric `X.Y.Z`; unique per upload | `3.12.0` |
| `author` | ✅ | | ✅ |
| `email` | ✅ | | ✅ |
| `repository` | ✅ | Public source URL, not a ZIP | GitHub ✅ |
| `homepage` | — (approval expects) | Usage/README page | docs site ✅ |
| `tracker` | — (approval expects) | Issue tracker | GitHub issues ✅ |
| `changelog` | — (updates) | Multiline, no HTML | ✅ 3.12.0 entry |
| `experimental` | — | `True`/`False`, per version | `False` |
| `deprecated` | — | `True`/`False`, whole plugin | `False` |
| `tags` | — | Comma-separated, English | ✅ |
| `category` | — | Raster, Vector, Database, Mesh, Web | `Vector` |
| `icon` | — | PNG/JPEG relative to package root | `icon.png` (⚠️ 23×24) |
| `server` | — | `True`/`False` | `False` |
| `hasProcessingProvider` | — | `True`/`False` | `False` |
| `plugin_dependencies` | — | Names from other plugins' `name` | not needed |

Additional validation rules (Cookbook, *Releasing*):

- The ZIP's top-level folder must be ASCII letters/digits, `_` or `-`, and must not
  start with a digit (`sec_interp` is valid).
- `metadata.txt` must exist and contain every required field.
- `version` must be unique.
- `LICENSE` must exist with **no extension** (not `LICENSE.txt`).
- The ZIP must contain a single plugin folder with `metadata.txt`, `__init__.py` and
  `LICENSE` inside it.
- Package size **≤ 25 MB** (official publish page).
- No binaries; compiled translations (`*.qm`) are normal in QGIS packages.
- Version ordering is **string comparison**: use strict numeric `X.Y.Z` (FAQ).

---

## 4. Package structure

- One plugin folder at the ZIP root; QGIS unzips it into the plugins directory.
- Required: `metadata.txt`, `__init__.py` (with `classFactory`), `LICENSE`.
- Recommended: `README`, icon, translations, sample data, minimal documentation.
- Do not ship development files: `.git`, `tests`, `scripts`, `docs`, build caches,
  `__pycache__`, `.pyc`, CI config, virtualenvs.
- QGIS docs recommend **not committing generated files** (`ui_*.py`,
  `resources_rc.py`, generated help) to the source repository; compiled resources in
  the ZIP are normal for plugins that need them.

---

## 5. Security scanning (plugins.qgis.org)

| Tool | Severity | Blocking? | Scope |
| :--- | :--- | :---: | :--- |
| Bandit | CRITICAL | **Yes** | Python security issues (shell injection, eval/exec, pickle, hardcoded passwords, weak crypto, …) |
| detect-secrets | CRITICAL | **Yes** | Credentials, API keys, private keys, connection strings, high-entropy strings |
| Flake8 | INFO | No | PEP 8, undefined names, unused imports, syntax |
| File analysis | WARNING | No | Suspicious files, executable/odd permissions, hidden files |

- A CRITICAL finding blocks the version until a new clean ZIP is uploaded.
- Config files are supported **only at the ZIP top level**:
  `.bandit`, `.secrets.baseline`, `.flake8`. Their presence yields the status
  `Validated (configured)`; they suppress findings, they do not lower the bar.
- Scans run asynchronously; upload → `Validating` → results email → `Validated`/
  `Blocked` → approval.

---

## 6. QGIS 4 readiness

- `qgisMaximumVersion=4.99` (or ≥ 4.0) lists the plugin in
  [QGIS 4 Ready Plugins](https://plugins.qgis.org/plugins/new_qgis_ready/).
  SecInterp already has `3.28` + `4.99`, so it is listed.
- The temporary `supportsQt6=True` flag is **deprecated**; the version range is the
  source of truth.
- Code must work under Qt 6: use `qgis.PyQt`, avoid direct PyQt5/PySide imports, use
  scoped enums, and keep `QAction` imports compatible (`qgis.PyQt.QtWidgets` maps to
  QtGui under QGIS 4).
- The repository's Qt6 checker is informational; SecInterp reports **0 findings**.

---

## 7. Approval and trust

- New uploads by users without `plugins.can_approve` are unapproved until a staff
  member reviews them; trusted users (previous approved plugins) are auto-approved
  after validation.
- Reviewers may install/run the plugin at random and expect it to work on Linux and
  Windows; cross-platform claims should be real.
- Rejection causes are mostly metadata (broken/irrelevant homepage, tracker or
  repository links), missing license, binaries, duplicate functionality, or a plugin
  that crashes QGIS.
- Existing plugins keep their identifier/folder; renaming is discouraged and can make
  QGIS treat the plugin as uninstalled.

---

## 8. SecInterp audit (2026-10-25, ZIP `sec_interp.3.12.0.zip`)

| Check | Result |
| :--- | :--- |
| Metadata required fields | ✅ all present |
| `repository`, `homepage`, `tracker` | ✅ valid HTTPS, public |
| `LICENSE` exact name | ✅ (`LICENSE`, no extension; GPL-2.0-or-later) |
| Folder/slug | ✅ `sec_interp` (ASCII, no leading digit) |
| Version | ✅ `3.12.0`, numeric, new |
| ZIP top-level folder | ✅ `sec_interp/` |
| ZIP size | ✅ 2.4 MB (limit 25 MB) |
| Prohibited binaries | ✅ none (`.qm` translations only) |
| Hidden/cache/build files | ✅ none |
| `README` in ZIP | ✅ yes |
| Bandit (default config, extracted ZIP) | ✅ 0 findings |
| detect-secrets (no baseline) | ✅ 0 findings |
| Flake8 (plugin scope, `.flake8`) | ⚠️ 3.12.0 ZIP had F811/E402; fixed in `main` (target 3.12.1) |
| Qt6 checker | ✅ 0 findings |
| QGIS 4 Ready | ✅ `qgisMaximumVersion=4.99` |
| Direct PyQt5/PySide imports | ✅ none |
| `qgis-manage validate --strict --repo` | ✅ pass |
| `qgis-manage validate --zip` (0.14+) | ✅ pass (warnings: permissions/icon in 3.12.0; fixed in new builds) |

---

## 9. Gaps and recommendations

### Blocking

None found. Bandit and detect-secrets are clean, the metadata and LICENSE are valid,
and the package size is well below the limit.

### Recommended before the next portal upload (3.12.1)

1. **Normalize ZIP permissions**: the 3.12.0 ZIP contains 27 files with `0600` and 307
   with `0640` (plus 8 with `0644`). They work for the installing user, but the
   portal's file analysis may flag restrictive/odd modes. Run
   `chmod -R u+rwX,go+rX` before packaging (or add a packaging step) so entries are
   `0644`/`0755` only.
2. **Use a proper icon**: `icon.png` is 23×24 px. QGIS recommends a clear icon; a
   64×64 or 128×128 PNG is safer for the plugin list and Plugin Manager.
3. **Expand `about`**: it is currently a single sentence, almost identical to
   `description`. Reviewers expect a detailed, no-HTML description of what the plugin
   does and any caveats (use the same text style as the README).
4. **Keep the README license consistent**: it now says GPL-2.0-or-later, matching
   `LICENSE` and `pyproject.toml` (it previously said GPLv3).

### Optional / long-term

- **Generated files tracked**: `resources/resources.py` is generated and tracked. QGIS
  recommends not storing generated files in the repository; keep the build step that
  regenerates it for packaging, or document why it is committed.
- **`.ts` files**: QGIS recommends distributing translation sources with the plugin;
  the ZIP currently ships only `.qm` (accepted, but `.ts` would help translators).
- **Flake8 config in the ZIP**: `.flake8` is excluded. Flake8 is informational, so
  this is only worth doing if the portal report becomes noisy; shipping it changes the
  status to `Validated (configured)`.
- **Cross-platform**: CI runs Linux/Docker. A Windows smoke test before upload reduces
  approval risk.

---

## 10. Portal upload checklist

1. Bump `metadata.txt` + `pyproject.toml` (e.g. `3.12.1`), update the metadata
   `changelog`, `docs/CHANGELOG.md` and release notes.
2. `make pre-release` (includes `make flake8`, mypy, analyzer, i18n, Qt6, security,
   Docker) and `make docs-check`.
3. `make zip` (runs `qgis-manage package --repo-check` and `portal-check`
   automatically) or `make portal-check` for an existing ZIP; verify:
   - `unzip -l dist/sec_interp.X.Y.Z.zip` has a single `sec_interp/` root;
   - size ≤ 25 MB; no `.agent`, `tests`, `scripts`, `docs`, caches or binaries;
   - `metadata.txt` version and `LICENSE` are present;
   - file modes are `0644`/`0755` (normalize before packaging).
4. Upload at <https://plugins.qgis.org/plugins/sec_interp/> and wait for the
   validation email (`Validating` → `Validated`/`Blocked`).
5. If `Blocked`: fix the critical Bandit/detect-secrets finding and upload a new
   version; never reuse the same version string.
6. After approval, publish the GitHub release (if still draft) and update the README
   badge.

---

## 11. Notes on local tooling

- `qgis-manage validate --strict --repo` checks metadata, structure, LICENSE and
  prohibited binaries. Since 0.14, `qgis-manage validate --zip` (and
  `package --repo-check` after building) covers the artifact: root, size, modes,
  icon, README, embedded metadata. It still does **not** run Bandit/detect-secrets;
  use `make pre-release` (flake8 + `make security-scan`) for that.
- `make security-scan` uses `qgis-manage security --portal` (0.15+), which runs
  native + Bandit + detect-secrets + Flake8 with `--fail-on critical`; it excludes
  non-packaged dirs (`tests`, `docs`, `scripts`, `tools`, agent state). The portal
  ignores project configs unless they are packaged; our default-config scans were
  clean.
- `make flake8` is intentionally stricter than the portal (blocking) to keep the
  portal's INFO report empty and prevent regressions.
