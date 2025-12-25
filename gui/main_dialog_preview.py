"""Preview management module for SecInterp main dialog.

This module handles preview generation, rendering, and updates,
separating preview logic from the main dialog class.
"""

from __future__ import annotations

from pathlib import Path
import tempfile
import traceback
from typing import TYPE_CHECKING, Any, Optional

from qgis.core import QgsRasterLayer, QgsVectorLayer
from qgis.PyQt.QtCore import QTimer

from sec_interp.core import utils as scu
from sec_interp.core import validation as vu
from sec_interp.core.performance_metrics import (
    MetricsCollector,
    PerformanceTimer,
    format_duration,
)
from sec_interp.core.services.preview_service import (
    PreviewParams,
    PreviewResult,
    PreviewService,
)
from sec_interp.core.types import GeologyData, ProfileData, StructureData
from sec_interp.logger_config import get_logger

from .main_dialog_config import DialogConfig
from .parallel_geology import ParallelGeologyService


if TYPE_CHECKING:
    from .main_dialog import SecInterpDialog

logger = get_logger(__name__)


class PreviewManager:
    """Manages preview generation and rendering for the dialog.

    This class encapsulates all preview-related logic, including data
    generation, rendering, and updates based on user interactions.
    """

    def __init__(self, dialog: sec_interp.gui.main_dialog.SecInterpDialog):
        """Initialize preview manager with reference to parent dialog.

        Args:
            dialog: The :class:`sec_interp.gui.main_dialog.SecInterpDialog` instance
        """
        self.dialog = dialog
        self.cached_data: dict[str, Any] = {
            "topo": None,
            "geol": None,
            "struct": None,
            "drillhole": None,
        }
        self.metrics = MetricsCollector()

        # Initialize services
        self.async_service = ParallelGeologyService()
        self.async_service.all_finished.connect(self._on_geology_finished)
        self.async_service.batch_progress.connect(self._on_geology_progress)
        self.async_service.error_occurred.connect(self._on_geology_error)

        self.preview_service = PreviewService(self.dialog.plugin_instance.controller)

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
                # 1. Validation
                raster_layer, line_layer, band_num = self._validate_requirements()

                self.dialog.preview_widget.results_text.setPlainText(
                    "Generating preview..."
                )

                # 2. Collect Parameters
                params = self._collect_preview_params(
                    raster_layer, line_layer, band_num
                )

                # 3. Data Generation (Synchronous parts)
                transform_context = (
                    self.dialog.plugin_instance.iface.mapCanvas()
                    .mapSettings()
                    .transformContext()
                )
                result = self.preview_service.generate_all(params, transform_context)

                # Merge results and metrics
                self.cached_data["topo"] = result.topo
                self.cached_data["struct"] = result.struct
                self.cached_data["drillhole"] = result.drillhole
                self.metrics.timings.update(result.metrics.timings)
                self.metrics.counts.update(result.metrics.counts)

                # Start Async Geology if needed
                if self.dialog.page_geology.is_complete():
                    self._start_async_geology(line_layer, raster_layer, band_num)
                    self.cached_data["geol"] = None  # Reset until async finished

                # 4. Visualization
                try:
                    if not self.dialog.plugin_instance or not hasattr(
                        self.dialog.plugin_instance, "draw_preview"
                    ):
                        self._handle_invalid_plugin_instance()

                    with PerformanceTimer("Rendering", self.metrics):
                        preview_options = self.dialog.get_preview_options()
                        auto_lod_enabled = preview_options["auto_lod"]
                        use_adaptive_sampling = (
                            preview_options["use_adaptive_sampling"]
                        )

                        # Calculate max_points via PreviewService
                        max_points_for_render = PreviewService.calculate_max_points(
                            canvas_width=self.dialog.preview_widget.canvas.width(),
                            manual_max=preview_options["max_points"],
                            auto_lod=auto_lod_enabled,
                        )

                        self.dialog.plugin_instance.draw_preview(
                            self.cached_data["topo"],
                            None,  # Geology handled by async finish Redraw
                            self.cached_data["struct"],
                            drillhole_data=self.cached_data["drillhole"],
                            max_points=max_points_for_render,
                            use_adaptive_sampling=use_adaptive_sampling,
                        )
                except Exception as e:
                    logger.error(f"Error drawing preview: {e}", exc_info=True)
                    raise ValueError(f"Failed to render preview: {e!s}") from e

                # 5. Results Reporting
                result_msg = self._format_results_message(result)
                self.dialog.preview_widget.results_text.setPlainText(result_msg)

                if DialogConfig.LOG_DETAILED_METRICS:
                    logger.info(f"Preview Performance: {self.metrics.get_summary()}")

        except ValueError as e:
            error_msg = f"⚠ {e!s}"
            self.dialog.preview_widget.results_text.setPlainText(error_msg)
            return False, str(e)
        except Exception as e:
            error_details = traceback.format_exc()
            error_msg = (
                f"⚠ Error generating preview: {e!s}\n\nDetails:\n{error_details}"
            )
            self.dialog.preview_widget.results_text.setPlainText(error_msg)
            logger.error(f"Preview generation failed: {e}", exc_info=True)
            return False, str(e)
        else:
            return True, "Preview generated successfully"

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

    def _collect_preview_params(
        self, raster_layer, line_layer, band_num
    ) -> PreviewParams:
        """Collect all parameters for preview generation."""
        values = self.dialog.get_selected_values()
        return PreviewParams(
            raster_layer=raster_layer,
            line_layer=line_layer,
            band_num=band_num,
            buffer_dist=self.dialog.page_section.buffer_spin.value(),
            outcrop_layer=self.dialog.page_geology.layer_combo.currentLayer(),
            outcrop_name_field=self.dialog.page_geology.field_combo.currentField(),
            struct_layer=self.dialog.page_struct.layer_combo.currentLayer(),
            dip_field=self.dialog.page_struct.dip_combo.currentField(),
            strike_field=self.dialog.page_struct.strike_combo.currentField(),
            collar_layer=values.get("collar_layer_obj"),
            collar_id_field=values.get("collar_id_field"),
            collar_use_geometry=values.get("collar_use_geometry", True),
            collar_x_field=values.get("collar_x_field"),
            collar_y_field=values.get("collar_y_field"),
            collar_z_field=values.get("collar_z_field"),
            collar_depth_field=values.get("collar_depth_field"),
            survey_layer=values.get("survey_layer_obj"),
            survey_id_field=values.get("survey_id_field"),
            survey_depth_field=values.get("survey_depth_field"),
            survey_azim_field=values.get("survey_azim_field"),
            survey_incl_field=values.get("survey_incl_field"),
            interval_layer=values.get("interval_layer_obj"),
            interval_id_field=values.get("interval_id_field"),
            interval_from_field=values.get("interval_from_field"),
            interval_to_field=values.get("interval_to_field"),
            interval_lith_field=values.get("interval_lith_field"),
            dip_scale_factor=self.dialog.page_struct.scale_spin.value(),
        )

    def _validate_requirements(self) -> tuple[QgsRasterLayer, QgsVectorLayer, int]:
        """Validate minimum requirements for preview generation.

        Returns:
            Tuple of (raster_layer, line_layer, band_num)

        Raises:
            ValueError: If validation fails
        """
        raster_layer = self.dialog.page_dem.raster_combo.currentLayer()
        if not raster_layer:
            raise ValueError("No raster layer selected")

        line_layer = self.dialog.page_section.line_combo.currentLayer()
        if not line_layer:
            raise ValueError("No crossline layer selected")

        band_num = self.dialog.page_dem.band_combo.currentBand()
        if not band_num:
            raise ValueError("No band selected")

        return raster_layer, line_layer, band_num

    def _get_buffer_distance(self) -> float:
        """Get buffer distance from dialog, with fallback to default.

        Returns:
            Buffer distance in meters
        """
        return self.dialog.page_section.buffer_spin.value()

    def _format_results_message(self, result: PreviewResult) -> str:
        """Format results message for display using core result objects."""
        lines = [
            "✓ Preview generated!",
            "",
            f"Topography: {len(result.topo) if result.topo else 0} points",
        ]

        # Add components
        lines.append(self._format_geology_summary(result.geol))
        lines.append(self._format_structure_summary(result.struct, result.buffer_dist))
        lines.append(self._format_drillhole_summary())

        # Add ranges
        metrics = self._format_result_metrics(result)
        lines.extend(metrics)

        # Add performance metrics if enabled
        if (
            DialogConfig.ENABLE_PERFORMANCE_METRICS
            and DialogConfig.SHOW_METRICS_IN_RESULTS
        ):
            timings = self.metrics.timings
            if timings:
                lines.append("")
                lines.append("Performance:")
                if "Topography Generation" in timings:
                    lines.append(
                        f"  Topo: {format_duration(timings['Topography Generation'])}"
                    )
                if "Geology Generation" in timings and result.geol:
                    lines.append(
                        f"  Geol: {format_duration(timings['Geology Generation'])}"
                    )
                if "Structure Generation" in timings and result.struct:
                    lines.append(
                        f"  Struct: {format_duration(timings['Structure Generation'])}"
                    )
                if "Rendering" in timings:
                    lines.append(f"  Render: {format_duration(timings['Rendering'])}")
                if "Total Preview Generation" in timings:
                    lines.append(
                        f"  Total: {format_duration(timings['Total Preview Generation'])}"
                    )

        lines.extend(["", "Adjust 'Vert. Exag.' and click Preview to update."])

        return "\n".join(lines)

    def _format_geology_summary(self, geol_data: Optional[GeologyData]) -> str:
        """Format a summary line for geology data."""
        if not geol_data:
            return "Geology: No data"
        return f"Geology: {len(geol_data)} segments"

    def _format_structure_summary(
        self, struct_data: Optional[StructureData], buffer_dist: float
    ) -> str:
        """Format a summary line for structural data."""
        if not struct_data:
            return "Structures: No data"
        return f"Structures: {len(struct_data)} measurements (buffer: {buffer_dist}m)"

    def _format_drillhole_summary(self) -> str:
        """Format a summary line for drillhole data."""
        drillhole_data = self.cached_data.get("drillhole")
        if not drillhole_data:
            return "Drillholes: No data"
        return f"Drillholes: {len(drillhole_data)} holes found"

    def _format_result_metrics(self, result: PreviewResult) -> list[str]:
        """Format elevation metrics for the results message."""
        min_elev, max_elev = result.get_elevation_range()
        min_dist, max_dist = result.get_distance_range()

        return [
            "",
            "Geometry Range:",
            f"  Elevation: {min_elev:.1f} to {max_elev:.1f} m",
            f"  Distance: {min_dist:.1f} to {max_dist:.1f} m",
        ]

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

    def _start_async_geology(self, line_layer, raster_layer, band_num):
        """Start asynchronous geology generation."""
        outcrop_layer = self.dialog.page_geology.layer_combo.currentLayer()
        outcrop_name_field = self.dialog.page_geology.field_combo.currentField()

        if not outcrop_layer or not outcrop_name_field:
            return

        # Prepare arguments package
        # We pass the bound method and its arguments. The ParallelGeologyService
        # will execute it automatically.
        args = (
            self.dialog.plugin_instance.controller.geology_service.generate_geological_profile,
            line_layer,
            raster_layer,
            outcrop_layer,
            outcrop_name_field,
            band_num,
        )

        self.dialog.preview_widget.results_text.setPlainText(
            "Generating Geology in background..."
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
                msg = self._format_results_message(result)
                self.dialog.preview_widget.results_text.setPlainText(msg)

        except Exception as e:
            logger.error(f"Error updating UI after async geology: {e}", exc_info=True)

    def _on_geology_progress(self, progress):
        """Handle progress updates from parallel service."""
        self.dialog.preview_widget.results_text.setPlainText(
            f"Generating Geology: {progress}%..."
        )

    def _on_geology_error(self, error_msg):
        """Handle error during parallel geology generation."""
        logger.error(f"Async geology error: {error_msg}")
        self.dialog.preview_widget.results_text.append(
            f"\n⚠ Geology Error: {error_msg}"
        )

    def _handle_invalid_plugin_instance(self):
        """Handle case where plugin instance is not available for rendering."""
        raise AttributeError("Plugin instance or draw_preview method not available")
