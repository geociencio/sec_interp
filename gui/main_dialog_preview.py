from __future__ import annotations

"""Preview management module for SecInterp main dialog.

This module handles preview generation, rendering, and updates,
separating preview logic from the main dialog class.
"""

import hashlib
from typing import TYPE_CHECKING, Any

from qgis.core import QgsApplication, QgsVectorLayer
from qgis.PyQt.QtCore import QCoreApplication, QTimer

from sec_interp.core.domain import (
    PreviewParams,
    PreviewResult,
)
from sec_interp.core.exceptions import ProcessingError, SecInterpError
from sec_interp.core.interfaces.preview_interface import IPreviewService
from sec_interp.core.performance_metrics import (
    MetricsCollector,
    PerformanceTimer,
)
from sec_interp.core.services.preview_service import PreviewService
from sec_interp.logger_config import get_logger

from .main_dialog_config import DialogConfig
from .preview_reporter import PreviewReporter
from .tasks.drillhole_task import DrillholeGenerationTask
from .tasks.geology_task import GeologyGenerationTask

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)


class PreviewManager:
    """Manages preview generation and rendering for the dialog.

    This class encapsulates all preview-related logic, including data
    generation, rendering, and updates based on user interactions.
    """

    def __init__(
        self,
        dialog: Any,
        preview_service: IPreviewService | None = None,
    ) -> None:
        """Initialize preview manager with reference to parent dialog.

        Args:
            dialog: The parent SecInterpDialog instance.
            preview_service: Optional preview service for dependency injection.

        """
        self.dialog = dialog
        self.cached_data: dict[str, Any] = {
            "topo": None,
            "geol": None,
            "struct": None,
            "drillhole": None,
        }
        self.last_params_hash: str | None = None
        self.last_result: PreviewResult | None = None
        self.metrics = MetricsCollector()

        # Initialize services
        # self.async_service removed in favor of QgsTask
        # self.async_service removed in favor of QgsTask
        self.active_task: GeologyGenerationTask | None = None
        self.active_drill_task: DrillholeGenerationTask | None = None

        self.preview_service = preview_service or PreviewService(
            self.dialog.plugin_instance.controller
        )

        # Initialize zoom debounce timer
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._update_lod_for_zoom)

        # Connect extents changed signal
        # We need to do this carefully to avoid signal loops
        # Initial connection is safe
        self.dialog.preview_widget.canvas.extentsChanged.connect(self._on_extents_changed)

    def cleanup(self) -> None:
        """Clean up resources and stop background tasks."""
        if self.active_task:
            self.active_task.cancel()
            self.active_task = None
        if self.active_drill_task:
            self.active_drill_task.cancel()
            self.active_drill_task = None
        self.debounce_timer.stop()

    def generate_preview(self) -> tuple[bool, str]:
        """Generate complete preview with all available data layers."""
        self.metrics.clear()

        try:
            with PerformanceTimer("Total Preview Generation", self.metrics):
                params = self.dialog.plugin_instance._get_and_validate_inputs()
                if not params:
                    return False, QCoreApplication.translate(
                        "PreviewManager", "Invalid configuration"
                    )

                result = self._process_preview_data(params)
                self._update_ui_state(params, result)

        except SecInterpError as e:
            self.dialog.handle_error(e, "Preview Error")
            return False, str(e)
        except (AttributeError, TypeError, ValueError) as e:
            logger.exception("Unexpected UI error during preview generation")
            self.dialog.handle_error(e, "Unexpected Preview Error")
            return False, str(e)
        except Exception as e:
            logger.exception("Critical unexpected error in preview generation")
            self.dialog.handle_error(e, "Critical Error")
            return False, str(e)
        else:
            return True, QCoreApplication.translate(
                "PreviewManager", "Preview generated successfully"
            )

    def _update_ui_state(self, params: PreviewParams, result: PreviewResult) -> None:
        """Update UI and trigger render pipeline."""
        self._update_crs_label(params.line_layer)
        self._run_render_pipeline(result)

        result_msg = PreviewReporter.format_results_message(result, self.metrics)
        self.dialog.preview_widget.results_text.setPlainText(result_msg)

        if DialogConfig.LOG_DETAILED_METRICS:
            logger.info(f"Preview Performance: {self.metrics.get_summary()}")

    def _process_preview_data(self, params: PreviewParams) -> PreviewResult:
        """Process or retrieve cached preview data."""
        if self._is_data_unchanged(params):
            logger.info("Using cached data (params unchanged)")
            return self.last_result

        self._handle_geometric_changes(params)
        transform_context = self._get_transform_context()

        # Skip drillholes in sync generation
        result = self.preview_service.generate_all(
            params,
            transform_context,
            skip_drillholes=True,
        )

        self._update_cache_and_metrics(result)
        self._cancel_active_tasks()
        self._trigger_async_updates(params)

        self.last_result = result
        return result

    def _get_transform_context(self) -> Any:
        """Safely retrieve transform context from canvas."""
        if not self.dialog.plugin_instance:
            return None
        return self.dialog.plugin_instance.iface.mapCanvas().mapSettings().transformContext()

    def _update_cache_and_metrics(self, result: PreviewResult) -> None:
        """Update local cache and cumulative metrics."""
        self.cached_data.update(
            {
                "topo": result.topo,
                "struct": result.struct,
            }
        )
        self.metrics.timings.update(result.metrics.timings)
        self.metrics.counts.update(result.metrics.counts)

    def _trigger_async_updates(self, params: PreviewParams) -> None:
        """Launch background tasks for biology and drillholes."""
        # Start Async Geology if needed
        if self.dialog.page_geology.is_complete():
            self._start_async_geology(params)
            self.cached_data["geol"] = None

        # Start Async Drillholes if needed
        if params.collar_layer:
            self._start_async_drillhole(params)
            self.cached_data["drillhole"] = None

    def _is_data_unchanged(self, params: PreviewParams) -> bool:
        """Check if parameters haven't changed since last generation."""
        current_hash = self._calculate_params_hash(params)
        unchanged = current_hash == self.last_params_hash
        self.last_params_hash = current_hash
        return unchanged and self.last_result is not None

    def _handle_geometric_changes(self, params: PreviewParams) -> None:
        """Clear interpretations if the section geometry has changed."""
        old_geo_params = getattr(self, "_last_geo_params", None)
        line_feat = next(params.line_layer.getFeatures(), None) if params.line_layer else None
        line_geom = line_feat.geometry().asWkt() if line_feat else None

        new_geo_params = (
            params.line_layer.id() if params.line_layer else None,
            params.raster_layer.id() if params.raster_layer else None,
            line_geom,
        )
        self._last_geo_params = new_geo_params

        if old_geo_params and old_geo_params != new_geo_params:
            if hasattr(self.dialog, "interpretations"):
                logger.info("Geometric change detected: Clearing interpretations.")
                self.dialog.interpretations = []
                self.dialog._save_interpretations()

    def _cancel_active_tasks(self) -> None:
        """Cancel any existing async work before starting new ones."""
        if self.active_task:
            self.active_task.cancel()
            self.active_task = None

        if self.active_drill_task:
            self.active_drill_task.cancel()
            self.active_drill_task = None

    def _run_render_pipeline(self, result: PreviewResult) -> None:
        """Orchestrate the rendering of generated data.

        Args:
            result: The preview data to render.

        """
        if not self.dialog.plugin_instance:
            self._handle_invalid_plugin_instance()
            return

        try:
            with PerformanceTimer("Rendering", self.metrics):
                opts = self.dialog.get_preview_options()

                # Calculate max_points via PreviewService
                max_points = PreviewService.calculate_max_points(
                    canvas_width=self.dialog.preview_widget.canvas.width(),
                    manual_max=opts["max_points"],
                    auto_lod=opts["auto_lod"],
                )

                self.dialog.plugin_instance.draw_preview(
                    self.cached_data["topo"],
                    self.cached_data.get("geol"),
                    self.cached_data["struct"],
                    drillhole_data=self.cached_data["drillhole"],
                    max_points=max_points,
                    use_adaptive_sampling=opts["use_adaptive_sampling"],
                )
        except (AttributeError, TypeError, ValueError) as e:
            logger.exception(f"Rendering error: {e}")
            raise ValueError(f"Failed to render preview: {e!s}") from e
        except Exception as e:
            logger.exception("Unexpected rendering pipeline error")
            raise ValueError(f"Critical rendering error: {e!s}") from e

    def update_from_checkboxes(self) -> None:
        """Update preview when checkboxes change.

        This method re-renders the preview using cached data and
        current checkbox states without regenerating data.
        """
        if not self.last_result:
            return  # No data to display

        # Get checkbox states
        show_topo = self.dialog.preview_widget.chk_topo.isChecked()
        show_geol = self.dialog.preview_widget.chk_geol.isChecked()
        show_struct = self.dialog.preview_widget.chk_struct.isChecked()
        show_drill = self.dialog.preview_widget.chk_drillholes.isChecked()

        # Prepare data based on checkboxes
        topo_data = self.cached_data["topo"] if show_topo else None
        geol_data = self.cached_data["geol"] if show_geol else None
        struct_data = self.cached_data["struct"] if show_struct else None
        drillhole_data = self.cached_data["drillhole"] if show_drill else None

        # Re-render
        try:
            if not self.dialog.plugin_instance or not hasattr(
                self.dialog.plugin_instance, "draw_preview"
            ):
                logger.warning("Plugin instance not available for preview update")
                return

            preview_options = self.dialog.get_preview_options()
            auto_lod_enabled = preview_options["auto_lod"]
            use_adaptive_sampling = preview_options["use_adaptive_sampling"]

            # Calculate max_points via PreviewService
            max_points_for_render = PreviewService.calculate_max_points(
                canvas_width=self.dialog.preview_widget.canvas.width(),
                manual_max=preview_options["max_points"],
                auto_lod=auto_lod_enabled,
            )

            self.dialog.plugin_instance.draw_preview(
                topo_data,
                geol_data,
                struct_data,
                drillhole_data=drillhole_data,
                max_points=max_points_for_render,
                use_adaptive_sampling=use_adaptive_sampling,
            )
        except (AttributeError, TypeError, ValueError) as e:
            logger.exception(f"UI Sync error in preview: {e}")
        except Exception:
            logger.exception("Unexpected error updating preview from checkboxes")

    def _calculate_params_hash(self, params: PreviewParams) -> str:
        """Calculate a unique hash for preview parameters to check for changes."""

        def get_id(layer: QgsVectorLayer | None) -> str:
            """Safe layer ID retrieval."""
            return layer.id() if layer and layer.isValid() else "None"

        data_parts = [
            get_id(params.raster_layer),
            get_id(params.line_layer),
            str(params.band_num),
            str(params.buffer_dist),
            get_id(params.outcrop_layer),
            str(params.outcrop_name_field),
            get_id(params.struct_layer),
            str(params.dip_field),
            str(params.strike_field),
            get_id(params.collar_layer),
            str(params.collar_id_field),
            get_id(params.survey_layer),
            get_id(params.interval_layer),
        ]

        # Add geometry WKT if available to detect line changes
        line_feat = next(params.line_layer.getFeatures(), None)
        if line_feat:
            data_parts.append(line_feat.geometry().asWkt())

        hasher = hashlib.sha256()
        for part in data_parts:
            hasher.update(str(part).encode("utf-8"))

        return hasher.hexdigest()

    def _get_buffer_distance(self) -> float:
        """Get buffer distance from dialog, with fallback to default.

        Returns:
            Buffer distance in meters

        """
        return self.dialog.page_section.buffer_spin.value()

    def _on_extents_changed(self) -> None:
        """Handle map canvas extent changes (zoom/pan)."""
        self.debounce_timer.start(DialogConfig.ZOOM_DEBOUNCE_MS)
        # Only handle if Auto LOD is enabled
        if not self.dialog.preview_widget.chk_auto_lod.isChecked():
            return

        # Restart debounce timer
        self.debounce_timer.start(200)

    def _update_lod_for_zoom(self) -> None:
        """Update LOD based on current zoom level."""
        if not self.last_result:
            return
        canvas = self.dialog.preview_widget.canvas
        if not self.cached_data["topo"]:
            return

        full_extent = canvas.fullExtent()
        current_extent = canvas.extent()

        if current_extent.width() <= 0 or full_extent.width() <= 0:
            return

        # Calculate zoom ratio
        ratio = full_extent.width() / current_extent.width()

        # If ratio is close to 1, we are at full extent, use standard calculation
        if ratio < 1.1:
            # Let the standard update logic handle it or just do nothing if consistent?
            # Actually standard logic just uses canvas width.
            # If we return here, we might miss resetting to low detail when zooming out.
            pass

        # Calculate max_points via PreviewService
        new_max_points = PreviewService.calculate_max_points(
            canvas_width=canvas.width(), ratio=ratio, auto_lod=True
        )

        # Check if we actually need to update (hysteresis)
        # This requires knowing the last used max_points...
        # We can just re-render, it handles caching of data, but re-decimation takes time.

        logger.debug(f"Zoom LOD update: ratio={ratio:.2f}, new_max_points={new_max_points}")

        if not self.dialog.plugin_instance:
            return

        preview_options = self.dialog.get_preview_options()
        use_adaptive_sampling = preview_options["use_adaptive_sampling"]

        # Re-render with preserve_extent=True
        self.dialog.plugin_instance.draw_preview(
            self.cached_data["topo"],
            self.cached_data["geol"],
            self.cached_data["struct"],
            drillhole_data=self.cached_data["drillhole"],
            max_points=new_max_points,
            preserve_extent=True,
            use_adaptive_sampling=use_adaptive_sampling,
        )

    def _start_async_geology(self, params: PreviewParams) -> None:
        """Start asynchronous geology generation."""
        if self.active_task:
            self.active_task.cancel()
        outcrop_layer = params.outcrop_layer
        outcrop_name_field = params.outcrop_name_field

        if not outcrop_layer or not outcrop_name_field:
            return

        self.dialog.preview_widget.results_text.setPlainText(
            QCoreApplication.translate("PreviewManager", "Generating Geology in background...")
        )

        # 1. Prepare Data (Sync - Main Thread)
        try:
            task_input = self.dialog.plugin_instance.controller.geology_service.prepare_task_input(
                params.line_layer,
                params.raster_layer,
                outcrop_layer,
                outcrop_name_field,
                params.band_num,
            )
        except (AttributeError, TypeError, ValueError, SecInterpError) as e:
            logger.exception(f"Failed to prepare geology task: {e}")
            self._on_geology_error(str(e))
            return
        except Exception:
            logger.exception("Unexpected error preparing geology task")
            self._on_geology_error("Internal error during task preparation")
            return

        # 2. Launch Task (Async - Background Thread)
        self.active_task = GeologyGenerationTask(
            service=self.dialog.plugin_instance.controller.geology_service,
            task_input=task_input,
            on_finished=self._on_geology_finished,
            on_error=self._on_geology_error,
        )

        # Connect progress signal from QgsTask
        self.active_task.progressChanged.connect(self._on_geology_progress)

        # Add to QGIS Task Manager
        QgsApplication.taskManager().addTask(self.active_task)

    def _on_geology_finished(self, results: list[Any]) -> None:
        """Handle completion of geology generation task."""
        self.active_task = None
        self.cached_data["geol"] = results if results else None

        logger.info(f"Async geology finished: {len(results) if results else 0} segments")

        try:
            self.update_from_checkboxes()
            self._update_results_display()
        except SecInterpError as e:
            logger.exception(f"Error updating UI after async geology: {e}")
        except (AttributeError, TypeError, ValueError):
            logger.exception("Unexpected UI error after async geology")

    def _update_results_display(self) -> None:
        """Update results text and status display based on current cache."""
        topo = self.cached_data.get("topo")
        if not topo:
            return

        result = PreviewResult(
            topo=topo,
            geol=self.cached_data.get("geol"),
            struct=self.cached_data.get("struct"),
            drillhole=self.cached_data.get("drillhole"),
            buffer_dist=self._get_buffer_distance(),
        )
        msg = PreviewReporter.format_results_message(result, self.metrics)
        self.dialog.preview_widget.results_text.setPlainText(msg)

        # Sync last_result so checkbox updates work correctly
        self.last_result = result

    def _on_geology_progress(self, progress: float) -> None:
        """Handle progress updates from parallel service.

        Args:
            progress: Progress percentage (0-100).

        """
        self.dialog.preview_widget.results_text.setPlainText(
            QCoreApplication.translate("PreviewManager", "Generating Geology: {}%...").format(
                progress
            )
        )

    def _on_geology_error(self, error_msg: str) -> None:
        """Handle error during parallel geology generation."""
        logger.error(f"Geology Task Error: {error_msg}")
        self.active_task = None
        # Map string error to ProcessingError for centralized handling
        error = ProcessingError(
            QCoreApplication.translate("PreviewManager", "Geology processing failed: {}").format(
                error_msg
            )
        )
        self.dialog.handle_error(error, "Geology Error")

    def _start_async_drillhole(self, params: PreviewParams) -> None:
        """Start asynchronous drillhole generation."""
        if self.active_drill_task:
            self.active_drill_task.cancel()
        if not params.collar_layer:
            return

        self.dialog.preview_widget.results_text.setPlainText(
            self.dialog.preview_widget.results_text.toPlainText()
            + "\n"
            + QCoreApplication.translate("PreviewManager", "Generating Drillholes in background...")
        )

        # 1. Prepare Data (Sync)
        try:
            # Map simplified fields for the service
            survey_fields = {
                "id": params.survey_id_field,
                "depth": params.survey_depth_field,
                "azim": params.survey_azim_field,
                "incl": params.survey_incl_field,
            }
            interval_fields = {
                "id": params.interval_id_field,
                "from": params.interval_from_field,
                "to": params.interval_to_field,
                "lith": params.interval_lith_field,
            }

            task_input = (
                self.dialog.plugin_instance.controller.drillhole_service.prepare_task_input(
                    line_layer=params.line_layer,
                    buffer_width=params.buffer_dist,
                    collar_layer=params.collar_layer,
                    collar_id_field=params.collar_id_field,
                    use_geometry=params.collar_use_geometry,
                    collar_x_field=params.collar_x_field,
                    collar_y_field=params.collar_y_field,
                    collar_z_field=params.collar_z_field,
                    collar_depth_field=params.collar_depth_field,
                    survey_layer=params.survey_layer,
                    survey_fields=survey_fields,
                    interval_layer=params.interval_layer,
                    interval_fields=interval_fields,
                    dem_layer=params.raster_layer,
                )
            )
        except (AttributeError, TypeError, ValueError, SecInterpError) as e:
            logger.exception(f"Failed to prepare drillhole task: {e}")
            return
        except Exception:
            logger.exception("Unexpected error preparing drillhole task")
            return

        # 2. Launch Task
        self.active_drill_task = DrillholeGenerationTask(
            service=self.dialog.plugin_instance.controller.drillhole_service,
            task_input=task_input,
            on_finished=self._on_drillhole_finished,
            on_error=self._on_geology_error,  # Reuse error handler or make generic
        )

        QgsApplication.taskManager().addTask(self.active_drill_task)

    def _on_drillhole_finished(self, result: Any) -> None:
        """Handle completion of drillhole task."""
        self.active_drill_task = None
        if not result:
            return

        # result is (geol_data, drillhole_data)
        _, drill_part = result
        self.cached_data["drillhole"] = drill_part

        logger.info(f"Async Drillholes finished: {len(drill_part)} holes")

        try:
            self.update_from_checkboxes()
            self._update_results_display()
        except (AttributeError, TypeError, ValueError, SecInterpError):
            logger.exception("Error syncing UI after async drillhole")

    def _handle_invalid_plugin_instance(self) -> None:
        """Handle case where plugin instance is not available for rendering."""
        logger.error("Plugin instance not available in PreviewManager")
        raise AttributeError("Plugin instance or draw_preview method not available")

    def _update_crs_label(self, layer: QgsVectorLayer | None) -> None:
        """Update the CRS label in the dialog status bar.

        Args:
            layer: The reference layer to get CRS from.

        """
        if not layer or not layer.isValid():
            return

        try:
            if layer:
                auth_id = layer.crs().authid()
                self.dialog.preview_widget.lbl_crs.setText(
                    QCoreApplication.translate("PreviewManager", "CRS: {}").format(auth_id)
                )
            else:
                self.dialog.preview_widget.lbl_crs.setText(
                    QCoreApplication.translate("PreviewManager", "CRS: None")
                )
        except (AttributeError, TypeError, ValueError):
            self.dialog.preview_widget.lbl_crs.setText(
                QCoreApplication.translate("PreviewManager", "CRS: Unknown")
            )
        except Exception:
            logger.exception("Unexpected error updating CRS label")
