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
- **Gates green (2026-10-25)**: **839 local tests OK / 888 static**; Docker suite
  exit 0 (agentic + core + exporters + gui + integration, last group 76 OK);
  `ruff`, `ruff format`, `mypy` (102 files; sandbox needs `MYPY_CACHE_DIR` inside
  the workspace), `check_docs` (37), `i18n-check` (6 OK), `security-scan`
  (bandit/detect-secrets PASS), Qt6 checker 0 findings, analyzer **CC PASS**,
  37 issues, docstring 99.1 % (baseline 99.0), security 100, module size PASS.
- **Packaging**: `package --repo-check --stamp --release-version 3.12.0` passes;
  ZIP = 340 files, 2.4 MB, no `.agent/tests/docs/tools`, no `.qgis-manage`.
- **USER_GUIDE v3.12.0 refreshed**: 22 figures in `docs/source/images/` (six-entry
  sidebar, new Symbology/Interpretation tabs), stale `ui_main_dialog_v26` and
  `workflow_*` assets removed, `es` guide catalog at 100 %.
- **QGIS UI reference** (for screenshots): Qt6 follows the KDE dark scheme;
  `QT_QPA_PLATFORMTHEME=generic` forces the light palette (empty does not).
  Current profile uses `UITheme=Blend of Gray`; set `default` for the basic theme.

## 🚨 Release 3.12.0 is NOT prepared

Code/gates are green, but the release artifacts are missing:

1. Bump `metadata.txt` + `pyproject.toml` to **3.12.0** (`docs/source/conf.py` reads
   the version from `metadata.txt`).
2. `docs/CHANGELOG.md`: move `[Unreleased]` → `[3.12.0] - 2026-10-25`.
3. Create `docs/releases/notes/v3.12.0.md`.
4. README: version badge + "What's New" (still v3.9.1).
5. `docs/DEVELOPMENT_LOG.md` milestone.
6. Commit the changes, push `main` (it is ahead of `origin/main`), tag `v3.12.0`.
7. `make zip` + ZIP audit + `gh release create v3.12.0 ... --draft`.
8. Portal upload is manual: `plugin_upload.py` no longer exists, so `make upload`
   is broken.

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

0. **Prepare release 3.12.0** (recommended next task).
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
