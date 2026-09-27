# SecInterp — File → note map (v2 vault)

> Every plugin Python file with a wiki link to the vault note documenting it. Unlike `project_structure*.md` (mirrors of `docs/structure/`), this document is vault-owned and its links are navigable in Obsidian.
>
> Tier C files (< 50 lines) share their package note.

## `core/` (76)

| File | Lines | Tier | Note |
|---|--:|:---:|---|
| `core/__init__.py` | 6 | C | [[core]] |
| `core/algorithms.py` | 14 | C | [[core]] |
| `core/config.py` | 253 | A | [[config]] |
| `core/controller.py` | 426 | A | [[controller]] |
| `core/data_cache.py` | 169 | A | [[data_cache]] |
| `core/domain/__init__.py` | 68 | B | [[domain]] |
| `core/domain/dtos.py` | 209 | A | [[dtos]] |
| `core/domain/entities.py` | 161 | A | [[entities]] |
| `core/domain/enums.py` | 22 | C | [[core_domain]] |
| `core/domain/spatial_meta.py` | 48 | C | [[core_domain]] |
| `core/domain/task_inputs.py` | 79 | B | [[task_inputs]] |
| `core/exceptions.py` | 65 | B | [[exceptions]] |
| `core/interfaces/__init__.py` | 3 | C | [[core_interfaces]] |
| `core/interfaces/cache_interface.py` | 62 | B | [[cache_interface]] |
| `core/interfaces/drillhole_interface.py` | 26 | C | [[core_interfaces]] |
| `core/interfaces/geology_interface.py` | 26 | C | [[core_interfaces]] |
| `core/interfaces/i_renderer_3d.py` | 31 | C | [[core_interfaces]] |
| `core/interfaces/preview_interface.py` | 25 | C | [[core_interfaces]] |
| `core/interfaces/structure_interface.py` | 37 | C | [[core_interfaces]] |
| `core/models/__init__.py` | 0 | C | [[core_models]] |
| `core/models/settings_model.py` | 179 | A | [[settings_model]] |
| `core/performance_metrics.py` | 321 | A | [[performance_metrics]] |
| `core/services/__init__.py` | 19 | C | [[core_services]] |
| `core/services/access_control_service.py` | 36 | C | [[core_services]] |
| `core/services/drillhole/__init__.py` | 3 | C | [[core_services_drillhole]] |
| `core/services/drillhole/collar_processor.py` | 100 | A | [[collar_processor]] |
| `core/services/drillhole/interval_processor.py` | 50 | B | [[interval_processor]] |
| `core/services/drillhole/projection_engine.py` | 30 | C | [[core_services_drillhole]] |
| `core/services/drillhole/survey_processor.py` | 15 | C | [[core_services_drillhole]] |
| `core/services/drillhole/trajectory_engine.py` | 111 | A | [[trajectory_engine]] |
| `core/services/drillhole_service.py` | 113 | A | [[drillhole_service]] |
| `core/services/export/__init__.py` | 9 | C | [[core_services_export]] |
| `core/services/export/compat.py` | 129 | A | [[compat]] |
| `core/services/export/handlers/__init__.py` | 0 | C | [[core_services_export_handlers]] |
| `core/services/export/handlers/axes.py` | 39 | C | [[core_services_export_handlers]] |
| `core/services/export/handlers/drillholes.py` | 70 | B | [[drillholes]] |
| `core/services/export/handlers/drillholes_3d.py` | 82 | B | [[drillholes_3d]] |
| `core/services/export/handlers/geology.py` | 66 | B | [[geology]] |
| `core/services/export/handlers/interpretations.py` | 93 | B | [[interpretations]] |
| `core/services/export/handlers/structures.py` | 85 | B | [[structures]] |
| `core/services/export/handlers/topography.py` | 63 | B | [[topography]] |
| `core/services/export/map_settings_factory.py` | 34 | C | [[core_services_export]] |
| `core/services/export/orchestrator.py` | 207 | A | [[orchestrator]] |
| `core/services/export/path_resolver.py` | 60 | B | [[path_resolver]] |
| `core/services/export_service.py` | 13 | C | [[core_services]] |
| `core/services/geology_service.py` | 87 | B | [[geology_service]] |
| `core/services/preview_service.py` | 176 | A | [[preview_service]] |
| `core/services/structure_service.py` | 187 | A | [[structure_service]] |
| `core/services/vertical_exaggeration_service.py` | 186 | A | [[vertical_exaggeration_service]] |
| `core/utils/__init__.py` | 82 | B | [[core_utils___init___py]] |
| `core/utils/drillhole.py` | 298 | A | [[drillhole]] |
| `core/utils/geology.py` | 40 | C | [[core_utils]] |
| `core/utils/geometry_utils/__init__.py` | 3 | C | [[core_utils_geometry_utils]] |
| `core/utils/geometry_utils/measurement.py` | 136 | A | [[measurement]] |
| `core/utils/geometry_utils/optimization.py` | 197 | A | [[optimization]] |
| `core/utils/geometry_utils/processing.py` | 97 | B | [[processing]] |
| `core/utils/i18n.py` | 30 | C | [[core_utils]] |
| `core/utils/io.py` | 101 | A | [[io]] |
| `core/utils/metadata_reader.py` | 129 | A | [[metadata_reader]] |
| `core/utils/parsing.py` | 222 | A | [[parsing]] |
| `core/utils/rendering.py` | 129 | A | [[rendering]] |
| `core/utils/safe_loader.py` | 79 | B | [[safe_loader]] |
| `core/utils/sampling.py` | 43 | C | [[core_utils]] |
| `core/utils/spatial.py` | 30 | C | [[core_utils]] |
| `core/validation/__init__.py` | 49 | C | [[core_validation]] |
| `core/validation/base_validator.py` | 25 | C | [[core_validation]] |
| `core/validation/crs_plausibility.py` | 99 | B | [[crs_plausibility]] |
| `core/validation/field_validator.py` | 184 | A | [[field_validator]] |
| `core/validation/layer_metadata.py` | 61 | B | [[layer_metadata]] |
| `core/validation/layer_validator.py` | 200 | A | [[layer_validator]] |
| `core/validation/path_validator.py` | 111 | A | [[path_validator]] |
| `core/validation/pipeline.py` | 29 | C | [[core_validation]] |
| `core/validation/project_validator.py` | 211 | A | [[project_validator]] |
| `core/validation/project_validators.py` | 292 | A | [[project_validators]] |
| `core/validation/validation_helpers.py` | 195 | A | [[validation_helpers]] |
| `core/validation/validators.py` | 252 | A | [[validators]] |

