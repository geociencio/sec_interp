"""Preview management module for SecInterp main dialog.

This module handles preview generation, rendering, and updates,
separating preview logic from the main dialog class.
"""

from __future__ import annotations

import contextlib
from collections.abc import Callable
from typing import Any

from qgis.core import QgsVectorLayer
from qgis.PyQt.QtCore import QTimer

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
from sec_interp.core.utils.i18n import TranslatableMixin
from sec_interp.gui.adapters.layer_resolver import resolve_layer
from sec_interp.logger_config import get_logger

from .main_dialog_config import DialogConfig
from .preview_param_hasher import PreviewParamHasher
from .preview_reporter import PreviewReporter
from .preview_state import PreviewCache
from .preview_task_orchestrator import PreviewTaskOrchestrator

logger = get_logger(__name__)


class PreviewManager(TranslatableMixin):
    """Manages preview generation and rendering for the dialog.

    This class encapsulates all preview-related logic, including data
    generation, rendering, and updates based on user interactions.
    """

    def __init__(
        self,
        dialog: Any,
        preview_service: IPreviewService | None = None,
        cache: PreviewCache | None = None,
    ) -> None:
        """Initialize preview manager with specialized components."""
        self.dialog = dialog
        self.preview_service = preview_service or PreviewService(
            self.dialog.plugin_instance.controller
        )
        self.metrics = MetricsCollector()

        # Specialized components
        self.orchestrator = PreviewTaskOrchestrator(self)
        self.hasher = PreviewParamHasher()

        # Cache & State
        self.cached_data = cache if cache is not None else PreviewCache()
        self.last_params_hash: str | None = None
        self.last_result: PreviewResult | None = None

        # Decoupled callback invoked when section geometry changes
        self._on_interpretations_cleared: Callable[[], None] | None = None

        # Initialize zoom debounce timer
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)

        # Connect all signals
        self.connect_signals()

    def set_interpretations_cleared_handler(self, handler: Callable[[], None]) -> None:
        """Register the callback invoked when section geometry changes.

        Args:
            handler: Callable that clears persisted interpretations.

        """
        self._on_interpretations_cleared = handler

    def connect_signals(self) -> None:
        """Connect all signals for the preview manager."""
        self.disconnect_signals()

        self.debounce_timer.timeout.connect(self._update_lod_for_zoom)
        self.dialog.preview_widget.canvas.extentsChanged.connect(self._on_extents_changed)

    def disconnect_signals(self) -> None:
        """Disconnect all signals for the preview manager."""
        with contextlib.suppress(TypeError, RuntimeError):
            self.debounce_timer.timeout.disconnect()

        with contextlib.suppress(AttributeError, TypeError, RuntimeError):
            self.dialog.preview_widget.canvas.extentsChanged.disconnect(self._on_extents_changed)

    def cleanup(self) -> None:
        """Clean up resources and stop background tasks."""
        self.orchestrator.cancel_active_tasks()
        self.debounce_timer.stop()
        self.disconnect_signals()

    def generate_preview(self) -> tuple[bool, str]:
        """Generate complete preview with all available data layers."""
        self.metrics.clear()

        try:
            with PerformanceTimer("Total Preview Generation", self.metrics):
                params = self.dialog.plugin_instance._get_and_validate_inputs()
                if not params:
                    return False, self.tr("Invalid configuration")

                result = self._process_preview_data(params)
                self._update_ui_state(params, result)

        except SecInterpError as e:
            self.dialog.handle_error(e, self.dialog.tr("Preview Error"))
            return False, str(e)
        except (AttributeError, TypeError, ValueError) as e:
            logger.exception("Unexpected UI error during preview generation")
            self.dialog.handle_error(e, self.dialog.tr("Unexpected Preview Error"))
            return False, str(e)
        except Exception as e:
            logger.exception("Critical unexpected error in preview generation")
            self.dialog.handle_error(e, self.dialog.tr("Critical Error"))
            return False, str(e)
        else:
            return True, self.tr("Preview generated successfully")

    def _update_ui_state(self, params: PreviewParams, result: PreviewResult) -> None:
        """Update UI and trigger render pipeline."""
        line_lyr = resolve_layer(params.line_layer)
        self._update_crs_label(line_lyr)
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

        # Drillholes are generated asynchronously (see _trigger_async_updates)
        result = self.preview_service.generate_all(params, transform_context)

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
                "geol": result.geol,
                "struct": result.struct,
                "drillhole": result.drillhole,
            }
        )
        self.metrics.timings.update(result.metrics.timings)
        self.metrics.counts.update(result.metrics.counts)

    def _trigger_async_updates(self, params: PreviewParams) -> None:
        """Launch background tasks via orchestrator."""
        self.orchestrator.start_geology_task(params, self.preview_service.geology_service)
        self.orchestrator.start_drillhole_task(params, self.preview_service.drillhole_orchestrator)

    def _is_data_unchanged(self, params: PreviewParams) -> bool:
        """Check if parameters haven't changed since last generation."""
        current_hash = self._calculate_params_hash(params)
        unchanged = current_hash == self.last_params_hash
        self.last_params_hash = current_hash
        return unchanged and self.last_result is not None

    def _handle_geometric_changes(self, params: PreviewParams) -> None:
        """Clear interpretations if the section geometry has changed."""
        old_geo_params = getattr(self, "_last_geo_params", None)
        line_lyr = resolve_layer(params.line_layer)
        line_feat = next(line_lyr.getFeatures(), None) if line_lyr else None
        line_geom = line_feat.geometry().asWkt() if line_feat else None

        new_geo_params = (
            params.line_layer,
            params.raster_layer,
            line_geom,
        )
        self._last_geo_params = new_geo_params

        if old_geo_params and old_geo_params != new_geo_params:
            logger.info("Geometric change detected: Clearing interpretations.")
            if self._on_interpretations_cleared:
                self._on_interpretations_cleared()

    def _cancel_active_tasks(self) -> None:
        """Cancel any existing async work via orchestrator."""
        self.orchestrator.cancel_active_tasks()

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
                self._render_cached_data()
        except (AttributeError, TypeError, ValueError) as e:
            logger.exception(f"Rendering error: {e}")
            raise ValueError(f"Failed to render preview: {e!s}") from e
        except Exception as e:
            logger.exception("Unexpected rendering pipeline error")
            raise ValueError(f"Critical rendering error: {e!s}") from e

    def _render_cached_data(self, preserve_extent: bool = False) -> None:
        """Re-render the cached preview data using the current options.

        Args:
            preserve_extent: Keep the current canvas extent instead of zooming.

        """
        if not self.dialog.plugin_instance:
            return

        opts = self.dialog.get_preview_options()
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
            preserve_extent=preserve_extent,
            use_adaptive_sampling=opts["use_adaptive_sampling"],
        )

    def update_from_checkboxes(self) -> None:
        """Update preview when checkboxes change.

        This method re-renders the preview using cached data. Visibility
        filtering is handled by the plugin's draw_preview.
        """
        if not self.last_result:
            return  # No data to display

        try:
            self._render_cached_data()
        except (AttributeError, TypeError, ValueError) as e:
            logger.exception(f"UI Sync error in preview: {e}")
        except Exception:
            logger.exception("Unexpected error updating preview from checkboxes")

    def _calculate_params_hash(self, params: PreviewParams) -> str:
        """Analyze params via hasher."""
        return self.hasher.calculate_hash(params)

    def _get_buffer_distance(self) -> float:
        """Get buffer distance from dialog, with fallback to default.

        Returns:
            Buffer distance in meters

        """
        return self.dialog.page_section.buffer_spin.value()

    def _on_extents_changed(self) -> None:
        """Handle map canvas extent changes (zoom/pan)."""
        # Only handle if Auto LOD is enabled
        if not self.dialog.preview_widget.chk_auto_lod.isChecked():
            return

        self.debounce_timer.start(DialogConfig.ZOOM_DEBOUNCE_MS)

    def _update_lod_for_zoom(self) -> None:
        """Update preview detail based on current zoom level."""
        if not self.dialog.preview_widget.canvas:
            return
        # Re-render with preserve_extent=True
        self._render_cached_data(preserve_extent=True)

    def _on_geology_finished(self, results: Any) -> None:
        """Handle completion of geology generation task."""
        logger.debug(f"_on_geology_finished called with results type: {type(results)}")

        try:
            if results and isinstance(results, list):
                self.cached_data["geol"] = results
                logger.info(f"Async geology finished: {len(results)} segments")
            else:
                self.cached_data["geol"] = None
                logger.debug("Geology task returned no results or invalid format.")

            self.update_from_checkboxes()
            self._update_results_display()
            self.orchestrator.remove_task(self.orchestrator.geology_task)
        except (AttributeError, TypeError, ValueError, SecInterpError) as e:
            logger.exception(f"Error updating UI after async geology: {e}")
        except Exception as e:
            logger.exception(f"Unexpected critical error after async geology: {e}")

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
            self.tr("Generating Geology: {}%...").format(progress)
        )

    def _on_geology_error(self, error_msg: str) -> None:
        """Handle error during parallel geology generation."""
        logger.error(f"Geology Task Error: {error_msg}")
        # Map string error to ProcessingError for centralized handling
        error = ProcessingError(self.tr("Geology processing failed: {}").format(error_msg))
        self.dialog.handle_error(error, self.dialog.tr("Geology Error"))

    def _on_drillhole_progress(self, progress: float) -> None:
        """Handle progress updates from parallel drillhole service."""
        self.dialog.preview_widget.results_text.setPlainText(
            self.tr("Generating Drillholes: {:.1f}%...").format(progress)
        )

    def _on_drillhole_error(self, error_msg: str) -> None:
        """Handle error during parallel drillhole generation."""
        logger.error(f"Drillhole Task Error: {error_msg}")
        error = ProcessingError(self.tr("Drillhole processing failed: {}").format(error_msg))
        self.dialog.handle_error(error, self.dialog.tr("Drillhole Error"))

    def _on_drillhole_finished(self, result: Any) -> None:
        """Handle completion of drillhole task."""
        logger.debug(f"_on_drillhole_finished called with result type: {type(result)}")

        if not result:
            logger.debug("Drillhole task returned no results.")
            return

        # result is expected to be (geol_data, drillhole_data)
        MIN_RESULT_PARTS = 2
        try:
            if isinstance(result, tuple) and len(result) >= MIN_RESULT_PARTS:
                _, drill_part = result[:MIN_RESULT_PARTS]
                self.cached_data["drillhole"] = drill_part
                logger.info(f"Async Drillholes finished: {len(drill_part)} holes")
            else:
                logger.warning(f"Unexpected result format from drillhole task: {type(result)}")
                return

            self.update_from_checkboxes()
            self._update_results_display()
            self.orchestrator.remove_task(self.orchestrator.drillhole_task)
        except (AttributeError, TypeError, ValueError, SecInterpError) as e:
            logger.exception(f"Error syncing UI after async drillhole: {e}")
        except Exception as e:
            logger.exception(f"Unexpected critical error after async drillhole: {e}")

    def _handle_invalid_plugin_instance(self) -> None:
        """Handle case where plugin instance is not available for rendering."""
        logger.error("Plugin instance not available in PreviewManager")
        raise AttributeError("Plugin instance or draw_preview method not available")

    def _update_crs_label(self, layer: QgsVectorLayer | None) -> None:
        """Update the CRS label in the dialog status bar.

        Args:
            layer: The reference layer to get CRS from.

        """
        try:
            if layer and layer.isValid():
                auth_id = layer.crs().authid()
                self.dialog.preview_widget.lbl_crs.setText(self.tr("CRS: {}").format(auth_id))
            else:
                self.dialog.preview_widget.lbl_crs.setText(self.tr("CRS: None"))
        except (AttributeError, TypeError, ValueError):
            self.dialog.preview_widget.lbl_crs.setText(self.tr("CRS: Unknown"))
        except Exception:
            logger.exception("Unexpected error updating CRS label")
