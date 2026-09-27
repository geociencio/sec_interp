# Release Schedule — Incremental Train from v3.8.0

This document describes the scheduled rollout of the releases prepared from the
`feature/dem-section-v3.9.0` work. Each release lives on its own cumulative branch and is
published automatically on its Sunday.

## Calendar

| Version | Scheduled | Branch | Highlights |
| :--- | :--- | :--- | :--- |
| v3.9.0 | 2026-09-27 (published) | `main` | DEM/Section insights, CRS safety, Adaptive VE |
| v3.9.1 | **2026-10-04** | `release/v3.9.1` | Optional smoothed topography profile |
| v3.10.0 | **2026-10-11** | `release/v3.10.0` | Interactive preview legend (side panel, per-unit controls, drillhole lithologies) |
| v3.11.0 | **2026-10-18** | `release/v3.11.0` | Live symbology, per-unit editor, legend layout |

## How it works

- `.release-queue.json` lists the pending releases with their date and branch.
- `.github/workflows/scheduled-release.yml` runs **every Sunday at 15:00 UTC**. It picks the
  first release that is **due** (date reached) and **not yet published** (tag absent on
  `origin`), then:
  1. checks out the release branch,
  2. runs the QGIS headless test suite,
  3. builds `sec_interp.<version>.zip`,
  4. publishes the GitHub release with the versioned ZIP and `docs/releases/notes/v<version>.md`.
- If nothing is due (all published or dates in the future), the workflow does nothing.

### Manual trigger

To publish a specific version immediately (or retry a failed run), use
*Actions → Scheduled Release → Run workflow* and enter the version (e.g. `3.9.1`), or:

```bash
gh workflow run scheduled-release.yml -f version=3.9.1
```

## Manual steps (not automatable here)

1. **QGIS plugin repository**: upload `dist/sec_interp.<version>.zip` at
   <https://plugins.qgis.org/plugins/>. There is no `plugin_upload.py` in this repository, so
   this step is manual for every release.
2. **Sync `main`**: the scheduled workflow publishes from the release branch and does **not**
   advance `main` (to keep the automation non-destructive). Once a release is validated,
   fast-forward `main`:

   ```bash
   git checkout main && git merge --ff-only release/v3.11.0 && git push origin main
   ```

## Adding the next releases

Append an entry to `.release-queue.json` (version, branch, date) after preparing the branch —
no workflow change is required.
