# Documentation Staleness Audit — 2026-09-20

> **Report only — no documentation was edited.** Generated to list outdated
> module/file references in the **active** documentation after the Core/GUI
> decoupling and module-size refactors.

## Summary

- Active docs scanned: **22**
- Outdated `.py` references found: **36**
- Historical docs (plans, `docsec/archive/`, releases, walkthroughs, `DEVELOPMENT_LOG`,
  `CHANGELOG`, ADRs, `maintenance/`) were **excluded** on purpose: they are records of
  past states and should not be rewritten.

## Outdated references by file

| File | Line | Stale reference | Context |
|------|:----:|-----------------|---------|
| `README.md` | 45 | `verify_i18n_hygiene.py` | - **AST-Based Translation Hygiene**: Developed `verify_i18n_hygiene.py`, a static analyzer that scans UI co... |
| `docs/ARCHITECTURE_EN.md` | 69 | `services/profile_service.py` | - `services/profile_service.py` → [[profile_service]] · [doc](code_walkthrough/profile_service.md) |
| `docs/ARCHITECTURE_EN.md` | 525 | `services/profile_service.py` | \| `ProfileService` \| `services/profile_service.py` → [[profile_service]] \| Topography extraction, sampli... |
| `docs/CORE_DISTINCTION_GUIDE.md` | 41 | `core/types.py` | 3.  **Resultado**: El Core devuelve DTOs (Data Transfer Objects) definidos en `core/types.py`. La capa GUI ... |
| `docs/CORE_DISTINCTION_GUIDE_EN.md` | 41 | `core/types.py` | 3.  **Result**: The Core returns DTOs (Data Transfer Objects) defined in `core/types.py`. The GUI layer is ... |
| `docs/LOGGING_GUIDELINES.md` | 32 | `core/types.py` | - Corregido `ValueError` en `core/types.py`. |
| `docs/docsec/PROJECT_STRUCTURE.md` | 130 | `validation.py` | #### `validation.py` ⭐ |
| `docs/docsec/PROJECT_STRUCTURE_EN.md` | 130 | `validation.py` | #### `validation.py` ⭐ |
| `docs/docsec/ARCHITECTURE.md` | 24 | `main_dialog_preview.py` | - **`main_dialog_preview.py` (PreviewManager)**: Manages preview state, hash-based caching, and task launch... |
| `docs/docsec/ARCHITECTURE.md` | 35 | `core/types.py` | #### Types and DTOs (`core/types.py`) |
| `docs/source/ARCHITECTURE.md` | 308 | `main_dialog_data.py` | \| `get_all_values()` \| Actual data aggregation from pages \| `main_dialog_data.py` \| |
| `docs/source/ARCHITECTURE.md` | 309 | `main_dialog_signals.py` | \| `connect_all()` \| Bulk signal connection \| `main_dialog_signals.py` \| |
| `docs/source/ARCHITECTURE.md` | 1288 | `main_dialog_signals.py` | \| `main_dialog_signals.py`\| ~200 \| 1 \| 10 \| Medium \| |
| `docs/source/ARCHITECTURE.md` | 1289 | `main_dialog_data.py` | \| `main_dialog_data.py` \| ~150 \| 1 \| 8 \| Medium \| |
| `docs/source/ARCHITECTURE.md` | 1373 | `seismic_service.py` | 1. Create the new file in `core/services/` (e.g., `seismic_service.py`). |
| `docs/source/CORE_DISTINCTION_GUIDE.md` | 41 | `core/types.py` | 3.  **Result**: Core returns DTOs (Data Transfer Objects) defined in `core/types.py`. The GUI layer handles... |
| `docs/source/CORE_DISTINCTION_GUIDE_EN.md` | 41 | `core/types.py` | 3.  **Result**: The Core returns DTOs (Data Transfer Objects) defined in `core/types.py`. The GUI layer is ... |
| `docs/source/MAINTENANCE_LOG.md` | 106 | `main_dialog_validation.py` | - **Changes**: 38 tests for `main_dialog_validation.py`, `legend_renderer`, and `lod_calculator`. |
| `docs/maintainer/TECHNICAL_COMPENDIUM.md` | 59 | `gui/services/parallel_geology_service.py` | 2.  **Parallel Processing (`gui/services/parallel_geology_service.py`)**: |
| `docs/maintainer/TECHNICAL_COMPENDIUM.md` | 63 | `gui/main_dialog_validation.py` | 3.  **Dialog Validation (`gui/main_dialog_validation.py`)**: |
| `docs/maintainer/TECHNICAL_COMPENDIUM.md` | 67 | `gui/main_dialog_tools.py` | 4.  **Tool Management (`gui/main_dialog_tools.py`)**: |
| `docs/maintainer/CODE_ANALYSIS.md` | 132 | `gui/lod_calculator.py` | \| `gui/lod_calculator.py` \| Clase completa \| |
| `docs/maintainer/TECHNICAL_ANALYSIS_REPORT.md` | 50 | `core/utils/qgis.py` | 1.  **Crear `core/utils/qgis.py`:** Centralizar la resolución de capas en una única función robusta que val... |
| `docs/maintainer/TEST_TASK_LOG.md` | 36 | `gui/services/parallel_geology_service.py` | - [x] `gui/services/parallel_geology_service.py` |
| `docs/maintainer/TEST_TASK_LOG.md` | 38 | `gui/main_dialog_tools.py` | - [x] `gui/main_dialog_tools.py` (100% coverage) |
| `docs/maintainer/TEST_TASK_LOG.md` | 39 | `gui/main_dialog_validation.py` | - [x] `gui/main_dialog_validation.py` (100% coverage) |
| `docs/qa/CONSOLIDATED_DIAGNOSIS.md` | 26 | `qt6_compat.py` | \| 🟡 QT_SHIM \| 3 \| `data_cache.py`, `i18n.py`, `qt6_compat.py` (solo `qgis.PyQt` para `tr()`/enums) \| |
| `docs/qa/CONSOLIDATED_DIAGNOSIS.md` | 34 | `core/utils/qgis.py` | - **`core/utils/qgis.py` (`LayerResolver`)** — mayor fuga transitiva. `resolve()` llama `QgsProject.instanc... |
| `docs/qa/CONSOLIDATED_DIAGNOSIS.md` | 51 | `utils/resource_manager.py` | \| `utils/resource_manager.py` \| `temporary_memory_layer(...) -> QgsVectorLayer`, `ResourceManager.cleanup... |
| `docs/qa/CONSOLIDATED_DIAGNOSIS.md` | 54 | `interfaces/profile_interface.py` | \| `interfaces/profile_interface.py` \| `generate_topographic_profile(QgsVectorLayer, QgsRasterLayer, ...)` \| |
| `docs/qa/CONSOLIDATED_DIAGNOSIS.md` | 57 | `services/profile_service.py` | \| `services/profile_service.py` \| `generate_topographic_profile(QgsVectorLayer, QgsRasterLayer, ...)` \| |
| `docs/qa/CONSOLIDATED_DIAGNOSIS.md` | 72 | `services/drillhole/data_fetcher.py` | **Mejores prácticas detectadas:** `domain/task_inputs.py` (DTOs), `services/drillhole/data_fetcher.py` (cap... |
| `docs/qa/CONSOLIDATED_DIAGNOSIS.md` | 155 | `lod_calculator.py` | \| `lod_calculator.py` \| 48 \| **muerto** (solo tests) \| |
| `docs/qa/CONSOLIDATED_DIAGNOSIS.md` | 173 | `tests/gui/test_lod_calculator.py` | - `gui/lod_calculator.py` (solo `tests/gui/test_lod_calculator.py`). |
| `docs/qa/CONSOLIDATED_DIAGNOSIS.md` | 173 | `gui/lod_calculator.py` | - `gui/lod_calculator.py` (solo `tests/gui/test_lod_calculator.py`). |
| `docs/qa/MANUAL_CODE_ANALYSIS.md` | 26 | `core/services/drillhole/data_fetcher.py` | *   **[`core/services/drillhole/data_fetcher.py`](file:///home/jmbernales/qgispluginsdev/sec_interp/core/se... |

## Suggested replacements (module → current location)

| Removed / renamed | Current equivalent |
|---|---|
| `core/types.py` | `core/domain/` (`dtos.py`, `entities.py`, `enums.py`, `task_inputs.py`) |
| `core/validation.py` | `core/validation/` package |
| `core/services/profile_service.py` | `gui/adapters/profile_extractor.py` (`ProfileService`) |
| `gui/main_dialog_*.py` (preview/data/signals/settings/status/tools/export/validation) | `gui/dialog_*_manager.py` + `gui/dialog_*_mixin.py` |
| `gui/services/parallel_geology_service.py` | `gui/tasks/geology_task.py` (+ `preview_task_orchestrator.py`) |
| `gui/lod_calculator.py` | LOD in `core/services/preview_service.py` + `gui/renderers/` |
| `gui/main_dialog_validation.py` | `gui/dialog_input_manager.py` + `core/validation/` |
| `gui/main_dialog_tools.py` | `gui/dialog_tool_manager.py` |
| `core/utils/qgis.py` | `gui/adapters/geometry.py` |
| `services/drillhole/data_fetcher.py` | `gui/adapters/feature_fetcher.py` (`DataFetcher`) |
| `interfaces/profile_interface.py`, `interfaces/export_interface.py` | removed (no `IProfileService`/`IExportService`) |
| `core/services/interpretation_service.py` | `gui/dialog_interpretation_manager.py` + mixins |
| `core/services/drillhole_orchestrator.py` | `core/services/drillhole/trajectory_engine.py` |
| `qt6_compat.py` | removed (scoped enums) |
| `verify_i18n_hygiene.py`, `check_cc.py` | upstreamed into `qgis-plugin-analyzer` (gates in `scripts/sync_metrics.py`) |
| `scripts/context_selector.py`, `memory_prune.py`, `metrics_report.py` | folded into `scripts/sync_metrics.py` / `validate_agent_system.py` |
| `scripts/run_tests_in_qgis.py` | `scripts/run_in_qgis.py` |
| `core/utils/resource_manager.py`, `core/utils_legacy.py` | removed |
| `seismic_service.py` | removed (geology only) |

## Structural staleness (beyond file references)

Docs whose described **architecture/tree** predates the refactor (not just a wrong filename):

| Doc | Issue |
|-----|-------|
| `docs/docsec/PROJECT_STRUCTURE.md` / `_EN.md` | Version says **2.5.0** (current 3.8.0); tree predates `core/domain/`, `core/services/export/`, `plugin/`, the `dialog_*_mixin` split and the drillhole/settings tabs |
| `docs/source/ARCHITECTURE.md` | Describes the old `main_dialog_*` split (`data`/`signals`/`preview`/`status`/`tools`/`export`/`validation`) and lists `seismic_service.py` as an example |
| `docs/docsec/ARCHITECTURE.md` | Same old `main_dialog_preview.py` / `core/types.py` split |
| `docs/maintainer/TECHNICAL_COMPENDIUM.md` | Describes `parallel_geology_service`, `main_dialog_validation`, `main_dialog_tools` |
| `docs/maintainer/CODE_ANALYSIS.md` | References `gui/lod_calculator.py` (removed) |
| `docs/qa/CONSOLIDATED_DIAGNOSIS.md` | References `qt6_compat.py`, `core/utils/qgis.py`, `interfaces/profile_interface.py`, `lod_calculator.py`, `utils/resource_manager.py` |
| `docs/ARCHITECTURE_EN.md` | Tree + Concrete Services table still list `services/profile_service.py` (moved to `gui/adapters/profile_extractor.py`) |

> [!note] Already fixed in this session
> The `ARCHITECTURE_EN.md` **Core Interfaces** table (phantom `IProfileService`/`IExportService`)
> and the Mermaid interface nodes were corrected in commit `625923e`. The remaining
> `services/profile_service.py` rows still need updating.

## Documentation pipeline / CI

**Local build:** `make docs` → `make apidoc` → `scripts/build_docs.sh`:

1. `sphinx-apidoc` → `docs/source` stubs.
2. `scripts/i18n/translate_docs.py compile` (`.po` → `.mo`).
3. `sphinx-build` for 14 locales → `docs/build/<lang>`.
4. Copy to **`../sec_interp_docs`** = `/home/jmbernales/qgispluginsdev/sec_interp_docs/`.
5. Sync offline `help/html/<lang>`.
6. If `../sec_interp_docs/.git` exists → auto commit + `git push origin main`.

**External docs repo:**

| Item | Value |
|------|-------|
| Local path | `/home/jmbernales/qgispluginsdev/sec_interp_docs/` |
| Remote | `https://github.com/geociencio/sec_interp_docs.git` (branch `main`) |
| GitHub Pages | https://geociencio.github.io/sec_interp_docs/ |

**⚠️ CI inconsistency** — `.github/workflows/docs.yml` is stale/broken:
- runs `make apidocs-html` → **target does not exist** (Makefile has `apidoc` / `docs`);
- deploys `docs/build/html` to the **main repo's `gh-pages`**, not the external `sec_interp_docs` repo;
- trigger `paths: sec_interp/**` does not match the layout (plugin files are at the repo root).

## Notes

- `docs/source/*.md` are Sphinx sources compiled into 14 languages by
  `scripts/build_docs.sh`; fixing them will change the published docs.
- Some entries may be illustrative examples rather than claims (review before editing).
- Historical docs were intentionally **not** audited for correction (they document past states).

---
*Generated by the documentation staleness audit — no files were modified.*
