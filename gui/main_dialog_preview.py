"""Preview management module for SecInterp main dialog.

This module handles preview generation, rendering, and updates,
separating preview logic from the main dialog class.
"""

from __future__ import annotations

import hashlib
import tempfile
import traceback
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from qgis.core import QgsRasterLayer, QgsVectorLayer
from qgis.PyQt.QtCore import QCoreApplication, QTimer

from sec_interp.core import utils as scu
from sec_interp.core import validation as vu
from sec_interp.core.exceptions import ProcessingError, SecInterpError
from sec_interp.core.interfaces.preview_interface import IPreviewService
from sec_interp.core.performance_metrics import (
    MetricsCollector,
    PerformanceTimer,
    format_duration,
)
from sec_interp.core.services.preview_service import PreviewService
from sec_interp.core.types import (
    GeologyData,
    PreviewParams,
    PreviewResult,
    ProfileData,
    StructureData,
)
from sec_interp.logger_config import get_logger

from .main_dialog_config import DialogConfig
from .services.parallel_geology_service import ParallelGeologyService
from .preview_reporter import PreviewReporter

if TYPE_CHECKING:
    from .main_dialog import SecInterpDialog

logger = get_logger(__name__)


class PreviewManager:
    """Manages preview generation and rendering for the dialog.

    This class encapsulates all preview-related logic, including data
    generation, rendering, and updates based on user interactions.
    """

    def __init__(
        self,
        dialog: sec_interp.gui.main_dialog.SecInterpDialog,
        preview_service: Optional[IPreviewService] = None,
    ):
        """Initialize preview manager with reference to parent dialog.

        Args:
            dialog: The :class:`sec_interp.gui.main_dialog.SecInterpDialog` instance
            preview_service: Optional preview service for dependency injection
        """
        self.dialog = dialog
        self.cached_data: dict[str, Any] = {
            "topo": None,
            "geol": None,
            "struct": None,
            "drillhole": None,
        }
        self.last_params_hash = None
        self.last_result: Optional[PreviewResult] = None
        self.metrics = MetricsCollector()

        # Initialize services
        self.async_service = ParallelGeologyService()
        self.async_service.all_finished.connect(self._on_geology_finished)
        self.async_service.batch_progress.connect(self._on_geology_progress)
        self.async_service.error_occurred.connect(self._on_geology_error)

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
        self.dialog.preview_widget.canvas.extentsChanged.connect(
            self._on_extents_changed
        )

    def cleanup(self):
        """Clean up resources and stop background tasks."""
        self.async_service.cancel_processing()
        self.debounce_timer.stop()

    def generate_preview(self) -> tuple[bool, str]:
        """Generate complete preview with all available data layers.

        This is the main preview generation method that orchestrates
        data generation and rendering.

        Returns:
            Tuple of (success, message)
        """
        self.metrics.clear()

        try:
            with PerformanceTimer("Total Preview Generation", self.metrics):
                # 1. Validation & Parameter Collection
                params = self.dialog.plugin_instance._get_and_validate_inputs()
                if not params:
                    return False, QCoreApplication.translate(
                        "PreviewManager", "Invalid configuration"
                    )

                # 2. Data processing (with caching)
                result = self._process_preview_data(params)

                # 3. UI Update & Visualization
                self._update_crs_label(params.line_layer)
                self._run_render_pipeline(result)

                # 4. Results Reporting
                result_msg = PreviewReporter.format_results_message(
                    result, self.metrics
                )
                self.dialog.preview_widget.results_text.setPlainText(result_msg)

                if DialogConfig.LOG_DETAILED_METRICS:
                    logger.info(f"Preview Performance: {self.metrics.get_summary()}")

        except SecInterpError as e:
            self.dialog.handle_error(e, "Preview Error")
            return False, str(e)
        except Exception as e:
            self.dialog.handle_error(e, "Unexpected Preview Error")
            return False, str(e)
        else:
            return True, QCoreApplication.translate(
                "PreviewManager", "Preview generated successfully"
            )

    def _process_preview_data(self, params: PreviewParams) -> PreviewResult:
        """Process or retrieve cached preview data."""
        current_hash = self._calculate_params_hash(params)
        data_unchanged = current_hash == self.last_params_hash
        self.last_params_hash = current_hash

        if data_unchanged and self.last_result:
            logger.info("Using cached data (params unchanged)")
            return self.last_result

        # Generate fresh data
        transform_context = (
            self.dialog.plugin_instance.iface.mapCanvas()
            .mapSettings()
            .transformContext()
        )
        result = self.preview_service.generate_all(params, transform_context)

        # Merge results and metrics
        self.cached_data.update(
            {
                "topo": result.topo,
                "struct": result.struct,
                "drillhole": result.drillhole,
            }
        )
        self.metrics.timings.update(result.metrics.timings)
        self.metrics.counts.update(result.metrics.counts)

        # Cancel any existing async work before starting new one
        self.async_service.cancel_processing()

        # Start Async Geology if needed
        if self.dialog.page_geology.is_complete():
            self._start_async_geology(params)
            self.cached_data["geol"] = None  # Reset until async finished

        self.last_result = result
        return result

    def _run_render_pipeline(self, result: PreviewResult) -> None:
        """Orchestrate the rendering of generated data."""
        try:
            if not self.dialog.plugin_instance or not hasattr(
                self.dialog.plugin_instance, "draw_preview"
            ):
                self._handle_invalid_plugin_instance()

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
        except Exception as e:
            logger.error(f"Error drawing preview: {e}", exc_info=True)
            raise ValueError(f"Failed to render preview: {e!s}") from e

    def update_from_checkboxes(self) -> None:
        """Update preview when checkboxes change.

        This method re-renders the preview using cached data and
        current checkbox states without regenerating data.
        """
        if not self.cached_data["topo"]:
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
        except Exception as e:
            logger.error(f"Error updating preview from checkboxes: {e}", exc_info=True)

    def _calculate_params_hash(self, params: PreviewParams) -> str:
        """Calculate a unique hash for preview parameters to check for changes."""

        def get_id(layer: Optional[QgsVectorLayer]) -> str:
            """Safe layer ID retrieval."""
            return layer.id() if layer else "None"

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

    def _on_extents_changed(self):
        """Handle map canvas extent changes (zoom/pan)."""
        # Only handle if Auto LOD is enabled
        if not self.dialog.preview_widget.chk_auto_lod.isChecked():
            return

        # Restart debounce timer
        self.debounce_timer.start(200)

    def _update_lod_for_zoom(self):
        """Update LOD based on current zoom level."""
        try:
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

            logger.debug(
                f"Zoom LOD update: ratio={ratio:.2f}, new_max_points={new_max_points}"
            )

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

        except Exception as e:
            logger.error(f"Error in zoom LOD update: {e}", exc_info=True)

    def _start_async_geology(self, params: PreviewParams):
        """Start asynchronous geology generation."""
        outcrop_layer = params.outcrop_layer
        outcrop_name_field = params.outcrop_name_field

        if not outcrop_layer or not outcrop_name_field:
            return

        # Prepare arguments package
        args = (
            self.dialog.plugin_instance.controller.geology_service.generate_geological_profile,
            params.line_layer,
            params.raster_layer,
            outcrop_layer,
            outcrop_name_field,
            params.band_num,
        )

        self.dialog.preview_widget.results_text.setPlainText(
            QCoreApplication.translate(
                "PreviewManager", "Generating Geology in background..."
            )
        )
        # No need for a custom worker function anymore
        self.async_service.process_profiles_parallel([args])

    def _on_geology_finished(self, results):
        """Handle completion of parallel geology generation."""
        # Flatten results (results -> chunks -> items -> segments)
        final_geol_data = []
        for chunk in results:
            if chunk:
                for item_result in chunk:
                    if item_result:
                        final_geol_data.extend(item_result)

        self.cached_data["geol"] = final_geol_data if final_geol_data else None

        # Log success
        logger.info(f"Async geology finished: {len(final_geol_data)} segments")

        # Trigger update of preview
        try:
            # We reuse the update logic but need to ensure it uses the new cached data
            # Since checkbox logic handles 'if show_geol -> use cached', we just need
            # to force redraw
            # But first we might want to update the result text to say "Done"

            # Re-render
            self.update_from_checkboxes()

            # Update results text (we need to regenerate the whole message)
            # Note: This requires current state of other layers
            topo = self.cached_data["topo"]
            struct = self.cached_data["struct"]
            buffer_dist = self._get_buffer_distance()

            if topo:  # Only valid if we have topo
                # Reconstruct a partial result for formatting
                result = PreviewResult(
                    topo=topo,
                    geol=final_geol_data,
                    struct=struct,
                    drillhole=self.cached_data.get("drillhole"),
                    buffer_dist=buffer_dist,
                )
                msg = PreviewReporter.format_results_message(result, self.metrics)
                self.dialog.preview_widget.results_text.setPlainText(msg)

                # CRITICAL: Update last_result so cached renders include geology
                self.last_result = result

        except Exception as e:
            logger.error(f"Error updating UI after async geology: {e}", exc_info=True)

    def _on_geology_progress(self, progress):
        """Handle progress updates from parallel service."""
        self.dialog.preview_widget.results_text.setPlainText(
            QCoreApplication.translate(
                "PreviewManager", "Generating Geology: {}%..."
            ).format(progress)
        )

    def _on_geology_error(self, error_msg: str):
        """Handle error during parallel geology generation."""
        logger.error(f"Async geology error: {error_msg}")
        # Map string error to ProcessingError for centralized handling
        error = ProcessingError(
            QCoreApplication.translate(
                "PreviewManager", "Geology processing failed: {}"
            ).format(error_msg)
        )
        self.dialog.handle_error(error, "Geology Error")

    def _handle_invalid_plugin_instance(self):
        """Handle case where plugin instance is not available for rendering."""
        raise AttributeError("Plugin instance or draw_preview method not available")

    def _update_crs_label(self, layer: Optional[QgsVectorLayer]) -> None:
        """Update the CRS label in the dialog status bar.

        Args:
            layer: The reference layer to get CRS from.
        """
        try:
            if layer:
                auth_id = layer.crs().authid()
                self.dialog.preview_widget.lbl_crs.setText(
                    QCoreApplication.translate("PreviewManager", "CRS: {}").format(
                        auth_id
                    )
                )
            else:
                self.dialog.preview_widget.lbl_crs.setText(
                    QCoreApplication.translate("PreviewManager", "CRS: None")
                )
        except Exception:
            self.dialog.preview_widget.lbl_crs.setText(
                QCoreApplication.translate("PreviewManager", "CRS: Unknown")
            )
