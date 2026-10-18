# Maintenance Session: 2026-09-23 - Smoothed Geology (v3.9.1) + Preview Side Panel (v3.10.0)

## Technical Summary

Two follow-up features after the smoothed topography profile. First (v3.9.1):
geology now follows the smoothed profile (Option A — smooth the geology master
profile at extraction). Second (v3.10.0): the preview legend moved off the canvas
into a collapsible side panel with an interpretations list and per-unit
visibility/color controls; drillhole interval lithologies are listed too. Several
real-QGIS bugs found during manual testing were fixed. 10 commits
(`1e2a4ea9..471017b`), 729 tests, analyzer 0 issues, manual smoke on QGIS 4.

## Changes Made

### v3.9.1 — Geology on the smoothed profile (Option A)
- `PreviewParams` gains `smooth` / `smooth_window` (from the preview options) and
  the hasher includes them, so changing Smooth invalidates S2.
- `GeologyExtractor.extract_context(..., smoothing_window_m)`; the master profile
  is smoothed (`smooth_profile_by_distance`) and propagated to `master_grid_dists`.
- Controller + preview task orchestrator pass the window; Smooth now invalidates the
  preview instead of re-rendering from cache.
- Structures/collars and the perfil-vs-DEM stats stay raw.

### v3.10.0 — Preview side panel (L-A + L-B)
- New `gui/preview_side_panel.py`: collapsible panel next to the canvas with a
  scrollable legend and an interpretations list. The `LegendWidget` overlay was
  removed; the export legend (`PreviewLegendRenderer`) is unchanged.
- `PreviewWidget` uses a canvas|panel `QSplitter` (sizes persisted).
- L-B: `ColorManager` overrides/hidden/registry (survives `active_units` reset,
  dump/load); `build_categorized_line_style(hidden=...)`; per-unit visibility
  checkbox + color button (QColorDialog); persistence via `DialogSettingsPersistence`
  (`unit_style`).
- Drillholes: a "Drillholes" trace legend entry (panel + export) and registration
  of the interval lithologies so they appear in the legend and can be hidden/colored.

### Fixes found in manual QGIS 4 testing
- `QColorDialog` imported from `QtWidgets` (was `QtGui`) — broke plugin startup.
- Legend rows are destroyed with `deleteLater()` on refresh (using `setParent(None)`
  promoted each visible row to an orphan top-level "QGIS4" window).
- Interpretations list: load after settings (persisted source) and refresh the panel
  on every render so persistent polygons appear on reopen.

## Verification Results

- Local suite: **729 tests OK**; new tests for smoothing plumbing, ColorManager,
  hidden categories, panel rows, drillhole legend items.
- `ruff check` + `ruff format`: clean; `qgis-analyzer analyze . --max-cc 10`: **0 issues**.
- All new Qt imports verified against real QGIS 4.2.1; the full plugin imports clean.
- Manual smoke: smoothed geology aligns with the overlay; side panel legend +
  interpretations; hide/color per unit; drillhole lithologies; persistence; PNG export.

## Impact

- v3.9.1: geology and its export follow the smoothed profile.
- v3.10.0: the profile is no longer covered by the legend; users can read, hide and
  recolor geological and drillhole lithology units and see interpretations, persisted
  between sessions.

## Commits

- `1e2a4ea9` docs(plans): add geology-on-smoothed-profile plan (v3.9.1)
- `ccd081b9` feat(gui): follow the smoothed profile for geology (v3.9.1)
- `bc29b4fb` docs(plans): add preview side panel + unit interaction plan (v3.10.0)
- `1d82db0f` feat(gui): move legend to a collapsible preview side panel with interpretations list
- `99e00a06` feat(gui): per-unit visibility and color in the preview legend (Goal 1.1 core)
- `aa14a45` fix(gui): import QColorDialog from QtWidgets
- `1ca3208` fix(gui): destroy legend rows on refresh to avoid orphan windows
- `148cb14` feat(gui): show drillholes in the preview and export legends
- `ffcb1bb` feat(gui): list drillhole interval lithologies in the legend
- `471017b` fix(gui): refresh the interpretations list in the side panel

## Deferred

- Multi-line section selector (resolver + `section_feature_id` ready).
- Decouple geology vs drillhole hidden state if same-name units should not share it.
- Legend export layout options (position/size); bilinear DEM resampling.
- Data origin: re-import the geology/drillhole CSV as UTF-8 (accents/`?` already lost).
