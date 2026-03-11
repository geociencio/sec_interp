# 🧪 SecInterp Testing Status

## 📊 Overview
| Metric | Value | Status |
| :--- | :--- | :--- |
| **Total Tests** | <!-- TOTAL_TESTS -->607<!-- /TOTAL_TESTS --> | ✅ Stable |
| **Platform** | Docker (QGIS 3.x) | 🐳 Active |
| **Last Updated** | <!-- LAST_UPDATE -->2026-03-11<!-- /LAST_UPDATE --> | 🕒 Auto |

---

## 🏗️ Test Coverage Breakdown

| Category | Tests | Progress | Status |
| :--- | :---: | :--- | :---: |
| **Core Services** | <!-- CORE_COUNT -->275<!-- /CORE_COUNT --> | ██████████ 100% | ✅ |
| **GUI Components** | <!-- GUI_COUNT -->221<!-- /GUI_COUNT --> | ██████░░░░ 60% | 🏗️ |
| **Exporters** | <!-- EXP_COUNT -->40<!-- /EXP_COUNT --> | ██████████ 100% | ✅ |
| **Integration** | <!-- INT_COUNT -->71<!-- /INT_COUNT --> | █████████░ 86% | ✅ |

---

## 📂 Detailed Inventory
<!-- START_INVENTORY -->
- **tests/test_translation_loading.py**: 8 tests
- **tests/core/test_algorithms.py**: 3 tests
- **tests/core/test_async_drillhole.py**: 2 tests
- **tests/core/test_config.py**: 4 tests
- **tests/core/test_config_integration.py**: 2 tests
- **tests/core/test_controller_di.py**: 2 tests
- **tests/core/test_controller_orchestration.py**: 3 tests
- **tests/core/test_data_cache_fix.py**: 3 tests
- **tests/core/test_drillhole_service.py**: 3 tests
- **tests/core/test_drillhole_service_optional.py**: 1 tests
- **tests/core/test_drillhole_utils.py**: 16 tests
- **tests/core/test_export_service.py**: 13 tests
- **tests/core/test_field_validator.py**: 6 tests
- **tests/core/test_geology_service.py**: 5 tests
- **tests/core/test_geology_service_optional.py**: 1 tests
- **tests/core/test_geometry_utils.py**: 17 tests
- **tests/core/test_layer_validator.py**: 9 tests
- **tests/core/test_path_validator.py**: 6 tests
- **tests/core/test_preview_service.py**: 12 tests
- **tests/core/test_profile_exporters.py**: 14 tests
- **tests/core/test_project_validator.py**: 7 tests
- **tests/core/test_rendering_utils.py**: 6 tests
- **tests/core/test_settings_model.py**: 6 tests
- **tests/core/test_spatial_utils.py**: 9 tests
- **tests/core/test_structure_service.py**: 2 tests
- **tests/core/test_utils.py**: 26 tests
- **tests/core/test_utils_standalone.py**: 20 tests
- **tests/core/test_validation.py**: 10 tests
- **tests/core/test_validation_refactor.py**: 4 tests
- **tests/core/validation/test_service_validation.py**: 6 tests
- **tests/core/validation/test_validation_helpers.py**: 9 tests
- **tests/core/validation/test_validators.py**: 28 tests
- **tests/core/utils/test_metadata_reader.py**: 4 tests
- **tests/core/utils/test_safe_loader_di.py**: 5 tests
- **tests/core/services/test_access_control.py**: 3 tests
- **tests/core/services/test_drillhole_engine_crash.py**: 2 tests
- **tests/core/services/drillhole/test_processors.py**: 6 tests
- **tests/gui/test_attribute_inheritance.py**: 1 tests
- **tests/gui/test_cache_fix.py**: 1 tests
- **tests/gui/test_dialog_export_manager.py**: 10 tests
- **tests/gui/test_dialog_input_manager.py**: 5 tests
- **tests/gui/test_dialog_interpretation_manager.py**: 10 tests
- **tests/gui/test_dialog_preview_manager.py**: 18 tests
- **tests/gui/test_dialog_settings_persistence.py**: 7 tests
- **tests/gui/test_dialog_state_manager.py**: 4 tests
- **tests/gui/test_export_reproduction.py**: 3 tests
- **tests/gui/test_geology_task.py**: 2 tests
- **tests/gui/test_gui_utils.py**: 3 tests
- **tests/gui/test_interpretation_export.py**: 1 tests
- **tests/gui/test_interpretation_tool.py**: 22 tests
- **tests/gui/test_lod_calculator.py**: 4 tests
- **tests/gui/test_main_dialog_core.py**: 15 tests
- **tests/gui/test_main_dialog_interpretation.py**: 4 tests
- **tests/gui/test_main_dialog_settings.py**: 3 tests
- **tests/gui/test_main_dialog_signals_wiring.py**: 3 tests
- **tests/gui/test_main_dialog_tools.py**: 14 tests
- **tests/gui/test_main_dialog_validation_manager.py**: 7 tests
- **tests/gui/test_measure_tool.py**: 20 tests
- **tests/gui/test_message_manager.py**: 5 tests
- **tests/gui/test_multi_session_persistence.py**: 3 tests
- **tests/gui/test_preview_components.py**: 21 tests
- **tests/gui/test_preview_legend_renderer.py**: 3 tests
- **tests/gui/test_preview_renderer_custom.py**: 2 tests
- **tests/gui/test_preview_task_orchestrator.py**: 6 tests
- **tests/gui/test_settings_page.py**: 4 tests
- **tests/gui/test_signal_restoration.py**: 5 tests
- **tests/gui/tasks/test_drillhole_task.py**: 6 tests
- **tests/gui/tasks/test_geology_task.py**: 6 tests
- **tests/gui/renderers/test_renderers.py**: 3 tests
- **tests/exporters/test_drillhole_3d_exporter.py**: 4 tests
- **tests/exporters/test_drillhole_export_objects.py**: 4 tests
- **tests/exporters/test_dynamic_attrs.py**: 1 tests
- **tests/exporters/test_exporters.py**: 7 tests
- **tests/exporters/test_image_exporter.py**: 4 tests
- **tests/exporters/test_interpretation_3d_exporter.py**: 3 tests
- **tests/exporters/test_interpretation_exporters.py**: 5 tests
- **tests/exporters/test_pdf_exporter.py**: 4 tests
- **tests/exporters/test_shp_exporter.py**: 5 tests
- **tests/exporters/test_svg_exporter.py**: 3 tests
- **tests/integration/test_3d_integration.py**: 4 tests
- **tests/integration/test_3d_integration_advanced.py**: 2 tests
- **tests/integration/test_3d_projections.py**: 1 tests
- **tests/integration/test_async_orchestrators.py**: 5 tests
- **tests/integration/test_export_service_e2e.py**: 8 tests
- **tests/integration/test_export_workflow.py**: 2 tests
- **tests/integration/test_geology_structure_workflow.py**: 18 tests
- **tests/integration/test_interpretation_workflow.py**: 3 tests
- **tests/integration/test_measurement_workflow.py**: 2 tests
- **tests/integration/test_preview_pipeline.py**: 23 tests
- **tests/integration/test_qgis_smoke.py**: 3 tests
- **tests/benchmarks/test_export_benchmarks.py**: 2 tests
- **tests/benchmarks/test_geometry_benchmarks.py**: 4 tests
<!-- END_INVENTORY -->

---

## 🛠️ Environment & Tools
- **Test Runner**: `unittest` / `pytest`
- **Environment**: Containerized (Docker)
- **Framework**: `qgis-manage` + `uv`

### Quick Run Commands
```bash
# Full test suite
make docker-test

# Core services only
docker run --rm -v $(pwd):/app/sec_interp sec_interp_test /bin/bash -c "python3 -m unittest discover tests/core"
```

---
> [!NOTE]
> This file is updated dynamically. Do not edit sections marked with HTML comments.
