# Maintenance Session: 2026-09-27 — Release Train, CI Hardening & Vault Refresh

## Technical Summary

This session turned the accumulated feature branch into a **progressive release train
from v3.8.0**: v3.9.0 was released, and v3.9.1 / v3.10.0 / v3.11.0 were prepared on
cumulative release branches and scheduled to publish automatically on the following three
Sundays. Along the way the project's CI was repaired (it had been red on every push to
`main`) and the bilingual Code Walkthrough **v2 vault was refreshed to v3.9.0**.

## Changes Made

### 1. v3.9.0 released (first of the train)
- Merged the v3.9.0 boundary (`76908843`) into `main`; bumped `metadata.txt` /
  `pyproject.toml` / `uv.lock` to 3.9.0; cut the CHANGELOG into `[3.9.0]`; added
  `docs/releases/notes/v3.9.0.md` and a DEVELOPMENT_LOG milestone.
- Fixed a **release-blocking test-isolation bug**: three `tests/gui` files imported
  `sec_interp.tests.base_test`, loading a second copy of the mocks
  (`tests.mocks.*` vs `sec_interp.tests.mocks.*`) so `docker-test` failed. Unified on
  `tests.base_test` with a file-level `I001` ignore for the mock-bootstrap order.
- Gates: analyzer 0 issues · 696 local / 681 Docker tests OK · security PASS. ZIP audited
  (495 files, no agentic/tests/docs). Commits `e00604e`, `664d775`; tag `v3.9.0`; GitHub
  release published live. **Portal upload pending (manual).**

### 2. Incremental release train (v3.9.1 → v3.11.0)
- Prepared three cumulative branches, each with a boundary merge, version bump, changelog
  cut, release notes and a development-log entry:
  - `release/v3.9.1` (smoothed topography profile) — 714 tests.
  - `release/v3.10.0` (interactive preview legend / side panel) — 729 tests.
  - `release/v3.11.0` (live symbology & legend styling) — 743 tests.
- Automated rollout: `.release-queue.json` + `.github/workflows/scheduled-release.yml`
  (every Sunday 15:00 UTC) publishes the due, not-yet-tagged release from its branch:
  checks out the branch, runs the Docker test gate, builds `sec_interp.<v>.zip`, and
  creates the GitHub release. Supports `workflow_dispatch` with `version` / `dry_run`.
- Validated: no-op run OK; `dry_run` of v3.9.1 OK (branch checkout + Docker tests + build,
  no publish). Portal upload remains manual; `main` is **not** auto-advanced.

### 3. CI hardening (main was red on every push)
- **Lint**: pinned the job to the project's locked ruff (`uv run --frozen`) instead of
  `uvx` latest (which added ISC004 / PLR0917 rules the pin does not enforce).
- **Qt6 check**: detect real findings (`grep "Enum error"`) instead of treating the
  always-present log header as a failure; fixed the one real finding
  `QgsRasterBandStats.All` → `QgsRasterBandStats.Stats.All`.
- **Tests job**: the in-container job never worked (obsolete `/root/.cargo/bin/uv` → 127,
  then a masked import error); replaced with the project's validated Docker image, with a
  tolerated QGIS teardown segfault (exit 139 only when all groups report OK).
- **Docs deployment**: `DOCS_DEPLOY_TOKEN` is not configured (no secrets), so the push to
  the external `sec_interp_docs` repo failed on every run; the clone/publish steps are now
  skipped when the secret is absent.
- **Legacy `release.yml`** (tag-triggered) deleted — broken and superseded by
  `scheduled-release.yml`.

### 4. Qt6 / QGIS 4 runtime fixes
- `gui/ui/pages/dem_page.py`: `QgsRasterBandStats.All` is an error on PyQt6; scoped it and,
  for the QGIS ≥3.40 deprecation, use `Qgis.RasterBandStatistic.All` with a fallback to the
  legacy enum on 3.28–3.39 (`_all_band_statistics`). Applied to `main` and cherry-picked to
  all three release branches.

### 5. Code Walkthrough v2 vault refreshed to v3.9.0
- Enriched `preview_param_hasher` and `ui_status_manager` (ES+EN) to tier A (400+ lines),
  reflecting their v3.9.0 growth.
- Added `crs_plausibility`, `layer_metadata` and `topo_renderer` notes (ES+EN).
- Bumped the vault label and all note footers to v3.9.0 (346 notes), updated the Index
  reading paths, the validation/renderers/gui hubs, and regenerated the file-to-note map.

## Verification Results

- `check_notes.py --strict`: **PASS** — 308 notes, 0 skeletons.
- `check_docs.py`: **PASS** (36 active docs); `generate_structure_links.py --check`: up-to-date.
- CI on `main`: **all green** (Ruff, Docs Consistency, Qt6, Tests Docker) and Docs Deployment green.
- Local suite: 696 tests OK (main); release branches 714 / 729 / 743.
- Scheduled-release dry-run: success without publishing.

## Impact

- The release train is now progressive and largely automated; the portal remains the only
  manual step.
- `main` no longer produces failed-run notifications; the Qt6 enum bug that would disable
  DEM band statistics on QGIS 4 is fixed everywhere.
- The vaults are consistent again with the v3.9.0 code.

## Commits (main, this session)

- `e00604e` fix(tests): use canonical tests.base_test import …
- `664d775` chore(release): prepare v3.9.0
- `ec889027` ci(release): add weekly scheduled release workflow and queue
- `f5978341`, `48bc640a`, `622ca33c` scheduled-release workflow fixes
- `630b1354` ci: stop the recurring failed-run notifications on main
- `4d2957bd` fix(gui): scope QgsRasterBandStats enum for Qt6/QGIS 4
- `1e31c9e5`, `29d107c3`, `2b226b35`, `73a40505` CI test-job repairs
- `93d836c9` fix(gui): use Qgis.RasterBandStatistic for band statistics
- `c63712ae` docs(vault): refresh v2 walkthrough to v3.9.0

## Deferred / Next

- Upload `dist/sec_interp.3.9.0.zip` to the QGIS portal is **skipped** by decision; publish
  v3.9.1 (Oct 4) instead, which already carries both Qt6 fixes.
- Full vault refresh to v3.11.0 once `main` consolidates the train (after Oct 18).
- Optional: configure `DOCS_DEPLOY_TOKEN` to re-enable the docs deployment.
- Goal 1.1 Fase 4 (symbology presets), multi-line selector, Goal 1.5 tests.
