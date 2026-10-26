# Release Process — Manual

> **Status (2026-10-25)**: the scheduled release train was retired. The queue
> (`.release-queue.json`), its selector (`scripts/next_scheduled_release.py`) and the
> `scheduled-release.yml` workflow were removed. **v3.9.1, v3.10.0 and v3.11.0 were the
> last queue-driven releases**; from 3.12.0 on, releases are cut manually from `main`.

## Manual release checklist

1. **Prepare the version**
   - `metadata.txt` and `pyproject.toml` → `X.Y.Z` (`docs/source/conf.py` reads the version
     from `metadata.txt`).
   - `docs/CHANGELOG.md`: move `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD`.
   - Create `docs/releases/notes/vX.Y.Z.md`.
   - Update the README version badge and "What's New", plus `docs/DEVELOPMENT_LOG.md`.
2. **Run the gates**
   ```bash
   make pre-release   # mypy, analyzer, i18n, Qt6, security, Docker tests
   ```
3. **Build and audit the ZIP**
   ```bash
   make zip            # includes make portal-check
   make portal-check   # qgis-manage validate --zip (0.14+)
   unzip -l dist/sec_interp.X.Y.Z.zip | grep -E "\.agent|scripts|tests|AI_CONTEXT"
   ```
   The audit must return nothing and `portal-check` must PASS.
4. **Commit, tag and push**
   ```bash
   git add metadata.txt pyproject.toml docs/ README.md
   git commit -m "chore(release): prepare vX.Y.Z"
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin main && git push origin vX.Y.Z
   ```
5. **GitHub release**
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z" \
     --notes-file docs/releases/notes/vX.Y.Z.md dist/*.zip --draft
   ```
6. **QGIS plugin repository (manual, unavoidable)**
   Upload `dist/sec_interp.X.Y.Z.zip` at <https://plugins.qgis.org/plugins/>. There is no
   `plugin_upload.py` in this repository, so this step is always manual.

## QGIS portal pre-upload checks

- `metadata.txt` with every required field (`name`, `qgisMinimumVersion`,
  `description`, `about`, `version`, `author`, `email`, `repository`).
- `LICENSE` with no extension; a single `sec_interp/` folder at the ZIP root.
- ZIP ≤ 25 MB, no binaries or development files; numeric unique `X.Y.Z` version.
- `qgisMaximumVersion=4.99` for the **QGIS 4 Ready** listing.
- Bandit and detect-secrets clean (blocking); Flake8 informational (`make flake8`
  keeps it clean).
- File modes `0644`/`0755` (`package --repo-check` normalizes them in 0.14+).
- Full rules and the SecInterp audit:
  [docs/research/qgis_plugin_repository_requirements.md](../research/qgis_plugin_repository_requirements.md).

Releases are cut from `main`; there are no `release/vX.Y.Z` branches and no fast-forward
step.
