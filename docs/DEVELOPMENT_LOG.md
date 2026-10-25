## [2026-10-25] Tooling: qgis-manage 0.12.0 & Release Readiness
- **Achievement**: adopted `qgis-manage` 0.12.0 (from 0.10.0), hardened the Makefile/packaging around it, retired the scheduled release train, and re-validated the 3.12.0 gate. All quality gates are green; the release artifacts (version, changelog, notes, README, tag) are still pending.
- **Changes**: repeatable `--type` + `--jobs` compile (resources rebuilt only when their inputs change); project-owned `clean` that preserves `resources.py` and the tracked `.cpg` sample sidecars; `zip` with `--repo-check`; `docker-test` post-step via `uv run python`; `[tool.qgis-manager]` pins QGIS 4, one backup and no implicit compile; `.qgis-manage/` ignored.
- **Release automation**: removed `.release-queue.json`, `scripts/next_scheduled_release.py` and `.github/workflows/scheduled-release.yml`; 3.9.1–3.11.0 were the last queue releases and 3.12.0 onward are manual (`docs/releases/SCHEDULE.md`).
- **Verification**: **839 tests OK / 888 static**; Docker suite exit 0; `ruff`, `format`, `mypy` (102 files), `check_docs` (37), `i18n-check`, `security-scan`, Qt6 (0 findings), analyzer CC PASS; `package --repo-check --stamp` = 340 files, 2.4 MB.
- **Analysis**: `docs/research/qgis_manage_0.12.0_analysis.md` records the 0.10.0 → 0.12.0 fixes, measurements (`--repo-check` 3.2 s → 0.67 s) and the remaining upstream limitations (`--require-docs` layout, `clean` vs tracked `.cpg`, `profiles list` QGIS 3 only).
- **Maintenance**: [session_2026-10-25_qgis_manage_0120.md](maintenance/session_2026-10-25_qgis_manage_0120.md).

## [2026-10-24] Session Close: Core QGIS-Agnostic
- **Achievement**: `core/` has no QGIS/PyQt imports; translations, settings and map settings are injected via ports/adapters; `qgis_io.py` and `map_settings.py` moved to `exporters/`; logger imports QGIS lazily.
- **Verification**: **839 tests OK / 888 static**; architecture allowlist **empty**; core imports in a plain venv; `ruff`, `format`, `mypy`, `check_docs`, `forge validate`, `sync_metrics --validate` and mirror-check PASS.
- **Docs**: code walkthrough consolidated on v2; public architecture rebuilt; [v3.11.0 technical analysis](https://geociencio.github.io/sec_interp_docs/en/v3.11.0_technical_analysis.html) published.
- **Maintenance**: [session_2026-10-24_core_qgis_agnostic.md](maintenance/session_2026-10-24_core_qgis_agnostic.md).
- **Pending**: `uv` stable, interop §9 B1, `ProfileController` GOD_OBJECT, `Invert line`.

## [2026-10-24] Refactor: Core QGIS-Agnostic
- **Achievement**: `core/` no longer imports `qgis.*` or `qgis.PyQt`. Translations are injected (`TranslatableMixin.set_translator`), settings use the `SettingsStore` port (`QgsSettingsStore` in `gui/adapters`), and `ExportService` receives `create_map_settings` from `exporters/map_settings.py`. `core/utils/io.py` moved to `exporters/qgis_io.py`.
- **Composition**: `SecInterp` creates `QgsSettingsStore`, `ConfigService` and `AccessControlService`; `ProfileController`, `SettingsPage`, `ExportService` receive them. Headless core defaults to `InMemorySettingsStore`; `logger_config` lazy-loads QGIS handlers.
- **Tests**: **839 OK** (static count synced next); new `test_i18n_port`, `test_settings_store` and `test_core_purity`; architecture allowlist is **empty**.
- **Plan**: [implementation_plan_core_qgis_agnostic.md](plans/implementation_plan_core_qgis_agnostic.md).

## [2026-10-24] Docs: Code Walkthrough v2 Consolidation
- **Achievement**: v2 (ES/EN) is now the single active code-walkthrough vault. Migrated `access_control_service`, `i18n`, `projection_engine` and `survey_processor`; added `section_feature_selector` and `interpretation_tab`; retargeted architecture/index/README links.
- **Archive**: v1 moved to `docs/archive/code_walkthrough_v1*` with `DEPRECATED` banners and archive READMEs; history preserved via `git mv`.
- **Validation**: `sync_vault_mirrors.sh --check`, `check_docs`, `make docs-check` PASS; v2 link audit has no missing note targets.
- **Reference**: [implementation_plan_code_walkthrough_v2_consolidation.md](plans/implementation_plan_code_walkthrough_v2_consolidation.md).

## [2026-10-24] Refactor: Interpretation Settings Tab
- **Achievement**: moved `InterpretationPage` into `SettingsPage` as the **Interpretation Settings** tab; sidebar now has 6 entries (DEM, Section, Geology, Structural, Drillholes, Settings).
- **Compatibility**: `MainWindow.page_interpretation` aliases `page_settings.interpretation_tab`; persisted keys (`source_type`, `custom_fields`, `interp_inherit_*`), the `dump/load` protocol, the `"InterpretationPage"` translation context and all consumers remain unchanged.
- **Files**: new `gui/ui/pages/settings/interpretation_tab.py`; `interpretation_page.py` kept as a compatibility shim; `settings_page.py`, `main_window.py` and `dialog_signal_manager.py` updated.
- **Tests**: **829 OK** (878 static); tab hosting/alias tests added; `ruff`, `format` and i18n PASS.

## [2026-10-24] Session Close: Section Feature Selection
- **Closed**: selector `fid — label` (only exactly-2-vertex lines, selectable label field) and full `section_feature_id` propagation to preview/export/LOD/tasks; **Invert line** deferred.
- **Quality**: **827 tests OK** (876 static) · CC/i18n/module-size PASS · security 100 · issues 36 · quality 56.4.
- **Deploy**: QGIS 4 `uv run qgis-manage deploy --no-compile --qgis-version 4`; manual validation confirmed OK (`secc1.shp`: 4/7 lines by design).
- **Maintenance**: [session_2026-10-24_section_feature_selection.md](maintenance/session_2026-10-24_section_feature_selection.md).
- **Pending**: push `main`, interop §9 B1, deferred `ProfileController` GOD_OBJECT.

## [2026-10-24] Fix: Section Feature Selection (`section_feature_id`)
- **Achievement**: `SectionPage` now lists only 2-vertex section lines in an `fid — label` combo, with a selectable label field (`Auto` or any attribute); `section_feature_id` is forwarded end-to-end to topography, geology, structures, drillholes, LOD and async tasks.
- **Files**: new `gui/ui/pages/section_feature_selector.py` (245 lines); `section_page.py` 291; wired `core/services/profile/{topography,geology,structures,drillholes}.py`, `core/services/preview_service.py` and `gui/preview_task_orchestrator.py`.
- **Tests**: **827 OK** (876 static); new selector/page/processor regression tests plus preview/async assertions; `ruff`, `format`, `mypy`, `i18n-check` and analyzer PASS.
- **Metrics**: CC PASS · i18n PASS · module size PASS · security 100 · issues **36** (GOD_OBJECT 19) · quality **56.4** (MI, diagnostic).
- **Plan**: [implementation_plan_section_feature_id.md](plans/implementation_plan_section_feature_id.md); `Invert line` deferred.

## [2026-10-24] Session Close: Module-Size Gate Completion
- **Achievement**: closed the five `module_size_gate` violations and left `main` clean and pushed. Controller 465→295, geometry 598→69, preview factory 535→202, 3D exporter 472→155 and renderer 438→335; **0 modules >400**.
- **Quality**: **808 tests OK** (857 static) · CC PASS · i18n PASS · security 100 · issues 36 · quality score 56.5 (Module Stability / MI, diagnostic).
- **Maintenance**: [session_2026-10-24_module_size_gate_completion.md](maintenance/session_2026-10-24_module_size_gate_completion.md).
- **Follow-up**: `uv` 0.13.0 (pacman), interop §9 **B1**, deferred `ProfileController` `GOD_OBJECT` (21 attrs), optional translation/help review.

## [2026-10-24] Session: Preview Renderer Module-Size Refactor & Gate Closure
- **Achievement**: reduced `gui/preview_renderer.py` from 438 to **335 lines** by extracting layer collection and cleanup helpers. With this change the **`module_size_gate` is PASS** for the first time since the audit: **0 modules >400**.
- **Changes**:
    - **Split** (`418417b3`): `preview_renderer_layers.py` (data-layer collection, structural/drillhole layers, extents) and `preview_renderer_cleanup.py` (project layers and rubber bands); `PreviewRenderer` keeps the public API and private wrappers used by tests.
- **Quality**: **808 tests OK** (857 static) · CC PASS · i18n PASS · quality **56.5** · issues 36 · module size **PASS (0)**.
- **Follow-up**: `GOD_OBJECT` remains deferred (19 project-wide); next project work is `uv` 0.13.0, interop §9 **B1**, or the optional docs/i18n review.

## [2026-10-24] Session: 3D Interpretation Exporter Module-Size Refactor
- **Achievement**: replaced the 472-line `exporters/interpretation_3d_exporter.py` with a **155-line facade** and three focused helper modules, preserving the public methods and the private hooks used by tests/integration. Module-size gate now lists 1 module (was 2).
- **Changes**:
    - **Split** (`08af6693`): `interpretation_3d/fields.py` (field definitions + vector writer), `interpretation_3d/geometry.py` (2D→3D rings/projection/validation) and `interpretation_3d/style.py` (QML, 2D category renderer, rule-based 3D renderer). Modules are 67–178 lines.
    - **Compatibility**: `export`, `_write_shapefile`, `_prepare_fields`, `_calculate_section_geometry` and `_collect_projected_features` remain as facade methods, so existing mocks and integration tests keep working.
- **Quality**: **808 tests OK** (857 static) · CC PASS · i18n PASS · quality **56.5** (was 56.3) · issues 37 → 36 · module size 2 → 1.
- **Follow-up**: only `gui/preview_renderer.py` (439) remains above 400.

## [2026-10-24] Session: Preview Layer Factory Module-Size Refactor
- **Achievement**: replaced the 535-line `gui/preview_layer_factory.py` with a **202-line facade** and five focused builders, keeping the factory helpers, renderers, patch points and behavior intact. Module-size gate now lists 2 modules (was 3).
- **Changes**:
    - **Split** (`113f4345`): `gui/preview_layers/{topography,geology,structures,drillholes,interpretations}.py` (25–157 lines); each builder receives the factory and uses its helpers/renderers, preserving tests that patch `factory.create_memory_layer` and the create methods.
    - **i18n**: the three translated layer names keep the `PreviewLayerFactory` context.
- **Quality**: **808 tests OK** (857 static) · CC PASS · i18n PASS · quality **56.3** (was 56.1) · module size 3 → 2.
- **Follow-up**: remaining >400 modules are `exporters/interpretation_3d_exporter.py` (472) and `gui/preview_renderer.py` (439).

## [2026-10-24] Session: Geometry Adapter Module-Size Refactor
- **Achievement**: replaced the 598-line `gui/adapters/geometry.py` with a **69-line compatibility facade** and five focused modules, keeping every public import and behavior intact. Module-size gate now lists 3 modules (was 4).
- **Changes**:
    - **Split** (`cddd765d`): `geometry_crs` (CRS/interval), `geometry_lines` (vertices/densify/segment range), `geometry_sampling` (point/line raster sampling), `geometry_stats` (per-cell min/max/mean) and `geometry_sections` (section feature/context). Modules are 69–174 lines.
    - **Tests**: updated the two patch targets (`geometry_crs.QgsCoordinateTransform`, `geometry_sampling.build_sampling_transform`) and added a regression for `sample_elevation_along_line`.
- **Quality**: **808 tests OK** (857 static) · CC PASS · i18n PASS · quality **56.1** (was 56.0) · module size 4 → 3.
- **Follow-up**: next is `gui/preview_layer_factory.py` (535); `GOD_OBJECT` remains deferred.

## [2026-10-24] Session: Controller Module-Size Refactor
- **Achievement**: reduced `core/controller.py` from **465 to 295 lines** without changing the public API, cache semantics or translations. The module-size gate now lists 4 modules instead of 5; `ProfileController` keeps thin translation wrappers.
- **Changes**:
    - **Fase 0** (`e09693f1`): 12 characterization tests pin messages, cache hits, `None`/`[]` returns, service-missing messages and orchestration order.
    - **Fase 1** (`54998073`): cache-key builders moved to `core/services/profile/cache.py`; 7 key tests.
    - **Fase 2** (`6ba7e0ba`): drillhole and structure processors extracted to `profile/drillholes.py` and `profile/structures.py`; wrappers preserve translated messages.
    - **Fase 3** (`938b01b7`): topography/geology processors and `profile/pipeline.py` extracted; internal exception strings tagged `# no-i18n` (0 `MISSING_I18N`).
    - **Fase 4**: 10 direct processor/pipeline tests; metrics, task board and handoff updated.
- **Quality**: **807 tests OK** (856 static) · `module_size_gate` 5 → 4 modules · CC PASS · i18n PASS · quality **56.0** (was 55.7) · `mypy` 97 files.
- **Maintenance**: [implementation_plan_module_size_controller.md](plans/implementation_plan_module_size_controller.md).
- **Follow-up**: `GOD_OBJECT` remains deferred (21 attrs); next is one of the 4 remaining >400 modules (`gui/adapters/geometry.py` first).

## [2026-10-23] Milestone: v3.11.0 Approved in the QGIS Plugin Repository
- **Achievement**: the QGIS plugin repository marked **v3.11.0** green/approved; it is now the public version (the listing previously served 3.10.0).
- **Docs**: README version badge corrected from 3.9.1 to **3.11.0** and linked to the plugin page; `task.md`/`next_steps.md` portal item closed.
- **Follow-up**: `module_size_gate` (5 modules), `uv` 0.13.0 (pacman) and interop plan §9 **B1**.

## [2026-10-19] Session: Agentic Forge v1.4.1 → v1.4.2 Upgrade
- **Achievement**: updated the `.agent` framework from `f15d44a` (v1.2.0-4) to **v1.4.2** (`b264e35`, via v1.4.1 `537f9fd`) without losing the project's memory/overlay/unittest fixes, which were ancestors of the release, and adapted the project adapters to the new framework module layout.
- **Changes**:
    - **Metrics adapter**: `sync_metrics.py` imports checks from `forge_metrics_checks` and reporting from `forge_metrics_report`; the removed `_check_i18n_consistency` tests were deleted.
    - **Memory/validator tests**: `prune_lessons`/`prune_next_steps_snapshots` now receive `apply=True`; overlay tests use `workflow_graph.workflow_files/scan_workflows`; skill tests use `skill_conflicts.find_conflicts` + `validate_memory_budget`.
    - **Skills**: active workflows and `AGENTS.md` use `testing-standards`; the deprecated `qa-docker` alias remains only in historical docs. `release-plugin` prunes with `memory prune --apply`.
    - **v1.4.2 hotfix**: framework metrics scans now skip `.mypy_cache`/`.ruff_cache`/`.pytest_cache`/`__pycache__`, and TOML config errors are handled via `ValueError` with the fallback parser.
    - **Tooling config**: `forge.toml` declares `test_command_full`, `lint_command`, `format_command` and `type_command` for `forge.py project *`.
- **Quality**: **778 tests OK** (827 static) · `forge validate` 17 skills / 18 workflows · `sync_metrics --validate` PASS · i18n and release gates unchanged.
- **Maintenance**: [session_2026-10-19_agentic_forge_v142.md](maintenance/session_2026-10-19_agentic_forge_v142.md).
- **Follow-up**: keep the submodule on v1.4.2; re-run the release gate before the next package.

## [2026-10-19] Session: Reliability Hardening — Agentic System, Cache, Python 3.9, i18n & Release Gates
- **Achievement**: closed the P0/P1 gaps from the repository and `.agent` audits: metrics truth, memory compaction, unittest standardization, overlay validation, export-cache correctness, QGIS 3.28/Python 3.9 compatibility, complete translation catalogs and release quality gates.
- **Changes**:
    - **Metrics** (`80f5bcac`): `sync_metrics.py` reads `analysis_results/project_context.json`, counts all 37 issues, separates static/executed tests and validates freshness against the analyzer.
    - **Memory** (`95b10b2f`): `AGENT_LESSONS.md` 98 → 27 active lessons (318 lines), 71 archived; `forge.py memory check` + 350-line validator gate.
    - **Unittest/deps** (`a05814a6`): workflows/skills use unittest; removed unused `pytest`, `pytest-qt`, `pytest-mock`; lockfile refreshed to 68 packages.
    - **Overlay validation** (`1be25720`): `forge validate`/`--graph` scan framework + `.agent-state/workflows` (18 workflows); `.agent` bumped to `f15d44a`.
    - **Export cache** (`d8e1dcb7`): component keys include line/raster, section feature, band, LOD, smoothing and every drillhole field mapping; 4 regression tests.
    - **Python 3.9** (`e7d265d9`): removed PEP 604 `isinstance` unions and `zip(strict=)`; `safe_loader` future annotations; static compatibility gate; ruff `py39`.
    - **i18n** (`cf701d07`): 13 catalogs regenerated (363 messages), 0 `unfinished`, `.qm` recompiled, `make i18n-check` gate.
    - **Release gates** (`f3f95df2`): `scheduled-release.yml` runs ruff, mypy, docs, security, i18n and analyzer before Docker/packaging; `make pre-release` mirrors them.
- **Quality**: 780 tests OK (829 static) · ruff/format/mypy/check_docs/forge/sync/i18n PASS · 18 workflows validated · release YAML valid.
- **Maintenance**: [session_2026-10-19_reliability_hardening.md](maintenance/session_2026-10-19_reliability_hardening.md).
- **Follow-up**: confirm v3.11.0 portal approval; `module_size_gate` still FAIL on 5 modules; `uv` 0.13.0 blocked by pacman; next feature starts with interop §9 **B1**; `section_feature_id` still not wired into profile sampling.

## [2026-10-18] Session: Dependency Refresh, Security Scope, Packaging Hygiene & Local Deploy
- **Achievement**: refreshed the `uv`-managed toolchain (safe batch + four major bumps, each verified against its consumer), committed the pending `.agent` submodule update, fixed two **pre-existing** scope leaks found while verifying (bandit scanning dev tooling; `.qgisignore` shipping `graphify-out`), and deployed **v3.11.0** to the local QGIS 4 profile.
- **Changes**:
    - **Submodule** (`96a70d9` + pointer `d7963cc7`): the QGIS `release-plugin` workflow validated a stale `763` test count → `792`; pushed to Codeberg so the pointer resolves for other clones.
    - **Deps (safe batch)**: `ruff` 0.17.1, `pre-commit` 4.7.0, `pytest-mock` 3.17.0 + 19 patch/minor transitive updates (click, requests, urllib3, platformdirs, stevedore, …).
    - **Deps (majors)**: `rich` 15 (ai-ctx/bandit CLI), `virtualenv` 21 + `filelock` 4 (+ `python-discovery`; pre-commit envs rebuilt from scratch) and `imagesize` 2 (Sphinx). `docutils` held at 0.22.4 — Sphinx 9.1/myst cap it.
    - **Security** (`b4c150d0`): `.bandit` now excludes `.agent` and `tools`; the gate was red on 15 findings from dev tooling that never ships.
    - **Packaging** (`a2193112`): `.qgisignore` excludes `graphify-out/` (23 MB), `forge.toml`, `context_manifest.json` and `.gitmodules`, closing the same leak in local `make zip` and `qgis-manage deploy`.
    - **Local deploy**: `qgis-manage deploy --no-compile --qgis-version 4` installed 3.11.0; post-deploy cleanup of preserved dev artifacts took the install from 30 MB to 4.9 MB.
- **Quality**: ruff/format clean · `make mypy` 89 files · pre-commit hooks (clean cache) · `make context` fresh (2,641/8,000 tokens) · Sphinx build OK · security scan PASS · Docker **728 executed OK** (792 discovered) · test package **311 files, identical name set to the published ZIP**.
- **Maintenance**: [session_2026-10-18_deps_refresh_packaging.md](maintenance/session_2026-10-18_deps_refresh_packaging.md).
- **Follow-up**: confirm portal approval for v3.11.0; `uv` 0.13.0 waits for pacman; `module_size_gate` still FAIL on 5 modules; next feature work starts with the interop plan §9 **B1**.

## [2026-10-18] Session: v3.11.0 Train Merge, Vault Refresh & Portal Upload
- **Achievement**: Closed the release train — merged **v3.11.0** into `main` (still at 3.9.1) after the scheduled publication, refreshed the bilingual Code Walkthrough v2 vault to v3.11.0, and prepared/uploaded the release ZIP. `main` is now 3.11.0.
- **Changes**:
    - **Merge** (`03310c45`): 26 train / 83 main commits. The train predates the `.agent` submodule conversion, so a prep commit (`5cb954cc`) dropped its in-tree framework; conflicts in `CHANGELOG`/`DEVELOPMENT_LOG` resolved as unions; the duplicated `_all_band_statistics` (same Qt6 fix on both sides) removed; `gui/legend_widget.py` deleted in favour of `gui/preview_side_panel.py`.
    - **CC fix**: `PreviewLegendRenderer.draw_legend` arrived with CC 14 (the train CI never ran the analyzer) → split into row builders, **CC 5**.
    - **Docs**: architecture maps, structure trees, Sphinx stubs, vault mirrors and `make docs-version` (13 docs) updated to 3.11.0.
    - **Vault** (`ad3e4009`): 8 new notes (preview side panel, Symbology tab, per-unit mixin, `color_manager`; ES+EN), `legend_widget` notes removed, `preview_legend_renderer`/`topography` refreshed, 364 footers normalized; `check_notes --strict` PASS (314 notes).
    - **Release**: official `sec_interp.3.11.0.zip` (2.28 MiB) downloaded and verified; uploaded to the QGIS portal (**pending approval**).
- **Quality**: ruff/format clean · mypy 89 files · Docker **728 executed OK** · CC/i18n/security PASS · analyzer 36 issues (quality 55.7) · `check_docs` + `check_notes --strict` PASS.
- **Maintenance**: [session_2026-10-18_v311_merge_vault_portal.md](maintenance/session_2026-10-18_v311_merge_vault_portal.md).
- **Follow-up**: confirm portal approval; backlog `module_size_gate` + `GOD_OBJECT`; next feature work starts with interop plan §9 **B1** (drillhole 3D styles).

## [2026-10-18] Release: v3.11.0 — Live Symbology & Legend Styling
- **Milestone**: Fourth release of the incremental train from v3.8.0 (scheduled). Goal 1.1 Fases 1–3: live per-layer symbology, per-unit editor and configurable legend layout.
- **Highlights**: Settings → Symbology tab (live styles, project-persisted); per-unit hide/recolor/rename/reorder reflected in preview and exported legend; legend layout (position, font size, max items).
- **Artifacts**: `sec_interp.3.11.0.zip`; release notes [v3.11.0](releases/notes/v3.11.0.md).

## [2026-10-11] Session: Stereonet / 3D Interop Plan (Scoped & Deferred)
- **Achievement**: Turned the ecosystem scan into a concrete, sample-data-validated **interoperability plan** — hand SecInterp's data to the specialist tools (qgSurf/mplstereonet for stereonets, QGIS's native 3D Map View for 3D) instead of building those crowded features. **No code written**; the plan is saved for a future session.
- **Changes**:
    - **`docs/plans/implementation_plan_interop_stereonet_3d.md`**: Phase A (attitudes export — `dip`/`dip_dir` primary + `strike` auxiliary, CSV + GeoPackage, `source_point` added to the core DTO) and Phase B (QGIS 3D Map View — B1 drillhole 3D `.qml`, B3 interpretation extrusion, B2 a **GUI scene action** with DEM terrain + vertical scale, B4 VE consistency). §9 holds a resume checklist.
    - Grounded on verified extension points (`entities.py:46`, `structure_service.py:121→139`, `interpretation_3d_exporter.py:431`, `drillhole_3d_exporter.py`) and validated against `examples/sample_data` (MURALLA).
- **Quality**: docs-only; `check_docs` PASS · `sync_vault_mirrors --check` clean · `validate_agent_system` PASS · ruff clean · `unittest discover tests` green.
- **Follow-up**: implement in the planned order (B1 first) in a new session; the plan's §8 records the remaining decisions.
- **Maintenance**: [session_2026-10-11_ecosystem_scan_and_interop_plan.md](maintenance/session_2026-10-11_ecosystem_scan_and_interop_plan.md).