## `gui/` (80)

| File | Lines | Tier | Note |
|---|--:|:---:|---|
| `gui/__init__.py` | 14 | C | [[gui]] |
| `gui/adapters/__init__.py` | 7 | C | [[gui_adapters]] |
| `gui/adapters/drillhole_extractor.py` | 379 | A | [[drillhole_extractor]] |
| `gui/adapters/feature_fetcher.py` | 84 | B | [[feature_fetcher]] |
| `gui/adapters/geology_extractor.py` | 248 | A | [[geology_extractor]] |
| `gui/adapters/geometry.py` | 594 | A | [[geometry]] |
| `gui/adapters/layer_resolver.py` | 113 | A | [[layer_resolver]] |
| `gui/adapters/profile_extractor.py` | 91 | B | [[profile_extractor]] |
| `gui/adapters/structure_extractor.py` | 275 | A | [[structure_extractor]] |
| `gui/adapters/validation_extractor.py` | 269 | A | [[validation_extractor]] |
| `gui/dialog_dependencies.py` | 23 | C | [[gui]] |
| `gui/dialog_export_manager.py` | 218 | A | [[dialog_export_manager]] |
| `gui/dialog_facade_mixin.py` | 166 | A | [[dialog_facade_mixin]] |
| `gui/dialog_input_manager.py` | 237 | A | [[dialog_input_manager]] |
| `gui/dialog_interpretation_manager.py` | 107 | A | [[dialog_interpretation_manager]] |
| `gui/dialog_lifecycle_mixin.py` | 77 | B | [[dialog_lifecycle_mixin]] |
| `gui/dialog_message_mixin.py` | 78 | B | [[dialog_message_mixin]] |
| `gui/dialog_preview_manager.py` | 280 | A | [[dialog_preview_manager]] |
| `gui/dialog_settings_persistence.py` | 198 | A | [[dialog_settings_persistence]] |
| `gui/dialog_signal_manager.py` | 394 | A | [[dialog_signal_manager]] |
| `gui/dialog_state_manager.py` | 123 | A | [[dialog_state_manager]] |
| `gui/dialog_tool_manager.py` | 203 | A | [[dialog_tool_manager]] |
| `gui/dialogs/interpretation_properties_dialog.py` | 149 | A | [[interpretation_properties_dialog]] |
| `gui/interpretation_inheritance_mixin.py` | 190 | A | [[interpretation_inheritance_mixin]] |
| `gui/interpretation_persistence_mixin.py` | 177 | A | [[interpretation_persistence_mixin]] |
| `gui/layer_notification_manager.py` | 73 | B | [[layer_notification_manager]] |
| `gui/legend_widget.py` | 81 | B | [[legend_widget]] |
| `gui/main_dialog.py` | 201 | A | [[main_dialog]] |
| `gui/main_dialog_config.py` | 200 | A | [[main_dialog_config]] |
| `gui/main_dialog_utils.py` | 50 | B | [[main_dialog_utils]] |
| `gui/preview_axes_manager.py` | 204 | A | [[preview_axes_manager]] |
| `gui/preview_callbacks_mixin.py` | 127 | A | [[preview_callbacks_mixin]] |
| `gui/preview_layer_factory.py` | 479 | A | [[preview_layer_factory]] |
| `gui/preview_legend_renderer.py` | 178 | A | [[preview_legend_renderer]] |
| `gui/preview_param_hasher.py` | 133 | A | [[preview_param_hasher]] |
| `gui/preview_render_mixin.py` | 145 | A | [[preview_render_mixin]] |
| `gui/preview_renderer.py` | 330 | A | [[preview_renderer]] |
| `gui/preview_reporter.py` | 181 | A | [[preview_reporter]] |
| `gui/preview_state.py` | 57 | B | [[preview_state]] |
| `gui/preview_task_orchestrator.py` | 158 | A | [[preview_task_orchestrator]] |
| `gui/renderers/__init__.py` | 0 | C | [[gui_renderers]] |
| `gui/renderers/base_renderer.py` | 60 | B | [[base_renderer]] |
| `gui/renderers/color_manager.py` | 48 | C | [[gui_renderers]] |
| `gui/renderers/drillhole_renderer.py` | 71 | B | [[drillhole_renderer]] |
| `gui/renderers/geology_renderer.py` | 29 | C | [[gui_renderers]] |
| `gui/renderers/interpretation_renderer.py` | 43 | C | [[gui_renderers]] |
| `gui/renderers/structure_renderer.py` | 18 | C | [[gui_renderers]] |
| `gui/renderers/topo_renderer.py` | 71 | B | [[topo_renderer]] |
| `gui/services/__init__.py` | 7 | C | [[gui_services]] |
| `gui/tasks/__init__.py` | 0 | C | [[gui_tasks]] |
| `gui/tasks/drillhole_task.py` | 107 | A | [[drillhole_task]] |
| `gui/tasks/geology_task.py` | 101 | A | [[geology_task]] |
| `gui/tools/__init__.py` | 3 | C | [[gui_tools]] |
| `gui/tools/interpretation_tool.py` | 269 | A | [[interpretation_tool]] |
| `gui/tools/measure_tool.py` | 330 | A | [[measure_tool]] |
| `gui/tools/snapper.py` | 112 | A | [[snapper]] |
| `gui/ui/__init__.py` | 7 | C | [[gui_ui]] |
| `gui/ui/main_window.py` | 161 | A | [[main_window]] |
| `gui/ui/pages/__init__.py` | 7 | C | [[gui_ui_pages]] |
| `gui/ui/pages/base_page.py` | 105 | A | [[base_page]] |
| `gui/ui/pages/dem_page.py` | 392 | A | [[dem_page]] |
| `gui/ui/pages/drillhole/__init__.py` | 9 | C | [[gui_ui_pages_drillhole]] |
| `gui/ui/pages/drillhole/collar_tab.py` | 180 | A | [[collar_tab]] |
| `gui/ui/pages/drillhole/interval_tab.py` | 144 | A | [[interval_tab]] |
| `gui/ui/pages/drillhole/survey_tab.py` | 144 | A | [[survey_tab]] |
| `gui/ui/pages/drillhole_page.py` | 130 | A | [[drillhole_page]] |
| `gui/ui/pages/geology_page.py` | 120 | A | [[geology_page]] |
| `gui/ui/pages/interpretation_page.py` | 230 | A | [[interpretation_page]] |
| `gui/ui/pages/preview_page.py` | 262 | A | [[preview_page]] |
| `gui/ui/pages/section_page.py` | 350 | A | [[section_page]] |
| `gui/ui/pages/settings/__init__.py` | 9 | C | [[gui_ui_pages_settings]] |
| `gui/ui/pages/settings/advanced_tab.py` | 106 | A | [[advanced_tab]] |
| `gui/ui/pages/settings/default_tab.py` | 178 | A | [[default_tab]] |
| `gui/ui/pages/settings/info_tab.py` | 48 | C | [[gui_ui_pages_settings]] |
| `gui/ui/pages/settings/settings_persistence.py` | 75 | B | [[settings_persistence]] |
| `gui/ui/pages/settings_page.py` | 124 | A | [[settings_page]] |
| `gui/ui/pages/structure_page.py` | 170 | A | [[structure_page]] |
| `gui/ui/sidebar.py` | 67 | B | [[sidebar]] |
| `gui/ui_status_manager.py` | 221 | A | [[ui_status_manager]] |
| `gui/utils.py` | 76 | B | [[gui_utils_py]] |

