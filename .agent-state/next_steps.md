# Next Steps (Updated 2026-10-25)

## ✅ Current state

- **`qgis-manage` 0.12.0 adopted** (was 0.10.0): `pyproject.toml` requires `>=0.12.0`,
  `uv.lock` is at 0.12.0. The 0.10.0 analysis findings were fixed upstream in
  0.10.1/0.11.0/0.12.0 (backup collisions, repeatable `--type`, release-version
  guard, `deploy --yes`, pruned `--repo-check`, compile freshness, deploy manifest).
- **Makefile/CI hardened**:
  - `make compile` uses `--type resources --type translations` in one invocation
    when resources change (and translations only otherwise), with `--jobs`;
    `resources.py` stays clean.
  - `make clean` is project-owned (caches + `help/html` + `.qgis-manage`) because
    `qgis-manage clean` deletes tracked `*.cpg` sample sidecars and `resources.py`.
  - `make zip` runs `package --repo-check`.
  - Release CI packages with `--repo-check --stamp --release-version`.
  - `make docker-test` runs its metrics post-step with `uv run python` (the system
    `python3` lacked `qgis_plugin_analyzer`).
  - `[tool.qgis-manager]`: `qgis_version = 4`, `max_backups = 1`,
    `auto_compile = false`.
- **Analysis published**: `docs/research/qgis_manage_0.12.0_analysis.md` (0.10.0 →
  0.12.0: fixed findings, measurements, remaining limitations).
- **Gates green (2026-10-25)**: **848 local tests OK**; Docker suite
  exit 0 (agentic + core + exporters + gui + integration, last group 76 OK);
  `ruff`, `ruff format`, `mypy` (102 files; sandbox needs `MYPY_CACHE_DIR` inside
  the workspace), `check_docs` (37), `i18n-check` (6 OK), `security-scan`
  (bandit/detect-secrets PASS), Qt6 checker 0 findings, analyzer **CC PASS**,
  37 issues, docstring 99.1 % (baseline 99.0), security 100, module size PASS.
- **Agentic system**: new `qgis-release` skill, `make flake8` (QGIS portal scope,
  blocking) and `make portal-check` (ZIP layout/metadata/LICENSE/size/permissions),
  wired into `make zip`, CI and pre-commit.
- **Packaging**: `package --repo-check --stamp --release-version 3.12.0` passes;
  ZIP = 340 files, 2.4 MB, no `.agent/tests/docs/tools`, no `.qgis-manage`.
- **USER_GUIDE v3.12.0 refreshed**: 22 figures in `docs/source/images/` (six-entry
  sidebar, new Symbology/Interpretation tabs), stale `ui_main_dialog_v26` and
  `workflow_*` assets removed, `es` guide catalog at 100 %.
- **QGIS UI reference** (for screenshots): Qt6 follows the KDE dark scheme;
  `QT_QPA_PLATFORMTHEME=generic` forces the light palette (empty does not).
  Current profile uses `UITheme=Blend of Gray`; set `default` for the basic theme.

## 🚀 Release 3.12.0 published on GitHub (2026-10-25)

- Version **3.12.0** in `metadata.txt`/`pyproject.toml`; `[Unreleased]` moved to
  `[3.12.0]`; release notes in `docs/releases/notes/v3.12.0.md`; README and
  `DEVELOPMENT_LOG` updated.
- Gates green: 848 local tests, Docker suite, ruff/format, mypy (102 files),
  check_docs, i18n, flake8, bandit/detect-secrets, deep security 100/100, Qt6 0,
  CC PASS; `make portal-check` passes with warnings.
- ZIP `dist/sec_interp.3.12.0.zip` (342 files, 2.4 MB) with
  SHA256 `97d1ac197c53f28e1b8bacf0bfbe9bf869b39affd4add4dc49239332d0e97c38`.
- Commit `4f7cb048`, tag `v3.12.0`, `main` and the tag pushed to `origin`.
- GitHub release **published** as *Latest*:
  <https://github.com/geociencio/sec_interp/releases/tag/v3.12.0> (ZIP attached).
- **Do not upload the 3.12.0 ZIP**: it predates the F811/E402 fixes and has
  0600/0640 modes plus a 23×24 icon. Prepare **3.12.1** (see pending).

**Queue releases are retired (2026-10-25)**: `.release-queue.json`,
`scripts/next_scheduled_release.py` and `.github/workflows/scheduled-release.yml` were
removed. v3.9.1, v3.10.0 and v3.11.0 were the last queue-driven releases; 3.12.0 is a
manual release from `main` (no queue entry, no `release/v3.12.0` branch). The manual
checklist lives in `docs/releases/SCHEDULE.md`.

**Release-readiness caveats**: the Gen 8 release workflow still mentions the legacy
`docs/docsec/CHANGELOG.md`, `make package VERSION=main` (the Makefile ignores
`VERSION`), the outdated `git add` list and `make upload`. Treat those steps as
obsolete.

## 📌 Pending

0. **Prepare and upload v3.12.1** (blocking): normalize ZIP modes to 0644/0755,
   use a ≥64×64 icon, expand `about`, run `make pre-release` + `make zip`
   (`portal-check` included), then upload at
   <https://plugins.qgis.org/plugins/sec_interp/>. Do **not** upload 3.12.0.
1. **Review the refreshed USER_GUIDE** — 22 figures integrated (six-entry sidebar,
   Symbology/Interpretation tabs), `es` catalog at 100 %; check the new captions and
   the `guide_dem_setup` status-bar strip before the release build.
2. **`uv` 0.12.10 → 0.13.0** — blocked by pacman (Manjaro stable serves 0.12.10).
3. **Interop plan §9** — start with **B1** (drillhole 3D styles) → B3 → B2 → B4 → Phase A:
   `docs/plans/implementation_plan_interop_stereonet_3d.md`.
4. **Optional** — native review of the machine-assisted translations; refresh
   `help/html` with `make docs`.

## 🧾 Remaining debt (documented, non-blocking)

- **Analyzer**: 37 issues (20 `GOD_OBJECT`, 9 `MISSING_DOCSTRING`,
  4 `NON_PYTHONIC_LOOP`, 2 `POTENTIAL_MISSING_SLOT`, 1 `SPAGHETTI_CODE`,
  1 `UNPRECISE_LAYER`).
- **`ProfileController` GOD_OBJECT** (21 attributes) — deferred.
- **Docs i18n (optional)**: `USER_GUIDE` fr (28 %) / de (18 %).
- **Upstream `qgis-manage`**: `--require-docs` assumes `help/html/index.html`
  (false negative for per-language help); `clean` deletes tracked `*.cpg`;
  `profiles list` only enumerates QGIS 3; deploy manifest is neutral/slower on
  small plugins.
- **Framework pytest**: `.agent/tests` cannot run (pytest not installed); the
  workflow step is skipped, `conftest.py` remains.

## 🚀 How to resume

1. Run `/start-session` to refresh `AI_CONTEXT.md` and read this file.
2. Choose one:
   - prepare release **3.12.0** (recommended), or
   - capture/replace the USER_GUIDE screenshots, or
   - interop §9 **B1**.
3. For local gates: `export MYPY_CACHE_DIR=$PWD/.mypy_cache` before `make mypy`
   (sandbox only), and `UV_CACHE_DIR=/tmp/uv-cache-secinterp` for `uv`.
4. Before closing: `/close-session` and confirm the release gate is green.
