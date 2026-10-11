# Maintenance Session: 2026-10-11 - Release Train Unblock & v3.10.0 Publication

## Technical Summary

The scheduled release train (`.release-queue.json` → `scheduled-release.yml`) was
**blocked**: the first publish attempt for **v3.10.0** (due 2026-10-11) failed twice
because the train branches were cut (2026-09-27) *before* two tooling changes landed
on `main`. Both were fixed in the workflow, the dry-run then passed, and **v3.10.0
was published**.

## Root causes (two, both main-vs-branch tooling drift)

### 1. `.agent` representation changed (submodule vs directory)
- `main` tracks `.agent` as a **submodule** (`160000`, `.gitmodules` present, since
  2026-10-08). `release/v3.10.0` and `release/v3.11.0` track it as a **regular
  directory** (`040000`, no `.gitmodules`).
- The workflow checks out `main` (`submodules: recursive`, populating `.agent/`),
  then `git checkout release/v3.10.0` → `error: untracked working tree files would
  be overwritten ... Aborting`.

### 2. Offline-help toolchain not on the branches
- `main`'s `build_docs.sh` (added to the branches by the workflow's cache step)
  builds the offline manual with `root_doc=help_index` and relies on `main`'s
  `conf.py` help mode (`SECINTERP_DOCS_HELP=1`) + `docs/source/help_index.rst`.
- The branches carry neither → `sphinx.errors.SphinxError: Sphinx is unable to load
  the master document (.../help_index.rst)`.
- The workflow cached only `build_docs.sh`, so the fix was to cache the **full
  help toolchain** from `main`.

## Changes Made (committed to `main`, pushed)

| Commit | Change |
| :--- | :--- |
| `d9b13ebe` | `scheduled-release.yml`: `git submodule deinit -f .agent && rm -rf .agent` before `git checkout -f <branch>` (`.agent` is dev-only, never packaged). |
| `f202a083` | `scheduled-release.yml`: cache **and restore** `docs/source/conf.py` + `docs/source/help_index.rst` from `main` (not just `build_docs.sh`). |

Both fixes apply to **v3.10.0 and v3.11.0** (the workflow runs from `main` and
checks out the branch).

## Verification Results

| Run | Result |
| :--- | :--- |
| `38151134479` (dry-run, before fix) | ✗ failure — `Checkout release branch` |
| `38151363354` (dry-run, after fix #1) | ✗ failure — `Build offline help` |
| `38151593980` (dry-run, after fix #2) | ✓ **success** (docker tests OK, help built, package built) |
| `38151877186` (publish) | ✓ **success** |

**v3.10.0 published**: tag `v3.10.0` on `release/v3.10.0`, GitHub release
`2026-10-11T15:37Z`, asset `sec_interp.3.10.0.zip` (**2.27 MiB**, with the optimized
14-language offline manual), marked **Latest**. `next_scheduled_release.py` now
reports `nothing_due` (v3.11.0 is due 2026-10-18).

## Impact

- The train can publish again; the recurring "cron never fired / fired late" is now
  separable from an actual publish failure.
- **Still manual**: uploading the ZIP to the QGIS plugins portal (as for v3.9.1).
- **Known future risk**: the final train→`main` merge (`main` ahead many commits,
  train ahead others) will hit the same `.agent` representation diff — it needs a
  real merge, not `--ff-only`; plan it after v3.11.0 (2026-10-18).