## [2026-10-11] Session: Competitive Ecosystem Deep Scan & Report Refresh
- **Achievement**: Widened the competitive analysis from 7 to **~30 relevant QGIS plugins** across five clusters (sections, drillholes, structural/stereonet, 3D modelling, geological mapping) and corrected outdated claims in the public comparison report.
- **Changes**:
    - **New internal document** (not published): `.agent-state/history/ecosystem_comparison_2026-10-11.md` — full inventory with portal download counts, per-cluster matrices and internal recommendations.
    - **`docs/PLUGIN_REPORT_AND_COMPARISON_EN.md`** refreshed to v3.10.0 / 2026-10-11: added **OpenLog** (Apeiron/Oslandia — new direct competitor, Geoscience's successor), the **stereonet cluster** (§6.10), **3D modelling** (§6.11, LoopStructural/GemPy), an **adoption snapshot** (§7.5), and updated Geoscience (now QGIS 4-ready) and SWOT/roadmap. Vault v2 mirrors re-synced.
- **Quality**: `check_docs` PASS (36 docs) · `sync_vault_mirrors --check` clean.
- **Key finding (internal)**: SecInterp leads on breadth + engineering but not adoption (~4,640 downloads vs qProf ~212k, Geoscience ~124k, qgSurf ~83k); stereonet and 3D modelling are crowded/mature → prefer interoperation over reimplementation.
- **Follow-up**: upload v3.10.0 to the QGIS portal (currently 3.9.1); decide whether to close the stereonet gap by interop or build.

## [2026-10-11] Session: Release Train Unblock & v3.10.0 Publication
- **Achievement**: Unblocked and published **v3.10.0** on the scheduled release train. The train branches (cut 2026-09-27) had drifted from `main`'s tooling, which made the scheduled publish fail twice; both blockers were fixed in `scheduled-release.yml` and the release went out.
- **Changes**:
    - **`.agent` submodule drift** (`d9b13ebe`): `main` tracks `.agent` as a submodule (since 2026-10-08) while the train branches track it as a regular directory, so `git checkout <branch>` aborted with "untracked working tree files would be overwritten". Added `git submodule deinit -f .agent && rm -rf .agent` before the checkout.
    - **Offline-help toolchain drift** (`f202a083`): the workflow cached only `build_docs.sh`, but the help build needs `main`'s `conf.py` (help mode) and `help_index.rst`. Cache **and** restore all three from `main`.
    - Applies to **v3.10.0 and v3.11.0** (workflow runs from `main`, checks out the branch).
- **Quality**: dry-run `38151593980` **success** (Docker tests OK, help built, package built); publish `38151877186` **success**. **v3.10.0** released (`tag v3.10.0` on `release/v3.10.0`, `sec_interp.3.10.0.zip` 2.27 MiB, *Latest*); selector now `nothing_due`.
- **Follow-up**: upload the ZIP to the QGIS plugins portal (manual); the final train→`main` merge (after v3.11.0, 2026-10-18) needs a real merge, not `--ff-only`.
- **Maintenance**: [session_2026-10-11_release_train_v3.10.0.md](maintenance/session_2026-10-11_release_train_v3.10.0.md).

## [2026-10-11] Session: QGIS MCP Integration (Vendored Fork + `qgis_driver`)
- **Achievement**: SecInterp can now be **smoke-tested against a live QGIS session through the Model Context Protocol**. The exploration in `docs/plans/exploration_qgis4_qa_mcp.md` ("build a bespoke QGIS QA MCP") was superseded by research showing that design already exists, is published on `plugins.qgis.org` and supports `opencode`; we **adopted + forked + extended** `nkarasiak/qgis-mcp` instead of building from scratch.
- **Changes**:
    - **Fork** (`tools/qgis_mcp/`): vendored `nkarasiak/qgis-mcp` **v0.15.1** (`55519eb`); default port **9876 → 9877**; added `PROVENANCE.md` (upstream commit, changes, install, sync). Plugin `GPLv2+`, server `MIT` (compatible with `GPL-2.0-or-later`).
    - **SecInterp extension** (no `execute_code`): `qgis_mcp_plugin/handlers/secinterp.py` (mixin) + six `secinterp_*` tools in `src/qgis_mcp/server.py` + a compound `secinterp` group. Commands: `status`, `open`, `run_preview`, `assert_preview_ready`, `read_results`, `export_preview`. `open` mirrors `run()` **minus `exec()`** (a nested Qt loop would freeze the socket server); `export_preview` calls `_execute_preview_export` directly (the public method opens a modal dialog).
    - **opencode wiring**: `mcp.secinterp_qgis` (`cwd: tools/qgis_mcp`, compound, port 9877), `tools.secinterp_qgis*` disabled globally, and a new subagent **`qgis_driver`** that enables it.
    - **Scope**: `tools/` is a `qgis-manage` `DEV_DIRECTORY` → the fork is never packaged (verified); `.analyzerignore` and `[tool.ruff] exclude` gained `tools`. New workflow `.agent-state/workflows/smoke-qgis4.md` (+ row in `AGENTS.md`).
- **Quality**: fork suite **429 passed, 2 skipped** · `ruff check` clean (fork + root) · stdio handshake lists **131** granular / **28** compound tools · agent-system validator **14/14 PASS** · **live smoke on QGIS 4.2.1** green end-to-end (`ping` → `open` → `preview` → `ready` → `results` → `export`, PNG 2286×900 written).
- **Maintenance**: [session_2026-10-11_qgis_mcp_integration.md](maintenance/session_2026-10-11_qgis_mcp_integration.md).

## [2026-10-11] Session: Type-Check Gate (mypy wired)
- **Achievement**: Wired `mypy` into the workflow as a **blocking gate** over the strict layers (`core` + `exporters`) and drove them to **0 errors** (32 → 0), cleaning up real typing debt.
- **Changes**:
    - **Invocation** — mypy must run from the parent directory (the package base) to resolve `sec_interp.*` without the `core` vs `sec_interp.core` ambiguity. New `make mypy` target runs it from `$(CURDIR)/..` with `--explicit-package-bases sec_interp/core sec_interp/exporters`; added `mypy` to `pre-release`.
    - **CI** — new `typecheck` job in `.github/workflows/test.yml` (`UV_FROZEN=1 make mypy`).
    - **Fixes** — missing annotations (`validation_helpers`, `io.create_shapefile_writer`, `interpretation_3d_exporter._write_shapefile`/`_handle_post_export_styles`, `orchestrator.topo_handler`, `svg_exporter.export`); `None` guards (`io.create_vector_writer` project, `path_resolver.get_profile_name`, 3D exporter data provider); precise types (`layer_validator`, `parsing`, `drillhole`); QGIS-stub workarounds (enum params typed `Any`, index-based `QgsFields` iteration, `cast` for `QgsVectorFileWriter.create` and the collar point); aligned the `BaseExporter.export` override contract (image/pdf/svg accept the `layer_name` slot; 3D exporter widens `output_path` to `str | Path`); declared `ExportServiceCompatMixin.controller`/`access_control`.
- **Quality**: `make mypy` **Success: no issues found in 89 source files** · `ruff check`/`format` clean · `unittest discover tests` **763 OK** (Docker).
- **Follow-up**: `gui` is out of scope (338 pre-existing findings) — a future phase could extend the gate module by module, optionally with a `mypy-baseline` ratchet.

## [2026-10-11] Session: Toolchain Modernization (ruff 0.17 + mypy 2.4, drop black)
- **Achievement**: Completed the "lint/type" half of the toolchain refresh with the two upgrades deliberately held back from the safe batch: `ruff` 0.15.2 → **0.17.0** and `mypy` 1.19.1 → **2.4.0**, and removed the unused `black` dependency. No plugin-runtime impact.
- **Changes**:
    - **ruff**: `pyproject.toml` `ruff>=0.15.0` → `>=0.17.0`; `.pre-commit-config.yaml` `ruff-pre-commit` `v0.8.4` → `v0.17.0` (the project ruff and the hook had diverged). 0.17 adds `ISC004` (implicit string concatenation in a collection) and `PLR0917` (too many positional arguments): wrapped the 3 multi-line messages in `core/validation/validation_helpers.py` in explicit parentheses and extended the `# noqa` in `gui/adapters/drillhole_extractor.py`.
    - **Markdown**: ruff 0.17 now formats Python code blocks inside Markdown (it wanted to rewrite 381 `.md` docs). Added `**/*.md` to `[tool.ruff] exclude` so docs — and the vault/mirror gates — stay byte-stable.
    - **mypy**: `pyproject.toml` `mypy>=1.10` → `>=2.4.0`. `mypy .` reports the same 15 pre-existing findings (all in `scripts/`, `tests/`, `docs/`; none in plugin code) — no new errors from the major bump.
    - **black**: removed from the dev dependencies (unused; `ruff format` is canonical).
- **Quality**: `ruff check`/`format --check` clean · `uv run --frozen ruff check .` (CI parity) PASS · `pre-commit run ruff/ruff-format --all-files` PASS · `unittest discover tests` **763 OK** (Docker).
- **Follow-up**: `mypy` is not wired into CI and is mis-scoped (`mypy .` checks `scripts/`/`tests/`/`docs/` and bails early); consider a scoped `mypy core exporters` target if it should become a gate. `uv self update` (0.12.10 → 0.13.0) still pending.

## [2026-10-11] Session: Dependency Refresh (uv "safe batch")
- **Achievement**: Brought the `uv`-managed toolchain up to date with a deliberately **low-risk batch**, holding back the breaking upgrades. Adopted the ecosystem tool `qgis-manage` 0.9.0 → **0.9.2** (used by `make compile/deploy/package` and the release CI) plus a set of dev tools, with **no plugin-runtime impact**. `ruff`, `mypy` and `black` were intentionally left out (lint-rule/major-bump risk).
- **Changes**:
    - **Ecosystem**: `qgis-manage` 0.9.0 → 0.9.2; `qgis-stubs` 0.2.0.post1 → 0.5.0.
    - **Dev tools**: `bandit` 1.9.3 → 1.9.4, `flake8` 7.3.0 → 7.4.1, `pre-commit` 4.5.1 → 4.6.2, `pytest` 9.0.2 → 9.1.1, `pytest-mock` 3.15.1 → 3.16.0, `networkx` 3.6.1 → 3.7, `setuptools` 80.10.1 → 84.0.0, `sphinx-intl` 2.3.2 → 2.4.0, `sphinxcontrib-mermaid` 2.0.0 → 2.1.1, `myst-parser` 5.0.0 → 5.1.0, `linkify-it-py` 2.0.3 → 2.2.0 (+ transitives: `markdown-it-py`, `mdit-py-plugins`, `pycodestyle`, `pyflakes`; dropped `uc-micro-py`).
    - **Application**: `uv lock --upgrade-package …` (explicit list) via `--no-cache --refresh` + `uv sync`. `agent_metrics.json` untouched (no metric impact).
- **Quality**: `ruff check`/`format` clean · `unittest discover tests` **763 OK** (Docker) · `qgis-manage 0.9.2` packaging **smoke-tested** (`sec_interp.3.9.1.zip` built to `/tmp`, exit 0, repo clean) · `forge metrics validate` PASS.
- **Held back (deliberate)**: `ruff` 0.15.2 → 0.17.0 (new lint rules; must sync the pre-commit rev `v0.8.4` + CI + lock together) and `mypy` 1.19.1 → 2.4.0 (**major/breaking**). `black` is unused (`ruff format` is canonical) → candidate for removal.
- **Follow-up**: `uv self update` (0.12.10 → 0.13.0).

## [2026-10-11] Session: qgis-plugin-analyzer 1.16.0 Upgrade (Module-Coverage Fix + Triage)
- **Achievement**: Adopted `qgis-plugin-analyzer` **1.16.0** and, crucially, discovered that **1.15.2 was silently under-reporting module coverage**: the whole-project run analysed only **135** modules instead of the true **171** (the plugin's real `.py` count minus the 2 ignored root scripts). 1.16.0 fixed the discovery bug, so previously-ungated business logic (`core/validation/*`, `exporters/*`, `gui/adapters/*`, `gui/ui/pages/*`) is now analysed. All findings surfaced by the corrected coverage were triaged to keep the gates green.
- **Changes**:
    - **Dependency**: `qgis-plugin-analyzer>=1.15.2` → `>=1.16.0` (`pyproject.toml` deps + dev) via `uv lock --upgrade-package qgis-plugin-analyzer --no-cache --refresh` + `uv sync`.
    - **Coverage**: analysed modules **135 → 171** (matches `find core gui exporters plugin *.py` minus the 2 ignored root scripts). Proof it was a 1.15.2 bug: analysing `core/validation` alone, 1.15.2 saw all 12 modules; the whole-project run reported only 5.
    - **i18n triage**: 1.16.0 emitted **167 `MISSING_I18N`** (all in the 36 newly-covered modules; 0 in previously-covered ones → the rule itself did not change). Triaged to **0** via `[tool.qgis-analyzer.profiles.default.rules.MISSING_I18N] extra_ignore_calls` (`_stats_edit` / `_check_field` — strings translated internally via `self.tr`) plus **129 inline `# no-i18n`** tags (core is Qt-free by design; user-facing core-sourced messages are English and translating them requires injecting the GUI translator — tracked as debt).
    - **CC remediation**: refactored the **3 functions** that now exceeded `--max-cc 10` — `crs_plausibility.implausible_crs_reason` (14→7, split into `_geographic_out_of_bounds` / `_projected_maybe_geographic`), `export/handlers/topography.export_topography` (12→5, extracted `_export_profile_pair` / `_smoothed_topography`), `export/handlers/structures.export_structures` (11→7, extracted `_resolve_raster_resolution` / `_record_written`). `cc_gate` back to PASS.
    - **Metrics**: `agent_metrics.json` re-synced (quality 57.9 → **56.2**, maintainability 99.9, security 100.0, issues 35, `i18n_issues_qgis_analyzer` 0, `cc_gate` PASS, `module_size_gate` FAIL 4 modules); `meta.tools` → 1.16.0.
- **Quality**: `ruff check`/`format` clean · `unittest discover tests` **763 OK** (Docker) · `forge metrics validate` PASS · `sync_metrics --validate` PASS · `make context` fresh (**2,650/8,000 tokens**, 171 modules).
- **Backlog surfaced (newly gated, non-blocking)**: `module_size_gate` FAIL grows 1 → **4** (`core/controller.py` 428, `exporters/interpretation_3d_exporter.py` 466, `gui/adapters/geometry.py` 598, `gui/preview_layer_factory.py` 511); `GOD_OBJECT` 15 → 18 (rule now also flags classes with > 20 methods); core i18n debt (English-sourced user messages).
- **Maintenance**: [session_2026-10-11_qgis_analyzer_1_16_0.md](maintenance/session_2026-10-11_qgis_analyzer_1_16_0.md).

## [2026-10-11] Session: qgis-plugin-analyzer 1.15.2 Upgrade (B102 False-Positive Fix)
- **Achievement**: Adopted `qgis-plugin-analyzer` **1.15.2**, the upstream fix for the `B102`/`B307` false positives found on Qt `QDialog.exec()` during the 1.15.1 adoption. Security Score returns to 100.0 and the two spurious findings disappear.
- **Changes**:
    - **Dependency**: `qgis-plugin-analyzer>=1.15.1` → `>=1.15.2` (`pyproject.toml` deps + dev) via `uv lock --upgrade-package qgis-plugin-analyzer --no-cache --refresh` (stale-index workaround) + `uv sync`.
    - **Re-analysis**: `analyze . --max-cc 10` (175 files / 135 modules). Security Score 80.0 → **100.0**; total issues 34 → 32 (`SECURITY:B102` gone); `security.findings` empty.
    - **Metrics**: `agent_metrics.json` re-synced (`security_score`, `issue_breakdown`, ground truth); tool → 1.15.2.
    - **Upstream (same session)**: released qgis-plugin-analyzer **1.15.2** — `check_exec_eval` now ignores attribute/method calls; `release.yml` fixed so PyPI auto-publishes on release.
- **Quality**: `ruff check`/`format` clean · `unittest discover tests` **714 OK** · `forge metrics validate` PASS · `sync_metrics --validate` PASS · `make context` fresh.
- **Maintenance**: [session_2026-10-11_qgis_analyzer_1_15_2.md](maintenance/session_2026-10-11_qgis_analyzer_1_15_2.md).

## [2026-10-11] Session: qgis-plugin-analyzer 1.15.1 Upgrade (Security Scanning Restored)
- **Achievement**: Adopted `qgis-plugin-analyzer` **1.15.1**, the upstream fix for the disconnected security registry reported in the deep-analysis report. Security scanning now runs again (analyzer + `qgis-plugin-manager`, which delegates to it); it also ships the recommended hardening (shared `rules/scopes.py`, dead-code removal, lower complexity).
- **Changes**:
    - **Dependency**: `qgis-plugin-analyzer>=1.15.0` → `>=1.15.1` (`pyproject.toml` deps + dev) via `uv lock --upgrade-package qgis-plugin-analyzer --refresh`; `uv.lock` regenerated.
    - **Re-analysis**: `analyze . --max-cc 10` (175 files / 135 modules). Security Score 100.0 → **80.0** (scanner now executes); total issues 32 → 34 (+2 `SECURITY:B102`).
    - **Triage**: both `B102` are **false positives** on Qt `QDialog.exec()` (`gui/dialog_interpretation_manager.py:83`, `plugin/lifecycle.py:105`); the rule matches attribute calls and `# noqa` does not suppress it → flagged for an upstream fix (1.15.2).
    - **Parser fix**: `scripts/sync_metrics.py` now splits issue stats on the **last** colon, so the new `SECURITY:B102` rule-id is no longer dropped (`total_issues` was undercounted as 32).
    - **Metrics**: `agent_metrics.json` re-synced (`security_score`, `issue_breakdown`, ground truth); tool → 1.15.1.
- **Quality**: `ruff check`/`format` clean · `unittest discover tests` **714 OK** · `forge metrics validate` PASS · `sync_metrics --validate` PASS · `make context` fresh.
- **Maintenance**: [session_2026-10-11_qgis_analyzer_1_15_1.md](maintenance/session_2026-10-11_qgis_analyzer_1_15_1.md).

## [2026-10-11] Session: qgis-plugin-analyzer 1.15.0 Upgrade
- **Achievement**: Adopted `qgis-plugin-analyzer` **1.15.0** ("Repo Hygiene & Hardening") and refreshed ground-truth metrics. Tooling-only change (no plugin runtime code touched). The release adds anti-pattern detection (`GOD_OBJECT`, `SPAGHETTI_CODE`), Halstead metrics, module optimization suggestions, a transversal `# noqa`, `--workers N`, and a reliable ruff audit.
- **Changes**:
    - **Dependency**: `qgis-plugin-analyzer>=1.14.0` → `>=1.15.0` (`pyproject.toml` deps + dev) via `uv lock --upgrade-package qgis-plugin-analyzer --refresh`; `uv.lock` 1.14.0 → 1.15.0.
    - **Re-analysis**: `qgis-analyzer analyze . --max-cc 10` (175 files / 135 modules). Scores unchanged (Stability 57.9, Maintainability 99.9, Security 100.0, type-hints 95.2/99.5%, docstrings 98.5%); **total issues 16 → 32** from the new rules (15 `GOD_OBJECT`, 1 `SPAGHETTI_CODE`).
    - **Metrics**: `scripts/sync_metrics.py` refreshed `agent_metrics.json` (`issue_breakdown`, `ground_truth_sources`); `meta.tools.qgis-plugin-analyzer` → 1.15.0.
- **Quality**: `ruff check`/`format` clean · `unittest discover tests` **714 OK** · `forge metrics validate` PASS · `sync_metrics --validate` PASS · `make context` fresh.
- **Backlog (new, non-blocking)**: 15 `GOD_OBJECT` (GUI orchestrators > 15 attrs) + 1 `SPAGHETTI_CODE` (`drillhole_exporters.py::_write_traces`); `module_size_gate` still FAIL (`core/controller.py` 428 > 400).
- **Maintenance**: [session_2026-10-11_qgis_analyzer_1_15_0.md](maintenance/session_2026-10-11_qgis_analyzer_1_15_0.md).

## [2026-10-10] Session: ai-context-core v5.1.0 Adoption
- **Achievement**: Adopted `ai-context-core` **v5.1.0** ("Context Alignment & Hardening"), a **backward-compatible** release (no command/artifact contract removed). It turns off the token-heavy Mermaid styling by default, ships a default token budget, drops the retired analysis domains from `project_context.json`, and makes the unused-import detector honor `# noqa`.
- **Changes**:
    - **Dependency**: `ai-context-core>=5.0.1` → `>=5.1.0` (`pyproject.toml` deps + dev; `uv.lock`).
    - **Config**: `.ai-context/config.toml` aligned — `max_tokens` `6000` → `8000` + explicit `mermaid_style = false`.
    - **Metrics**: `agent_metrics.json` tool version → `5.1.0`; `context_tokens` `619` → `2639` (was stale).
- **Quality**: `ruff check`/`format` clean · `forge metrics validate` PASS · `unittest discover tests` **714 OK** · `make context` fresh (**2,639/8,000 tokens**).
- **Maintenance**: [session_2026-10-10_ai_context_core_v510.md](maintenance/session_2026-10-10_ai_context_core_v510.md).

## [2026-10-10] Session: ai-context-core Value Leverage (Context as a First-Class Session Input)
- **Achievement**: Turned `ai-context-core` from a stale, unused artifact into an always-fresh, curated session input. The keystone was fixing `.analyzerignore`, which scoped **both** `ai-ctx` and `qgis-plugin-analyzer` to `gui/` only — leaving `core/` and `exporters/` ungated. Scope now covers all plugin code: **71 → 135 modules**.
- **Changes**:
    - **Scope**: `.analyzerignore` rewritten (include `core/`, `gui/`, `exporters/`, `sec_interp_plugin.py`).
    - **Config v5**: `.ai-context/config.toml` rewritten (`[sources] external`, `[context]`, `[context.budget]`, `context_docs`); dead v4 keys removed.
    - **Curated context**: new `.ai-context/architecture_notes.md` + `docs/CORE_DISTINCTION_GUIDE_EN.md`; `AI_CONTEXT.md` = 2,639/6,000 tokens, 135 modules, no `antigravity-framerepo` leak.
    - **Freshness**: `make context` (+ `context-deps/git/roadmap/graph/health`); new "Context & Architecture Tooling" section in `AGENTS.md`.
    - **Wiring**: `docs/structure/architecture.mmd` (Mermaid) via `make context-graph`.
    - **Hygiene**: `README_DEV.md` + v5.0.0 session doc corrected; 44 dead legacy `.ai-context/` files removed; local `antigravity-framerepo/` deleted.
    - **Metrics**: `agent_metrics.json` re-synced (quality 56.9 → **57.9**, issues 4 → 16).
- **Quality**: `ruff check`/`format` clean · `forge metrics validate` PASS · `check_docs` PASS (36 docs) · CC gate PASS · i18n PASS.
- **Newly surfaced (backlog, deferred until after the release train)**: `module_size_gate=FAIL` (`core/controller.py` 428 > 400); 10 `MISSING_DOCSTRING`; 4 `NON_PYTHONIC_LOOP`; 2 `POTENTIAL_MISSING_SLOT`; +6 signal-leak heuristics.
- **Maintenance**: [session_2026-10-10_ai_context_core_value.md](maintenance/session_2026-10-10_ai_context_core_value.md).

## [2026-10-10] Session: agentic-forge v1.2.0 Migration (Submodule + QGIS Domain Pack)
- **Achievement**: Aligned SecInterp's agentic system with the genericized `agentic-forge` **v1.2.0**, bumping the `.agent/` submodule `a77548b` (v1.1.0) → `2de22cf` (v1.2.0) — the same revision already pinned by `ai-context-core` and `qgis-plugin-manager`. The QGIS skills/workflows extracted upstream to `scaffold/qgis/` are now **mounted as a project overlay** (`.agent-state/`), so framework updates no longer drop them.
- **Changes**:
    - **Submodule**: `.agent` `a77548b` → `2de22cf` (`v1.2.0`, `git merge --ff-only origin/main`).
    - **Overlay**: `.agent-state/skills/{qgis-core,qgis-migration-4x,ui-framework}` + `.agent-state/workflows/{audit-plugin,release-plugin,run-tests-in-qgis}.md`.
    - **`opencode.json`**: `skills.paths` → `[".agent/skills", ".agent-state/skills"]` (restart required).
    - **`AGENTS.md`**: 3 QGIS skills + 3 QGIS workflows repointed to `.agent-state/`; added `testing-standards`; clarified framework/overlay split.
    - **Fixes**: `gui/AGENTS.md`, `core/AGENTS.md`, `docs/research/TESTING_STRATEGIES.md` paths; `ai-ctx analyze .` → `--path .` in `README_DEV.md` + `docs/docsec/DEVELOPMENT_GUIDE*.md`.
- **Quality**: `forge validate` → 14 skills / 14 workflows, all pass · no dangling refs in living docs · no plugin code touched · `ai-ctx verify` fresh.
- **Maintenance**: [session_2026-10-10_agentic_forge_v120_migration.md](maintenance/session_2026-10-10_agentic_forge_v120_migration.md).

## [2026-10-10] Session: ai-context-core v5.0.1 Adoption
- **Achievement**: Adopted `ai-context-core` **v5.0.1** ("Post-Release Cleanup"), a patch release that follows the v5.0.0 context-only contract with **no command or artifact contract change**. Internal consolidation only: `analyze` now uses a single `compile_context → render_context` path for every source, and upstream residue (`ContextAggregator` alias, `deprecations`, `graph_engine`, duplicate Halstead helpers) was removed.
- **Changes**:
    - **Dependency**: `ai-context-core>=5.0.0` → `>=5.0.1` (`pyproject.toml` + `uv.lock` via `uv lock --no-cache` + `uv sync --no-cache`).
    - **Artifacts**: `AI_CONTEXT.md`, `PROJECT_SUMMARY.md`, `project_context.json`, `context_manifest.json` regenerated via `ai-ctx analyze --path . --no-cache` (source: external).
    - **Metrics**: `agent_metrics.json` tool version `5.0.0` → `5.0.1`.
- **Quality**: `ai-ctx verify` → `Context is fresh.` (exit 0) · context bundle **619 tokens** (structure 311 / metrics 90 / dependencies 40 / git 160) · quality score 56.9 (external, qgis-analyzer) · no `ai_context_core` imports in plugin runtime (CLI-only).
- **Maintenance**: [session_2026-10-10_ai_context_core_v501.md](maintenance/session_2026-10-10_ai_context_core_v501.md).

## [2026-10-10] Session: ai-context-core v5.0.0 Adoption (Scoped)
- **Achievement**: Adopted `ai-context-core` **v5.0.0**, a breaking major that repositions `ai-ctx` as a **context-only compiler** (`context` / `git` / `roadmap` / `verify` / `symbols`). The adoption is **scoped**: all quality gates (CC, i18n, module size, security, QGIS compliance) stay **single-sourced** in `qgis-plugin-analyzer`, resolving the documented "Multi-Tool Scope Mismatch".
- **Changes**:
    - **Dependency**: `ai-context-core>=4.1.1` → `>=5.0.0` (`pyproject.toml` + `uv.lock` via `uv lock` + `uv sync`).
    - **Removed commands** (`audit`, `qgis`, `security`, `patterns`, `inspect`, `fix`, `scaffold`, `doctor`, `interactive`, `serve`, `full-scan`); **new** `health`, `verify`, `symbols`; `analyze`/`context` kept.
    - **Artifacts**: `AI_CONTEXT.md`, `PROJECT_SUMMARY.md`, `project_context.json` regenerated via `ai-ctx analyze --path . --no-cache` (source: external) plus the new `context_manifest.json`; `.gitignore` updated.
    - **Metrics**: `agent_metrics.json` tool version `4.1.1` → `5.0.0`; obsolete `ai_context` block (from removed `ai-ctx qgis`) replaced by a context-only block.
- **Quality**: `ai-ctx verify` → `Context is fresh.` (exit 0) · context bundle **619 tokens** (structure 311 / metrics 90 / dependencies 40 / git 160) · `AI_CONTEXT.md` now context-only · no `ai_context_core` imports in plugin runtime (CLI-only).
- **Maintenance**: [session_2026-10-10_ai_context_core_v500.md](maintenance/session_2026-10-10_ai_context_core_v500.md).

## [2026-10-08] Session: ai-context-core v4.1.1 Adoption
- **Achievement**: Adopted `ai-context-core` **v4.1.1** ("Report Correctness Fixes"), resolving all five defects (F1–F5) from the v4.1.0 improvement report and removing the manual `ai-ctx clean` workaround. The cache is now versioned (`_meta`), security severities are real, intentional `__init__.py` re-exports are no longer flagged, git churn is code-scoped, and the generic Processing note is conditional. ai-ctx Quality Score unchanged at **68.2**.
- **Changes**:
    - **Dependency**: `ai-context-core>=4.1.0` → `>=4.1.1` (`pyproject.toml` + `uv.lock` via `uv lock --upgrade-package ai-context-core --refresh` + `uv sync`).
    - **Artifacts**: `AI_CONTEXT.md`, `PROJECT_SUMMARY.md`, `project_context.json` regenerated via `ai-ctx full-scan` (no manual cache clean needed).
    - **Metrics**: `agent_metrics.json` tool version `4.1.0` → `4.1.1`.
- **Quality**: ai-ctx Quality Score **68.2/100** · QGIS Compliance **85.0/100** · i18n **303/438 (69.2%)** · Edges 60 · Qt6-ready (no `PyQt5` imports) · no `ai_context_core` imports in plugin runtime (CLI-only).
- **Maintenance**: [session_2026-10-08_ai_context_core_v411.md](maintenance/session_2026-10-08_ai_context_core_v411.md).

## [2026-10-08] Session: ai-context-core v4.1.0 Adoption
- **Achievement**: Adopted `ai-context-core` **v4.1.0** ("Context Map & Debt Prioritization"), adding a context-only mode (`ai-ctx context`), configurable `[context].sections`, anti-pattern tuning (`allowlist`/`min_severity`), and fixes for import-graph resolution, realistic churn, and `__future__` unused-import false positives. ai-ctx Quality Score unchanged at **68.2**.
- **Changes**:
    - **Dependency**: `ai-context-core>=4.0.0` → `>=4.1.0` (`pyproject.toml` + `uv.lock` via `uv lock --upgrade-package ai-context-core` + `uv sync`).
    - **Artifacts**: `AI_CONTEXT.md`, `PROJECT_SUMMARY.md`, `project_context.json` regenerated via `ai-ctx full-scan`.
    - **Metrics**: `agent_metrics.json` tool version `4.0.0` → `4.1.0`.
- **Quality**: ai-ctx Quality Score **68.2/100** · QGIS Compliance **85.0/100** · i18n **303/438 (69.2%)** · Qt6-ready (no `PyQt5` imports) · no `ai_context_core` imports in plugin runtime (CLI-only).
- **Maintenance**: [session_2026-10-08_ai_context_core_v410.md](maintenance/session_2026-10-08_ai_context_core_v410.md).

## [2026-10-08] Session: ai-context-core v4.0.0 Adoption
- **Achievement**: Adopted `ai-context-core` **v4.0.0**, which removes the deprecated compatibility facades and dead `CheckerRegistry` chain, and surfaces anti-pattern detections (God Object, Spaghetti, Magic Numbers, Dead Code) that were previously computed but never rendered. ai-ctx Quality Score unchanged at **68.2**.
- **Changes**:
    - **Dependency**: `ai-context-core>=3.5.0` → `>=4.0.0` (`pyproject.toml` + `uv.lock` via `uv lock --upgrade-package ai-context-core` + `uv sync`).
    - **Artifacts**: `AI_CONTEXT.md`, `PROJECT_SUMMARY.md`, `project_context.json` regenerated via `ai-ctx full-scan`.
    - **New output**: `AI_CONTEXT.md` now has a `⚠️ DETECTED ANTI-PATTERNS` section (Magic Number findings in `gui/adapters/*`).
    - **Metrics**: `agent_metrics.json` tool version `3.3.0` → `4.0.0`.
- **Quality**: ai-ctx Quality Score **68.2/100** · QGIS Compliance **85.0/100** · i18n **303/438 (69.2%)** · Qt6-ready (no `PyQt5` imports) · no `ai_context_core` imports in plugin runtime (CLI-only).
- **Maintenance**: [session_2026-10-08_ai_context_core_v400.md](maintenance/session_2026-10-08_ai_context_core_v400.md).

## [2026-10-08] Session: Unify Agentic Systems on agentic-forge
- **Achievement**: Unified the agentic systems of the three sibling projects (`qgis-plugin-analyzer`, `ai-context-core`, `qgis-plugin-manager`) onto the **agentic-forge** framework (`v1.2.0`, Codeberg). No SecInterp code changed — this session coordinated the sibling repos.
- **Changes**:
    - **Upstream**: genericized `agentic-forge` core (9 skills + 14 workflows), extracted QGIS domain to `scaffold/qgis/`, added `testing-standards` + `release-package`/`audit-package`, tagged `v1.2.0`.
    - **analyzer**: submodule + `forge.toml` + `.agent-state/` + overlay; removed legacy `.ai-context/`/`scaffold/`/scripts/`ai-context-core` dep.
    - **ai-context-core**: same pattern; overlay `domain-logic`, `project-context`, `debug-specialist`, `skill-authoring`, `tech-stack`.
    - **manager**: Gen 5 → Gen 8 (root `AGENTS.md` + `opencode.json` + submodule); removed `skill_sync.py`.
- **Quality**: `forge validate` green on all three; `pytest` 126 / 299 / 190 passed.
- **Maintenance**: [session_2026-10-08_unify_agentic_systems.md](maintenance/session_2026-10-08_unify_agentic_systems.md).

## [2026-10-06] Session: ai-context-core v3.5.0 Adoption
- **Achievement**: Adopted `ai-context-core` **v3.5.0**, resolving all active correctness findings (A1–A5) from the v3.4.0 improvement report and enabling an explainable **Score Breakdown**. Regenerated the project analysis; ai-ctx Quality Score **36.2 → 68.2**.
- **Changes**:
    - **Dependency**: `ai-context-core>=3.4.0` → `>=3.5.0` (`pyproject.toml` + `uv.lock`).
    - **Config**: dropped the global `__init__.py` pattern from `.analyzerignore` so the plugin entry point (`classFactory`) is detected; modules 66 → 76.
    - **Artifacts**: `AI_CONTEXT.md`, `PROJECT_SUMMARY.md`, `project_context.json` regenerated via `ai-ctx full-scan`.
    - **Docs**: v3.5.0 verification addendum added to `improvement_report_v3.4.0.md`.
- **Quality**: `Test Files: 137` (was artificially 0) · QGIS Compliance **85.0/100** · i18n **303/438 (69.2%)** · Maintainability **43.8** · avg CC **13.2**.
- **Maintenance**: [session_2026-10-06_ai_context_core_v350.md](maintenance/session_2026-10-06_ai_context_core_v350.md).

## [2026-10-04] Session: Offline Help — User Guide only
- **Achievement**: The in-plugin **Help** button now opens an offline manual that contains **only the User Guide** (clean navigation, no dead links) in all 14 languages, without changing the plugin code and without affecting the published website. Also evaluated **graphify** (local code graph, git-ignored).
- **Changes**:
    - **Help build**: new `docs/source/help_index.rst` (USER_GUIDE-only master doc); `conf.py` excludes the other docs when `SECINTERP_DOCS_HELP=1` and hides `help_index.rst` from the site build; `build_docs.sh` splits **web** (`index.rst`) and **help** (`root_doc=help_index`) passes and renames `help_index.html` → `index.html` (patching links) so the Help button keeps working.
    - **Hygiene**: `.gitignore` now ignores `graphify-out/`.
    - **graphify** (dev-only): 192 files / 2929 nodes / 5216 edges; `benchmark` 13.7× token reduction.
- **Quality**: ruff (check + format) clean · pre-commit PASS · local `unittest discover tests` **714 OK** · full help build exercised for 14 locales (only `index.html` + `USER_GUIDE.html`); website output verified intact.
- **Maintenance**: [session_2026-10-04_help_userguide_only.md](maintenance/session_2026-10-04_help_userguide_only.md).

## [2026-10-04] Session: Agentic Forge Extraction (F1–F5)
- **Achievement**: Extracted the reusable agentic framework from SecInterp and published it on Codeberg as `agentic-forge` (MIT), consumed as a git submodule at `.agent/`; project state moved to `.agent-state/`; generic tooling exposed via `.agent/tools/forge.py`; `sync_metrics` split into a generic core plus a project collector.
- **Changes**:
    - **F1**: state -> `.agent-state/`; `forge.toml` + `scripts/forge_paths.py` path contract; tooling made path-aware.
    - **F2**: project skills -> `.agent-state/skills/` overlay; genericized `README`/`QUICK_REFERENCE`; **MIT** LICENSE; `export_agentic_forge.sh`; published (no history, public).
    - **F3**: `.agent/` -> git submodule; CI uses `submodules: recursive`.
    - **F4**: governance (`update_agentic_forge.sh`, tag `v1.0.0`, `FRAMEWORK_SYNC_GUIDE`).
    - **F5**: `forge` CLI + generic tools in `.agent/tools/`; split `sync_metrics` (generic `forge_metrics.py` + project collector); thresholds -> `forge.toml`.
    - **Fix**: framework `AGENTS.md` (was a broken compatibility pointer) -> framework default config.
- **Quality**: Docker suite green (23/237/40/323/76) - `forge validate` (13 skills) - `sync_metrics --validate` - `check_docs` - pre-commit.
- **Maintenance**: [session_2026-10-04_agentic_forge_extraction.md](maintenance/session_2026-10-04_agentic_forge_extraction.md).
- **Note**: framework at `codeberg.org/geociencio/agentic-forge` (`main` a77548b; tags v1.0.0/v1.1.0); pending repo description + topics.

## [2026-10-04] Session: v3.9.1 Release Follow-up, Docs v2-First & ZIP/CI Fixes
- **Achievement**: Published the scheduled v3.9.1 release manually, merged `release/v3.9.1` into `main`, froze the v1 docs vault, refreshed the v2 vault/architecture docs to v3.9.1, applied agentic quick wins, and fixed the release pipeline so the ZIP includes the (now optimized) offline help.
- **Changes**:
    - **Release**: `workflow_dispatch` publish of v3.9.1; merged `release/v3.9.1` into `main` (tests 745 -> 763); replaced the release asset with the fixed/optimized ZIP.
    - **Docs**: README + canonical architecture/report docs -> v3.9.1; v1 vault frozen (`sync_vault_mirrors.sh`); v2 vault footers (356) + structure docs updated.
    - **Agentic**: `black` -> `ruff format`, phantom refs and stale counts fixed, Gen 8 plan marked done, `qgis-migration-4x` referenced.
    - **Packaging/CI**: scheduled-release builds the offline help; `build_docs.sh` deduplicates shared `_static` and optimizes PNGs; `.release-queue.json` excluded. Offline help 8.5 -> 3.7 MiB; ZIP 3.76 -> 2.38 MiB.
- **Quality**: Docker suite green (23/237/40/323/76) - ruff/check_docs/check_notes/validate_agent_system PASS - analyzer 0 issues.
- **Maintenance**: [session_2026-10-04_v391_release_docs_v2_zip_fixes.md](maintenance/session_2026-10-04_v391_release_docs_v2_zip_fixes.md).
- **Note**: pending divergence `gui/legend_widget.py` (train branches vs `main`) to resolve when merging `v3.11.0`.

## [2026-10-11] Release: v3.10.0 — Interactive Preview Legend
- **Milestone**: Third release of the incremental train from v3.8.0 (scheduled). Moves the legend into an interactive side panel and adds per-unit controls and drillhole lithologies.
- **Highlights**: collapsible preview side panel with interpretations list; hide/color per geological unit (preview + export, persisted); drillhole interval lithologies in the legend.
- **Artifacts**: `sec_interp.3.10.0.zip`; release notes [v3.10.0](releases/notes/v3.10.0.md).

## [2026-10-04] Release: v3.9.1 — Optional Smoothed Topography Profile
- **Milestone**: Second release of the incremental train from v3.8.0 (scheduled). Adds the optional smoothed topography profile and geology that follows it.
- **Highlights**: Smooth control (window 10–500 m) overlaying a smoothed profile; extra `*_smoothed` export files; geology follows the smoothed profile while structures/drillholes keep raw sampling.
- **Artifacts**: `sec_interp.3.9.1.zip`; release notes [v3.9.1](releases/notes/v3.9.1.md).

## [2026-09-27] Session: Release Train Scheduling, CI Hardening & Vault Refresh
- **Achievement**: Released **v3.9.0** and prepared the incremental train **v3.9.1 / v3.10.0 / v3.11.0** on cumulative release branches, published automatically on consecutive Sundays (`scheduled-release.yml` + `.release-queue.json`, dry-run validated). Repaired the project **CI** (now green on `main`) and refreshed the bilingual **Code Walkthrough v2 vault to v3.9.0**.
- **Changes**:
    - **Release**: v3.9.0 tag + GitHub release (portal upload skipped by decision); fixed a release-blocking `tests/gui` mock-isolation bug (`tests.base_test` import duplication).
    - **CI**: lint pinned to the locked ruff; real Qt6 finding detection; test job migrated to the project Docker image; docs deploy skipped without `DOCS_DEPLOY_TOKEN`; legacy `release.yml` removed.
    - **QGIS 4**: `QgsRasterBandStats.Stats.All` + `Qgis.RasterBandStatistic.All` fallback in `dem_page.py` (cherry-picked to all release branches).
    - **Vault v2**: enriched `preview_param_hasher` / `ui_status_manager`, added `crs_plausibility` / `layer_metadata` / `topo_renderer`, footers to v3.9.0, Index/hubs/map updated (`check_notes --strict` PASS, 308 notes).
- **Quality**: main 696 tests OK / Docker 681 OK · analyzer 0 issues · security PASS · CI all green.
- **Maintenance**: [session_2026-09-27_release_train_and_vault_refresh.md](maintenance/session_2026-09-27_release_train_and_vault_refresh.md).

## [2026-09-27] Release: v3.9.0 — DEM/Section Insights, CRS Safety & Adaptive VE
- **Milestone**: First release of the incremental train from v3.8.0. Integrates the DEM/Section featureset on top of the unreleased `main` work (Adaptive VE, module-size refactor, documentation vaults).
- **Highlights**: CRS safety (mixed-CRS warning, mislabelled-CRS block, cross-CRS reprojection, freeze fix); DEM band statistics; profile-vs-DEM statistics; topographic profile color mode; Adaptive Vertical Exaggeration (`Auto`, 0.5×–20×); preview scratch-layer cleanup.
- **Quality**: 696 tests OK · CC ≤ 10 · i18n gate PASS · security scan clean · docstrings 100% · `qgis-analyzer` 0 issues.
- **Artifacts**: `sec_interp.3.9.0.zip`; release notes [v3.9.0](releases/notes/v3.9.0.md).

## [2026-09-23] Session: Live Symbology & Legend Styling (Goal 1.1 / v3.11.0)
- **Achievement**: Advanced Goal 1.1 through Fases 1–3 — a Settings → Symbology tab with live per-layer styles, a shared per-unit editor (hide/color/rename/reorder), and configurable legend layout (position/font/max items) — plus real-QGIS UI layout fixes so the dialog no longer covers the screen. 11 commits (`ba62083a..63b47c99`). Fase 4 (presets) pending.
- **Changes**:
    - **Fase 1**: Settings → Symbology tab (topo mode moved from Section; structures/drillhole/interp styles); `layer_styles` plumbed through the render pipeline; project persistence.
    - **Fase 2**: shared `UnitStyleEditor`; `ColorManager` labels/order; aliases/order reflected in panel + exported legend; "Reset unit styles".
    - **Fase 3**: `PreviewLegendRenderer.draw_rows(layout)` with position (top/bottom × left/right), font size (6–16) and max items ("+N more").
    - **Legend**: real symbology; Geology vs Drillhole lithologies headers; interpretations included and editable; overlap fix.
    - **Layout fixes**: Symbology in a `QScrollArea`; `QgsCollapsibleGroupBox` sections (collapsed by default); dialog height bounded to screen; Settings fills its height; Units list 220 → 340 px. Root cause: collapsible groups don't shrink their minimum until shown (dialog min 1007 → 692 px).
- **Quality**: 743/743 tests OK · `ruff`/format clean · analyzer 0 issues · layout measured on real QGIS 4.2.1 · Qt imports verified.
- **Maintenance**: [session_2026-09-23_symbology_legend_styling.md](maintenance/session_2026-09-23_symbology_legend_styling.md)

## [2026-09-23] Session: Smoothed Geology (v3.9.1) + Preview Side Panel (v3.10.0)
- **Achievement**: Geology now follows the smoothed profile (v3.9.1, Option A), and the preview legend moved off the canvas into a collapsible side panel with an interpretations list and per-unit hide/color controls (v3.10.0, Goal 1.1 core), including drillhole interval lithologies. 10 commits (`1e2a4ea9..471017b`).
- **Changes**:
    - **v3.9.1**: `PreviewParams.smooth/smooth_window` + hash; `GeologyExtractor.extract_context(smoothing_window_m)` smooths the master profile; controller/orchestrator pass the window; Smooth invalidates S2. Structures/collars/stats stay raw.
    - **v3.10.0 L-A**: new `gui/preview_side_panel.py` (legend + interpretations); canvas|panel `QSplitter` (persisted); overlay `LegendWidget` removed; export legend unchanged.
    - **v3.10.0 L-B**: `ColorManager` overrides/hidden/registry (dump/load); `build_categorized_line_style(hidden=…)`; per-unit visibility + color (QColorDialog) and persistence (`DialogSettingsPersistence.unit_style`); drillhole "Drillholes" entry + interval lithologies.
    - **Fixes**: `QColorDialog` import (QtWidgets); orphan "QGIS4" windows (deleteLater); interpretations list refreshed on load/render.
- **Quality**: 729/729 tests OK · `ruff`/format clean · analyzer 0 issues · Qt imports verified on real QGIS 4.2.1 · smoke OK.
- **Maintenance**: [session_2026-09-23_smoothed_geology_and_side_panel.md](maintenance/session_2026-09-23_smoothed_geology_and_side_panel.md)

## [2026-09-23] Session: Optional Smoothed Topography Profile
- **Achievement**: Added an optional smoothed topography profile — a Smooth control in the preview Controls overlays a soft-red smoothed line on the colored profile and the export writes extra smoothed CSV/vector files. 2 commits (`3094a1f1`, `76fc6206`).
- **Changes**:
    - **Core**: `smooth_profile_by_distance` (centered moving average over a distance window, endpoints preserved; stdlib only).
    - **Controls**: Smooth checkbox + Window (m) spin (10–500, off by default), persisted; re-render from cache without invalidating S2. Preview misc signal wiring refactored to loops to stay under the 400-line gate.
    - **Preview**: new "Smoothed Topography" soft-red layer above the profile; both listed in the legend.
    - **Export**: adds `topo_profile_smoothed.csv` and `profile_line_smoothed.<ext>` when enabled (raw unchanged).
- **Quality**: 710/710 tests OK · `ruff`/format clean · analyzer 0 issues · gates CC/Module Size/i18n PASS · smoke QGIS 4 OK.
- **Maintenance**: [session_2026-09-23_smoothed_profile.md](maintenance/session_2026-09-23_smoothed_profile.md)

## [2026-09-23] Session: DEM/Section v3.9.0 Phases (1.5, 1.6, 2, 3)
- **Achievement**: Completed the v3.9.0 DEM/Section plan — band statistics on the DEM page, a central section-feature resolver (prep multi-line), topographic profile color mode (gradient/single) and profile-vs-DEM statistics. 6 commits (`2a14767b..6d342189`).
- **Changes**:
    - **Fase 1.5**: `resolve_section_feature/geometry/start_point` in `gui/adapters/geometry.py`; migrated the 8 extractor/preview sites with `feature_id=None`; threaded `section_feature_id` through `PreviewParams`/hasher/`ValidationParams`/`SectionPage`/`InputManager`; mocks honor `fid`/`limit`.
    - **Fase 1.6**: read-only DEM band Min/Max/Mean/NoData (bounded sample, NaN-safe); wider raster combo + abbreviated units.
    - **Fase 2**: "Profile Style" (Gradient/Simple + `QgsColorRampButton`/`QgsColorButton`) persisted and plumbed to `TopoRenderer` (single → `QgsSingleSymbolRenderer`; gradient ramp with `Spectral→RdYlGn` fallback).
    - **Fase 3**: `ProfileRasterStats` + `profile_raster_statistics` (dedupe per pixel cell); "DEM Profile" group on the Section page fed by an injected DEM provider.
- **Quality**: 696/696 tests OK · `ruff`/format clean · analyzer **0 issues** · smoke QGIS 4 PASS.
- **Maintenance**: [session_2026-09-23_dem_section_v390_phases.md](maintenance/session_2026-09-23_dem_section_v390_phases.md)

## [2026-09-23] Session: CRS Sampling Hardening + Structure/Section UX Fixes
- **Achievement**: Fixed a machine-freezing failure when sampling a geographic DEM (EPSG:4326, misleadingly named `..._3857.tif`) with a projected section line under on-the-fly reprojection — the densify interval was taken from the raster pixel size and applied as line map units. Also fixed silent zero elevations for structures/collars across CRSs, added a blocking mislabelled-CRS heuristic, and fixed structural field combos. 6 commits (`baf11d8c..eb9ffa20`).
- **Changes**:
    - **Freeze/CRS sampling**: `MAX_DENSIFY_POINTS` cap in `densify_line_points`; `build_sampling_transform` / `raster_resolution_in_crs` / `resolve_sampling_interval` in `gui/adapters/geometry.py`; CRS-aware interval + point reprojection in profile/geology/structure/drillhole extractors and `render_pipeline`; dip-line resolution guard in `export/handlers/structures.py`.
    - **Mislabelled CRS (blocking)**: new `core/validation/crs_plausibility.py` + `CrsPlausibilityValidator` in `validate_all`/`validate_preview_requirements`; `LayerMetadata` extent/pixel fields; `InputManager` + `UIStatusManager` surface red dot + one-time remediation message; non-blocking mismatch stays amber.
    - **Structural UX**: `StructurePage` wiring moved into idempotent `connect_signals()` (was lost after `SignalManager.connect_all` → empty field combos).
    - **Pending UI gating** from the previous crashed session committed (`98758e92`).
- **Quality**: 666/666 tests OK · `ruff` + `ruff format` clean · manual QGIS 4 smoke PASS (no freeze; 430 pts/6109 m = 14.24 m; structures on profile; interpretations persist; GPKG/PNG export OK).
- **Maintenance**: [session_2026-09-23_crs_sampling_hardening.md](maintenance/session_2026-09-23_crs_sampling_hardening.md)

## [2026-09-23] Session: DEM/Section Enhancement Planning (Plan Mode)
- **Achievement**: Defined the DEM/Raster + Section Line scope (raster stats, 2-point simple-line invariant, profile-vs-DEM stats with same-pixel dedupe, selectable gradient/single topo color, Mandatory labels, S0/S1/S2 button gating, Geology/Structural/Drillholes page blocking) and wrote the phased plan `docs/plans/implementation_plan_dem_section_v3.9.0.md` (Fase 0→3, open decisions, LTR 3.44.14 compat matrix). No code changed; saved for next session (build mode).
- **Quality**: `ruff` PASS · local suite 594 tests OK · planning only, no CHANGELOG entry (no user-visible changes).
- **Maintenance**: [session_2026-09-23_dem_section_planning.md](maintenance/session_2026-09-23_dem_section_planning.md)

## [2026-09-23] Session: Code Walkthrough Vault v2 (Completion)
- **Achievement**: Completed the bilingual v2 vault: enriched Core 49 + GUI 73 + Exporters/Plugin/Root 22, added 23 `layer_*` hubs, finalized the bilingual `Index.md` MOC, and added a vault-owned file-to-note map (`project_structure_links.md`, 178 files → 151 notes). 5 commits (`1d4af77d`, `d5e8a82b`, `b7d221f7`, `dab9d27e`, `26ada077`).
- **Tooling**:
    - `scripts/generate_vault_v2.py`: shared `resolve_group_slugs()` — a Tier C package group never overwrites an individual file note (`resources/` → `resources_pkg`) and the repo root maps to `root` instead of `_`.
    - `scripts/check_notes.py`: same function in `build_expectations()` (single ground truth); SKIP_STEMS extended with the 23 hub slugs + `project_structure_links`.
    - New `scripts/generate_structure_links.py` (`--write`/`--check`) reusing the canonical slug logic.
    - Slug fixes: `core/utils/__init__.py` note `utils` → `core_utils___init___py`; `gui/utils.py` → `gui_utils_py` (canonical, zero slug warnings).
- **Docs**: 302 substantive notes + 46 hubs + final MOC, fully bilingual (ES+EN); fixed ~26 dangling wikilinks from earlier phases; verbatim `project_structure*` mirrors left untouched.
- **Quality**: docs-only (no plugin Python changed). `check_notes.py --strict` PASS (302 notes / 0 skeletons / 0 dangling links) · `check_docs.py` PASS · `sync_vault_mirrors.sh --check` PASS · `ruff` PASS · local suite 594 tests OK.
- **Maintenance**: [session_2026-09-23_vault_v2_completion.md](maintenance/session_2026-09-23_vault_v2_completion.md)

## [2026-09-22] Session: Code Walkthrough Vault v2 (Complete Bilingual Vault)
- **Achievement**: Started a new self-contained bilingual code-walkthrough vault v2 (`docs/code_walkthrough_v2/` ES + `docs/code_walkthrough_en_v2/` EN), leaving v1 untouched, with a 400–500-line depth standard and tooling to generate and gate the notes. 2 commits (`46fd3b45`, `59f3984`).
- **Tooling**:
    - `scripts/generate_vault_v2.py`: AST tiering (A/B/C), collision-safe slugs, package file enumeration, `HIGH_IMPORTANCE` → `note_lines: 700`, `--layer` filter, and a `_is_skeleton` guard so `--write` refreshes skeletons but never clobbers enriched notes.
    - `scripts/check_notes.py`: 400–500 line gate (tiered minimums A/C 400, B 300; ceiling 500 or `note_lines` up to 700), placeholder detection (`--strict`), ES↔EN slug parity.
    - `scripts/check_docs.py` (+v2 exclusions) and `scripts/sync_vault_mirrors.sh` (structure docs → v2 vaults).
- **Docs**: added `docs/structure/project_structure_table.md` (tabular Depth 1–5 view); 56 Core skeletons generated; 7 Core notes enriched (controller 500, drillhole 408, path_resolver 306, core_interfaces 423, dtos 407, entities 401, exceptions 307).
- **Quality**: docs-only (Python unchanged). `check_notes.py` PASS (112 notes / 98 skeletons) · `check_docs.py` PASS · `sync_vault_mirrors.sh --check` PASS · `ruff` PASS.
- **Maintenance**: [session_2026-09-22_code_walkthrough_v2.md](maintenance/session_2026-09-22_code_walkthrough_v2.md)

## [2026-09-21] Session: Adaptive Vertical Exaggeration + Preview Fixes
- **Achievement**: Implemented adaptive vertical exaggeration end-to-end (Goal 1.2) and fixed two preview defects (invisible VE, leaked scratch layers). 7 commits (`38c1c651..8f50994a`).
- **Adaptive VE**:
    - `core/services/vertical_exaggeration_service.py` (new, stdlib-only): base by aspect-ratio (elev/dist → 1/2/5/10) × structural density (×0.7/1.0/1.3), clamp `[0.5, 20.0]`. `calculate_from_result` uses topo+struct only (§5.1: excludes async geol/drillhole to avoid flicker).
    - `dem_page.py`: `Auto` toggle (default on) + read-only `auto_ve_value` label; `DialogDefaults.AUTO_VERTICAL_EXAGGERATION`, `DemSettings.auto_vert_exag`, `ConfigService`.
    - `PreviewRenderMixin._resolve_vertical_exaggeration()`, `draw_preview(vert_exag=...)`, DI of the service into `PreviewManager`; VE excluded from `PreviewParams`/hasher.
    - `PreviewReporter` shows `Vertical exaggeration: 2.6× (auto)/(manual)` + conditional footer.
- **Scratch-layer fix**: preview memory layers leaked because OK/Save uses `accept_handler` → `accept()` (no `closeEvent`). Added `PreviewRenderer.cleanup()` and wired it into `closeEvent`, `accept_handler`, and `unload()`.
- **Quality**: 643 tests (594 local + Docker 5/5 OK) · Quality 53.8/100 · Maintainability 100.0 · Security 100 · CC PASS · i18n PASS · analyzer 0 issues.
- **Maintenance**: [session_2026-09-21_adaptive_ve_and_preview_fixes.md](maintenance/session_2026-09-21_adaptive_ve_and_preview_fixes.md)

## [2026-09-21] MILESTONE: Module Size Gate + Documentation Overhaul
- **Achievement**: Closed `module_size_gate` (7 modules >400l → <300l) and cleared the last analyzer debt (0 issues), then overhauled the documentation system (gates, tooling, i18n, guides). 40 commits pushed to `origin/main` (`f6a17262..ffd1720e`).
- **Module Size**: `export_service` 645→13 shim + `core/services/export/`; `drillhole_page` 451→130; `settings_page` 417→124; `sec_interp_plugin` 508→129; `main_dialog` 481→193; `interpretation_manager` 445→107; `preview_manager` 435→231. New `plugin/` mixins, tab sub-packages and `dialog_*_mixin`/`interpretation_*_mixin`/`preview_*_mixin`.
- **Tech Debt (Goal 2 closed)**: `NON_PYTHONIC_LOOP` → `enumerate`; `SPATIAL_INDEX` → `QgsFeatureRequest().setFilterRect()`; analyzer **0 issues**, maintainability 100.0.
- **Vaults**: 23 `layer_*` notes per vault, 41 thin notes enriched, numbering cleanup, table/tree links, mirrors re-synced.
- **Docs Overhaul**: P1 (versions/drift/broken links), P2 (dedup via `sync_docs_mirrors.sh`, Archive toctree), P3 (`docs.yml` → `sec_interp_docs`); new gate `check_docs.py` (`make docs-check`, CI + pre-push), auto-version in `conf.py`, `sphinx-build -j auto`, and new guides (`DOCS_INDEX`, `DOCS_STYLE_GUIDE`, `DOCUMENTATION_PROCESS`, `USER_GUIDE_CONVENTIONS`).
- **i18n**: fixed `translate_docs.py update`; pruned catalogs (20 MB → 2.4 MB); published-language policy `en es` (≥80% USER_GUIDE); **USER_GUIDE español 100%**.
- **Operational Metrics**: 568 local tests OK (616 static) · Quality 54.0/100 · Maintainability 100.0/100 · Security 100/100 · CC PASS · module size PASS · `make docs-check` PASS.
- **Maintenance**: [session_2026-09-21_module_size_and_docs.md](maintenance/session_2026-09-21_module_size_and_docs.md)

## [2026-09-20] Session: Code Walkthrough Vaults — Module Size Refactor Sync
- **Achievement**: Updated both bilingual Obsidian vaults (`docs/code_walkthrough/` ES + `docs/code_walkthrough_en/` EN) to reflect the 2026-09-20 module-size refactor, then added layer/sub-layer notes. Each vault grew from 67 to **97 notes**.
- **New notes (ES+EN)**: `export_package`, `plugin_mixins`, `dialog_mixins`, `preview_mixins`, `interpretation_mixins`, `drillhole_tabs`, `settings_tabs`.
- **Updated notes (ES+EN)**: added a "Refactor 2026-09-20" callout and the new line counts to `export_service` (645→13 shim), `sec_interp_plugin` (507→129), `main_dialog` (480→193), `drillhole_page` (451→130), `settings_page` (416→124), `interpretation_manager` (444→107), `dialog_preview_manager` (434→231).
- **Indexes**: both `Index.md` list the new notes and a refactor callout.
- **Layer notes**: added 23 `layer_*` notes per vault documenting the 4 root layers (`core`, `gui`, `exporters`, `plugin`) and 19 sub-layers (`core/{domain,interfaces,models,services,services/drillhole,services/export,services/export/handlers,utils,utils/geometry_utils,validation}`, `gui/{adapters,dialogs,renderers,tasks,tools,ui,ui/pages,ui/pages/drillhole,ui/pages/settings}`), each with its layer rules, sub-layer map, module inventory and patterns. Each vault now has **97 notes**.
- **Depth pass**: enriched the 41 thinnest file notes per vault (exporters, core drillhole/services/utils, preview, GUI managers, adapters/tools/pages) to the full template — problem/solution, Mermaid diagram, imports reading, method-by-method walkthrough with real snippets, patterns, API table and observations. Removed the remaining `NN —` H1 prefixes and `Nota NN`/`Note NN` footers.
- **Validation**: all wikilinks in new/modified notes resolve; `scripts/sync_vault_mirrors.sh --check` PASS.
- **Docs-only**: no Python changes.

## [2026-09-20] Session: Analyzer Debt Cleared — NON_PYTHONIC_LOOP & SPATIAL_INDEX
- **Achievement**: `qgis-analyzer` now reports **0 issues** (was 3). Maintainability 99.9 → 100.0/100. Goal 2 (technical debt) fully closed.
- **Changes**:
    - **2.2 `NON_PYTHONIC_LOOP` ×2**: replaced the manual `feat_id += 1` counter with `enumerate` over a new `_iter_drillhole_interval_geoms()` generator in `gui/interpretation_inheritance_mixin.py`. The analyzer reported the same line twice because `ast.walk` sees it from both nested loops; its rule does not honor `# noqa`.
    - **2.3 `SPATIAL_INDEX`**: `sync_from_layer` now iterates `layer.getFeatures(QgsFeatureRequest().setFilterRect(layer.extent()))`, so the request is served through the spatial index (`gui/interpretation_persistence_mixin.py`).
    - **Tooling**: `sync_metrics.py` records `total_issues: 0` and an empty `issue_breakdown` when the analyzer is clean (previously the zero-issue case left stale values).
- **Quality**: 616 tests static (Docker: agentic 23 + core 197 + exporters 40 + gui 218 + integration 75 = 553, all OK) · Quality 54.0/100 · Maintainability 100.0/100 · Security 100/100 · CC PASS · i18n PASS · module size PASS · analyzer 0 issues · `ruff` PASS.

## [2026-09-20] Session: Module Size Gate Remediation — Decompose Oversized Modules
- **Achievement**: Removed the `module_size_gate` FAIL by decomposing all 7 modules > 400 lines to < 300, then merged the branch to `main` (fast-forward, pushed `1bcdc661..99138c05`). `module_size_gate` is now **PASS** and Module Stability rose 52.4 → 54.0.
- **Changes**:
    - `core/services/export_service.py` 645 → 13 (shim) + new `core/services/export/` package (orchestrator, path resolver, map-settings factory, 7 handlers, compat).
    - `gui/ui/pages/drillhole_page.py` 451 → 130 + `drillhole/{collar,survey,interval}_tab.py`.
    - `gui/ui/pages/settings_page.py` 417 → 124 + `settings/{default,advanced,info}_tab.py` + persistence.
    - `sec_interp_plugin.py` 508 → 129 + `plugin/{lifecycle,input_validator,render_pipeline}.py`.
    - `gui/main_dialog.py` 481 → 193 + `dialog_{message,lifecycle,facade}_mixin.py`.
    - `gui/dialog_interpretation_manager.py` 445 → 107 + `interpretation_{persistence,inheritance}_mixin.py`.
    - `gui/dialog_preview_manager.py` 435 → 231 + `preview_{callbacks,render}_mixin.py`.
    - Fixed `sync_metrics.py` to strip ANSI escapes so analyzer scores sync correctly (quality was stuck at 52.3), and refreshed the qgis-analyzer ground-truth block.
- **Quality**: 616 tests (Docker: agentic 23 + core 197 + exporters 40 + gui 217 + integration 75, all OK) · Quality 54.0/100 · Maintainability 99.9/100 · Security 100/100 · CC PASS · i18n PASS · module size PASS · `ruff` PASS.
- **Commits**: `c3116a6`, `39e1168`, `78bcb45`, `900afb8`, `ac58143`, `85cbbb5`, `77f193d`, `f8cb60e`, `99138c0`.
- **Spec**: [plans/Technical_Specification_module_size_gate.md](plans/Technical_Specification_module_size_gate.md)

## [2026-09-20] Session: Vault Architecture Links — Directory Structure Linkify
- **Achievement**: Linkified `docs/ARCHITECTURE_EN.md` Directory Structure so every module resolves to its vault note — dual-link `[[slug]]` (Obsidian) + `[doc](code_walkthrough/slug.md)` (GitHub/Sphinx). Replaced the fenced tree with a Markdown nested list, covering core/gui/exporters (67 notes/vault).
- **Scope**: Synced mirrors `docs/code_walkthrough*/ARCHITECTURE_EN.md` via `scripts/sync_vault_mirrors.sh` (`--check` PASS); marked v3.8.0 as PUBLICADO en plugins.qgis.org (`.agent/task.md` 13.5, `.agent/next_steps.md`).
- **Maintenance**: [session_2026-09-20_vault_architecture_links.md](maintenance/session_2026-09-20_vault_architecture_links.md)

## [2026-09-20] Session: Vault Completion — Numbering Removal & Remaining Modules
- **Achievement**: Removed numeric prefixes from all 68 vault notes (`NN - slug.md` → `slug.md`), updated 80 wikilinks and index tables (`#` column removed, callout added), and enriched the remaining 12 skeleton notes (export_service, preview_service, trajectory/collar/survey/interval/projection/access_control, drillhole/geology/structure/validation extractors, measure/interpretation tools, drillhole/settings pages, and 7 exporters 3D/PDF/SVG/image/profile/dxf/interpretation/drillhole).
- **Templates & Tooling**: Added number-free `_template.md` (ES+EN) and `scripts/sync_vault_mirrors.sh` (`--check` for CI); vault now navigates by sections/tags, not by number.
- **Commits**: `90247850`, `13db9a88`, `1bcdc661` (plus `165c93b`, `45fcf3b`). Pushed `4b7906cc..1bcdc661` to `origin/main` (12 commits, pre-push gate PASSED).
- **Maintenance**: [session_2026-09-20_vault_completion.md](maintenance/session_2026-09-20_vault_completion.md)

## [2026-09-20] Session: Code Walkthrough Vault (Bilingual) + Architecture Docs Refresh
- **Achievement**: Built bilingual Obsidian code-walkthrough vaults (ES/EN) documenting the full SecInterp architecture file-by-file, and refreshed the canonical architecture docs (diagrams, directory structure, QA section) plus competitive analysis.
- **Architecture Docs**:
  - `ARCHITECTURE.mmd` 34 → 260 lines (full GUI/Core/Exporters, color-coded).
  - `docs/ARCHITECTURE_EN.md` directory structure 130 → 280 lines + full Mermaid graph + Quality Assurance & Security Scanning section (Bandit/detect-secrets/Flake8, qgis-analyzer, Qt6 checker).
  - Added `docs/ARCHITECTURE_MONOLITHIC_VS_CLEAN_EN.md` (monolithic vs Clean) and `docs/PLUGIN_REPORT_AND_COMPARISON_EN.md` (feature + 7-plugin matrix; positioning map fixed).
  - Exported standalone `docs/architecture.mmd` (11 KB) for Obsidian/mermaid.live; fixed cycle bug in export subgraphs.
- **Code Walkthrough Vaults** (`docs/code_walkthrough/` ES + `code_walkthrough_en/` EN):
  - MOC `00 - Index.md` + 20 notes (00, 01, 02, 03, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 30, 31) + 3 mirror docs per vault; short-name convention; all wikilinks normalized.
  - Completed: `sec_interp_plugin`, `__init__`, `logger_config`, `controller`, `domain`, `exceptions`, `profile_service` (adapter), `geology/drillhole/structure_services`, `validation`, `safe_loader`, `i18n`, `main_dialog`, `dialog_preview/export_manager`, `renderers`, `tasks`, `adapters`, `base/vector_exporter`.
  - Added mirror-docs notice to indexes; excluded Obsidian editor state (`chore: ignore Obsidian vault configuration`).
- **Commits**: `bb511748`, `89b41565`, `75978374`, `29e1adff`, `2161b77`.
- **Operational Metrics**: Docs-only session; Python code unchanged. Ground truth: 606/606 tests, CC ≤ 10 PASS, i18n 0, Security 100/100.
- **Maintenance**: [session_2026-09-20_code_walkthrough_vault.md](maintenance/session_2026-09-20_code_walkthrough_vault.md)

## [2026-09-19] MILESTONE: Release v3.8.0 — Core/GUI Decoupling & Reliability
- **Achievement**: Publicación de SecInterp v3.8.0, release que consolida el refactor Core/GUI y dos correcciones de fiabilidad.
- **Release Content**:
    - **Architecture**: Extract-then-Compute con núcleo agnóstico de QGIS y capa `gui/adapters/`; allowlist 36 → 6.
    - **Compatibility**: Fix de `QEvent.Type.Resize` en la leyenda para QGIS 4.
    - **Export**: Exportación 3D de interpretaciones habilitada por defecto.
    - **Tooling**: Gates de CC e i18n nativos de `qgis-plugin-analyzer` 1.14.0.
- **Operational Metrics**:
    - Tests: 606/606 (Docker)
    - Quality: 52.4/100 · Maintainability 99.9/100 · Security 100/100
    - CC ≤ 10: PASS · i18n AST: PASS · Docstring: 100%
- **Status**: Release v3.8.0 completado y publicado en GitHub (latest).
- **Release Notes**: [notes/v3.8.0.md](releases/notes/v3.8.0.md)
- **Maintenance**: [session_2026-09-19_release_v3.8.0.md](maintenance/session_2026-09-19_release_v3.8.0.md)

## [2026-09-19] Session: Core/GUI Decoupling Refactor — Completion & Merge
- **Achievement**: Completed the Extract-then-Compute refactor and fast-forward merged it to `main`. Migrated all business services (`StructureService`, `GeologyService`, `ProfileService`, the drillhole domain, and the validation layer) to a QGIS-agnostic core, shrinking the architecture allowlist 36 → 6.
- **Changes**:
    - Services migrated to pure math + `gui/adapters/` extractors (structure, geology, profile, drillhole) and a `LayerMetadata` validation DTO.
    - Geometry Extract helpers moved to `gui/adapters/geometry.py`; `qt6_compat.py` retired; 12 dead modules removed.
    - Fixed Qt6 `QEvent.Type.Resize` (legend widget) and enabled 3D interpretation export by default.
    - Added missing `type()` to QGIS layer mocks (docker-test 606 OK).
    - Aligned the release workflow/skill checklist and fixed stale metrics (test count, changelog allowlist).
- **Quality**: 606/606 tests (Docker) OK · `qt6-check` 0 incompatibilities · gate 3/3 · `ruff` PASS.
- **Maintenance**: [session_2026-09-19_architecture_refactor_complete.md](maintenance/session_2026-09-19_architecture_refactor_complete.md)

## [2026-09-19] Session: Core/GUI Decoupling Refactor
- **Achievement**: Enforced the Extract-then-Compute boundary across `core/`/`gui/` on the `refactor/core-gui-decoupling` branch: added an architecture allowlist gate, decomposed the GUI God Object, consolidated the preview pipeline, and started migrating `core/` to QGIS-agnostic pure math.
- **Changes**:
    - `tests/core/test_architecture_boundary.py` gate (forbidden-QGIS-coupling allowlist, 36 → 31 files).
    - Fase 1-3: dead code removal, `PreviewCache`/`RenderState`, page `dump/load/reset` protocol, `SignalManager` event bus, single preview render path.
    - Fase 4: `LayerNotificationManager` and `DataFetcher` → `gui/adapters/`; `controller.py` QGIS-agnostic; Douglas-Peucker/metrics/azimuth/densify reimplemented in stdlib `math`.
- **Quality**: 576/576 tests OK · gate 3/3 · `ruff check` + `ruff format` PASS · manual QGIS 4 validation green.
- **Maintenance**: [session_2026-09-19_core_gui_decoupling.md](maintenance/session_2026-09-19_core_gui_decoupling.md)

## [2026-09-17] Session: Analyzer Upstream Migration
- **Achievement**: Retired the redundant SecInterp scripts (`check_cc.py`, `verify_i18n_hygiene.py`) now that qgis-plugin-analyzer 1.14.0 natively ships the AST `MISSING_I18N` rule and the `--max-cc` gate; both quality gates are now driven directly from the analyzer.
- **Actions Taken**:
    - Confirmed the upstreaming plan was already fully implemented in analyzer 1.14.0 (verified against installed `analyzer/` source).
    - `pyproject.toml`: added `[tool.qgis-analyzer.profiles.default.rules.MISSING_I18N]` with `extra_ignore_calls = ["PerformanceTimer"]` → `MISSING_I18N` 2 → 0.
    - Refactored `scripts/sync_metrics.py`: CC gate from `analyze --max-cc 10` exit code, i18n gate from `MISSING_I18N == 0`; removed `run_check_cc`/`run_verify_i18n`.
    - Fixed the pre-push hook (legacy `--output json` → `--max-cc 10`).
    - Rewrote `docs/plans/upstreaming_qgis_analyzer.md` and updated workflows/skills/metrics references.
- **Operational Metrics**: 640/640 tests (Docker) · `--max-cc 10` PASS · `MISSING_I18N` 0 (issues 5 → 3) · `sync_metrics --validate` PASS · `ruff check` PASS.
- **Status**: Commit `61de59f2` pushed to `origin/main`. Remaining debt: 2 `NON_PYTHONIC_LOOP` (2.2), 1 `SPATIAL_INDEX` (2.3), `module_size_gate` FAIL (2.4).
- **Maintenance**: [session_2026-09-17_analyzer_upstream_migration.md](maintenance/session_2026-09-17_analyzer_upstream_migration.md)

## [2026-09-14] Session: qgis-plugin-analyzer 1.14.0 Upgrade
- **Achievement**: Adopted `qgis-plugin-analyzer` 1.14.0 and refreshed ground-truth metrics in `agent_metrics.json`.
- **Actions Taken**:
    - Bumped `qgis-plugin-analyzer` `>=1.13.2` → `>=1.14.0` in `pyproject.toml` (deps + dev group); regenerated `uv.lock`.
    - Re-ran `qgis-analyzer analyze .` (38 modules). 1.14.0's narrower i18n heuristic cut `MISSING_I18N` 72 → 2 (remaining are `PerformanceTimer` labels) and recomputed type-hint params 94.3% → 90.4%.
    - Updated `agent_metrics.json` summary + `ground_truth_sources.qgis_analyzer` (total issues 75 → 5); `sync_metrics --validate` PASS.
- **Operational Metrics**: 640/640 tests (Docker) · Stability 52.3 · Maintainability 99.9 · Security 100.0 · 5 analyzer issues.
- **Status**: Ready. Remaining debt: 2 `NON_PYTHONIC_LOOP` (2.2), 1 `SPATIAL_INDEX` (2.3), `module_size_gate` FAIL (2.4).
- **Maintenance**: [session_2026-09-14_qgis_analyzer_1_14_0.md](maintenance/session_2026-09-14_qgis_analyzer_1_14_0.md)

## [2026-09-13] Session: Root Directory Cleanup
- **Achievement**: Reclaimed the repository root (~90 MB) from generated artifacts and stale editor configs; untracked 30 files from git and expanded `.gitignore`.
- **Actions Taken**:
    - Removed untracked build/analysis clutter (logs, caches, `analysis_results_*`, `_archive/`, `artifacts/`, `json/`, `quality_report*`, `sec_interp.egg-info/`, stray logs).
    - `git rm --cached` 26 generated artifacts (analyzer/coverage reports, empty placeholders, `dummy.qml`, `test_patch.py`, `symbology-style.db`, `.coverage`).
    - Untracked `.idea/`, `.vscode/`, `.continue/` (no longer used).
    - Expanded `.gitignore` with caches, IDE dirs, and generated artifact patterns.
    - Regenerated `.secrets.baseline` (dropped stale `.continue/` entry).
- **Operational Metrics**: 592 tests OK (local) · `ruff check` PASS · `sync_metrics --validate` PASS · `dist/` preserved.
- **Status**: `chore: clean root directory` committed (`69b75c15`). Pending: root `__pycache__` (root-owned), `skills-lock.json` legacy cleanup, unrelated `MURALLA.qgs`/`resources.py` edits.
- **Maintenance**: [session_2026-09-13_root_dir_cleanup.md](maintenance/session_2026-09-13_root_dir_cleanup.md)

## [2026-09-13] Session: Gen 8 Agentic System Evolution
- **Achievement**: Executed the Gen 7 → Gen 8 improvement plan (Phases A–E), consolidating the agentic tooling long-tail and aligning the system to opencode-native mechanisms.
- **Actions Taken**:
    - Phase A: root `AGENTS.md` as single source of truth; retired `skill_sync.py` + `context_selector.py`.
    - Phase B: folded 5 scripts into `sync_metrics.py` / `validate_agent_system.py` subcommands; fused test-runners into `run_in_qgis.py`; retired the CodeWhale bridge and redundant i18n shell scripts (`scripts/` 27 → 15).
    - Phase C: externalized CC/module-size thresholds (`check_cc.py --threshold`); recorded analyzer versions in `agent_metrics.json`.
    - Phase D: registered native subagents (`architect`/`qa_engineer`/`auditor`) in `opencode.json`; normalized workflow frontmatter; removed `runtimes:`.
    - Phase E: standardized skills to `name`+`description` (dropped `trigger`); registered `.agent/skills` via `skills.paths`.
- **Operational Metrics**:
    - Tests: 640/640 — 620 plugin + 20 agentic tooling
    - CC <= 10: PASS · i18n AST gate: PASS
    - validate_agent_system (default + --graph + --conflicts): PASS · sync_metrics --validate: PASS
- **Status**: Gen 8 Phases A–E complete. Phase F (session-as-durable-object) documented as a separate proposal. Restart opencode to load `opencode.json`.
- **Maintenance**: [session_2026-09-13_gen8_agentic_system_evolution.md](maintenance/session_2026-09-13_gen8_agentic_system_evolution.md)

## [2026-09-13] Session: v3.7.2 Portal Publication Closure
- **Achievement**: Confirmada la publicacion de SecInterp v3.7.2 en plugins.qgis.org y como latest release en GitHub (paso manual del release, task 3.5).
- **Actions Taken**:
    - `/start-session`: entorno en verde (docker-test OK, metricas coherentes, `uv sync` limpio).
    - Marcado task `3.5` como completado en `.agent/task.md`.
    - Actualizado `.agent/next_steps.md`: removido follow-up manual pendiente.
- **Operational Metrics**: 645/645 tests, Quality 52.3/100, CC PASS, i18n AST PASS, qt6-check 0.
- **Status**: Release v3.7.2 cerrado al 100%. Siguiente: Goal 1.1 (symbology) / Fase 1 adaptive VE / tech debt 2.1-2.3.
- **Maintenance**: [session_2026-09-13_v3.7.2_portal_published.md](maintenance/session_2026-09-13_v3.7.2_portal_published.md)

## [2026-09-12] MILESTONE: Release v3.7.2 — Qt6 / QGIS 4 Compatibility Patch
- **Achievement**: Publicacion de SecInterp v3.7.2, parche que resuelve los 114 hallazgos de compatibilidad Qt6 reportados por el repositorio de plugins de QGIS.
- **Release Content**:
    - **Compatibility**: Migracion de 114 enums planos a forma scoped ya existente en `HEAD` (commit `7ae8ac96`) que no habia sido publicada; la v3.7.1 en el portal aun contenia enums planos (`Qgis.Critical`, `Qt.NoPen`).
    - **Gate**: `make qt6-check` corre `pyqgis4-checker` (dry-run) → 0 incompatibilidades.
- **Operational Metrics**:
    - pyqgis4-checker: 0 incompatibilidades
    - Tests: 645/645 (Docker)
    - CC <= 10: PASS
- **Status**: Release v3.7.2 completado.
- **Release Notes**: [notes/v3.7.2.md](releases/notes/v3.7.2.md)

## [2026-09-12] Session: Agentic System Hardening
- **Achievement**: Hardening integral del sistema `.agent/` (6 recomendaciones de auditoria + plan A+B+C completados).
- **Actions Taken**:
    - Cierre de fase v3.7.0 (documento formal + logs + archivo de tasks).
    - Metric coherence: reconciliado `agent_metrics.json` (i18n 254→72, maintainability 90.7→99.9) + `validate_agent_metrics.py` con chequeos de consistencia interna.
    - History pruning: 44 snapshots `next_steps/` eliminados (retencion 90 dias) + unificacion de naming en `history/tasks/`.
    - Script audit: 9 scripts legacy eliminados + `scripts/README.md` creado.
    - `antigravity-framerepo/` marcado obsoleto (gitlink desvinculado + gitignored).
    - Gen 7 tooling: rotacion de `last_session` en `sync_metrics.py`, tabla de workflows auto-sync en ambos `AGENTS.md`, `check_skill_conflicts.py`, `context_selector.py` corregido.
    - 25 tests unitarios nuevos en `tests/agentic/`.
- **Operational Metrics**:
    - Tests: 645/645 (100%) — 620 plugin + 25 agentic tooling
    - CC <= 10: PASS
    - i18n AST Gate: PASS
    - Validators: validate_agent_system / validate_agent_metrics / workflow_graph / check_skill_conflicts: PASS
- **Status**: Sistema agéntico endurecido y testeado. Siguiente: metas v3.8.0 (Goal 1 symbology/VE).
- **Maintenance**: [session_2026-09-12_agentic_system_hardening.md](maintenance/session_2026-09-12_agentic_system_hardening.md)

## [2026-09-12] PHASE CLOSURE v3.7.0
- **Achievement**: Cierre formal de la fase v3.7.0 (i18n Quality Gate, UX, Qt6/QGIS 4 enum migration).
- **Summary**: Releases v3.7.0 y v3.7.1. Gate i18n AST (0 violaciones), 9 titulos envueltos en `self.tr()`, 114 enums migrados a forma scoped, patch de seguridad (Bandit B110), ZIP 25MB → 3.3MB.
- **Operational Metrics**: 620/620 tests, Maintainability 99.9/100, Security 100/100, CC <= 10 PASS, i18n AST PASS.
- **Reference**: [phase_closure_v3.7.0.md](maintenance/phase_closure_v3.7.0.md)

## [2026-09-06] Session: Qt6 Scoped Enum Migration
- **Achievement**: Migrados 114 enums planos a forma scoped para compatibilidad QGIS 4 / Qt6.
- **Root Cause/Context**: El repositorio de plugins de QGIS ejecuta `pyqt5_to_pyqt6.py` (pyqgis4-checker) al subir el ZIP, que reporta enums no calificados (Qgis.Critical vs Qgis.MessageLevel.Critical).
- **Actions Taken**:
    - Auto-fix con `pyqt5_to_pyqt6.py` (57 archivos fuente migrados).
    - Actualizados los mocks de tests para exponer enums scoped (Type, MessageLevel, Flag, RenderHint, Shape, IconType, StorageMode).
    - Bump `qgisMinimumVersion` 3.0 -> 3.28.
    - Gate: `make qt6-check`/`make qt6-fix` + job CI `qt6` + wiring en `pre-release`.
- **Operational Metrics**:
    - Tests: 620/620 (100%)
    - pyqgis4-checker: 0 incompatibilidades
    - CC <= 10: PASS
- **Status**: Migracion Qt6 completada. Pendiente retirar qt6_compat.py y Goals 2.x.
- **Maintenance**: [session_2026-09-06_qt6_scoped_enum_migration.md](maintenance/session_2026-09-06_qt6_scoped_enum_migration.md)

## [2026-09-06] MILESTONE: Release v3.7.1 — Security Patch
- **Achievement**: Publicacion de SecInterp v3.7.1 (parche de seguridad).
- **Release Content**:
    - **Security**: Reemplazado el `try/except/pass` silencioso en `_get_setting` por `logger.warning` (Bandit B110).
    - **Pipeline**: Cableado el escaner de seguridad completo (Bandit + detect-secrets + Flake8) al workflow de release.
- **Operational Metrics**:
    - Tests: 620/620 (100%)
    - Security: 100/100 (bandit PASS, detect-secrets PASS)
    - CC <= 10: PASS
- **Status**: Release v3.7.1 completado.
- **Release Notes**: [notes/v3.7.1.md](releases/notes/v3.7.1.md)

## [2026-09-06] MILESTONE: Release v3.7.0 — i18n Quality Gate & UX Improvements
- **Achievement**: Publicacion oficial de SecInterp v3.7.0.
- **Release Content**:
    - **i18n Quality Gate**: Script AST `verify_i18n_hygiene.py` para enforcement de `self.tr()`.
    - **i18n Dialog Titles**: 9 titulos de dialogo de error envueltos en `self.dialog.tr()`.
    - **UX**: Controles de preview agrupados en `QgsCollapsibleGroupBox("Controls")` colapsable.
    - **Packaging**: Exclusion de tooling de agentes (`.codewhale`, `.continue`, `.deepseek`) del ZIP.
- **Operational Metrics**:
    - Tests: 620/620 (100%)
    - Security: 100/100 (0 vulnerabilidades)
    - CC <= 10: PASS
    - i18n AST Gate: PASS
- **Status**: Release v3.7.0 completado. Proximo release: Goal 2 (adaptive vertical exaggeration, symbology preview, Cartesian tests).
- **Release Notes**: [notes/v3.7.0.md](releases/notes/v3.7.0.md)

## [2026-07-20c] Session: Collapsible Preview Controls
- **Achievement**: Separado el canvas de preview de los botones, controles LOD y checkboxes, permitiendo colapsarlos en un QgsCollapsibleGroupBox.
- **Root Cause/Context**: El PreviewWidget agrupaba canvas, status bar, botones, LOD y checkboxes en una sola columna no colapsable. El usuario requirio poder colapsar los controles hacia abajo para maximizar el area de visualizacion.
- **Actions Taken**:
    - Refactor de PreviewWidget: canvas + status bar siempre visibles, controles (botones, LOD, checkboxes) dentro de QgsCollapsibleGroupBox("Controls"), resultados en QgsCollapsibleGroupBox("Results") independiente.
    - _setup_action_buttons, _setup_lod_controls y _setup_layer_checkboxes ahora aceptan parent_layout en vez de self.frame_layout.
- **Operational Metrics**:
    - Tests Passing: 620/620 (100%)
    - Quality Score: 52.3/100
    - Ruff / CC / i18n: PASS
- **Status**: UX enhancement completado. Proxima sesion: Fase 1 de adaptive vertical exaggeration.
- **Maintenance**: [session_2026-07-20c_collapsible_preview_controls.md](maintenance/session_2026-07-20c_collapsible_preview_controls.md)

## [2026-07-20b] Session: Adaptive Vertical Exaggeration Plan
- **Achievement**: Plan de implementacion completo para exageracion vertical adaptiva (Goal 2.2 de v3.7.0).
- **Root Cause/Context**: El sistema actual usa un valor estatico de exageracion vertical (0.1-100, default 1.0) que no se adapta a la geometria del perfil. Perfiles largos con poco relieve quedan visualmente planos; perfiles cortos con mucho relieve se distorsionan.
- **Actions Taken**:
    - Analisis completo del flujo de exageracion vertical a traves de 15+ archivos (desde DemPage.vertexag_spin hasta PreviewLayerFactory._apply_exaggeration y PreviewAxesManager).
    - Diseno de algoritmo de dos componentes: VE base por aspect ratio (4 tiers: 1.0, 2.0, 5.0, 10.0) + multiplicador de densidad estructural (0.7-1.3).
    - Creacion del plan de 5 fases: Core service → GUI toggle → Integration → Persistence → Verification (7 tests).
    - Documentacion guardada en docs/plans/implementation_plan_adaptive_ve_v3.7.0.md.
- **Operational Metrics**:
    - Tests Passing: 620/620 (100%)
    - Quality Score: 52.3/100
    - Ruff: PASS
- **Status**: Plan listo para ejecucion. Proxima sesion: Fase 1 — implementar VerticalExaggerationService + tests.
- **Maintenance**: [session_2026-07-20b_adaptive_ve_plan.md](maintenance/session_2026-07-20b_adaptive_ve_plan.md)

## [2026-07-20] Session: i18n Genuine Gaps Fix
- **Achievement**: Auditoria completa de los 79 MISSING_I18N del qgis-analyzer y reparacion de los 9 gaps genuinos restantes.
- **Root Cause/Context**: La fase v3.7.0 Goal 1 requeria triage de los flags del analyzer. De 79 flags, 70 son falsos positivos (dict keys, CSS/QSS, colores hex, simbolos unicode, strings de logging) y 9 eran titulos de dialogo y labels HTML visibles al usuario sin envoltura tr().
- **Actions Taken**:
    - Clasificacion exhaustiva de los 79 flags en 10 categorias de falsos positivos vs 9 gaps genuinos.
    - Envuelto con self.dialog.tr() los 9 strings en dialog_export_manager.py (3), dialog_preview_manager.py (5), y dialog_interpretation_manager.py (1).
    - Verificacion: AST i18n gate 0 violaciones, ruff check PASS, CC gate PASS.
- **Operational Metrics**:
    - Tests Passing: 620/620 (100%)
    - AST i18n Gate: PASS (0 violations)
    - Quality Score: 52.3/100
- **Status**: Goal 1 de v3.7.0 completado. Pendiente Goal 2 (symbology preview) y deuda tecnica (qt6_compat, NON_PYTHONIC_LOOP, SPATIAL_INDEX).
- **Maintenance**: [session_2026-07-20_i18n_gaps_fix.md](maintenance/session_2026-07-20_i18n_gaps_fix.md)

## [2026-05-23] Session: i18n Hygiene & Quality Gate Implementation
- **Achievement**: Completada la auditoría de traducciones de la interfaz gráfica de usuario y establecida la herramienta AST de verificación estática de i18n (`verify_i18n_hygiene.py`).
- **Root Cause/Context**: La fase `v3.7.0` requiere reducir la deuda de internacionalización acumulada eliminando falsos positivos en variables técnicas de la GUI y traduciendo cadenas visibles genuinas.
- **Actions Taken**:
    - Se diseñó e implementó un script de higiene de i18n basado en árboles de sintaxis abstracta (AST) para rastrear cadenas sin envoltura de traducción o marcado `# no-i18n`.
    - Se envolvieron en `self.tr()` y `QCoreApplication.translate()` los títulos de diálogos y nombres dinámicos de capas de la leyenda (`Export Preview`, `Topography Fill`, `Drillhole Traces`, `Drillhole Intervals`).
    - Se marcaron con `# no-i18n` las claves internas de rendimiento, nombres técnicos de `QgsTask` y tags de logging para desarrolladores.
    - Se optimizó `.analyzerignore` para enfocar la herramienta estática de traducción únicamente en la capa de UI.
- **Operational Metrics**:
    - Tests Passing: 572/572 (100%)
    - i18n Quality Gate Violations: 0 en 53 archivos
    - Maintainability Score: 94.2/100
- **Status**: 🟢 Cierre de sesión y avance de i18n completado con éxito. Listo para Goal 2 de v3.7.0.
- **Maintenance**: [session_2026-05-23_i18n_hygiene_and_quality_gate.md](maintenance/session_2026-05-23_i18n_hygiene_and_quality_gate.md)

## [2026-05-18] Session: v3.6.0 Release Finalization & Verification
- **Achievement**: Completada la verificación de empaquetado del archivo `sec_interp.3.6.0.zip` y cierre formal del ciclo de desarrollo de la fase `v3.6.0`.
- **Root Cause/Context**: El plugin ya se encuentra publicado en el repositorio de QGIS, por lo que realizamos la auditoría final de exclusión de archivos de desarrollo y la sincronización total de logs.
- **Actions Taken**:
    - Se ejecutó `unzip -l` sobre el paquete verificado confirmando la total exclusión de archivos internos del agente (`.agent/`, `scripts/`, `tests/`, `docs/`, `AI_CONTEXT.md`).
    - Cierre formal de la versión mediante `/close-phase` y archivado de tareas a `tasks_v3.6.0.md`.
    - Actualización del registro maestro `MAINTENANCE_LOG.md` con los hitos de `v3.5.0` y `v3.6.0`.
    - Generación de metas preliminares para la fase `v3.7.0` (deuda técnica de traducciones y leyendas 3D).
- **Operational Metrics**:
    - Tests Passing: 572/572 (100%)
    - Maintainability Score: 94.2/100
    - Quality Score: 40.8/100
- **Status**: 🟢 Cierre de sesión y fase completada con éxito. Listo para v3.7.0.
- **Maintenance**: [session_2026-05-18_v3.6.0_release_finalization.md](maintenance/session_2026-05-18_v3.6.0_release_finalization.md)

## [2026-05-17] CIERRE FINAL DE FASE v3.6.0: Next-Gen Stability, Spatial Optimization & QGIS 4 Ready
- **Achievement**: Completada exitosamente la fase y empaquetamiento de v3.6.0.
- **Cambios Principales**:
    - **Compatibilidad**: 100% QGIS 4.x (Qt6) compatibility bridging (QImage, QPainter, QDialog.Accepted).
    - **Rendimiento**: Implementación de `QgsSpatialIndex` logrando tiempos sub-segundo para herencia de miles de polígonos geológicos.
    - **Mantenibilidad**: Score 94.2/100, 620 tests exitosos, CC <= 10.
    - **Lanzamiento**: CHANGELOG, README y notas de la versión generados y listos para distribución (Plugin-Only ZIP).
- **Status**: 🟢 Fase v3.6.0 completada, empaquetada y liberada exitosamente.

## [2026-05-12] Session: Qt6 QDialog Hotfix (Post-Release)
- **Achievement**: Resolved a runtime `AttributeError` crash in QGIS 4.0.1 (Qt6) caused by `QDialog.Accepted` enum being removed from the Qt6 API surface.
- **Root Cause**: In Qt6, `QDialog.Accepted` is no longer a flat class attribute — it moved to `QDialog.DialogCode.Accepted`. Both `exec_()` (deprecated in Qt5, removed in Qt6) and the enum constant failed at runtime.
- **Fix Applied**:
    - `gui/dialog_interpretation_manager.py`: `dlg.exec_() != QDialog.Accepted` → `dlg.exec() != 1`.
    - `sec_interp_plugin.py`: `self.dlg.exec_()` → `self.dlg.exec()`.
    - `tests/mocks/qt_mocks.py`: `MockQWidget.exec_()` → `MockQWidget.exec()`.
    - `tests/gui/test_dialog_interpretation_manager.py`: Mocks updated to return `1` (accepted) / `0` (rejected).
- **Operational Metrics**:
    - Tests Passing: 571/571 (100%)
    - Files Modified: 4
    - Commit: `0694e80`
- **Status**: 🟢 Hotfix committed. Pending push to `origin/main` and `v3.6.1` tag evaluation.
- **Maintenance**: session_2026-05-12_qt6_qdialog_hotfix.md

## [2026-05-12] CIERRE DE FASE v3.6.0: Next-Gen Stability & QGIS 4 Ready

- **Achievement**: Completada la fase v3.6.0. Resolvimos la compatibilidad asíncrona con QGIS 4.x y estabilizamos el motor de renderizado evitando segmentation faults mediante bloqueos y señales diferidas.
- **Cambios Principales**:
    - **Compatibilidad**: 100% de operaciones en QgsTask refactorizadas para evitar objetos in-hasheables en PyQt6.
    - **Estabilidad**: Uso extensivo de `QTimer.singleShot` para asegurar que las señales que involucran C++ pointers se procesan de forma segura en el main loop.
    - **Calidad**: 620 tests exitosos en Docker, sin regresiones en cobertura (CC <= 10).
    - **Deployment**: `qgis-manage` modernizado con soporte nativo para los perfiles de QGIS 3 y 4.
    - **i18n**: Sincronización global y completa (13 lenguajes).
- **Status**: 🟢 Fase completada y lista para release oficial.

## [2026-05-11] Session: Global i18n Synchronization (Phase v3.6.0)
- **Achievement**: Reached 100% internationalization coverage (wrapped strings) across all core services and UI managers. Synchronized and compiled 13 locales with updated Spanish master data.
- **Operational Metrics**:
    - Locales Synchronized: 13
    - CC Compliance: 100%
    - Maintainability Score: 87.1 (Analyzed)
- **Changes**:
    - **Core**: Added `tr()` support to `ExportService` and `ProfileService`. Wrapped all user-facing strings.
    - **GUI**: Updated `ExportManager` with translated UI titles and descriptions.
    - **i18n**: Populated `es.json` master data with new translations and some missing technical messages.
    - **Automation**: Created `apply-all-i18n.sh` and `sync-i18n.sh` for batch processing.
    - **Formatting**: Applied project-wide `ruff` and `black` formatting to 110 files.
- **Status**: Goal 1 (i18n) mostly completed. Ready for Goal 2 (Spatial Performance).
- **Maintenance**: [session_2026-05-11_global_i18n_synchronization.md](maintenance/session_2026-04-29_linting_resolution.md)

- **Achievement**: Successfully deployed **SecInterp v3.5.0**. Completed Generation 6 modernization with automated maintenance, metrics, and quality gates.

## [2026-04-29] Session: Linting Debt Resolution (Phase v3.6.0)
- **Achievement**: Resolved all W503, W504, F401, and F811 linting violations. Established a stable, formatted foundation for Phase 3.6.0.
- **Operational Metrics**:
    - Linting Violations: 0
    - Passing Tests: 571
    - Formatted Files: 86
- **Changes**:
    - **Core**: Refactored `export_service.py` conditions to avoid W503.
    - **GUI**: Fixed signal managers and button boxes for linting compliance.
    - **Mocks**: Cleaned up `qgis_layers.py` logic and imports.
- **Status**: Completed.
- **Maintenance**: [session_2026-04-29_linting_resolution.md](maintenance/session_2026-04-29_linting_resolution.md)
- **Operational Metrics**:
    - TCR: 1.0
    - Maintainability Score: 94.1/100
    - Quality Score: 40.9 (Standardized)
    - CC Compliance: 100% (CC <= 10)
- **Changes**:
    - **Release**: Tagged `v3.5.0` and pushed to GitHub.
    - **Automation**: Implemented `memory_prune.py`, `context_selector.py`, and `metrics_report.py`.
    - **Artifacts**: Optimized `make package` to produce a 100% agent-free distribution ZIP.
- **Status**: Phase v3.5.0 Closed.

## [2026-04-29] Session: Docstring Coverage Campaign (Phase v3.5.0)
- **Achievement**: Reached **100.0% Docstring Coverage** (Google style) and **100.0% Return Type Coverage** across the entire project.
- **Operational Metrics**:
    - Docstring Coverage: 100.0%
    - Return Type Coverage: 100.0%
    - Param Type Coverage: 97.3%
    - Passing Tests: 620 (baseline)
- **Changes**:
    - **Core**: Added comprehensive docstrings to `controller.py`, `export_service.py`, and `validators.py`.
    - **GUI**: Documented `main_dialog.py`, `dialog_interpretation_manager.py`, and `preview_param_hasher.py`.
    - **Plugin**: Standardized docstrings in `sec_interp_plugin.py`.
- **Status**: Completed. Transitioning to Gen 6 scripts.
- **Achievement**: Reached **100.0% Docstring Coverage** (Google style) and **100.0% Return Type Coverage** across the entire project.
- **Operational Metrics**:
    - Docstring Coverage: 100.0%
    - Return Type Coverage: 100.0%
    - Param Type Coverage: 97.3%
    - Passing Tests: 620 (baseline)
- **Changes**:
    - **Core**: Added comprehensive docstrings to `controller.py`, `export_service.py`, and `validators.py`.
    - **GUI**: Documented `main_dialog.py`, `dialog_interpretation_manager.py`, and `preview_param_hasher.py`.
    - **Plugin**: Standardized docstrings in `sec_interp_plugin.py`.
- **Status**: Completed. Transitioning to Gen 6 scripts.

## [2026-04-29] Start of Phase v3.5.0 (Operational Excellence & Agentic Autonomy)
- **Goal**: Achieve 100% docstring coverage and implement Generation 6 autonomous maintenance scripts.
- **Estimated Duration**: 1 week.
- **Priorities**: Docstring coverage campaign, `memory_prune.py`, `context_selector.py`, and `pre-push` CC gate.

## [2026-04-28] Session: QGIS 4 Readiness & CC Merge
- **Achievement**: Finalized QGIS 4.x (Qt6) compatibility and merged the massive Cyclomatic Complexity refactoring branch (`refactor/cc-compliance`) into `main`.
- **Changes**:
    - **Compatibility**: Updated `metadata.txt` (qgisMaximumVersion=4.99), `README.md`, and `conf.py` (version 3.4.0 + Qt6 mocks).
    - **Merge**: Integrated 4 batches of CC reduction, achieving project-wide compliance with CC <= 10.
    - **Verification**: 571/571 tests OK. 100% API-agnostic (no PyQt5).
- **Status**: Completed. Phase v3.4.0 initialization.
- **Maintenance**: [session_2026-04-28_qgis4_readiness_and_cc_merge.md](maintenance/session_2026-04-28_qgis4_readiness_and_cc_merge.md)

## [2026-04-28] Session: QGIS 4 Readiness & CC Merge
- **Achievement**: Finalized QGIS 4.x (Qt6) compatibility and merged the massive Cyclomatic Complexity refactoring branch (`refactor/cc-compliance`) into `main`.
- **Changes**:
    - **Compatibility**: Updated `metadata.txt` (qgisMaximumVersion=4.99), `README.md`, and `conf.py` (version 3.4.0 + Qt6 mocks).
    - **Merge**: Integrated 4 batches of CC reduction, achieving project-wide compliance with CC <= 10.
    - **Verification**: 571/571 tests OK. 100% API-agnostic (no PyQt5).
- **Status**: Completed. Phase v3.4.0 initialization.
- **Maintenance**: [session_2026-04-28_qgis4_readiness_and_cc_merge.md](maintenance/session_2026-04-28_qgis4_readiness_and_cc_merge.md)


## [2026-04-27] Session: CC Compliance Gen 6
- **Achievement**: Reached full compliance with cyclomatic complexity quality gates (CC <= 10). Extracted monolithic methods into specialized sub-methods while preserving the Extract-then-Compute core/GUI isolation.
- **Changes**:
    - **Refactoring**: Decomposed highly complex functions in `qgis.py`, `drillhole.py`, `collar_processor.py`, `drillhole_orchestrator.py`, `preview_layer_factory.py`, and more.
    - **Docstrings**: Formatted all new helper method docstrings to imperative mood to satisfy strict D401 requirements.
    - **Quality**: Enforced global code formatting using `ruff format` and `black`.
- **Status**: Completed. 0 HIGH_COMPLEXITY offenders.
- **Maintenance**: [session_2026-04-27_cc_compliance_gen6.md](maintenance/session_2026-04-27_cc_compliance_gen6.md)

## [2026-04-27] Agentic Standards Upgrade (Gen 5 → Gen 6 Roadmap)
- **Achievement**: Upgraded `.agent/` system to 2025/2026 agentic industry standards.
  Closed all Gen 5 targets and defined the Gen 6 roadmap.
- **Changes**:
    - **Agent system**: Fixed phantom skill reference (`domain-logic` → `geological-logic`).
    - **Stop conditions**: Added explicit escalation tables to `build-feature.md` and `close-session.md`.
    - **Memory**: Restructured `AGENT_LESSONS.md` (YAML fixed, 12 lessons pruned). Created `memory_policy.md` (3-tier model, 90-day rule, conflict resolution).
    - **Nested AGENTS.md**: Created `core/AGENTS.md` and `gui/AGENTS.md` with layer-specific constraints.
    - **Observability**: Upgraded `agent_metrics.json` to schema v2.0 (TCR, retries, stop events).
    - **Roadmap**: Updated `OPTIMIZATION_PLAN.md` — Gen 5 complete, Gen 6 targets defined.
- **Quality**: 571/571 tests OK. 0 skill_sync warnings. TCR: 100%.
- **Maintenance**: [session_2026-04-27_agentic_standards_upgrade.md](maintenance/session_2026-04-27_agentic_standards_upgrade.md)

## [2026-04-26] Complexity Refactoring (v3.4.0)
- **Achievement**: Eliminated all high-complexity functions identified by qgis-analyzer 1.13.1, achieving 0 HIGH_COMPLEXITY issues.
- **Changes**:
    - **Refactoring**: Decomposed monolithic functions in `drillhole_orchestrator.py`, `preview_service.py`, `drillhole_3d_exporter.py`, and `settings_page.py`.
    - **Standardization**: Applied project-wide formatting with `black` and `ruff`.
    - **Tooling**: Updated `qgis-plugin-analyzer` to 1.13.1.
- **Quality**: 571/571 tests OK. HIGH_COMPLEXITY: 0.
- **Maintenance**: [session_2026-04-26_complexity_refactoring.md](maintenance/session_2026-04-26_complexity_refactoring.md)

## [2026-04-26] Signal Leak Fix
- **Achievement**: Resolved a critical signal leak in the Interpretation settings page.
- **Changes**:
    - Refactored InterpretationPage to use the connect/disconnect_signals pattern.
    - Performed a deep audit of the qgis-analyzer tool source code.
- **Quality**: 620/620 tests OK. Signal Leaks: 0.
- **Maintenance**: [session_2026-04-26_fix_signal_leak.md](maintenance/session_2026-04-26_fix_signal_leak.md)

## [2026-04-25] Session: Flake8 Linting Cleanup
- **Achievement**: Cleaned up 104 Flake8 linting errors across the entire codebase to achieve full compliance with strict QGIS repository standards.
- **Changes**:
    - **Code Quality**: Added missing type hints and core imports, suppressed unfixable module-level import warnings for `flake8`, and ensured clean pipeline execution alongside `ruff` and `black`.
    - **Maintenance**: Deployed clean code and verified completely empty Flake8 logs.
- **Status**: Completed. 0 Flake8 errors remaining.
- **Maintenance**: [session_2026-04-25_flake8_linting_cleanup.md](maintenance/session_2026-04-25_flake8_linting_cleanup.md)

## [2026-03-30] Session: Documentation Modernization (v3.4.0 Audit)
- **Achievement**: Modernized the plugin's architectural documentation to reflect the major refactor reaching version 3.4.0. Updated i18n workflows to reflect the new Master Data SSoT system.
- **Changes**:
    - **Architecture**: Redrew Mermaid diagrams and updated `ARCHITECTURE_EN.md` with Manager-based GUI and Interface-driven Core details.
    - **i18n**: Rewrote `MAINTENANCE_I18N.md` in English, documenting the new automated `make transup` pipeline and parallel translation engines.
    - **Metrics**: Synchronized project SLOC and Complexity using `ai-context-core`.
- **Status**: Completed. Metrics: 121 modules, SLOC 12,633.
- **Maintenance**: [session_2026-03-30_docs_modernization_v340.md](maintenance/session_2026-03-30_docs_modernization_v340.md)

## [2026-03-29] Session: Autonomous Agent i18n Refactor
- **Achievement**: Refactored the core i18n workflow by consolidating translations into `master_data/*.json`, replacing error-prone XML Regex parsers with native `ElementTree.indent`, and enabling clean git diffs with `sort_keys=True` in Google Translate automatons.
- **Changes**:
    - **i18n Scripts**: Deleted legacy `apply_baseline.py` and `clean_translations.py`. Formatted `apply_full.py` to handle ast injection and formatting safely.
    - **Integration**: Updated `Makefile` to accommodate new streamlined `make transup` target.
    - **Documentation**: Overhauled `scripts/i18n/README.md` to reflect the new Single Source of Truth architecture and provide deep translation guidelines.
- **Status**: Completed. Pipeline 100% functional.
- **Maintenance**: [session_2026-03-29_autonomous_agent_i18n_refactor.md](maintenance/session_2026-03-29_autonomous_agent_i18n_refactor.md)

## [2026-03-29] Session: i18n Stabilization & v3.4.0 Release
- **Changes**:
    - **Core**: Repaired integration test assertions expecting raw `360` instead of properly normalized `0.0` azimuths.
    - **Release**: Built, checked, and signed `dist/sec_interp.3.4.0.zip` with full markdown English integration (Phase Closure v3.4.0).
- **Status**: Completed. 620/620 tests OK (Docker).
- **Maintenance**: [session_2026-03-29_i18n_release_v3.4.0.md](maintenance/session_2026-03-29_i18n_release_v3.4.0.md)

## [2026-03-25] Session: Unified Export Architecture & Sync
- **Achievement**: Refactored the export architecture to use a unified GeoPackage storage strategy and enabled layer-backed bi-directional synchronization for interpretation polygons.
- **Changes**:
    - **Core**: Grouped all Shapefiles inside `[SectionName]/` directories and placed multi-layer data inside one `export_all_[SectionName].gpkg`.
    - **Exporters**: Propagated `layer_name` correctly across all 3D/2D exporters to enable GeoPackage appending. Forced `QgsWkbTypes.Polygon` geometry for 2D interpretations. Added missing docstrings (`D417`).
    - **Sync**: Implemented `sync_from_layer()` and `save_to_layer()` in `InterpretationManager`.
- **Status**: Completed. 604/604 tests OK (Docker).
- **Maintenance**: [session_2026-03-25_unified_export_architecture.md](maintenance/session_2026-03-25_unified_export_architecture.md)

## [2026-03-22] Session: Update ai-context-core v3.3.0
- **Achievement**: Updated `ai-context-core` to v3.3.0, resolving a critical aggregation bug in reports and enabling new QGIS compliance analysis. Verified with `ai-ctx analyze`.
- **Changes**:
    - **Dependencies**: Updated `pyproject.toml` and `uv.lock` for `ai-context-core>=3.3.0`.
    - **Analysis**: Regenerated `AI_CONTEXT.md`, confirming fix for zeroed global metrics (Functions, Classes, MI).
    - **Verification**: Confirmed new "QGIS Standards Compliance" score (80.3/100).
- **Status**: Completed.
- **Maintenance**: [session_2026-03-22_update_ai_context_core_v330.md](maintenance/session_2026-03-22_update_ai_context_core_v330.md)

## [2026-03-19] Session: DXF/GPKG Export Stabilization
- **Achievement**: Stabilized DXF and GeoPackage export functionality by fixing a critical signature mismatch in `ExportService._export_drillholes_3d`. Verified all vector export formats (SHP, GPKG, DXF) using a reproduction script in the QGIS Docker environment. 604 tests passing.
- **Changes**:
    - **Core**: Fixed `TypeError` in `_export_drillholes_3d` where `DXFExporter` (generic) was being used for specialized drillhole data.
    - **Exporters**: Specialized exporters (`DrillholeTrace3DExporter`, etc.) correctly handle DXF/GPKG through the unified `scu_io.create_vector_writer`.
    - **Context**: Updated `AI_CONTEXT.md` and `TESTING_STATUS.md`.
- **Status**: Completed (v3.4.0 Phase).
- **Maintenance**: [session_2026-03-19_export_dxf_gpkg.md](maintenance/session_2026-03-19_export_dxf_gpkg.md)

## [2026-03-15] Agentic System Modernization: Generation 5 (v3.5.0-dev)
- **Achievement**: Successfully transitioned the `.agent/` system to Generation 5 architecture, implementing MCP native orchestration and achieving QGIS 4.x (Qt6) readiness.
- **Changes**:
    - **Architecture**: Implemented a native MCP server (`scripts/mcp_server.py`) for standardized tool orchestration.
    - **Context**: Standardized all system context (Lessons, Optimization Plan) to technical English for AI precision.
    - **Compatibility**: Removed legacy `PyQt5` hard dependencies from `pyproject.toml` and `requirements.txt`.
    - **Workflow**: Added `/fix-linting.md` for automated technical debt management.
- **Status**: System verified as Qt6-ready with `qgis-analyzer v1.10.0`.
- **Maintenance**: [session_2026-03-15_agentic_system_modernization.md](maintenance/session_2026-03-15_agentic_system_modernization.md)

## [2026-03-15] Fix: DXF Export and Robust Drillhole Intervals (v3.4.0)
- **Achievement**: Resolved critical DXF export failures and improved drillhole data integrity for small segments.
- **Changes**:
    - **Core**: Enhanced `drillhole.py` with mandatory interpolation at start/end depths to prevent missing intervals.
    - **Export**: Fixed `io.py` to strip unsupported fields for DXF format, resolving OGR driver errors.
    - **Bugfix**: Resolved `KeyError: 0` in `DXFExporter` and cleaned up redundant special-casing in `ExportService`.
    - **Quality**: Global reformatting and removal of ruff-detected magic numbers.
- **Status**: Export system fully functional for SHP, GPKG, and DXF.
- **Maintenance**: [session_2026-03-15_dxf_and_drillhole_fixes.md](maintenance/session_2026-03-15_dxf_and_drillhole_fixes.md)

## [2026-03-15] Fix: Export Format Persistence Standardized (v3.4.0)
- **Achievement**: Resolved issue where export format (GPKG, DXF) was not persisting and standardized settings prefix.
- **Changes**:
    - **Core**: Updated `ConfigService` to load the `export` category from `QgsSettings`.
    - **UI**: Standardized all `QgsSettings` keys to `SecInterp/` prefix in `SettingsPage`.
    - **Cleanup**: Updated `AccessControlService` and tests to match new standardized keys.
- **Status**: Export format persistence 100% verified.

## [2026-03-15] Export Refactoring & 3.4.0 Stabilization (v3.4.0)
- **Achievement**: Generalized the vector writing system and fixed all test regressions.
- **Changes**:
    - **Core**: Unified vector writer in `io.py` supporting SHP, GPKG, and DXF.
    - **Refactoring**: Ported all specialized exporters to the new centralized I/O system.
    - **Verification**: Achieved 100% test success in Docker (71/71 OK).
- **Status**: Export infrastructure stabilized for v3.4.0.
- **Maintenance**: [session_2026-03-15_export_refactoring.md](maintenance/session_2026-03-15_export_refactoring.md)

## [2026-03-15] Skill Integration: Changelog Generator (v3.4.0)
- **Achievement**: Successfully integrated the `changelog-generator` skill into the project's core workflows and updated AI standards.
- **Changes**:
    - **Skills**: Relocated `changelog-generator` to `.agent/skills/` for project compliance.
    - **Workflows**: Integrated the skill into `close-session`, `release-plugin`, and `close-phase` workflows.
    - **Documentation**: Updated `AGENTS.md` with comprehensive documentation for specialized AI skills.
- **Status**: Workflows enhanced and standardized.
- **Maintenance**: [session_2026-03-15_skill_integration_changelog.md](maintenance/session_2026-03-15_skill_integration_changelog.md)

## [2026-03-15] Advanced Export Planning (v3.4.0)
- **Achievement**: Fixed IDE language server and established implementation plan for Phase 3.4.0 (GeoPackage/DXF/Custom Naming).
- **Changes**:
    - **IDE**: Switched language server to "Default" to solve Pylance missing issue.
    - **Analysis**: Confirmed successful refactoring of `ExportService`.
    - **Planning**: Outlined architecture for `GpkgfileExporter`, `DXFExporter`, and naming patterns.
- **Status**: Ready for v3.4.0 implementation.
- **Maintenance**: [session_2026-03-15_advanced_export_planning.md](maintenance/session_2026-03-15_advanced_export_planning.md)

## [2026-03-14] Start of Phase v3.4.0 - Advanced Export & Complexity Reduction
- **Goal**: Implement new `GpkgfileExporter`, configurable naming options, and reduce architecture complexity.
- **Estimated Duration**: 2 weeks.
- **Priorities**:
    1. New `GpkgfileExporter` (independent from Shapefile).
    2. Native DXF 3D support.
    3. UI format selector and naming options.
    4. Complexity reduction in `ExportManager`.

## [2026-03-14] Release v3.3.0 - Extreme Stability & QGIS 4.x Readiness
- **Achievement**: Officially finalized and packaged v3.3.0. Verified with 607 tests, security scans, and API-agnostic audit.
- **Changes**:
    - **Documentation**: Finalized English/Spanish changelogs and generated official release notes.
    - **Verification**: Completed deep security scan (Score: 100/100) and verified QGIS 4.x compliance.
    - **Packaging**: Built optimized distribution ZIP (3.7MB) with full offline multi-language help.
    - **Analysis**: Archived detailed refactoring report for v3.3.0.
- **Status**: Suite 100% green (607/607 OK).
- **Maintenance**: [analysis_v3.3.0_refactoring.md](maintenance/analysis_v3.3.0_refactoring.md)

## [2026-03-12] Stability & Type Safety (v3.3.0 Final)
- **Achievement**: Completed v3.3.0 with robust resource cleanup, standardized core types, and 100% passing test suite (607 tests).
- **Changes**:
    - **Stability**: Implemented explicit resource cleanup in `main_dialog.py`, `measure_tool.py`, and `dialog_signal_manager.py`.
    - **Quality**: Standardized `DrillholeProjection` DTO and added comprehensive return type hints in core services.
    - **Deployment**: Refined `.qgisignore` for cleaner releases and verified deployment to local QGIS profile.
- **Quality**: Suite 100% green (607/607 OK).
- **Maintenance**: [session_2026-03-12_stability_v3.3.0_final.md](maintenance/session_2026-03-12_stability_v3.3.0_final.md)

## [2026-03-10] Unittest Standardization & Global Reformat
- **Achievement**: Codified strict `unittest` and "Mock-First" standards in `AGENTS.md` and normalized code style project-wide.
- **Changes**:
    - **Documentation**: Updated `AGENTS.md` with foundation rules (`BaseTestCase`), naming conventions, and QGIS best practices.
    - **Infrastructure**: Verified testing stability with `make test` (558 tests OK).
    - **Style**: Performed global reformatting covering 81 files using `ruff` and `black`.
    - **Brain**: Synchronized project context with session results.
- **Status**: Suite 100% green (558 tests).
- **Maintenance**: [sesion_2026-03-10_unittest_standardization.md](maintenance/sesion_2026-03-10_unittest_standardization.md)

## [2026-03-09] GUI Coverage Expansion (91%)
- **Achievement**: Exceeded the 90% GUI coverage goal, reaching 91% total for the `/gui` directory.
- **Changes**:
    - **Testing**: Implemented 7 new specialized test suites for Managers and Orchestrators.
    - **Infrastructure**: Standardized `qt_mocks.py` (QRectF, QSizeF, QWidget constants) enabling arithmetic-based rendering tests.
    - **Managers**: Achieved >94% coverage in `InterpretationManager`, `SettingsPersistence`, and `ExportManager`.
    - **Rendering**: Reached 100% coverage for `PreviewLegendRenderer` and 97% for `PreviewTaskOrchestrator`.
    - **Stability**: Fixed memory management in tests by enforcing strict `QApplication` instance handling and signal disconnection.
    - **Validation**: Verified all Phase 3 "Specialized Pages" targets.

---
## [2026-03-03] Start of Phase v3.3.0 (Strict Quality & i18n)
- **Goal**: Raise return type hints coverage, audit i18n, and refactor complexity hotspots.
- **Estimated Duration**: 1 week.
- **Priorities**:
    1. Return Type Hints Coverage (Target: >= 70%).
    2. i18n Audit and Cleanup (895 findings).
    3. Refactoring 3 high-complexity functions.

## [2026-03-02] - Phase 3.2.0: QGIS 4.x Readiness & Structural Refinement
- **Achievement**: Successfully completed 3.2.0 release cycle with 100% QGIS 4.x API compliance and suite expansion to 455 tests (all green).
- **Changes**:
    - **Compatibility**: Audit confirmed 100% adherence to API-agnostic principles (`qgis.PyQt`) and non-blocking `QgsTask` usage.
    - **Refactoring**: Extracted shared geometry logic in `PreviewLayerFactory` (`_apply_exaggeration`, `_to_qgs_points`).
    - **Refactoring**: Standardized widget reset logic in `DialogSettingsPersistence`.
    - **Security**: Implemented Path Traversal protection in all exporters.
    - **Testing**: Fixed 4 legacy skipped tests in `test_utils.py` by updating mocks to native QGIS API.
    - **Integration**: Created `test_3d_projections.py` to verify Cartesian robustness in 3D data exports.
    - **Validation**: Unified validation logic in `PreviewParams` delegating to `ProjectValidator`.
    - **UX**: Implemented real-time progress reporting for asynchronous drillhole tasks.
- **Status**: Suite 100% green (455 tests).
- **Maintenance**: [walkthrough.md](../walkthrough.md)

---
## [2026-03-09] Preview Signal Stability & 3D Style Fix
- **Achievement**: Restored real-time status bar updates in Preview and fixed color differentiation in 3D exports.
- **Changes**:
    - **Stability**: Standardized `connect_signals()`/`disconnect_signals()` pattern for `PreviewWidget` and `PreviewManager`.
    - **Reliability**: Integrated Preview components into `SignalManager` to ensure UI reactivity after page switches.
    - **3D Export**: Replaced unstable Data-Defined Properties with `QgsRuleBased3DRenderer` in `Interpretation3DExporter`.
    - **UI**: Fixed 3D material modulation by switching default base color to white.
- **Status**: Suite 100% green (540 tests - added 5 new restoration tests).
- **Maintenance**: [session_2026-03-09_preview_signals_and_3d_styling.md](maintenance/session_2026-03-09_preview_signals_and_3d_styling.md)

---
## [Unreleased]
## [2026-03-16] Type Hint Coverage Analysis & Bug Discovery
- **Achievement**: Re-verified the project's true Return Type Hint coverage via AST analysis (achieving 89.0%) and documented a fatal regex parsing bug in `qgis-plugin-analyzer`.
- **Changes**:
    - **Analysis**: Wrote `ast_coverage.py` script to bypass the `qgis-analyzer` parsing failure.
    - **Code Quality**: Corrected missing type hints in private methods throughout `core/services/drillhole/` and `ExportService`.
    - **Documentation**: Generated `docs/maintenance/qgis_analyzer_type_hint_bug.md` proposing an `ast`-based refactor to the plugin authors.
    - **Formatting**: Project-wide formatting applied via `ruff format` and `black`.
- **Status**: False positive resolved. Suite 100% stable.
- **Maintenance**: [session_2026-03-16_type_hints_bug_fix.md](maintenance/session_2026-03-16_type_hints_bug_fix.md)

## [2026-03-08] - Phase 3.3.0: Agentic System Standardization & 2025 Audit
- **Achievement**: Fully translated the internal agentic system (.agent/) to English and implemented 2025 industry enhancements (Reflection Loops & Structured Outputs).
- **Changes**:
    - **Documentation**: Translated 12 skills and 15 workflows to English.
    - **Architecture**: Integrated Formalized Reflection Loops in `AGENTS.md` and "Pre-flight Self-Audit" in memory protocols.
    - **Automation**: Formalized YAML structured completion in core workflows.
    - **Sync**: Updated `AGENTS.md` and `QUICK_REFERENCE.md` to reflect the new standardized state.
- **Status**: System synchronized (12 skills, 15 workflows, 535 tests OK).
- **Maintenance**: [session_2026-03-08_system_standardization.md](maintenance/session_2026-03-08_system_standardization.md)
- **Achievement**: Cubierta total (100%) del módulo de exportación de archivos mediante la generación de 5 nuevas suites completas de pruebas unitarias soportadas por Mocks.
- **Changes**:
    - **Tests**: Añadidos tests unitarios exhaustivos para `ImageExporter`, `PDFExporter`, `SVGExporter`, `ShapefileExporter` e `Interpretation2DExporter`.
    - **Mocks**: Robustecida la infraestructura de utilidades Qt en `tests/mocks/qt_mocks.py` resolviendo problemas de atributos perdidos sin instancia completa.
- **Status**: Suite 100% verde (535 tests).
- **Maintenance**: [session_2026-03-08_exporters_coverage.md](maintenance/session_2026-03-08_exporters_coverage.md)
## [2026-03-08] - Fase 3.3.0: Testing Expansion (Integración)
- **Achievement**: Alcanzado el hito de 514 pruebas exitosas en Docker con cobertura del 86% en integración de UI y orquestadores asíncronos.
- **Changes**:
    - **Tests**: Implementada cobertura End-to-End para el Servicio de Exportación completo.
    - **Tests**: Creado suite profunda de evaluación para el `PreviewManager` (LOD, dependencias resolutorias, bounding boxes).
    - **Tests**: Cubierta la filtración asíncrona de geología y buffer en in-memory layers.
    - **Tests**: Añadidos tests funcionales y de QA para el Despachador de Tareas Asíncronas (Tasks Orchestrators).
- **Status**: Suite 100% verde (514 tests).
- **Maintenance**: [session_2026-03-08_integration_testing.md](maintenance/session_2026-03-08_integration_testing.md)

---
## [2026-03-08] - Phase 3.3.0: Resource Stability and Lifecycle (Phase 1 completed)
- **Achievement**: Successfully finalized Phase 1 by resolving multiple GUI lifecycle issues and restoring export robustness.
- **Changes**:
    - **Memory Safety**: Implemented exhaustive memory cleanup in `closeEvent` (resolving `QgsRubberBand` leaks).
    - **GUI Lifecycle**: Created idempotent systems in `ToolManager` and `SignalManager` allowing clean re-executions.
    - **Data Models**: Refactored `Interpretations` to use standard mock vector layers ensuring export compatibility.
    - **Export Services**: Extended 2D and 3D drillhole export to recognize `DrillholeProjection` instances in addition to primitive tuples.
- **Status**: Phase 1 stable with 409 tests passing (100%).
- **Maintenance**: [session_2026-03-08_phase1_stability.md](maintenance/session_2026-03-08_phase1_stability.md)

---
## [2026-03-01] - Phase 3.2.0/3.2.1: Testing Expansion (Afternoon)
- **Achievement**: Reached milestone of 450 tests OK in Docker and automated testing documentation.
- **Changes**:
    - **Tests**: Implemented coverage for asynchronous tasks, core services, and state renderers.
    - **Automation**: Created `update_testing_status.py` script integrated into the `Makefile`.
    - **Stability**: Fixed regression in the trajectory engine.
- **Status**: Suite 100% green (450 tests).
- **Maintenance**: [session_2026-03-01_testing_expansion.md](maintenance/session_2026-03-01_testing_expansion.md)
### Added
- **Security**: Path Traversal protection in all data exporters.
- **Validation**: Type and range validation for preview parameters in `PreviewParams`.

### Fixed
- **Memory**: Resolved memory leaks from unreleased `QgsRubberBand` and missing signal disconnections in reset/clear buttons.
- **Stability**: Fixed critical system exception capture, allowing for clean QGIS termination.
- **Stability**: Fixed layer resolution via centralized `LayerResolver` with cache.
- **Validation**: Unified project validation logic, eliminating duplication in DTOs.
- **UX**: Implemented reactive progress reporting for drillhole generation in the UI.
- **Mocks**: Robust testing environment with support for unique layer IDs and strict geometry and field validation.
- **Stability**: Fixed `TypeError` in `ProfileController` due to dependency injection mismatch.

---
## [2026-03-01] - Fase 3.0.1: Estabilización, Seguridad y Gestión de Memoria (14:30)
- **Achievement**: Implemented critical security (Path Traversal) and stability (Signal Leaks & Memory) improvements, resolving renderer regressions and achieving a green suite.
- **Changes**:
    - **Security**: Path Traversal protection in exporters via absolute path resolution.
    - **Memory**: Explicit `QgsRubberBand` cleanup and reinforced UI signal disconnection.
    - **Resilience**: Correction of critical exception handling (`KeyboardInterrupt`) and early parameter validation in DTOs.
    - **Cleanup**: Elimination of dead duplicated code in the preview renderer.
- **Status**: Stabilization v3.0.1 verified with 124 tests OK.
- **Maintenance**: [session_2026-03-01.md](logs/session_2026-03-01.md)

---
## [2026-02-28] - Phase 3: LayerResolver Refactor and UX Feedback (20:30)
- **Achievement**: Centralized layer resolution with caching and unified parameter validation, improving performance and maintainability.
- **Changes**:
    - **LayerResolver**: Implemented caching system for layer resolution.
    - **Validation**: Unified validation logic in `PreviewParams` delegating to `ProjectValidator`.
    - **UX**: Implemented real-time progress reporting in `DrillholeGenerationTask`.
    - **Tests**: Robust mocked suite (unique IDs, WKB types, QgsFields).
- **Status**: Phase 3 (UX & Perf) verified with 229 tests OK.
- **Maintenance**: [session_2026-02-28_refactor_layer_resolver.md](maintenance/session_2026-02-28_refactor_layer_resolver.md)

---
## [2026-02-25] - Phase 2.1 Stabilization: Drillhole and Rendering Hotfixes (22:30)
- **Achievement**: Resolved 3 critical regressions introduced by Phase 2 optimization, restoring drillhole rendering and trajectory engine stability.
- **Changes**:
    - **Fix DI**: Corrected argument mismatch in `DrillholeTaskOrchestrator`.
    - **Fix Robustness**: Added guards against empty trajectories in `TrajectoryEngine` (Prevents `IndexError`).
    - **Fix Rendering**: Implemented polymorphic support in `PreviewLayerFactory` for `DrillholeProjection` objects.
- **Status**: System stabilized v4.1.0-hotfix.
- **Maintenance**: [session_2026-02-25_stabilization_phase_2_hotfixes.md](maintenance/session_2026-02-25_stabilization_phase_2_hotfixes.md)

---
## [2026-02-19] - Resilience Architecture (Lazy Loading) (07:15)
- **Achievement**: Implemented secure loading architecture post-SEV reversion to guarantee core stability.
- **Changes**:
    - Created `SafeLoader` for lazy and resilient import management.
    - Refactored `SecInterp` and `ProfileController` for service decoupling.
    - Regression tests (140+) confirmed successful post-refactor.
- **Status**: System robustified and in stable mode v4.0.4.
- **Maintenance**: [session_2026-02-19_resilience_architecture.md](maintenance/session_2026-02-19_resilience_architecture.md)

## [2026-02-18] GEOPHYSICAL INFRASTRUCTURE REGRESSION (SEV)
- **Note**: Decided to abort SEV implementation due to critical instabilities in the plugin loader post-refactoring.
- **Action**: Performed total regression to commit `d5b5837` to ensure v4.0.4 stability.
- **Lesson**: GUI refactoring and new dependency integration (`numpy`/`scipy`) require a more modular validation approach and isolated testing before final integration.
- **Maintenance**: [session_2026-02-18_cancelled_sev.md](maintenance/session_2026-02-18_cancelled_sev.md).

## [2026-02-18] INFRAESTRUCTURA (QGIS-MANAGER) Y TIPADO
- **Achievement**: Automatizado el parcheo de compatibilidad para QGIS (PyQt -> qgis.PyQt) en `qgis-manager` y reforzada la validación estructural del plugin.
- **Changes**:
    - **qgis-manager**: Implementado parcheo automático de recursos RCC y validación de `classFactory`.
    - **SecInterp**: Mejorado tipado en tareas asíncronas (`drillhole_task`, `geology_task`).
    - **Investigación**: Descartado soporte redundante de `.pluginignore`.
- **Maintenance**: [session_2026-02-18_infrastructure_qgis_manager.md](maintenance/session_2026-02-18_infrastructure_qgis_manager.md).
## [2026-02-18] I18N EXPANSION (HINDI/INDONESIAN) AND INFRASTRUCTURE AUDIT
- **Achievement**: Completed localization for `hi` and `id` and identified roadmap to modernize the deployment tool.
- **Changes**:
    - **i18n**: Injected master translations and compiled `.qm` files for Hindi and Indonesian.
    - **Technical Debt**: Removed `PyQt5` references in `resources.py`.
    - **Infrastructure**: Created Technical Roadmap to solve rigidities in `qgis-manager`.
- **Quality**: 382 tests OK. Clean `qgis-analyzer` report for legacy imports.
- **Maintenance**: [session_2026-02-18_i18n_qgis_manage.md](maintenance/session_2026-02-18_i18n_qgis_manage.md).

---
## [2026-02-18] DEEP TRANSLATION (USER GUIDE)
- **Achievement**: Completed deep localization for 7 priority languages (es, fr, de, it, pt_BR, ru, zh_CN, ja).
- **Changes**:
    - **i18n**: Finalized translation of tutorials and advanced functions in `.po` files.
    - **Quality**: Corrected language intrusion errors in `it.po` and `pt_BR.po`.
    - **Compilation**: Generated `.mo` binaries for all supported languages.
- **Maintenance**: [session_2026-02-18_deep_translation_user_guide.md](maintenance/session_2026-02-18_deep_translation_user_guide.md).

---
## [2026-02-18] EXPANSIÓN I18N (MARKET GAP)

- **Achievement**: Expandido el soporte a 14 idiomas (añadidos pl, nl, fi) con 100% de cobertura core.
- **Changes**:
    - **i18n**: Implementado motor de "Master Data" JSON y automatización de inyección.
    - **Infraestructura**: Creado workflow `/i18n-maintenance` y actualizada skill `i18n-standards`.
- **Calidad**: 16/16 Integration tests OK y 377+ unit tests validados.
- **Maintenance**: [session_2026-02-18_i18n_gap_expansion.md](maintenance/session_2026-02-18_i18n_gap_expansion.md).

---
## [2026-02-18] ESTABILIDAD DE MÓDULOS
- **Achievement**: Eliminados ciclos de importación circular y optimizada la estabilidad del sistema de validación.
- **Changes**:
    - **Refactorización**: Movida lógica a `validation_helpers.py` resolviendo 7 ciclos de dependencia.
    - **Maintenance**: Corregidos signal leaks en `settings_page.py`.
- **Calidad**: Module Stability optimizada de 0.0 a 53.7.
- **Maintenance**: [session_2026-02-18_module_stability.md](maintenance/session_2026-02-18_module_stability.md).

---
## [2026-02-17] RESUMEN: Refactorización de Hotspots (StateManager y ProjectValidator)
- **Achievement**: Reducción drástica de la complejidad ciclomática en los dos mayores "hotspots" del proyecto, mejorando la mantenibilidad y modularidad.
- **Changes**:
    - **StateManager**: Descompuesto en `DialogSettingsPersistence` y `UIStatusManager`. CC de 70 a modular.
    - **ProjectValidator**: Implementado patrón Pipeline con micro-validadores independientes (`IValidator`). CC de 44 a modular.
    - **Calidad**: Suite de 377 tests pasando al 100% tras la reubicación lógica.
- **Métricas**:
    - **Tests**: 377/377 OK (100%).
    - **CC**: Reducción significativa en el Top 10 de hotspots.
- **Maintenance**: [session_2026-02-17_refactor_hotspots.md](maintenance/session_2026-02-17_refactor_hotspots.md).

---
## [2026-02-16] RESUMEN: Estabilización de Señales e i18n
- **Achievement**: Resueltas fugas de señales en la GUI e internacionalizado el `ProfileController`. Suite de tests elevada a 386 OK.
- **Changes**:
    - **Señales**: Sistema de rastreo dinámico en `StateManager` para desconexión segura en `closeEvent`.
    - **i18n**: Cobertura total en `controller.py`.
    - **Estabilidad**: Ajuste de conexiones para compatibilidad dual con Mocks y tiempo de ejecución.
- **Métricas**:
    - **Tests**: 386/386 OK (Docker).
    - **i18n**: 100% en Core controller.
- **Maintenance**: [session_2026-02-16_stabilization_signals_i18n.md](maintenance/session_2026-02-16_stabilization_signals_i18n.md).

---
## [2026-02-15] RESUMEN: Estabilización de Mocks y Tests 3D Avanzados (Noche)
- **Achievement**: Suite completa (378 tests) estabilizada tras corregir fallos críticos de integridad de datos en mocks.
- **Changes**:
    - **Mocks Core**: Implementado parsing WKT en `MockQgsGeometry` y corregido bug de pérdida de atributos en `MockQgsFeature`.
    - **Exporters**: Estabilizada la exportación 3D asegurando tipos `LineStringZ` y `PolygonZ`.
    - **Integración**: Resuelta la falta de resultados en tests avanzados debido a fallos silenciosos en la recuperación de campos.
- **Métricas**:
    - **Tests**: 378/378 OK (100%).
    - **Calidad**: Entorno de pruebas 100% funcional y desacoplado.
- **Maintenance**: [session_2026-02-15_stabilization_mocks_3d.md](maintenance/session_2026-02-15_stabilization_mocks_3d.md).

---
## [2026-02-15] RESUMEN: Estabilización GUI y Exportación (Noche)
- **Achievement**: Estabilización final de la Fase 5 y reparación del subsistema de exportación.
- **Changes**:
    - **Critical Fix**: Resolución de capas por ID en `ExportService` (fin de `AttributeError`).
    - **Cleanup**: Eliminación definitiva de `message_manager` y `settings_manager` (Facade Pattern).
    - **UX**: Sistema de mensajes dual (QGIS Bar + Plugin Area) con feedback visual HTML.
- **Métricas**:
    - **Tests**: 361/361 OK (100%).
    - **Funcionalidad**: Exportación validada manualmente.
- **Maintenance**: [session_2026-02-15_stabilization_gui_export.md](maintenance/session_2026-02-15_stabilization_gui_export.md).

---
## [2026-02-15] RESUMEN: Resolución de Fugas de Señales y Estabilidad de UI
- **Achievement**: Resueltas 65 fugas de señales potenciales identificadas por `qgis-analyzer`.
- **Changes**:
    - **UI**: Implementado sistema de desconexión en cascada en `DialogSignalManager` y todas las páginas de configuración.
    - **Mantenibilidad**: Refactorizado `disconnect_all` para reducir complejidad y cumplir con estándares de `ruff`.
    - **Stability**: Asegurada la limpieza de señales en tareas asíncronas canceladas.
- **Métricas**:
    - **Signal Leaks**: Reducción neta de 36 fugas (Falsos positivos remanentes: 29).
    - **Tests**: 361/361 OK (100%).
- **Maintenance**: [session_2026-02-15_signal_leak_resolution.md](maintenance/session_2026-02-15_signal_leak_resolution.md).

---
## [2026-02-15] RESUMEN: Optimización Extrema del Paquete ZIP (v3.0.0)
- **Achievement**: Reducción del tamaño del plugin de **12.0 MB** a **2.5 MB** (-79%).
- **Changes**:
    - **Asset Pruning**: Eliminación de fuentes redundantes (~9MB), API docs y vistas de código fuente en el manual manual interno.
    - **Build System**: Makefile ajustado para evitar que `qgis-manage compile` sobreescriba la optimización.
    - **Infraestructura**: Despliegue automático de docs técnicos al repo externo `sec_interp_docs`.
- **Métricas**:
    - **ZIP**: 2.5 MB (Goal < 5MB OK).
    - **Tests**: 361/361 OK (100%).
- **Maintenance**: [session_2026-02-15_optimization_zip_size.md](maintenance/session_2026-02-15_optimization_zip_size.md).

---
## [2026-02-14] RESUMEN: Limpieza de Deuda Técnica (Documentación y PLR2004)
- **Achievement**: Alcanzado el 100% de cumplimiento en documentación (D100, D105, D107) y eliminación de números mágicos en los módulos `core/` y `gui/`.
- **Changes**:
    - **Documentación**: Corregidos 86 archivos con docstrings de módulo e inicializadores faltantes.
    - **Calidad**: Extraídas 40+ constantes para umbrales de validación, LOD y parámetros geológicos.
    - **Refinado**: El usuario pulió manualmente las cabeceras para una alineación estética total.
- **Métricas**:
    - **Quality Score**: 72.3/100 🟢.
    - **Tests**: 361/361 OK (100%).
- **Maintenance**: [session_2026-02-14_technical_debt_cleanup.md](maintenance/session_2026-02-14_technical_debt_cleanup.md).

---
## [2026-02-14] RESUMEN: Hotfixes de Exportación y Capas Opcionales
- **Achievement**: Resueltos bugs críticos de validación y manejo de capas opcionales detectados durante pruebas manuales exhaustivas.
- **Changes**:
    - **Drillholes**: Reparada lógica en `DrillholeService` para manejar limpiamente la ausencia de capas de Survey o Intervals.
    - **Validación**: Corregido typo en `DialogStatusManager` y reforzada la regla de validación de `output_path`.
    - **Exportación**: Añadida verificación de seguridad en `ExportManager`.
- **Métricas**:
    - **Tests**: 16 Integration tests OK + Suite base verificada.
    - **Status**: 🟢 Todas las componentes principales (Topo, Geología, Estructural, Sondajes, Interpretación, Exportación) validadas visualmente y funcionalmente.
- **Maintenance**: [session_2026-02-14_fixing_export_and_optional_layers.md](maintenance/session_2026-02-14_fixing_export_and_optional_layers.md).

---
## [2026-02-09] Tooling: Update qgis-plugin-analyzer v1.7.0
- **Achievement**: Actualizado `qgis-plugin-analyzer` a la versión 1.7.0.
- **Changes**:
    - **CLI**: Se detectó que el punto de entrada cambió de `qgis-plugin-analyzer` a `qgis-analyzer`.
    - **Dep**: Actualizado `pyproject.toml` y sincronizado el entorno con `uv sync`.
- **Verificación**: Ejecutada auditoría de línea base con `qgis-analyzer analyze .` exitosamente.
- **Diferenciación**: Se clarificó en toda la documentación la distinción entre el nombre de la herramienta (`qgis-plugin-analyzer`) y el comando CLI (`qgis-analyzer`).
- **Status**: 🟢 Herramienta operativa y actualizada.

---
## [2026-02-08] RESUMEN: Auditoría de Calidad y Enlace Ruff
- **Achievement**: Revelada la "falsa perfección" del 100/100. Identificado y parchado bug crítico en `qgis-analyzer` relacionado con flags de Ruff.
- **Changes**:
    - **Linting**: Activadas reglas estrictas de Docstrings (`D10x`) y Complejidad (`C901`, `PLR`).
    - **Análisis**: 686 incidencias detectadas tras habilitar auditoría real.
    - **Docs**: Creado reporte técnico de bugs en `docs/dev/qgis_analyzer_issues.md`.
- **Métricas**:
    - **Maintainability**: 100.0 (Masked by low CC & line count dilution).
    - **Compliance**: 66.4/100 OK.
- **Status**: 🟡 Fase de Calidad Estricta iniciada. 686 problemas identificados para corrección.
- **Maintenance**: [session_2026-02-08_qgis_quality_strict_audit.md](maintenance/session_2026-02-08_qgis_quality_strict_audit.md).

---
## [2026-02-08] CIERRE DE ESTABILIZACIÓN: 100% Tests Passing
- **Achievement**: Alcanzada la "Victoria Absoluta" con 347/347 tests pasando en entorno Docker (Core, GUI, Exporters, Integration).
- **Changes**:
    - **Refactorización de Tests**: `test_attribute_inheritance` y `test_cache_fix` desacoplados de la UI completa.
    - **Mocks**: Robustecidos `MockQWidget` y `MockQgsMapTool` para soportar ciclo de vida completo.
    - **Fixes Críticos**: Resuelto `TypeError` en exportación de estructuras y `AttributeError` en hashing de parámetros.
    - **Integración**: Corregido entorno de ejecución para tests de integración headless.
- **Métricas**:
    - **Quality Score**: 71.6/100 (Estable).
    - **Tests**: 347/347 OK (100%).
- **Docs**: Registro en [session_2026-02-08_stabilization_complete.md](maintenance/session_2026-02-08_stabilization_complete.md).
- **Status**: 🟢 Listo para Release v2.10.0.

---
## [2026-02-08] Resumen: Update ai-context-core v3.2.1
- **Achievement**: Actualizada la dependencia de `ai-context-core` a v3.2.1, resolviendo errores críticos de i18n scope (segmentación).
- **Changes**:
    - **Dep**: Actualizado `ai-context-core` de v3.2.0 a v3.2.1 en `pyproject.toml`.
    - **Fix**: Verificada la corrección de los Bug 1 (configuración), Bug 2 (recursion) y Bug 3 (CLI option) de la v3.2.0.
    - **Estilo**: Formateo masivo del proyecto con `black` para asegurar consistencia tras los cambios.
    - **Docs**: Creado reporte de resolución en [bug_report_v320.md](maintenance/ai-context-core/bug_report_v320.md) y registro de sesión en [session_2026-02-08_update_ai_core_v321.md](maintenance/session_2026-02-08_update_ai_core_v321.md).
- **Status**: 🟢 Verificado y estable. El scope `gui_only` ahora funciona correctamente.

---
## [2026-02-06] CIERRE DE FASE v2.10.0: Massive CC Reduction & 3D Prep
- **Achievement**: Completada la refactorización masiva de complejidad ciclomática y preparación arquitectónica para soporte 3D completo.
- **Cambios Principales**:
    - **Refactorización Core**: Reducción de CC en servicios (`DrillholeService`, `GeologyService`, `StructureService`) y utilidades críticas.
    - **Arquitectura 3D**: Implementación de `SpatialMeta` DTO con campos `x_proj`, `y_proj` para coordenadas proyectadas.
    - **Documentación**: Google-style docstrings completos en todos los módulos core (servicios, dominio, utilidades).
    - **Corrección de Regresiones**: 5 regresiones críticas detectadas y corregidas mediante validación rigurosa en Docker.
    - **Compatibilidad Dual**: Exportadores 3D y `PreviewLayerFactory` ahora soportan tanto formato nuevo (SpatialMeta) como legacy (tuplas).
- **Métricas**:
    - **Quality Score**: 59.0 (+0.5 desde baseline 58.5).
    - **Tests**: 347 tests pasando en contenedor Docker oficial de QGIS (206 Core + 15 Exporters + 110 GUI + 16 Integration).
    - **Archivos**: 78 modificados (+1,401 líneas, -456 líneas).
- **Commit**: `5a79417` - `refactor(core): massive CC reduction, 3D preparation, and core documentation`.
- **Docs**: Ver [session_2026-02-06_phase_closure_v2.10.0.md](maintenance/session_2026-02-06_phase_closure_v2.10.0.md).
- **Status**: 🟢 Estable y validado. Listo para v2.11.0.

---
## [2026-02-06] INICIO DE FASE v2.10.0: Calidad y QGIS 4.x
- **Objetivo**: Elevar el Quality Score > 60 y resolver deuda crítica de PyQt5.
- **Duración Estimada**: 1-2 días.
- **Prioridades**:
    1. Eliminación de importaciones directas de PyQt5 en `resources.py`.
    2. Reducción de complejidad en `ExportService`.
    3. Completar docstrings y type hints (meta 85% coverage).
- **Estado Inicial**: 199 tests OK, Quality Score 58.5. Plan oficial en `docs/plans/implementation_plan_v2.10.0.md`.

---
## [2026-02-05] Resumen: Evolución Arquitectónica (Cerebro Gen 3)
- **Achievement**: Implementada la Generación 3 del framework con Memoria Semántica, Auditoría Proactiva y Observabilidad.
- **Changes**:
    - **Cerebro**: Nueva skill `agentic-memory` y reestructuración de `AGENT_LESSONS.md` a YAML.
    - **Auditoría**: Registro del rol **Agent Auditor** y creación del workflow `/ia-critic`.
    - **Framework**: Actualización total del `antigravity-framerepo` (scaffold, docs, README) a Gen 3.
    - **Automatización**: Integración de actualización de memoria en `/inicia-sesion` y `/cierra-sesion`.
    - **Docs**: Registro de sesión [session_2026-02-05_agentic_brain_evolution_gen3.md](maintenance/session_2026-02-05_agentic_brain_evolution_gen3.md).
- **Status**: Sistemas Gen 3 verificados y operativos. Framework maestro actualizado.

---
## [2026-02-01] Resumen: Security Scan & Inicio Fase v2.10.0 (Tarde)
- **Achievement**: Implementado sistema de seguridad local compatible con QGIS Portal y arranque de fase de calidad.
- **Changes**:
    - **Security**: Script unificado `security_scan.py` (Bandit, detect-secrets, Flake8) e integración en CI/CD.
    - **Fase v2.9.0**: Cierre formal con 199 tests pasando y release estable.
    - **Fase v2.10.0**: Plan aprobado para eliminación de PyQt5 (QGIS 4.x) y refactorización de exportadores.
    - **Docs**: Registro de sesión [session_2026-02-01_security_scan_and_phase_init.md](maintenance/session_2026-02-01_security_scan_and_phase_init.md).
- **Status**: 199/199 tests OK. Escaneo de seguridad limpio.

## [2026-02-01] Resumen: Refactorización de ExportService y Estandarización
- **Achievement**: Reducida la complejidad técnica de `export_service.py` (CC de >60 a <10) y estandarizado el uso de `ai-ctx` vs `qgis-analyzer`.
- **Changes**:
    - **Refactor**: Descomposición de métodos monolíticos de exportación 3D.
    - **Tooling**: Integración de `ai-ctx` para mantenimiento diario.
    - **Docs**: Guía Generación 2 con recursos técnicos completos para el framework.
- **Status**: 126 tests OK (Core + Integration). Ver [session_2026-02-01_export_refactor_and_framework_standardization.md](maintenance/session_2026-02-01_export_refactor_and_framework_standardization.md).

## [2026-01-28] Resumen: Consolidación de Redundancias Fase 3 (Noche)
- **Achievement**: Completada la consolidación de redundancias en servicios core (v2.9.0) y resolución de regresiones críticas de importación y geometría.
- **Changes**:
    - **Refactor**: Unificación de `StructureService`, `GeologyService` y `DrillholeService` bajo flujo de datos desacoplado.
    - **Utils**: Centralización de extracción de líneas y preparación de contexto de sección en `core/utils`.
    - **Fix**: Resolución de error `AttributeError: 'QgsGeometry' object has no attribute 'clone'` mediante uso de constructores robustos.
    - **Ambiente**: Estandarización de `PYTHONPATH` y prefijos `sec_interp.` en todo el proyecto.
- **Status**: 206 tests OK (Total success en Phase 3). Ver [session_2026-01-28_phase3_consolidation_regressions.md](maintenance/session_2026-01-28_phase3_consolidation_regressions.md).

---
## [2026-01-27] Resumen: Suite 3D Completa y Preparación QGIS 4 (Noche)
- **Achievement**: Finalizada la implementación de la Suite de Integración 3D (v2.9.0) y establecida la infraestructura para QGIS 4.x.
- **Changes**:
    - **3D**: Pruebas de integración para transformaciones CRS complejas y corrección de proyección de collares en el Core.
    - **QGIS 4**: Creación de rama `qgis4-migration` y entorno `docker-test-nightly`.
    - **Calidad**: 100% Type Hints en servicios críticos y corrección de regresiones en tests.
- **Status**: 377 tests OK (Docker). Ver [session_2026-01-27_3d_integration_and_qgis4_prep.md](maintenance/session_2026-01-27_3d_integration_and_qgis4_prep.md).

## [2026-01-26] Resumen: Estabilización de Ai-Context-Core (v2.5.2)
- **Achievement**: Resuelto el bloqueo crítico en el análisis del proyecto mediante la actualización a la v2.5.2 de `ai-context-core`.
- **Changes**:
    - Identificada y verificada la persistencia del bug en la v2.5.1 de PyPI.
    - Actualizada dependencia a `ai-context-core>=2.5.2` en `pyproject.toml`.
    - Regenerado `AI_CONTEXT.md` y `PROJECT_SUMMARY.md` con métricas reales.
- **Status**: Análisis funcional completado exitosamente (Score 38.8). Ver [session_2026-01-26_ai_context_core_stabilization.md](maintenance/session_2026-01-26_ai_context_core_stabilization.md).

---
## [2026-01-25] INICIO DE FASE v2.9.0: Análisis Avanzado y Geometría
- **Objetivo**: Implementar soporte para secciones poligonales (túneles) y suite de tests 3D avanzada.
- **Duración Estimada**: 2 semanas.
- **Prioridades**: Soporte multi-segmento, integridad topológica 3D y optimización de grandes datasets.
- **Estado Inicial**: 359 tests OK, Quality Score 55.2.

---
## [2026-01-25] CIERRE DE FASE v2.8.0: Reducción de Deuda y Mejoras de UI
- **Hito**: Cierre formal de la Fase v2.8.0.
- **Achievements**: Desacoplamiento total del Core (WKT/DTO), refactorización de servicios y control de leyenda.
- **Calidad**: 359 tests OK (Docker). Quality Score estabilizado.
- **Status**: Fase completada. Ver [phase_closure_v2.8.0.md](maintenance/phase_closure_v2.8.0.md).

---
## [2026-01-25] Resumen: Refactorización Arquitectónica Core v2.9.1 (Tarde)
- **Achievement**: Descomposición exitosa del monolito `DrillholeService` y modularización del sistema de tipos.
- **Changes**:
    - Creado sistema de procesadores en `core/services/drillhole/` (`Collar`, `Survey`, `Interval`, `Projection`).
    - Implementado paquete `core/types/` separando Dominio, DTOs y Enums.
    - Creado **ADR-0008** y actualizado `ARCHITECTURE_EN.md`.
    - Eliminado código legacy y corregidos tests de integración core.
- **Status**: 208 Tests Core OK. Versión v2.9.1 lista para fase de Geometría. Ver [session_2026-01-25_refactorizacion_arquitectonica.md](maintenance/session_2026-01-25_refactorizacion_arquitectonica.md).

---
## [2026-01-25] Resumen: Refactorización de Tareas Background (Día)
- **Achievement**: Centralizada la extracción de datos en el hilo principal y optimizado el flujo asíncrono.
- **Changes**:
    - Refactorizados `GeologyService` y `DrillholeService` para usar DTOs planos (WKT/dicts) en la preparación de tareas.
    - Implementado método `azimuth` en `MockQgsPointXY` para soporte geométrico en tests.
    - Simplificado `PreviewManager` delegando lógica compleja a servicios.
    - Actualizada la suite de pruebas para coincidir con el desacoplamiento Core-QGIS.
- **Status**: 359 tests OK (Docker). Ver [session_2026-01-25_background_task_refactor.md](maintenance/session_2026-01-25_background_task_refactor.md).

---
## [2026-01-24] Resumen: Estabilización de Tests en Docker (Noche)
- **Achievement**: Restaurada la integridad de la CI/CD con 100% de éxito en entorno Docker.
- **Changes**:
    - Sincronizada la nomenclatura de DTOs (`GeologySegment`) en toda la suite de tests.
    - Implementado aislamiento de procesos en el `Dockerfile` para evitar contaminación de Mocks vs API Real.
    - Refactorizada la carga de Mocks en `tests/base_test.py` con control dinámico.
    - Robustecidos los Mocks con métodos de geometría faltantes.
- **Status**: 359 tests OK (Docker). Ver [session_2026-01-24_docker_test_stabilization.md](maintenance/session_2026-01-24_docker_test_stabilization.md).

---
## [2026-01-24] Resumen: Desacoplamiento Arquitectónico Core-QGIS (Noche)
- **Achievement**: Finalizada la arquitectura agnóstica del Core con 100% de éxito en tests.
- **Changes**:
    - Refactorizados `GeologyService` y `DrillholeService` para operar sobre DTOs agnósticos (WKT/primitivos).
    - Mocks de QGIS reconstruidos en `base_test.py` con soporte WKT.
    - Eliminada deuda técnica de shadowing de métodos en mocks.
- **Status**: Core validado (204 tests OK). Ver [session_2026-01-24_core_decoupling.md](maintenance/session_2026-01-24_core_decoupling.md).

---
## [2026-01-23] Hotfix: Sincronización y Persistencia de Medición (Noche)
- **Achievement**: Corregido el comportamiento de la herramienta de medición para permitir persistencia visual tras desactivación.
- **Changes**:
    - Eliminado el reset automático de `ProfileMeasureTool` al desactivar.
    - Implementado señal `measurementFinished` para sincronizar el estado del botón `btn_measure` en la UI.
    - Corregido `NameError` en `PreviewRenderer.export_to_image` relacionado con el parámetro `show_legend`.
    - Añadido reset explícito de mediciones en `Clear Cache` y `Reset Defaults`.
- **Status**: 110/110 GUI tests OK. Comportamiento verificado contra reporte de usuario.

---
## [2026-01-23] Refactorización de DrillholeService (Noche)
- **Achievement**: Reducida la complejidad de los métodos principales de `DrillholeService` mediante modularización.
- **Changes**:
    - Extraídas validaciones a métodos `_validate_*`.
    - Modularizado `prepare_task_input` con `_detach_collar_features` y `_pre_sample_z_for_task`.
    - Modularizado `process_task_data` con `_process_detached_collar_item`.
    - Fragmentados `_process_single_hole` y `_get_collar_info`.
    - Añadidos type hints y docstrings faltantes.
- **Status**: 361 tests OK (Docker). Estructura del núcleo más mantenible.

---
## [2026-01-22] Integración Completa de Workflows + Skills
- **Achievement**: Sistema de workflows completamente integrado con AGENTS.md y skills (100% de workflows).
- **Changes**:
    - Creadas 2 nuevas skills: `commit-standards` y `release-management`.
    - Actualizados 10 workflows con metadata YAML (agent, skills, validation).
    - Añadidas 40+ anotaciones `🤖 Agent Action` en workflows.
    - Mejorado `skill_sync.py` con validación automática de workflows.
    - Creado `QUICK_REFERENCE.md` para consulta rápida.
- **Skills totales**: 6 (commit-standards, geological-logic, qa-docker, qgis-core, release-management, ui-framework).
- **Workflows validados**: 10/10 (inicia-sesion, crea-commit, run-tests, refactor-code, release-plugin, release-plugin-en, cierra-sesion, cierra-fase, inicia-fase, run-tests-in-qgis).
- **Status**: 361 tests OK (Docker). Sistema workflow-aware completamente funcional.

---
## [2026-01-21] Refactorización de GeologyService (Tarde)
- **Achievement**: Fragmentados métodos largos en `GeologyService` para cumplir con los estándares de mantenibilidad.
- **Changes**:
    - Extraídas validaciones a `_validate_inputs`.
    - Extraída recopilación de datos a `_extract_outcrop_data`.
    - Modularizado procesamiento geométrico en `_extract_geometries` y `_calculate_segment_range`.
- **Status**: 361 tests OK (Docker). Deuda técnica reducida en el núcleo.

---
## [2026-01-20] Corrección de Documentación API (Noche)
- **Achievement**: Restaurada visibilidad completa de docstrings en el sitio de documentación.
- **Changes**:
    - Configurado mocking de QGIS/PyQt en `conf.py`.
    - Aplicado `from __future__ import annotations` a nivel de proyecto para soportar Union types con mocks.
    - Build de documentación estabilizado y desplegado.
- **Status**: Infraestructura de documentación 100% funcional.

---

## [2026-01-20] Implementación de Visibilidad de Leyenda (Mañana)
- **Achievement**: Implementado control granular de visibilidad para la leyenda en el preview y exportadores.
- **Changes**:
    - Añadido `show_legend` a `PreviewSettings` y persistencia en proyecto.
    - Nuevo checkbox `chk_legend` en la UI de Preview con actualización reactiva.
    - Actualizados exportadores (`Image`, `PDF`, `SVG`) para honrar el ajuste de visibilidad.
- **Bugs Corregidos**:
    - Resuelto problema de visibilidad persistente en `LegendWidget` interactivo.
    - Corregida fuga de leyenda en archivos exportados.
- **Status**: Funcionalidad verificada por el usuario y tests unitarios de modelo OK.

---

## [2026-01-19] Start of Phase v2.8.0 (Reducción de Deuda y Mejoras de UI)
- **Objetivo**: Reducción de deuda técnica en servicios core e implementación de controles de visibilidad para la leyenda.
- **Estado Inicial**: Calidad 83.5/100, 361 Tests OK (Docker).
- **Prioridades**:
    1. Refactorización de `GeologyService` (métodos largos).
    2. Checkbox para visibilidad de leyenda en Preview.
    3. Suite de tests de integración 3D.

---

## [2026-01-18] Resumen: Infraestructura de Documentación Externa (Noche)
- **Documentación Desacoplada**: Implementado repositorio externo `sec_interp_docs` con despliegue automático a GitHub Pages desde `build_docs.sh`.
- **Soporte Markdown**: Habilitado `myst_parser` para renderizar guías `.md` como parte del sitio de documentación oficial.
- **Soporte Mermaid**: Configurado `sphinxcontrib-mermaid` y `myst_fence_as_directive` para renderizar diagramas en archivos Markdown.
- **Metadatos**: Actualizados enlaces de documentación en `metadata.txt`, `README.md` y `pyproject.toml`.
- **Limpieza**: Repositorio principal saneado de archivos HTML generados.
- **Status**: Lista la infraestructura para el Release v2.7.0.

## [2026-01-18] Resumen: Release v2.7.0 Finalizado
**Fecha Última Actualización:** 2026-01-18
**Autor:** Antigravity
**Estado:** ¡Fase v2.7.0 Completada! 🎉 Todos los objetivos principales de excelencia operativa, documentación y exportación han sido alcanzados. Se han añadido mejoras finales de UI (iconos) e i18n en la última sesión. El proyecto está listo para el siguiente ciclo mayor.

Ciclo completo de release para la versión 2.7.0 "Operational Excellence & Documentation". Se estabilizó el entorno de pruebas (mocking fixes), se ejecutó la validación de calidad (analyzer, tests), se generaron los artefactos de distribución (ZIP, GitHub Release Draft) y se realizó una limpieza profunda del proyecto.

**Actividades Principales:**
- **Release:** Tag `v2.7.0` publicado, ZIP generado, GitHub Release creado.
- **Calidad:** 361 Tests pasando verificados en Docker.
- **Documentación:** Actualización exhaustiva de `USER_GUIDE.md` (3D Export details), `README.md` y centralización de Notas de Versión en `docs/releases/`.
- **Limpieza:** Reorganización del directorio raíz (logs, scripts, fixtures).
- **Detalles:** Ver [session_2026-01-18_release_v2.7.0.md](maintenance/session_2026-01-18_release_v2.7.0.md).

***

## [2026-02-14] Session Closing: Optimización del Sistema Agentico (Gen 4)

### Resumen Ejecutivo
Se realizó una actualización mayor al sistema `.agent` para consolidar las lecciones aprendidas durante el lanzamiento de v3.0.0 y preparar el terreno para el ciclo v3.0.1 y la futura migración a QGIS 4.x.

### Logros Clave
1.  **Arquitectura "Gen 4"**: Definido plan de optimización en `.agent/architecture/OPTIMIZATION_PLAN.md`.
2.  **Nuevas Capacidades**:
    *   **Skill `qgis-migration-4x`**: Guía experta para escribir código compatible con el futuro QGIS 4.0.
    *   **Skill `i18n-standards`**: Estandarización del flujo de traducción.
    *   **Workflow `/fix-linting`**: Automatización de limpieza de código (Ruff/Black).
3.  **Eficiencia Operativa**:
    *   Actualizados workflows críticos (`release-plugin`, `inicia-sesion`, `cierra-sesion`) para usar `uv run` y validaciones más estrictas.
    *   Integración de skills en `AGENTS.md` con disparadores automáticos.

### Próximos Pasos (Inmediato)
*   Ejecutar `/fix-linting` para cerrar issues de estilo en v3.0.1.
*   Iniciar refactorización gradual usando `qgis-migration-4x`.

---

## [2026-01-18] Cierre de Fase v2.7.0 (Noche)
- **Hito**: Cierre formal de la fase "Excelencia Operativa".
- **Entregables**: Documento de cierre generado (`docs/maintenance/phase_closure_v2.7.0.md`).
- **Validación**: 100% Tests Passing (361/361) en entorno Dockerizado.
- **Calidad**: Score 83.2/100.
- **Próximos Pasos**: Inicio de fase v2.8.0 (Análisis Avanzado).

## [2026-01-18] Resumen (Noche)
- **Overhaul Visual**: Generada nueva imagen "Hero" profesional y actualizada la estética del `README.md`.
- **Sincronización Documental**: Corregidos enlaces rotos hacia `docs/source` y unificada terminología (Sidebar/Page).
- **Doc Técnica**: Documentada la arquitectura de validación de 3 niveles y herencia de atributos.
- **i18n**: Audit de cadenas finalizado.
- **Status**: ¡Fase v2.7.0 Completada! 🎉

## [2026-01-18] Resumen (Tarde)
- **Limpieza de Repo**: Eliminado rastreo de archivos HTML pesados (`analysis_results/`).
- **Sphinx**: Validada la infraestructura de documentación con salida externa y sincronización local.
- **Higiene**: Actualizado `.gitignore` para mantener el repositorio libre de artefactos de análisis.
- **Calidad**: 361 tests OK en Docker.

## [2026-01-18] Resumen (Mañana)
- **Refactorización de Validación**: Implementado `DialogValidationManager` declarativo para centralizar reglas de UI.
- **Desacoplamiento**: `DialogStatusManager` ahora consume el estado de validación desde el manager especializado.
- **Arquitectura**: Completado Objetivo 4 de la fase v2.7.0 (Reducción de Deuda Técnica en Dialog).
- **Calidad**: 361 tests en verde en Docker; eliminada lógica redundante en `main_dialog_validation.py`.

## [2026-01-18] Resumen (Mañana)
- **Refactorización de UI (Fase 2)**: Extraída gestión de mensajes y errores a `MessageManager`.
- **Desacoplamiento**: Eliminada dependencia directa de `main_dialog_export.py` con widgets de QGIS.
- **Simplificación**: Lógica de botones de Cache y Reset delegada a gestores especializados.
- **Bug Fix**: Resuelto `AttributeError` en `SecInterpDialog` mediante métodos proxy para interpretaciones y ajustes, restaurando compatibilidad con el plugin.
- **Calidad**: Añadidos tests unitarios para mensajería; 358 tests en verde en Docker.

## [2026-01-17] Resumen
- **Refactorización de Arquitectura**: Completada Fase 1 de fragmentación de `main_dialog.py`.
- **Modularidad**: Creado `DialogInterpretationManager` para manejar lógica de interpretaciones.
- **Complejidad**: Reducida complejidad ciclomática de `main_dialog.py` de 95 a 13.
- **Estabilidad**: 353 tests passing en Docker.

## [2026-01-16] - Infraestructura de Testing Docker (19:35)

### Resumen
Implementación exitosa de la infraestructura de testing robusta mediante Docker (Objetivo 7). Se logró centralizar y estandarizar la ejecución de los 349 tests en un entorno QGIS headless idéntico para todos los desarrolladores.

### Logros
- **Testing en Contenedor**:
    - Creación de imagen Docker optimizada con `uv`.
    - Targets en `Makefile` para ciclo build/test simplificado.
- **Estandarización**: Unificación de la ejecución de pruebas bajo `unittest discover` eliminando dependencias de `pytest`.
- **Corrección de Configuración**: Ajustes en `pyproject.toml` para compatibilidad global de empaquetado.

### Resultados
- **Tests**: 349 pasando (100% stable).
- **Commits**: 1 (feat: docker testing infrastructure).
- **Reporte**: [session_2026-01-16_docker_testing_infrastructure.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/maintenance/session_2026-01-16_docker_testing_infrastructure.md)

---
## [2026-01-16] - Sphinx Documentation Infrastructure (05:26)

### Resumen
Implementación exitosa del sistema automatizado de documentación con Sphinx (Objetivo 1). Se logró desacoplar la documentación generada del repositorio git mientras se mantiene la funcionalidad de ayuda local en tiempo de desarrollo.

### Logros
- **Infraestructura Docs**:
    - Scripts y configuración para generar documentación API automática.
    - Sincronización inteligente de carpeta `help/html` (untracked).
- **Limpieza**: Reducción drástica de ruido en el repositorio al eliminar HTMLs.
- **Calidad**: Corrección de regresiones menores en tests y formateo global.

### Resultados
- **Tests**: 369 pasando (100% stable).
- **Commits**: 1 (feat: sphinx docs).
- **Reporte**: [session_2026-01-16_sphinx_docs.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/maintenance/session_2026-01-16_sphinx_docs.md)

---
## [2026-01-15] - Level 3 Domain Validation (18:12)

### Resumen
Session focused on completar la arquitectura de validación de 3 niveles mediante la implementación de "Domain Guards" (Nivel 3) en los servicios principales del núcleo. Se aseguró que operaciones inválidas fallen rápido ("Fail Fast") antes de procesamiento costoso.

### Logros
- **Validación Nivel 3 (Dominio)**:
    - Implementadas cláusulas de guarda en `GeologyService` (capas, bandas, campos) y `DrillholeService` (buffer, azimut).
    - Creada suite de pruebas dedicada: `tests/core/validation/test_service_validation.py` (6 nuevos tests).
- **Mejora de Infraestructura de Tests**:
    - Parcheado `MockQgsFields` en `tests/base_test.py` añadiendo `indexFromName` para paridad con API de QGIS.
- **Documentación**:
    - Actualizado `implementation_plan_v2.7.0.md` marcando Objetivo 3 como completado.
    - Generado `walkthrough.md` con detalles de la implementación.

### Resultados
- **Tests**: 369 pasando (+6 nuevos).
- **Commits**: 1 (feat: implement Level 3 Domain Validation).
- **Status**: Objetivo 3 al 100%. Siguiente paso: Documentación Sphinx.

---
## [2026-01-15] - ADR Documentation & Async Drillholes (16:26)

### Resumen
Sesión dual enfocada en: (1) Implementación completa de procesamiento asíncrono de sondajes para prevenir congelamiento de UI, y (2) Documentación exhaustiva del sistema de ADRs reflejando la evolución arquitectónica del proyecto.

### Logros
- **Async Drillholes**:
    - Implementado `DrillholeTaskInput` DTO y refactorizado `DrillholeService` con patrón prepare/process.
    - Creado `DrillholeGenerationTask` (QgsTask) e integrado en `PreviewManager`.
    - Tests unitarios: 11/11 pasando (drillhole_service + async_drillhole).
- **Sistema ADR Completo**:
    - Documentados 7 ADRs en orden cronológico (v1.0 → v2.7.0).
    - Análisis de 376 commits históricos para identificar decisiones arquitectónicas clave.
    - ADRs: Exporters, Commits, Decoupling, Mocks, Logging, Concurrency, Linting.

### Resultados
- **Commits**: 2 (feat: async drillholes, docs: ADR reorganization)
- **Quality Score**: 83.6/100
- **Tests**: 347 pasando
- **Reporte**: [session_2026-01-15_adr_async_drillholes.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/maintenance/session_2026-01-15_adr_async_drillholes.md)

## [2026-01-15] - Estabilización de la Suite de Tests y Mocks (14:35)

### Resumen
Sesión técnica intensiva para restaurar la estabilidad del proyecto tras detectar fallas masivas en los tests (de 45 fallas a 0). Se refactorizó la infraestructura de mocks para QGIS/PyQt.

### Logros
- **Estabilización de Tests**: Alcanzado el 100% de éxito (347 tests OK).
- **Mocks Reutilizables**: Implementados `ModuleProxy` y `MockSignal` en `tests/base_test.py` para asegurar referencias estables y comunicación por señales en entornos simulados.
- **Detección Z en Mocks**: Mejorada la creación de geometrías mock para detectar automáticamente coordenadas Z y tipos 25D.
- **Bug Fix en Config**: Implementada la lógica de `ConfigService.reset_defaults()` que estaba pendiente.
- **Optimización de Workflows**: Actualizado el workflow de inicio de sesión para reflejar la nueva infraestructura de pruebas.

## [2026-01-13] - Centralización de Logging y Modernización de Infraestructura (20:25)

### Resumen
Session dedicated to cumplir el Objetivo 2 de la fase v2.7.0, consolidando el sistema de registro (logging) para mejorar la estabilidad y diagnóstico de crashes, seguida de la unificación del monitoreo de rendimiento.

### Logros
- **Logging Centralizado**:
    - Refactorizado `logger_config.py` para usar un logger raíz ("SecInterp") con propagación jerárquica.
    - Implementada inicialización temprana en `sec_interp_plugin.py`.
- **Performance Monitor**: Unificado el sistema de monitoreo de rendimiento con el logger centralizado.
- **Calidad y Commits**:
    - Adoptado el estándar de **Conventional Commits** en inglés para todos los commits futuros.
    - Formateado preventivo con `black` y validación con `pre-commit`.
- **Fase v2.7.0**: Marcado Objetivo 2 como completado en el plan de implementación.

### Resultados
- **Archivos Modificados**: `logger_config.py`, `sec_interp_plugin.py`, `core/performance_metrics.py`.
- **Estado de Tests**: ⚠️ **45 fallas/51 errores** (Incidencia heredada, pendiente de investigación).
- **Reporte Detallado**: [session_2026-01-13_logging_centralization.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/maintenance/session_2026-01-13_logging_centralization.md).

---
## [2026-01-12] - Reparación de Bugs y Estandarización de Logs (20:38)

### Resumen
Session focused on la corrección de errores críticos de desempaquetado de sondajes que impedían el funcionamiento del preview y las métricas, seguida de la estandarización del sistema de registro de desarrollo.

### Logros
- **Fix Crítico**: Reparado `ValueError: too many values to unpack` en `core/types.py` y `gui/preview_layer_factory.py` mediante detección dinámica de estructura (3 o 5 elementos).
- **Estandarización de Logs**:
    - Creado `docs/LOGGING_GUIDELINES.md` con reglas formales para registro de actividades.
    - Reorganizado `docs/DEVELOPMENT_LOG.md` en orden cronológico inverso estricto.
- **Optimización de Workflows**: Actualizados 5 workflows en `.agent/workflows/` para integrar `LOGGING_GUIDELINES.md` y `black`.
- **Verificación Completa**: Tests automatizados (30 OK) y pruebas manuales exitosas en QGIS (10 sondajes exportados sin errores).

### Resultados
- **Tests**: 312+ OK (Core + GUI)
- **Formateo**: 65 archivos reformateados con `black`
- **Despliegue**: Exitoso y validado manualmente
- **Calidad**: Score 83.8/100

### Documentación
- Informe de sesión: [session_2026-01-12_bug_fix_y_estandarizacion.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/maintenance/session_2026-01-12_bug_fix_y_estandarizacion.md)

---
## [2026-01-12] - Exportación 3D de Sondajes y Estabilización Core (01:10)

### Resumen
Session focused on la implementación de la exportación 3D de sondajes y la resolución de inestabilidades en la suite de pruebas core tras los cambios arquitectónicos de la fase v2.7.0.

### Logros
- **Exportación 3D**: Implementación de `DrillholeTrace3DExporter` y `DrillholeInterval3DExporter` para salida en `LineStringZ` (Original y Proyectado).
- **QA & Estabilización**:
    - **Fix Crítico**: Reparado `ValueError: too many values to unpack` en preview y métricas por cambio de estructura en sondajes (de 3 a 5 elementos).
    - Resolución de `NameError` y `Mock Pollution` en `base_test.py`.
    - Estabilización de `test_drillhole_utils` y `test_drillhole_service` (Fetching 3D robusto).
    - Creación de nueva suite de validación 3D dedicada.
- **Integración UI**: Adición de controles de modo de coordenadas en la pestaña Export.

### Documentación
- Informe de sesión: [session_2026-01-12_exportacion_3d_sondajes.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/maintenance/session_2026-01-12_exportacion_3d_sondajes.md)

---
## [2026-01-11] - Refactorización de Analyzer e Integración de Workflows (12:25)

### Resumen
Sesión técnica enfocada en potenciar la autoconsciencia del proyecto mediante la mejora del script de análisis y su integración profunda en los flujos de trabajo diario.

### Logros
- **Analyzer v2.1**: Implementación de métricas de Halstead, Type Hints y auditoría de i18n.
- **Contexto IA**: Generación automática de diagramas Mermaid y extracción de palabras clave.
- **Automatización**: Integración en workflows de inicio, cierre y commit con soporte para ejecución automática (`// turbo`).
- **Calidad**: Score estabilizado en 92.0 con integración de linter `ruff`.

### Documentación
- Informe de sesión: [session_2026-01-11_analyzer_refactor_and_workflow_integration.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/maintenance/session_2026-01-11_analyzer_refactor_and_workflow_integration.md)

---
## [2026-01-10] - Cierre de Fase v2.6.0 (02:58)

### Resumen
Lanzamiento oficial de la versión 2.6.0 consolidando todas las mejoras de infraestructura, estabilidad de tests y correcciones de internacionalización. Esta versión marca el estado final estable para el repositorio de QGIS.

### Logros Clave
- **Tests de Integración**: 10 tests reales pasando en QGIS Headless.
- **CI/CD**: Pipeline automatizado con imágenes oficiales.
- **Calidad**: Complejidad ciclomática reducida y tipado al 100% en áreas críticas.
- **Mantenibilidad**: Código reformateado con `black` y mocks estabilizados.

### Estado Final
- **Tests**: 312 OK (Unit + Integration).
- **Deuda Técnica**: Identificada y priorizada para v2.7.0 (Docs Sphinx, Logging).
- **Informe Completo**: [phase_closure_v2.6.0.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/maintenance/phase_closure_v2.6.0.md)

---
## [2026-01-09-3] - Planificación Detallada Fase v2.7.0 (23:10)

### Resumen
Finalización de la etapa de planificación para la versión 2.7.0, integrando requisitos avanzados de exportación 3D, validación nativa y mejora de la infraestructura de desarrollo.

### Actividades Clave
- **Planificación v2.7.0**:
    - **Validación Nativa**: Decisión de usar `dataclasses` y validación manual para evitar la dependencia de `pydantic`.
    - **Sphinx Externo**: Configuración de estrategia para generar documentación fuera del repo (`../sec_interp_docs`) y limpieza de archivos HTML rastreados.
    - **Exportación 3D Avanzada**: Diseño de exportadores para trazas e intervalos de sondajes en modos **Original** y **Proyectado**.
    - **Integración UI**: Diseño de la integración de opciones 3D en la pestaña `Settings > Advanced`.
    - **Dockerización**: Plan para centralizar el testing mediante `make docker-test` y eliminar errores de entorno local.
- **Documentación**:
    - Creación del plan formal: [implementation_plan_v2.7.0.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/plans/implementation_plan_v2.7.0.md).

### Estado Final
- **Plan v2.7.0**: Aprobado conceptualmente y listo para ejecución.
- **Seguimiento**: [task.md](file:///home/jmbernales/.gemini/antigravity/brain/a439de8b-240a-494d-a4cb-9405cc1d99f7/task.md).

---
## [2026-01-09] - Estabilización de Tests y Traducción de UI (21:35)

### Actividades
- **Estabilización de Tests**:
    - **Fix Crítico (Mock Pollution)**: Resuelto el error `StopIteration` en tests de GUI mediante clases de mock explícitas (`MockQListWidget`) en `base_test.py`.
    - **Reset de Estado**: Mejora en `BaseTestCase.tearDown` para resetear mocks globales y limpiar estado en `MockQgsProject` y `MockQgsSettings`.
    - **Re-aplicación de Mocks**: Corregida la pérdida de `side_effect` en mocks de `QgsWkbTypes.geometryType` tras el reset.
- **Internacionalización**:
    - **Traducción de Measure Tool**: Resultados de medición traducidos al inglés y hechos localizables mediante `tr()`.
    - **Default Naming**: Traducido "New Interpretation" para soporte multi-idioma en `interpretation_tool.py`.
- **Estandarización**: Refactorizado `tests/gui/test_geology_task.py` para heredar de `BaseTestCase`.
- **Verificación**: Ejecución exitosa de la suite completa (312 tests: 204 core, 98 gui, 10 integración).

### Resultados
- **Tests Unitarios**: 302 OK ✅
- **Tests de Integración**: 10 OK ✅
- **Status**: Suite de pruebas 100% estable.

---
## [2026-01-08-4] - Despliegue v2.6.0 y Mejora de UX (23:00)

### Actividades
- **Fix Crítico**: Solucionado bug donde el diálogo se cerraba inesperadamente al presionar 'Save'.
    - Desconectado `QDialogButtonBox.accepted` genérico.
    - Implementada conexión manual de señales para OK, Cancel y Save.
- **Fix Persistencia**: Solucionado bug donde configuraciones antiguas de interpretaciones (polígonos) persistían incluso tras usar "Reset Defaults".
    - Ahora `reset_to_defaults` limpia explícitamente `self.interpretations` y fuerza el guardado inmediato al proyecto.
- **Fix Herencia de Atributos**:
    - Corregida lógica de selección de unidad geológica/drillhole. Ahora busca la distancia mínima a *cualquier* punto del segmento geométrico, no solo al punto medio.
    - Resuelto problema donde polígonos cercanos a geometrías largas pero lejos de su centro heredaban atributos incorrectos.
    - **HOTFIX**: Solucionado `AttributeError` al iterar datos de sondajes; se manejaba incorrectamente una tupla como objeto.
    - **HOTFIX**: Solucionado `TypeError` al guardar interpretaciones con atributos heredados (`QVariant` no es serializable). Se añadió un codificador JSON personalizado.
    - **HOTFIX**: Solucionado `AttributeError: 'GeologySegment' object has no attribute 'rock_unit'`. Se añadió soporte polimórfico para leer `unit_name` si `rock_unit` no existe.
- **Documentación**:
    - **Guía de Usuario**: Integración de todas las imágenes generadas por el usuario, reemplazando marcadores de posición con enlaces Markdown válidos.
- **Refactorización de UI**:
    - **SettingsPage**: Reestructurada con sistema de pestañas (Default, Advanced, Info).
    - **Control de Exportación**: Añadidos controles selectivos en 'Settings > Default' para definir qué productos generar al guardar.
- **Documentación**:
    - Actualizado `USER_GUIDE.md` clarificando la diferencia entre 'Save' (salida a disco) y 'OK' (persistencia en proyecto).
    - Corregida documentación sobre Exportación 3D.
- **Despliegue**:
    - Ejecutado despliegue local exitoso de la versión v2.6.0.

---
## [2026-01-08-3] - Integración de CI/CD Permanente (22:15)

### Actividades
- **Infraestructura Docker**:
    - Refactorizado el `Dockerfile` para utilizar `qgis/qgis:latest` como imagen base, asegurando un entorno de pruebas idéntico al del usuario final.
    - Configurado `uv` con soporte para `--system-site-packages` para integrar las librerías de QGIS del sistema con el entorno virtual del proyecto.
- **Automatización CI/CD**:
    - Actualizado `.github/workflows/test.yml` para utilizar contenedores oficiales de QGIS.
    - Migración total de `pytest` a `unittest` en el pipeline de CI, manteniendo consistencia con el estándar del proyecto.
    - Implementado soporte para ejecución *headless* nativa mediante `QT_QPA_PLATFORM: offscreen`.
- **Roadmap v2.6.0**:
    - Marcadas como completadas las tareas de Benchmarks, Reducción de Complejidad en Exportadores e Integración CI/CD.

### Resultados
- **Infraestructura**: Pipeline de GitHub Actions listo para validar tests de integración reales.
- **Portabilidad**: El `Dockerfile` ahora sirve como entorno de desarrollo local reproducible y estable.

---
## [2026-01-08-2] - Armonización de Validación y Calidad en GUI (21:48)

### Actividades
- **Refactorización de Validación**:
    - Centralización de la recolección de parámetros en `DialogDataAggregator` para asegurar consistencia con el core.
    - Simplificación de `DialogValidator` eliminando recolección manual de widgets y delegando en `ProjectValidator`.
- **Calidad de Código**:
    - Aplicación de **Type Hints** completos y docstrings estilo Google en `main_dialog_validation.py` e `interpretation_properties_dialog.py`.
- **Armonización de UI**:
    - Estandarización del método `is_complete` en `DemPage`, `GeologyPage`, `StructurePage` y `DrillholePage` utilizando lógica centralizada del core.
- **Estabilización de Tests**:
    - Actualización de `tests/gui/test_main_dialog_validation.py` para reflejar la nueva arquitectura, corrigiendo fallos por patches obsoletos.

### Resultados
- **Tests**: Suite de GUI pasando exitosamente (**96 tests OK**).
- **Mantenibilidad**: Reducción de redundancia en la capa de interfaz y mejor soporte para análisis estático.

### Documentación
- Walkthrough: [walkthrough.md](file:///home/jmbernales/.gemini/antigravity/brain/21a89546-b249-4109-a555-97ccf59480fb/walkthrough.md)

---
## [2026-01-08-1] - Mejora Continua de Calidad (Docstrings, Type Hints y Complejidad) (20:10)

### Actividades
- **Fase 1 (Core)**: Mejora de cobertura en `__init__.py`, `core/performance_metrics.py` y docstrings iniciales en `core/controller.py`.
- **Fase 2 (Servicios y Refactorización)**:
    - Cobertura completa de Type Hints en `export_service.py`, `geology_service.py` y `drillhole_service.py`.
    - Refactorización de `ProfileController.generate_profile_data` para reducir su complejidad ciclomática de 23 a <15.
    - Modularización de `PreviewParams.validate` para mejorar mantenibilidad (reducción de CC de 18 a <15).
- **Fase 3 (Gui & Validation)**:
    - Refactorización de `DialogEntityManager` y `DialogValidator` para centralizar lógica de GUI y validaciones.
    - Adición de Type Hints en `main_dialog.py` y gestores de señales.
- **Fase 4 (Technical Debt & UI Cleanup)**:
    - Tipado completo y corrección de bugs en `DrillholePage`.
    - Documentación y tipado en `logger_config.py`, `measure_tool.py` e `interpretation_tool.py`.
    - Limpieza de importaciones legacy (`PyQt5` -> `qgis.PyQt`) y remoción de `print` statements.
    - **Infraestructura**: Integración de `conventional-pre-commit` para asegurar el cumplimiento de `COMMIT_GUIDELINES.md` y actualización de workflows de agent.
- **Validación**: Análisis con `qgis-analyzer` y verificación con suite de pruebas unitarias.

### Resultados
- **Type Hint Coverage (Params)**: Incremento de **62.1% → 76.4%**.
- **Type Hint Coverage (Returns)**: Incremento de **28.5% → 38.3%**.
- **Issue Statistics**: Reducción neta de **76 incidencias** (527 a 451).
- **Mantenibilidad**: Se mantiene en **100/100**.

### Documentación
- Walkthrough: [walkthrough.md](file:///home/jmbernales/.gemini/antigravity/brain/420250bf-835d-4495-944e-0528f9570fef/walkthrough.md)

---
## [2026-01-08-0] - Refactorización de Exporters y Benchmarks v2.6.0 (19:42)

### Actividades
- **Refactorización de Exporters**: Se redujo la complejidad ciclomática de `Interpretation3DExporter` de 6 a <= 5 mediante la extracción de lógica en métodos privados.
- **Verificación de Calidad**: Validación de complejidad con Ruff y ejecución de tests unitarios del exportador.
- **Benchmarks**: Ejecución exitosa de la suite de performance completa en modo QGIS headless.

### Resultados
- **Ruff**: `Interpretation3DExporter` ahora cumple con los estándares de calidad del proyecto.
- **Tests**: Unit tests pasando (3/3 para el módulo modificado).
- **Benchmarks**: Todos los tests de performance pasando (<0.1s para 10k registros).

### Documentación
- Walkthrough: [walkthrough.md](file:///home/jmbernales/.gemini/antigravity/brain/420250bf-835d-4495-944e-0528f9570fef/walkthrough.md)

---
## [2026-01-08] - Estabilización de Salud y Refactorización de Exporters

### Resumen
Session focused on la estabilización del plugin tras la refactorización de `QgsTask` y la reducción de deuda técnica en el módulo de exportadores.

### Logros
- **Estabilización de Tests**:
    - Corregida regresión en `GeologyService` (`NameError: task_input`).
    - Estabilizados mocks en `tests/base_test.py` agregando `MockQgsTask`, `Qgis` constants y ampliando soporte para UI (`LayerFilters`).
    - Verificados 102 tests unitarios pasando.
- **Refactorización de Exporters**:
    - Todos los exportadores de Shapefile (`shp`, `drillhole`, `profile`, `interpretation_3d`) fueron refactorizados para reducir complejidad ciclomática mediante delegación de lógica a métodos privados.
    - La complejidad de los métodos `export` se redujo de 8-9 a 6 en promedio, mejorando significativamente la legibilidad y mantenibilidad.

### Estado Final
- **Tests Unitarios**: OK (102/102).
- **Deuda Técnica**: Significativamente reducida en el módulo `exporters`.
- **Siguiente Paso**: Continuar con el roadmap v2.6.0 (Optimización de carga y benchmarks).

---
## [2026-01-07] - Refactorización de Threading y Fix de Crashes (21:10)

### Problema
- **Crashes Intermitentes**: Se identificaron segfaults aleatorios causados por el acceso a la API de QGIS (`QgsVectorLayer`, `QgsRasterLayer`, `QgsProject`) desde hilos secundarios en la generación de perfiles geológicos.

### Solución Arquitectónica
- **Native QgsTask**: Migración completa del custom `ParallelGeologyService` a `GeologyGenerationTask`, una implementación nativa de `QgsTask` gestionada por `QgsApplication.taskManager()`.
- **Patrón "Extract-then-Compute" (DTO)**:
    - **Fase 1 (Síncrona)**: Extracción segura de datos en el hilo principal mediante `GeologyService.prepare_task_input`. Se copian geometrías y atributos a estructuras en memoria (`GeologyTaskInput`), desconectándolas de QGIS.
    - **Fase 2 (Asíncrona)**: Procesamiento geométrico puro en el hilo de trabajo (`GeologyService.process_task_data`), garantizando thread-safety al no acceder a punteros de C++ de QGIS.

### Cambios Clave
- **[NUEVO]** `core/types.py`: DTO `GeologyTaskInput` para transferencia segura de datos.
- **[REFACTOR]** `core/services/geology_service.py`: Separación estricta de lógica de lectura y cálculo.
- **[NUEVO]** `gui/tasks/geology_task.py`: Clase encapsulada para la tarea en background.
- **[FIX]** `gui/main_dialog_preview.py`: Integración con `QgsTaskManager` y manejo de ciclo de vida.
- **[ELIMINADO]** `gui/services/parallel_geology_service.py` (Deuda técnica).

### Verificación
- **Tests Unitarios**: Creado `tests/gui/test_geology_task.py` validando éxito, fallo y manejo de logs.
- **Walkthrough**: [Native QgsTask Refactor](file:///home/jmbernales/.gemini/antigravity/brain/ea9a4214-70d6-4f52-95ce-7f891d75b04c/walkthrough.md)

---
## [2026-01-06-1] - Implementación de Benchmarks de Performance (21:15)

### Actividades
- **Infraestructura**: Creación de `tests/benchmarks/benchmark_utils.py` con decoradores para medición de tiempos y aserciones de SLAs.
- **Implementación de Tests**:
    - `test_geometry_benchmarks.py`: Validación de performance en cálculos geométricos y proyecciones.
    - `test_export_benchmarks.py`: Medición de tiempos de escritura de Shapefiles (1k y 10k registros).
- **Runner Dedicado**: Creación de `scripts/run_benchmarks.py` para ejecución aislada dentro del entorno QGIS.
- **Validación Manual**: Verificación visual de exportación 3D y carga de estilos QML.

### Resultados
- **Benchmarks**: Verificados y pasando con holgura (ej. escritura de 10k shapefiles en <0.1s).
- **Roadmap v2.6.0**: Completada la fase de benchmarks y refactorización de exportadores.

### Documentación
- Archivo de Walkthrough: [session_2026-01-06_benchmarks.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/maintenance/session_2026-01-06_benchmarks.md)

---
## [2026-01-06-0] - Fix Infraestructura de Tests de Integración (18:40)

### Actividades
- **Fix Runner**: Se corrigió `scripts/run_tests_in_qgis.py` para manejar casos donde `__file__` no está definido (ejecucción vía `--code` o terminal QGIS).
- **Aislamiento de Tests**: Se configuró el runner para priorizar tests de integración (`tests/integration`) al ejecutar dentro de QGIS, evitando interferencia de mocks de tests unitarios.
- **Detección de QGIS**: Mejorada la detección de entorno real en `tests/base_test.py` para evitar sobrescribir `sys.modules["qgis"]` si la API ya está disponible.

### Resultados
- **10 tests de integración pasando** exitosamente dentro de QGIS 3.44.
- Infraestructura estabilizada para validación de flujos de trabajo reales (Interpretación, Medición y Exportación 3D).

### Documentación
- Archivo de Walkthrough: [session_2026-01-06_fix_integracion.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/maintenance/session_2026-01-06_fix_integracion.md)

---
## [2026-01-05-2] - Implementación de Infraestructura de Tests de Integración Nativa (22:00)

### Actividades
- **Tests de Integración**: Se estableció la infraestructura para ejecutar tests de integración utilizando la API real de QGIS en modo headless.
- **Clase Base**: Creación de `BaseIntegrationTest` en `tests/integration/base_integration.py` para gestión de `QgsApplication`.
- **Nuevos Tests**:
    - `test_qgis_smoke.py`: Verificación de instanciación de objetos QGIS y diálogos de la UI.
    - `test_interpretation_workflow.py`: Validación de guardado/carga de interpretaciones en el proyecto.
    - `test_measurement_workflow.py`: Verificación de cálculos de la herramienta de medición multi-punto.
    - `test_export_workflow.py`: Validación de la lógica de proyección 3D.
- **Resultados**: 10 tests de integración pasando exitosamente junto con los 319 tests unitarios existentes.

### Decisiones Técnicas
- **Mode Headless**: Uso de `QgsApplication([], False)` para evitar requerimientos de servidor X en entornos CI/CD sugeridos.
- **Mocks Híbridos**: Uso de `DummyPlugin` para inyectar controladores reales en tests que requieren lógica de negocio sin conexión total a la interfaz iface de QGIS.

### Documentación
- Archivo de Walkthrough: [session_2026-01-05_integracion.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/maintenance/session_2026-01-05_integracion.md)

---
## [2026-01-05-1] - Cierre Formal de Fase v2.5.0 (20:30)

### Actividades
- **Cierre de Fase**: Documentación formal del cierre de la fase de desarrollo y estabilización post-release v2.5.0.
- **Revisión Comprehensiva**:
    - Evaluación de logros principales: Exportación 3D, I18n (5 idiomas), Herramienta de Interpretación, Infraestructura Docker.
    - Análisis de desafíos enfrentados y soluciones implementadas.
    - Identificación y priorización de deuda técnica acumulada (Crítica, Moderada, Menor).
- **Control de Versiones**:
    - Estado actual: 2 commits ahead de `origin/main`, cambios pendientes en devcontainer y tests.
    - Preparación de commits para sincronización con remoto.
    - Tag actual: `v2.5.0` (2026-01-03).
- **Comunicación**: Preparación de mensaje para stakeholders alineando expectativas para la siguiente fase.

### Métricas del Proyecto
- **Archivos Python**: 3,198
- **Tests Unitarios**: 319 (316 pasando, 3 skipped)
- **Pylint Score**: 10/10
- **Docstring Coverage**: 75.9%
- **Idiomas Soportados**: 5 (ES, FR, DE, RU, PT_BR)

### Deuda Técnica Identificada
- **Crítica**: Tests de integración GUI limitados, complejidad ciclomática en exportadores, falta de benchmarks.
- **Moderada**: Documentación de API incompleta, configuración de logging dispersa, falta de validación de schemas.
- **Menor**: Código duplicado en exportadores, nombres inconsistentes, imports no utilizados.

### Recomendaciones para Siguiente Fase
1. Implementar tests de integración en QGIS real (`qgis_testrunner`)
2. Reducir complejidad ciclomática en exportadores
3. Establecer benchmarks de performance con `pytest-benchmark`
4. Mejorar documentación de API con Sphinx

### Documentación
- Documento completo de cierre de fase: [phase_closure_2026-01-05.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/maintenance/phase_closure_2026-01-05.md)
- Walkthrough del proceso: [phase_closure_walkthrough_2026-01-05.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/maintenance/phase_closure_walkthrough_2026-01-05.md)

---
## [2026-01-05-0] - Configuración de Dev Container para qgis-analyzer (04:50)

### Objetivos Completados
- Configuración exitosa de `.devcontainer/devcontainer.json` y `Dockerfile` para soportar `qgis-analyzer` y dependencias del proyecto.
- Corrección de errores de importación (`PYTHONPATH`) en el entorno de pruebas Dockerizado.
- Solución de fallos en tests unitarios (`test_profile_exporters.py` por mocking de `QgsGeometry`, y eliminación de tests frágiles en herramientas de GUI por limitación de SIP).
- Verificación exitosa de la ejecución de `qgis-analyzer` dentro del contenedor.

### Detalles Técnicos
- Se actualizó `Dockerfile` para usar `uv sync` y copiar `pyproject.toml`.
- Se configuró `devcontainer.json` para construir la imagen localmente y establecer `PYTHONPATH`.

---
## [2026-02-17] Zero-Leak Milestone & v3.0.1 Release
- **Fugas de Señales**: Resolución del 100% de las fugas de señales detectadas (22 leaks).
- **Lanzamiento**: Liberación de la versión 3.0.1 (Expert Stability & Global Reach).
- **Idiomas**: Integración de soporte para Hindi y Japonés.
- **Calidad**: Formateo masivo (Black/Ruff) y validación de integridad en Docker (386 tests).
- **Optimización**: Reducción del 80% del paquete ZIP mediante `.qgisignore`.

---
## [2026-01-04-1] - Dev Containers Architecture (21:30)

### Actividades
- **Zero-Setup Environment**: Established a fully reproducible development environment using `.devcontainer`.
- **Infrastructure Fixes**:
    - **Caching Issues**: Bypassed Docker layer caching issues by manually building `sec_interp_dev` image.
    - **Dependency Resolution**: Added mandatory `wget`, `curl`, and `ca-certificates` to `Dockerfile` to enable VS Code Server installation.
    - **Process Management**: Configured `overrideCommand: true` to prevent container exit after test execution, allowing interactive sessions.
- **Portability**: Verified that "Reopen in Container" now works seamlessly, installing all `uv` dependencies automatically.

### Verification
- Container successfully launched and sustained connection.
- Verified `root` shell access within the container.
- Confirmed environment isolation from host system.

---
## [2026-01-04-0] - Docker Learning Workshop (00:05)

### Actividades
- **Fase 1: Interactive Exploration**: Launched containers, managed volumes (`-v`), and identified system dependencies inside `python:3.10-slim`.
- **Fase 2: Dockerfile Automation**:
    - Implemented a production-ready `Dockerfile` featuring `uv` for dependency management.
    - Integrated `.dockerignore` to optimize build context and ignore `__pycache__`.
    - Resolved critical permission issues caused by `root` user in isolated environments.
- **Fase 3: Containerized Verification**:
    - Automated unit tests execution within the container.
    - Resolved `PYTHONPATH` package discovery issues relative to the `/app` mounting point.

### Verification
- Successfully executed **319 tests** inside the Docker container.
- Proof of work archived in: [docker_workshop_2026-01-04.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/maintenance/docker_workshop_2026-01-04.md)

---
## [2026-01-03-4] - Release Workflow Standardization (13:15)

### Activities
- **Workflow Adaptation**: Customized [`release_process_ai.md`](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/release_process_ai.md) for SecInterp, including 5 distinct phases (Quality, Versioning, Verification, Git, and Distribution).
- **Agent Integration**: Standardized internal agent workflows (`/release-plugin` and `/release-plugin-en`) to strictly follow the AI-guided 5-phase process.
- **Documentation Cleanup**: Removed legacy/redundant release documentation (`docs/docsec/RELEASE_PROCESS.md`).
- **Template Creation**: Implemented [`.github/release_template.md`](file:///home/jmbernales/qgispluginsdev/sec_interp/.github/release_template.md) with QGIS-specific instructions.

### Verification
- Sync confirmed between guide, template, and agent internal workflows.
- Phase 2 synchronization (metadata.txt vs pyproject.toml) verified as mandatory.

---
## [2026-01-03-3] - Official Release Version 2.5.0 (12:35)

### Activities
- **Release Automation**: Executed `make package` to compile translations and help files, creating `sec_interp.2.5.0.zip`.
- **Changelog Consolidation**: Merged multi-day improvements into a unified technical changelog in [`CHANGELOG.md`](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/CHANGELOG.md).
- **Metadata Update**: Synchronized `metadata.txt` and `MAINTENANCE_LOG.md` with version 2.5.0.
- **Git Deployment**: Created and pushed tag `v2.5.0` to GitHub.

### Verification
- GitHub repository synchronized with `main` and `v2.5.0` tag.
- Final test verification passed: **319 tests**.

---
## [2026-01-03-2] - Data Persistence Fix & UI Robustness (12:20)

### Activities
- **Proactive Persistence**: Reorganized `accept_handler` and `preview_profile_handler` in `main_dialog.py` to save settings immediately upon success or dialog acceptance, even if secondary validation fails.
- **Robust Settings Hub**:
    - Enhanced `DialogSettingsManager` with multi-scope support (`SecInterp` and `SecInterpUI`).
    - Implemented layer name fallback for restoration when IDs change.
    - Added type-safe parsing for persistent string values ("True", "None", etc.).
- **Forced Sync**: Added `self.settings.sync()` in `ConfigService` to ensure immediate disk writes.
- **Validation Fix**: Resolved `AttributeError` in `validate_inputs` that caused crashes on validation failure.
- **Workflow Automation**: Followed `/cierra-sesion` workflow to archive results.

### Verification
- Full test suite passed: **110 GUI tests** + all core tests.
- User confirmed automatic loading of previous configurations.
- Verified persistent restoration of layers and spinbox values after QGIS restart.

---
## [2026-01-03-1] - Bug Fix: Preview Render TypeError (10:45)

### Problem
- **TypeError**: `cannot unpack non-iterable GeologySegment object` in `gui/preview_renderer.py`.
- **Cause**: After refactoring `GeologyData` to use `GeologySegment` objects, a legacy list comprehension in `render()` was still trying to unpack them as 3-tuples.

### Fix
- Updated `gui/preview_renderer.py` to extract points from `GeologySegment.points` when calculating `reference_data`.
- Added a regression test case in `tests/gui/test_preview_components.py`.

### Verification
- Full test suite passed: **316 tests**.
- Regression confirmed manually via test case.

---
## [2026-01-03-0] - Global Ruff Activation & Cleanup (10:20)

### Activities
- **Ruff Rule Enablement**: Activated `F401` (unused imports), `F841` (unused variables), and `I001` (isort) project-wide.
- **Automated Fixes**: Executed `ruff check --fix` and `ruff format`. 253 fixes applied, 102 files reformatted.
- **Mock System Refactor**: Enhanced `tests/base_test.py` to fix regressions in `MockQWidget`, `MockQgsProject`, and `MockQApplication`.
- **Regression Fixes**:
    - Restored missing `logger` in `gui/main_dialog_settings.py`.
    - Fixed 3D component discovery in `exporters/interpretation_3d_exporter.py`.
    - Modernized `isinstance` checks in `gui/services/parallel_geology_service.py` (Rule `UP038`).

### Verification
- Full test suite passed: **316 tests** (312 passed, 4 skipped).
- Detailed report saved in: [ruff_cleanup_2026-01-03_10-20.md](file:///home/jmbernales/qgispluginsdev/sec_interp/docs/maintenance/ruff_cleanup_2026-01-03_10-20.md)

---
## [2026-01-15] - Arquitectura de Validación (Niveles 1 y 2) (17:48)

### Resumen
Implementación exitosa de los dos primeros niveles de la arquitectura de validación jerárquica y estandarización del código base.

### Logros
- **Nivel 1 (Type Validation)**: Implementados validadores reutilizables en `core/validation/validators.py` e integrados en `settings_model.py`.
- **Nivel 2 (Business Logic)**: Creado `validation_helpers.py` con `ValidationContext` para acumulación de errores. Refactorizado `ProjectValidator` para usar este contexto.
- **Estandarización**: Formateo global aplicado con `black` y `ruff`.

### Resultados
- **Tests**: 363 tests pasando (16 nuevos añadidos para lógica de validación).
- **Calidad**: Codebase consistente y listo para validación de dominio (Nivel 3).

---
## [2026-01-13] - Unificación de Registro de Versiones (22:45)
- **Achievement**: Centralizado el historial de mantenimiento en un único log estructurado.
- **Changes**:
    - Fusionado `MAINTENANCE_LOG.md` en `DEVELOPMENT_LOG.md`.
    - Estandarizado el formato de entradas con secciones de Logros, Cambios y Resultados.
- **Status**: Registro histórico depurado y unificado.

---
## [2026-02-14] - Lanzamiento de Versión 3.0.0 (Major Release)
- **Achievement**: Formalización de la versión 3.0.0 con soporte i18n masivo y arquitectura modular.
- **Changes**:
    - Consolidación de 8 idiomas con automatización `ai-context-core`.
    - Refactorización de `DrillholeService` y creación de `AccessControlService`.
    - Cumplimiento del 100/100 en QGIS Compliance tras auditoría con `qgis-plugin-analyzer` v1.7.0.
- **Status**: Fase de estabilización completada. Listos para iniciar migración a QGIS 4.x.

---
## [2025-12-28] - Migración a QgsTask para Boreholes
- **Achievement**: Implementado procesamiento asíncrono para la carga de sondajes masivos.
- **Changes**:
    - Creada clase `BoreholeLoadTask` heredando de `QgsTask`.
    - Añadida barra de progreso reactiva en la UI de Preview.
- **Status**: Reducido tiempo de bloqueo de UI en un 95%.

---
## [2025-12-15] - Implementación de Exporter Service
- **Achievement**: Desacoplada la lógica de exportación del controlador principal.
- **Changes**:
    - Creado `ExportService` utilizando el patrón Factory para diferentes formatos.
    - Implementados exporters para PDF, SVG e Imagen.
- **Status**: Cobertura de tests de exportación sube al 85%.

---
## [2025-11-21] Initial project setup
- Core structure established
- QGIS plugin skeleton generated

## [2026-03-15] DXF Integration and ExportService Refactor

**Goal**: Implement DXF export and reduce cyclomatic complexity in `ExportService`.

**Changes:**
- Added `ExportSettings` with `default_format` and `naming_pattern`.
- Implemented `DXFExporter` using `QgsVectorFileWriter`.
- Refactored `ExportService` to dynamically use exporters based on settings and extracted layer resolution to pure functions.
- Updated Settings GUI with a `QComboBox` for default format and `QLineEdit` for naming scheme.
- Added missing UI Qt Mocks for `QComboBox` and `QLineEdit` to allow tests to pass.

**Outcome**: Cyclomatic complexity successfully reduced. Full test suite (607 tests) passing via Docker.

## [2026-03-15] Pyright Workspace Configuration and Workflow Fixes

**Goal**: Clarify changelog workflow usage and resolve IDE static analysis ghost issues.

**Changes:**
- Clarified prompt-based execution in `close-session.md` workflow.
- Configured `.pyre_configuration` and `.vscode/settings.json` to constrain Pyright to correct workspace paths.

**Outcome**: Accurate changelog instructions prevent command execution failures. Phantom IDE diagnostics safely isolated.
- **2026-04-05**: Modernized ecosystem to Gen 5. Integrated Reflect Loop (Self-Critique) and established the Blueprint Scaffolding architecture. [Antigravity]
