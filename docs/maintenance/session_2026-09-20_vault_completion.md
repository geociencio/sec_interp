# Session 2026-09-20 — Vault Expansion & Numbering Cleanup

- **Achievement**: Removed numeric prefixes from the entire bilingual vault (68 notes renamed `NN - slug.md` → `slug.md`, 80 wikilinks updated, index `#` column removed) and enriched the vault with the remaining 12 skeleton notes (export_service, preview_service, drillhole processors, adapters, tools, pages, exporters 3D).
- **Scope**:
  - **Numbering removal**: Script `renumber_remove.py` renamed 34 notes per vault (68 total) and updated all `[[NN - slug]]` → `[[slug]]` plus `[[Index]]` anchors; `_template.md` no longer requires `{{NUM}}`; indexes now use `| Archivo | Estado |` without `#`.
  - **Template + sync**: Added `docs/code_walkthrough/_template.md` and `_en/_template.md` without `{{NUM}}` and `scripts/sync_vault_mirrors.sh` (`--check` for CI).
  - **Vault expansion**: Generated 25 filtered skeletons via `generate_vault_skeletons.py` (core/services, exporters 3D, adapters, tools, pages) and progressively enriched 12 of them from `skeleton` to full notes: `export_service` (645 l.), `preview_service` (175 l.), `trajectory_engine` (111 l.), `collar/survey/interval/projection_engine` (15–100 l.), `access_control_service` (36 l.), `drillhole/geology/structure/validation_extractor` (176–369 l.), `measure/interpretation_tool`, `drillhole/settings_page`, `interpretation_3d/drillhole_3d/pdf/svg/image/profile/dxf/interpretation/drillhole_exporters` (58–465 l.).
  - **Index hygiene**: Converted all `⏳` rows to `✅` as notes were enriched; added mirror-docs callout and naming-convention info; vault now has 67 files per language (≈43 notes + 3 mirrors + templates).
- **Commits in session** (since `21323ff6`):
  - `90247850` `docs(code-walkthrough): abandon numbers and expand vault`
  - `13db9a88` `docs(code-walkthrough): remove numeric prefixes from all notes`
  - `1bcdc661` `docs(code-walkthrough): enrich vault with remaining modules` (+ 8 prior notes: 27 config, 28 data_cache, 29 performance, 32–40 preview/managers)
  - Plus `165c93b` (templates + sync script) and `45fcf3b` (ui_pages) from earlier in the day.
- **Operational Metrics**: Docs-only; Python unchanged. Ground truth holds: 606/606 tests, CC ≤10 PASS, i18n 0, Security 100/100. Pre-push gate **PASSED** on `git push 4b7906cc..1bcdc661`.
- **Status**: Bóveda number-free, navegable por capas/tags. Quedan 12 skeletons 🔄 (interpretation_tool, drillhole_page, settings_page, 9 exporters) — todos ya generados como borradores, listos para enriquecer bajo demanda. `main` pushed to `origin/main` (12 commits).
- **Next**: Enriquecer los 12 skeletons restantes bajo demanda o expandir `core/utils`/`gui/ui/pages` según prioridad del próximo release.
