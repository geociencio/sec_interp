# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Research — QGIS plugin repository requirements**: added `docs/research/qgis_plugin_repository_requirements.md` (metadata rules, ZIP structure and 25 MB limit, Bandit/detect-secrets blocking vs Flake8 informational, QGIS 4 Ready version range, approval/trust, and a full SecInterp 3.12.0 audit). The README license was corrected to **GPL-2.0-or-later** to match `LICENSE` and `pyproject.toml`.
- **Tooling/CI — flake8 is now a blocking gate**: `make flake8` (alias `make pep8`, the QGIS convention) runs flake8 7.4.1 with `.flake8` on the packaged plugin scope (`core gui exporters plugin` + root modules). It is part of `make pre-release`, the CI `quality` job and the pre-commit hooks, matching the checker used by the QGIS plugin repository. `.flake8` no longer redirects output to JSON by default; `scripts/security_scan.py` requests the JSON report explicitly.

### Fixed
- **Lint (portal checker)**: removed the F811 redefinitions in `gui/preview_layer_factory.py` (renderer imports hoisted to module level) and the E402 late imports in `gui/ui/pages/settings/symbology_tab.py`; both plugin modules now pass flake8 clean.

## [3.12.0] - 2026-10-25

### Added
- **Developer tooling — `qgis-manage` 0.10.0 → 0.12.0 analysis**: `docs/research/qgis_manage_0.12.0_analysis.md` records the follow-up review of 0.10.1/0.11.0/0.12.0: which findings were fixed (backup collisions, repeatable `--type`, release-version guard, non-interactive purge, pruned repository scan), the new measurements (`--repo-check` 3.2 s → 0.67 s; the deploy manifest is neutral on a small plugin) and the remaining limitations (`--require-docs` assumes `help/html/index.html`, `clean` deletes tracked `.cpg`, `profiles list` only lists QGIS 3). Historical/research note; no plugin-runtime impact.
- **Developer tooling — QGIS smoke testing via MCP**: added a vendored fork of [`nkarasiak/qgis-mcp`](https://github.com/nkarasiak/qgis-mcp) under `tools/qgis_mcp/` with a `secinterp` tool group that drives the plugin's dialog over the Model Context Protocol (`status`, `open`, `preview`, `ready`, `results`, `export`). This lets an agent run the QGIS 4 smoke test (`/smoke-qgis4` workflow, `qgis_driver` subagent) programmatically instead of by hand. Dev-only: excluded from the plugin ZIP, static analysis and translation scopes; **no plugin-runtime impact**.

### Changed
- **README refreshed for v3.12.0**: new hero image from the repository (the old `file://` local path is gone), "What's New" covering the section-line selector, Interpretation Settings, the QGIS-agnostic core and the module-size work, a Symbology feature section, current screenshots, QGIS 4.x badges and an English developer section. Docs-only.
- **Documentation — USER_GUIDE v3.12.0 screenshots**: refreshed the 20 existing figures for the six-entry sidebar and added `guide_settings_symbology.png` and `guide_settings_interpretation.png`; §4.4 now documents the five Settings tabs (Default, Advanced, Symbology, Interpretation, Plugin Information) and §4.1 points to the Interpretation Settings tab. Removed the superseded `ui_main_dialog_v26.png` and the ten unused `workflow_*` assets; the Spanish guide catalog is at 100 %. Docs-only.
- **Developer tooling — hardened `qgis-manage` usage**: `make compile` uses the now-repeatable `--type resources --type translations` in one invocation when resources need rebuilding (and translations only otherwise), with `--jobs`; the manual `sed` patch is gone because 0.10.0+ auto-patches rcc/uic imports to `qgis.PyQt`; `transcompile` is no longer a dependency of `test`/`deploy`; `make zip` packages with `--repo-check`; release builds can use `package --stamp` so the ZIP's `metadata.txt` always matches `--release-version`; `.qgis-manage/` (deploy manifest) is ignored; and `[tool.qgis-manager]` pins `qgis_version = 4`, `max_backups = 1` and `auto_compile = false`. Dev-only; **no plugin-runtime impact**.
- **Release automation retired**: removed `.release-queue.json`, `scripts/next_scheduled_release.py` and `.github/workflows/scheduled-release.yml`. v3.9.1, v3.10.0 and v3.11.0 were the last queue-driven releases; 3.12.0 onward are cut manually from `main` (`docs/releases/SCHEDULE.md`). Dev-only; **no plugin-runtime impact**.
- **Developer tooling — `qgis-manage` 0.9.2 → 0.12.0**: 0.10.0 hardened the lifecycle (slugs, path confinement, `--trust`, metadata preservation); 0.10.1 fixed backup collisions, made `--type` repeatable, guarded `--release-version` and added `deploy --yes`; 0.11.0 added the deploy manifest, reflink backups, compile freshness and a pruned `--repo-check` (3.2 s → 0.67 s); 0.12.0 added `--json`, `ignore check`, `deploy --dry-run`, `profiles list`, `analyze --max-cc` and made hooks non-shell by default (SecInterp has no `plugin_hooks.py`). A 2.4 MB / 340-file package and a deploy to a temporary profile were smoke-tested. Documented in `docs/maintainer/qgis_manage_deployment_guide.md`. Dev-only; **no plugin-runtime impact**.
- **Core is now QGIS-agnostic**: removed the last seven QGIS/PyQt couplings from `core/`. Translations use an injectable backend (`TranslatableMixin.set_translator`), settings use a `SettingsStore` port (`QgsSettingsStore` lives in `gui/adapters`), and the vector writer/map-settings factory moved to `exporters/`. `ExportService` receives its map-settings factory from the composition root. The architecture gate now has an **empty allowlist**, and `core.controller`/`ExportService` import in a plain venv without QGIS.
- **Code Walkthrough consolidated on v2**: `docs/code_walkthrough_v2/` (ES) and `docs/code_walkthrough_en_v2/` (EN) are now the only active vaults. The legacy `code_walkthrough*` vaults moved to `docs/archive/` with redirect banners; the four missing notes and two new notes (`section_feature_selector`, `interpretation_tab`) were added to v2, and architecture/index/README links now point to v2.
- **Interpretation settings moved into Settings**: `InterpretationPage` is now the **Interpretation Settings** tab inside `SettingsPage` (Default, Advanced, Symbology, Interpretation, Plugin Information); the sidebar shrank from 7 to 6 entries. The persisted keys, `dump/load` protocol, translation context and `MainWindow.page_interpretation` alias are preserved, so existing projects and consumers keep working. No data migration required.
- **Preview renderer module-size refactor**: `gui/preview_renderer.py` (438 lines) is now a 335-line facade; data-layer collection and project/rubber-band cleanup moved to `preview_renderer_layers.py` (123) and `preview_renderer_cleanup.py` (68). Public methods and private wrappers are preserved. With this change the **module_size_gate is PASS** (0 modules >400).
- **3D interpretation exporter module-size refactor**: `exporters/interpretation_3d_exporter.py` (472 lines) is now a 155-line facade; field/writer, 2D-to-3D geometry and QML/3D styling helpers moved to `exporters/interpretation_3d/` (67–178 lines). Public methods and test patch points are preserved.
- **Preview layer factory module-size refactor**: `gui/preview_layer_factory.py` (535 lines) is now a 202-line facade; layer builders moved to `gui/preview_layers/{topography,geology,structures,drillholes,interpretations}.py` (25–157 lines). Factory helpers and renderers remain on the facade, so patch points and behavior are unchanged.
- **Geometry adapter module-size refactor**: `gui/adapters/geometry.py` (598 lines) is now a 69-line compatibility facade; the implementation moved to `geometry_crs`, `geometry_lines`, `geometry_sampling`, `geometry_stats` and `geometry_sections` (69–174 lines). Public imports and behavior are unchanged; one line-sampling regression added.
- **Controller module-size refactor**: `core/controller.py` dropped from 465 to **295 lines**. Cache-key builders and the four profile component processors moved to `core/services/profile/` (`cache`, `topography`, `geology`, `structures`, `drillholes`, `pipeline`); `ProfileController` keeps its public API, cache semantics and translation context. No functional change; 21 tests added.
- **Agentic Forge v1.4.1 → v1.4.2**: bumped the `.agent` submodule to `b264e35` (`537f9fd` was v1.4.1). The framework split metrics checks/reporting into dedicated modules and made `memory prune` dry-run by default; v1.4.2 is a quality-gate hotfix (skip cache directories and harden TOML config error handling). The project adapters and tests were updated accordingly. Active workflows and `AGENTS.md` now use `testing-standards` instead of the deprecated `qa-docker` alias. Dev-only; no plugin-runtime impact.
- **Testing workflow**: the project is standardized on `unittest` (mock-first) across the Makefile, agent workflows and docs; the unused `pytest`, `pytest-qt` and `pytest-mock` development dependencies were removed and `uv.lock` regenerated (68 packages). No plugin-runtime impact.
- **Developer toolchain**: refreshed the `uv`-managed dependencies — `ruff` 0.17.1, `pre-commit` 4.7.0, `pytest-mock` 3.17.0 plus 19 patch/minor transitive updates, and the major bumps `rich` 15 (ai-context-core/bandit CLI), `virtualenv` 21 + `filelock` 4 (pre-commit hook environments) and `imagesize` 2 (Sphinx). `docutils` stays at 0.22.4 because Sphinx 9.1 and myst-parser cap it. No plugin-runtime impact.
- **Documentation — Code Walkthrough vault v3.11.0**: the bilingual vault now documents the Symbology tab, the preview side panel and the per-unit editor, updates the legend renderer/topography notes and removes the retired `legend_widget` module. Developer-facing only; no plugin-runtime impact.
- **Documentation — competitive analysis**: expanded `PLUGIN_REPORT_AND_COMPARISON_EN.md` from 7 to ~30 relevant QGIS plugins across sections, drillholes, structural/stereonet, 3D modelling and geological mapping, adding OpenLog, the stereonet cluster, 3D-modelling tools (LoopStructural/GemPy) and an adoption snapshot; corrected the QGIS 4 readiness claim (Geoscience 2.0 is now QGIS 4-ready).
- **In-plugin offline help**: the manual shipped with the plugin now contains only the **User Guide** — a single document with clean navigation — instead of a landing page plus developer/API pages that linked to content removed from the offline build. The published documentation website is unchanged.
- **Tooling**: upgraded `qgis-plugin-analyzer` 1.14.0 → 1.16.0 and refreshed static-analysis metrics. 1.15.0 added anti-pattern detection; 1.15.1 restored the security scanner; 1.15.2 removed the `B102` false positives on Qt `QDialog.exec()` (Security Score back to 100.0); 1.16.0 fixed a whole-project module-discovery bug (analysed modules 135 → **171**, the true plugin-wide count) and emits per-rule severities. The corrected coverage surfaced previously-ungated code: the resulting i18n and complexity findings were triaged in the same cycle (see Development Log). No functional impact on the plugin.

### Fixed
- **`make clean` preserves tracked files**: `qgis-manage clean` deletes the generated `.py` next to each `.qrc`/`.ui` and every `*.cpg`/`*.qpj`; this repo tracks `resources/resources.py` and the sample-data sidecars `examples/sample_data/*.cpg`. `make clean` now removes only caches and `help/html`, keeping all tracked files (the CLI equivalents are `--keep-generated` and `--dry-run`).
- **Metadata boolean**: `metadata.txt` declared `hasProcessingProvider=no`; the stricter validator in `qgis-manage` 0.10.0 warns unless boolean fields use `True`/`False`, so it is now `False` (same behavior, clean `qgis-manage validate`).
- **Section feature selection**: `SectionPage` now exposes an `fid — label` combo that lists only section lines with **exactly 2 vertices** (3+ point lines are discarded) and lets the user choose the label field (`Auto` or any attribute). `section_feature_id` is now forwarded to topography, geology, structures, drillholes, LOD and the async geology/drillhole tasks, so switching features changes the sampled section; the existing cache keys already isolate features. Label-field choice only affects the combo text, not the preview/cache. `Invert line` remains a future feature.
- **QGIS repository status**: v3.11.0 is approved in the QGIS plugin repository; the README version badge was corrected from 3.9.1 to 3.11.0 and now links to the plugin listing. Documentation only.
- **Export cache correctness**: changing the DEM/section line, enabling Smooth or remapping drillhole fields could reuse stale component data during export. Component cache keys now include the line/raster, section feature, band, LOD, smoothing window and every drillhole field mapping; four regression tests cover the export path.
- **QGIS 3.28 / Python 3.9 compatibility**: QGIS 3.28 on OSGeo4W ships Python 3.9, so PEP 604 `isinstance` unions and `zip(strict=...)` were replaced; `safe_loader` now uses future annotations. A static gate (`tests/core/test_python_compat.py`) and ruff `py39` keep the plugin runtime compatible, while the development environment stays on 3.12.
- **Release workflow**: the scheduled release now runs the same gates as CI before packaging — `ruff`, `mypy`, `check_docs`, `security-scan`, `i18n-check` and `qgis-analyzer --max-cc 10` — so a release branch cannot publish code that the normal pipeline would reject. `make pre-release` mirrors these gates locally.
- **Translations (i18n)**: regenerated all 13 catalogs from the current source (363 messages, up from 282), completed the v3.9–v3.11 strings (0 `unfinished`), recompiled the `.qm` files and added `make i18n-check` (`tests/core/test_i18n_catalogs.py`) to guard placeholders, HTML tags and missing catalogs. Machine-assisted with a curated UI glossary; review key labels before a public release.
- **Local packaging and deploy**: `.qgisignore` now excludes the local code-graph output (`graphify-out/`, 23 MB) and the agentic/context metadata (`forge.toml`, `context_manifest.json`, `.gitmodules`), so `qgis-manage package` and `qgis-manage deploy` no longer ship development artifacts. The published ZIP was unaffected because CI builds from a clean checkout.
- **Developer security scan**: bandit no longer scans the `.agent` submodule or `tools/qgis_mcp`, which produced 15 findings that never ship in the plugin. `make security-scan` is green again.
- **Scheduled release (CI)**: unblocked the release train for branches cut before the `.agent` submodule conversion and the offline-help rework — the `scheduled-release.yml` workflow now clears the stale `.agent` submodule before switching branches and caches/restores `main`'s offline-help toolchain (`conf.py`, `help_index.rst`). This published **v3.10.0**. No plugin-runtime impact.
- **Release packaging**: the distributed plugin ZIP now includes the in-plugin offline help (it was missing from the v3.9.1 build) and no longer ships the internal release-queue file.

- **Tooling (dev)**: refreshed the `uv`-managed developer toolchain — `qgis-manage` 0.9.0 → **0.9.2**, `pre-commit` 4.6.2, `pytest` 9.1.1, `setuptools` 84.0.0, `sphinx-intl` 2.4.0, `sphinxcontrib-mermaid` 2.1.1 and others — with no plugin-runtime impact. Also modernized the linters: `ruff` 0.15.2 → **0.17.0** (pre-commit rev synced to `v0.17.0`; Markdown is excluded from `ruff format` so docs are untouched) and `mypy` 1.19.1 → **2.4.0** (no new findings), and removed the unused `black` dependency (`ruff format` is canonical). `mypy` is now wired as a gate over `core` + `exporters` (`make mypy`, plus a CI `typecheck` job), which were driven to zero type errors (32 → 0).

## [3.11.0] - 2026-10-18

### Added
- **Legend layout options (Settings → Symbology → Legend)**: choose the legend **position** (top/bottom, left/right), **font size** and a **maximum number of items** (the rest are summarized as "+N more") for the exported image; the font size also applies to the preview panel.
- **Per-unit editor (Settings → Symbology → Units)**: hide, recolor, **rename** and **reorder** geological and drillhole units. Renames (aliases) and order are reflected in the preview legend and the exported image legend, and persist in the project; a "Reset unit styles" button clears the customization.
- **Live symbology (Settings → Symbology)**: a new tab styles the preview/export live — topography color mode, ramp/color and line width (moved here from the Section page), structures color/width, drillhole trace color/width/labels, and the default interpretation color. Settings are stored in the project.

### Changed
- **Legend panel editing**: Topography, Structures and Drillhole traces rows in the legend panel now have a **visibility checkbox** (synced with the Show controls) and a **color button** (synced with Settings → Symbology); each **Interpretation** can be hidden and recolored individually from the panel too.
- **Legend content**: the preview and exported legends now show the actual symbology (topography mode/color, structures color, drillhole trace color), separate **Geology units** from **Drillhole lithologies** under their own headers, and include the **Interpretations** (they no longer live in a separate panel section and now appear in the exported legend too).
- **Legend controls**: removed the "Show Legend" checkbox from the preview Controls (the legend now lives in the collapsible side panel). Whether the legend is drawn in the exported image is configured from **Settings → Symbology → Legend**.
- **Settings — Symbology layout**: the sections (Topography, Structures, Drillholes, Interpretations, Legend, Units) are now **collapsible and start collapsed**, and the tab scrolls, so a long list no longer forces the dialog to grow. The **Units** list is roomier (up to 340 px) and the settings panel fills the available height.

### Fixed
- **Plugin window size**: the dialog no longer opens covering (almost) the whole screen — its height is bounded, the Symbology content scrolls instead of expanding it, and the settings panel no longer leaves empty space below.

## [3.10.0] - 2026-10-11

### Added
- **Drillhole lithologies in the legend**: the drillhole interval units now appear in the preview legend (and the exported image) alongside geology, so subsurface lithologies can be interpreted; hide/color controls apply to them too. A "Drillholes" entry represents the traces.
- **Per-unit legend controls**: in the preview side panel you can **hide/show** and **change the color** of each geological unit; the choice is applied to the preview (and its exported image) and is remembered between sessions. Structures and drillholes are unaffected.
- **Preview side panel**: the legend moved off the canvas into a collapsible panel beside the preview (no longer covering the profile), together with a list of the drawn interpretations. The exported image/PDF/SVG legend is unchanged.

## [3.9.1] - 2026-10-04

### Added
- **Geology on the smoothed profile**: with **Smooth** active, the geological profile (and its export) now follow the smoothed topography using the same window. Structures and drillholes keep their raw sampling. Because the geology geometry now depends on it, changing Smooth regenerates the preview on the next **Preview**.
- **Smoothed topography profile**: a **Smooth** control in the preview Controls (with a **Window** in metres, 10–500, off by default) overlays a smoothed line on the topographic profile and, on export, also writes `topo_profile_smoothed.csv` and `profile_line_smoothed.<ext>` alongside the raw outputs. Smoothing is a distance-window moving average; the sampled data is unchanged.

### Fixed
- **QGIS 4 / DEM band statistics**: scoped the `QgsRasterBandStats` enum and switched to `Qgis.RasterBandStatistic` (with a 3.28–3.39 fallback), fixing an `AttributeError` on PyQt6 and a deprecation warning on QGIS ≥3.40.

## [3.9.0] - 2026-09-27

### Added
- **Topographic profile color mode**: choose **Gradient** (with a color ramp, e.g. *Spectral* or *Terrain*) or **Simple** (a single color) for the profile from the Section Line page. The change only affects the preview/export styling, never the source layer.
- **Profile-vs-DEM statistics**: the Section Line page now shows the section's **Minimum**, **Maximum**, **Mean** elevation and the number of samples at the DEM resolution, refreshed when the line, DEM or band changes.
- **DEM page — band statistics**: the DEM/Raster page now shows read-only **Minimum**, **Maximum**, **Mean** and **NoData** for the selected band, computed with a bounded sample size so large or remote rasters do not block the UI.
- **DEM / Section — CRS safety checks**: SecInterp now warns when the section line, DEM and data layers use different coordinate reference systems (amber status) and **blocks** preview/export when a layer's declared CRS contradicts its coordinates (e.g. geographic data declared as projected), explaining how to fix it with *Assign Projection*. Sampling across CRS now reprojects correctly for topography, geology, structures and drillhole collars.
- **Adaptive Vertical Exaggeration**: the DEM page now has an `Auto` toggle (default on) that computes the vertical exaggeration automatically from the profile aspect ratio and structural density (clamped `0.5×–20×`), with the manual spin preserved as an override. A read-only value is shown next to the toggle and in the results panel (`Vertical exaggeration: 2.6× (auto)`).
- **Documentation — Architecture**: Expanded `ARCHITECTURE.mmd` (34 → 260 lines) and `docs/ARCHITECTURE_EN.md` (directory structure, full Mermaid diagram, Quality Assurance & Security Scanning section with Bandit/detect-secrets/Flake8, qgis-analyzer, Qt6 checker, and pre-release pipeline).
- **Documentation — Analysis**: Added `docs/ARCHITECTURE_MONOLITHIC_VS_CLEAN_EN.md` (monolithic vs Clean Architecture comparison) and `docs/PLUGIN_REPORT_AND_COMPARISON_EN.md` (feature inventory and 7-plugin competitive matrix).
- **Documentation — Code Walkthrough Vault**: Added a bilingual Obsidian vault (`docs/code_walkthrough/` ES + `docs/code_walkthrough_en/` EN, initially 20 notes plus 3 mirror docs per vault). Covers entry point, logger, controller, domain, exceptions, profile/geology/drillhole/structure services, validation, safe_loader, i18n, main_dialog, preview/export managers, renderers, tasks, adapters, and base/vector exporters. Expanded with number-free templates and `scripts/sync_vault_mirrors.sh` (mirror sync), then enriched with `config`, `data_cache`, `performance_metrics`, `state/input/signal/interpretation/tool` managers, `preview_state/layer_factory/renderer/axes_manager`, and `export_service` + 9 exporters (csv/pdf/svg/image/profile/dxf/interpretation/drillhole 3D).

- **Documentation — Guides**: Added `docs/DOCS_INDEX.md` (canonical map), `DOCS_STYLE_GUIDE.md`, `DOCUMENTATION_PROCESS.md`, `USER_GUIDE_CONVENTIONS.md` and a generated `docs/structure/` tree.
- **Documentation — Tooling**: Added `scripts/check_docs.py` (`make docs-check`), `scripts/sync_docs_version.py` (`make docs-version`), `scripts/docs_i18n_status.py` (`make docs-i18n`) and `scripts/sync_docs_mirrors.sh`.
- **Documentation — Vault Layers**: Added per-vault `layer_*` notes (root layers + sub-layers) and enriched the thinnest file notes (ES + EN).
- **Documentation — Code Walkthrough Vault v2 (completed)**: Enriched the full vault to 151 substantive notes per language (Core 56, GUI 73, Exporters/Plugin/Root 22) at the 400–500-line depth standard, added 23 `layer_*` navigation hubs, finalized the bilingual `Index.md` (hub map, reading paths, layer diagram), and added a vault-owned file-to-note map (`project_structure_links.md`, 178 files → 151 notes) backed by `scripts/generate_structure_links.py`. All 302 notes pass the size/completeness gate with zero dangling links.
- **Documentation — Code Walkthrough Vault v2**: Added a new self-contained bilingual vault (`docs/code_walkthrough_v2/` ES + `docs/code_walkthrough_en_v2/` EN) with a 400–500-line depth standard, backed by new tooling — `scripts/generate_vault_v2.py` (AST tiering A/B/C, collision-safe slugs, package file enumeration, high-importance `note_lines` ceiling) and `scripts/check_notes.py` (size/completeness gate with placeholder detection and ES↔EN slug parity). The existing v1 vaults are left untouched.
- **Documentation — Structure**: Added `docs/structure/project_structure_table.md`, a tabular Depth 1–5 view of the plugin directory tree.

### Changed
- **Documentation — Vault Numbering**: Removed numeric prefixes from all 68 vault notes (`NN - slug.md` → `slug.md`) and updated all wikilinks and index tables (`#` column removed); navigation is now by sections/tags.
- **Repository**: Ignored Obsidian vault editor state (`.obsidian/`) via `.gitignore`.
- **Documentation — Website**: the published site now builds `en` + `es` (was 14 near-English languages); a language is published once its `USER_GUIDE` reaches ≥80%. The in-plugin offline help keeps all UI languages.
- **Documentation — Sphinx**: `conf.py` reads the version from `metadata.txt`; the autodoc API pages now populate (fixed `sys.path`); the build runs with `-j auto`.
- **Documentation — i18n**: Spanish `USER_GUIDE` translated to 100%; catalogs pruned to user-facing pages (`docs/locales` 20 MB → 2.4 MB).
- **CI**: `.github/workflows/docs.yml` builds all languages and publishes to `geociencio/sec_interp_docs`; `test.yml` runs the docs consistency check.

### Fixed
- **DEM / Section — freeze with mixed CRS**: fixed a hang that could freeze QGIS (and force rebooting) when the DEM and section line were in different CRS (common with on-the-fly reprojection). Densification is now bounded and the sampling interval is computed in the section line's units.
- **Structural measurements**: symbols now sit on the topographic profile (they were drawn at elevation 0), and the Dip/Strike field selectors populate again after choosing the structural layer.
- **Drillholes**: collar elevation sampled from the DEM now respects the CRS difference.
- **Documentation**: corrected stale module references, broken links, version headers and phantom interfaces across the active docs.
- **Code quality**: `module_size_gate` PASS (7 modules decomposed to <300 lines) and `qgis-analyzer` reports **0 issues**.
- **Temporary scratch layers**: closing the dialog no longer leaves preview memory layers in the project (removed on OK/Save, Cancel/X and plugin unload), eliminating the "temporary scratch layers" warning on QGIS exit.

## [3.8.0] - 2026-09-19

### Changed
- **Architecture (internal, no user-facing impact)**: Enforced the Core/GUI Extract-then-Compute boundary. Migrated `StructureService`, `GeologyService`, `ProfileService`, the drillhole domain, and the validation layer to a QGIS-agnostic core; moved QGIS feature-reading, buffering, raster sampling, and layer resolution into a new `gui/adapters/` layer; and reimplemented decimation, polyline metrics, line azimuth, projection, and densification in pure standard-library math. Guarded by a new architecture allowlist gate (36 → 6 `core/` modules).
- **Repository Housekeeping**: Removed generated analyzer/coverage reports, build logs, and stale editor configurations (`.idea/`, `.vscode/`, `.continue/`) from the repository root and expanded `.gitignore` to prevent their re-introduction. No functional impact on the plugin.
- **Tooling**: Upgraded `qgis-plugin-analyzer` 1.13.2 → 1.14.0 and refreshed static-analysis metrics. The new i18n heuristic reduced `MISSING_I18N` findings from 72 → 2 (remaining two are developer-facing `PerformanceTimer` timing labels). No functional impact on the plugin.
- **Tooling**: Retired the internal `scripts/check_cc.py` and `scripts/verify_i18n_hygiene.py` scripts now that the cyclomatic-complexity gate (`analyze --max-cc 10`) and the AST-based `MISSING_I18N` rule are natively provided by `qgis-plugin-analyzer` 1.14.0. Both quality gates are now driven directly from the analyzer. No functional impact on the plugin.

### Fixed
- **Qt6 / QGIS 4 Legend Resize**: Replaced the flat `QEvent.Resize` enum with the scoped `QEvent.Type.Resize` in the legend widget, resolving a runtime `AttributeError` on QGIS 4.
- **3D Interpretation Export**: Enabled the 3D interpretation export by default (the `SecInterp/enable_3d` setting previously defaulted to restricted).

## [3.7.2] - 2026-09-12

### Fixed
- **Qt6 / QGIS 4 Enum Compatibility**: Migrated 114 flat enum usages to their scoped form (`Qgis.Critical` → `Qgis.MessageLevel.Critical`, `Qt.NoPen` → `Qt.PenStyle.NoPen`, `QgsWkbTypes.LineString` → `QgsWkbTypes.Type.LineString`, etc.). This resolves all 114 "Enum error" findings reported by the QGIS plugin repository Qt6 checker.

## [3.7.1] - 2026-09-06

### Fixed
- **Settings Persistence**: Replaced a silent `try/except/pass` in `_get_setting` with a logged `logger.warning`, so configuration restoration failures are visible instead of hidden (Bandit `B110`).

## [3.7.0] - 2026-09-06

### Added
- **i18n Quality Gate**: Developed an Abstract Syntax Tree (AST) validation script (`verify_i18n_hygiene.py`) to systematically scan UI components for untranslated strings and enforce translation hygiene.

### Fixed
- **i18n Dialog Titles**: Wrapped 9 untranslated error dialog titles (`Export Error`, `Preview Error`, `Geology Error`, `Drillhole Error`, etc.) and the `"ID:"` results HTML label with `self.dialog.tr()` in `ExportManager`, `PreviewManager`, and `InterpretationManager`.

### Changed
- **Collapsible Preview Controls**: Grouped the preview action buttons, LOD controls, and layer checkboxes into a collapsible `QgsCollapsibleGroupBox("Controls")`, keeping the map canvas and status bar always visible.
- **UI Translation Coverage**: Wrapped user-facing text in `self.dialog.tr()` and dynamic layer names (`Topography Fill`, `Drillhole Traces`, `Drillhole Intervals`) in `QCoreApplication.translate()`.
- **Developer Noise Isolation**: Applied `# no-i18n` exclusion annotations to internal performance metrics, timing dictionaries, developer log tags, and orchestrator task names.
- **Static Translation Tuning**: Calibrated `.analyzerignore` to completely bypass core services, internal exporters, and headless GUI managers from `MISSING_I18N` analysis.

## [3.6.0] - 2026-05-17

### Added
- **Global i18n Coverage**: Achieved full internationalization coverage for `ExportService`, `ProfileService`, and `ExportManager`.
- **Locale Synchronization**: Batch synchronization and compilation of all 13 supported locales (`de`, `es`, `fi`, `fr`, `hi`, `id`, `it`, `ja`, `nl`, `pl`, `pt_BR`, `ru`, `zh_CN`).
- **QGIS 4.x & Qt6 Readiness**: Implemented 100% thread-safe background processing by transitioning away from unhashable QgsTask structures.

### Changed
- **Spatial Performance Optimization**: Completely overhauled the Interpretation Manager's spatial inheritance algorithms. Shifted from O(N*M) pure Python point distance checks to native C++ `QgsSpatialIndex` nearest-neighbor lookups, achieving sub-second lookup speeds for massive datasets.
- **Geological Precision**: Attribute inheritance now accurately measures perpendicular distances against geological line segments instead of isolated points.
- **i18n Master Data**: Updated Spanish (`es.json`) with refined translations for export status and data processing messages.
- **Deployment Ecosystem**: Modernized `qgis-manage` to natively support multi-version profiles (QGIS 3 and QGIS 4).

### Fixed
- **Qt6 Compatibility (API Bridging)**: Resolved runtime `AttributeError` and `TypeError` crashes on QGIS 4.0.1 / PyQt6 by replacing deprecated `exec_()`, applying dynamic enum resolution for `QImage` formats, and bridging missing `Qt` enums (`PenStyle`, `BrushStyle`, `GlobalColor`) via `qt6_compat`.
- **Asynchronous Rendering Stability**: Eradicated legacy UI threading segmentation faults by implementing strict re-entry locks and deferred signal emission via `QTimer.singleShot`.
- **Test Infrastructure**: Refactored the integration suite with synchronous mock emission, securing a 100% pass rate (620+ tests) across Docker and local environments.
- **Linting**: Resolved project-wide W503/W504 binary operator conflicts and F401/F811 unused import violations.
- **Formatting**: Standardized the entire codebase using `black` and `ruff`.

## [3.5.0] - 2026-04-28

### Added
- **Generation 6 Agentic Autonomy**: Implemented `memory_prune.py`, `context_selector.py`, and `metrics_report.py` for autonomous maintenance and observability.
- **Strict Quality Gate**: Enforced CC <= 10 project-wide with automated pre-push audits.
- **100% Documentation**: Achieved full Google-style docstring coverage for all classes and methods.
- **QGIS 4.x Readiness**: Metadata and core services updated for Qt6/QGIS 4.x compatibility.
- **Type Hinting**: Reached 100% return type coverage and >97% parameter coverage.

### Fixed
- **Signal Leaks**: Resolved critical memory leak in Interpretation Page storage selector.
- **Spatial Indexing**: Optimized feature iteration in Interpretation Manager.
- **Linting**: Cleared all Flake8 and Ruff warnings across the codebase.

## [3.4.0] - 2026-03-29

### Added
- **i18n**: Achieved 100% complete translation for the UI across all 13 supported languages.
- **Testing**: Added comprehensive Integration Tests for Vector Drivers (GPKG, SHP, DXF).
- **Export (GeoPackage)**: Implemented unified GeoPackage layer appending under unique section subdirectories (`[SectionName]/`).
- **Interpretations**: Added full bi-directional "Vector Layer Mode" synchronization between QGIS Vector Layers and internal features.
- Unified export system supporting **DXF**, **GeoPackage**, and **Shapefile** for all data types.
- Robust 3D interpretation export with automatic coordinate transformation.
- Persistent export settings across sessions.

### Changed
- **i18n**: Rewrote translation injection (`apply_full.py`) with `ElementTree` for stable XML parsing and safe placeholder handling.
- **Plugin Ecosystem**: Refined `Makefile` logic to recursively capture deep source files for full translation propagation.
- **Parsing**: Restored and improved structural string parsing logic capable of handling multiple combined dip/strike notations simultaneously.
- Refactored `ExportService` to decouple 2D and 3D drillhole exports for better accuracy.
- Enhanced `TrajectoryEngine` with mandatory interval points at start/end depths.
- Reduced cyclomatic complexity in export orchestration logic.

### Fixed
- **Export (DXF/GPKG)**: Resolved a critical signature mismatch in `ExportService._export_drillholes_3d` where `DXFExporter` was being incorrectly used for specialized 3D drillhole data.
- **Type Safety**: Verified an 89.0% Return Type Hint coverage and bypassed a regex parsing bug in `qgis-plugin-analyzer`, correctly adding remaining missing hints to internal methods in `drillhole` and `export` services.
- **Tooling**: Updated `ai-context-core` to **v3.3.0**, resolving the aggregation bug in project reports and enabling specialized **QGIS Standards Compliance** analysis.
- **DXF**: Fixed critical failure during field creation by stripping unsupported attributes for DXF format.
- **Drillholes**: Resolved duplicated entries in logs and missing segments for very short geological intervals.
- **Stability**: Fixed `KeyError: 0` in `DXFExporter` when processing empty or malformed feature sets.
- **UI**: Fixed export format reset issue by synchronizing `SettingsPage` with `ConfigService`.

## [3.3.0] - 2026-03-14

### Added
- **Core**: Standardized `DrillholeProjection` as a Dataclass DTO across `DrillholeService`. Implemented explicit Return Type Hints (covering ~45% of core).
- **Architecture**: Achieved **100% QGIS 4.x Readiness** by ensuring all Qt dependencies use `qgis.PyQt` (API-agnostic principle).
- **Documentation**: New automated "Documentation-as-Code" system for testing and architectural metrics.
- **Infrastructure**: Refined `.qgisignore` to eliminate 80% of development noise from the final package.

### Changed
- **Architecture**: Replaced unsafe `contextlib.suppress` with explicit exception handling and logging in `controller.py`.
- **Rendering**: Migrated 3D Exporters to `Rule-Based Rendering` for cross-version coordinate and style integrity.
- **GUI**: Raised GUI testing coverage to **91%**, including full orchestration logic for background tasks.

### Fixed
- **Stability**: Resolved critical memory leaks and "orphaned" `QgsRubberBand` instances in `measure_tool.py`.
- **UI**: Fixed "Dead Status Bar" regression in preview widget by implementing a robust signal restoration loop in `SignalManager`.
- **Mocks**: Fixed arithmetic `TypeError` in Qt mocks, allowing for verified headless layout calculations.

## [3.2.0] - 2026-03-02
### Added
- **Testing**: Massive expansion of the test suite reaching **455 successful tests** in Docker.
- **Automation**: Implemented "Documentation-as-Code" system for dynamic updating of `TESTING_STATUS.md`.
- **Testing**: New integration suite for 3D vertical projections in Cartesian coordinate systems.
- **Security**: Path Traversal protection in all data exporters via absolute path resolution.
- **Validation**: Type and range validation for preview parameters in `PreviewParams`.

### Changed
- **Compatibility**: 100% compliance with QGIS 4.x API-agnostic principles (`qgis.PyQt`).
- **UI**: Refactored `PreviewLayerFactory` to use shared geometry/exaggeration helpers (extracted `_apply_exaggeration`, `_to_qgs_points`).
- **GUI**: Standardized `DialogSettingsPersistence` to reduce boilerplate in session management and widget resets.

### Fixed
- **Core**: Fixed regression in `TrajectoryEngine` affecting buffer filtering.
- **Integration**: Restored translation loading for systems using `SafeLoader`.
- **Memory**: Resolved memory leaks due to unreleased `QgsRubberBand` and missing signal disconnections in reset/clear buttons.
- **Stability**: Fixed critical system exception capture, allowing for clean QGIS termination.
- **Stability**: Fixed layer resolution via centralized `LayerResolver` with cache.
- **Testing**: Fixed 4 legacy skipped tests in `test_utils.py` by updating mocks to native API.
- **Validation**: Unified project validation logic, eliminating duplication in DTOs.
- **UX**: Implemented reactive progress reporting for drillhole generation in the UI (added `progress_changed` signal).
- **Mocks**: Robust testing environment with support for unique layer IDs and strict geometry and field validation.
- **Stability**: Fixed `TypeError` in `ProfileController` due to dependency injection mismatch and `DrillholeProjection` subscriptable error in rendering.
- **Core**: Fixed `IndexError` in `TrajectoryEngine` for drillholes outside the section plane.

## [3.1.0] - 2026-02-19
### Added
- `SafeLoader` utility for resilient module imports and error handling.
- **i18n**: Localización complementaria para Hindi (`hi`) e Indonesio (`id`), ampliando la cobertura al mercado asiático.
- **Auditoría**: Publicado Roadmap Técnico para la modernización de `qgis-manage` (soporte `.pluginignore` y parcheo de RCC).
- **Desarrollo**: Nueva guía de despliegue y problemas conocidos para desarrolladores en `docs/maintainer`.
- **i18n**: Localización profunda de la guía de usuario para 7 idiomas prioritarios (FR, DE, IT, PT_BR, RU, ZH_CN, JA), cubriendo tutoriales y funciones avanzadas.

### Changed
- Refactorized plugin initialization (`SecInterp` class) to use lazy loading.
- Decoupled domain services in `ProfileController` using `SafeLoader` for better resilience.

## [3.0.0] - 2026-02-14
### Added
- **i18n**: Soporte expandido a 8 idiomas (Hindi, Japonés, Inglés, Español, etc.).
- **Calidad**: 100% Docstrings y CC <= 10 en servicios core.

### Fixed
- **Exportación**: Resolución de IDs de capa en `ExportService`.

## [2.0.0] - 2025-12-14
### Added
- **Major Feature**: Integración de Sondajes (Proyección e Intervalos).