## `exporters/` (13)

| File | Lines | Tier | Note |
|---|--:|:---:|---|
| `exporters/__init__.py` | 81 | B | [[exporters]] |
| `exporters/base_exporter.py` | 137 | A | [[base_exporter]] |
| `exporters/csv_exporter.py` | 58 | B | [[csv_exporter]] |
| `exporters/drillhole_3d_exporter.py` | 243 | A | [[drillhole_3d_exporter]] |
| `exporters/drillhole_exporters.py` | 239 | A | [[drillhole_exporters]] |
| `exporters/dxf_exporter.py` | 126 | A | [[dxf_exporter]] |
| `exporters/image_exporter.py` | 72 | B | [[image_exporter]] |
| `exporters/interpretation_3d_exporter.py` | 465 | A | [[interpretation_3d_exporter]] |
| `exporters/interpretation_exporters.py` | 146 | A | [[interpretation_exporters]] |
| `exporters/pdf_exporter.py` | 79 | B | [[pdf_exporter]] |
| `exporters/profile_exporters.py` | 362 | A | [[profile_exporters]] |
| `exporters/svg_exporter.py` | 85 | B | [[svg_exporter]] |
| `exporters/vector_exporter.py` | 122 | A | [[vector_exporter]] |

## `plugin/` (4)

| File | Lines | Tier | Note |
|---|--:|:---:|---|
| `plugin/__init__.py` | 9 | C | [[plugin]] |
| `plugin/input_validator.py` | 80 | B | [[input_validator]] |
| `plugin/lifecycle.py` | 167 | A | [[lifecycle]] |
| `plugin/render_pipeline.py` | 119 | A | [[render_pipeline]] |

## `resources/` (2)

| File | Lines | Tier | Note |
|---|--:|:---:|---|
| `resources/__init__.py` | 4 | C | [[resources_pkg]] |
| `resources/resources.py` | 176 | A | [[resources]] |

## `root` (4)

| File | Lines | Tier | Note |
|---|--:|:---:|---|
| `__init__.py` | 49 | C | [[root]] |
| `logger_config.py` | 220 | A | [[logger_config]] |
| `run_qgis_manage.py` | 11 | C | [[root]] |
| `sec_interp_plugin.py` | 129 | A | [[sec_interp_plugin]] |

*Vault-owned map — regenerate with `scripts/generate_structure_links.py --write`.*
