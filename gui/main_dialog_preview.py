"""Preview management module for SecInterp main dialog.

This module handles preview generation, rendering, and updates,
separating preview logic from the main dialog class.
"""

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
from sec_interp.core.types import GeologyData, ProfileData, StructureData
from sec_interp.logger_config import get_logger

from sec_interp.core.services.parallel_geology import ParallelGeologyService
from .main_dialog_config import DialogConfig


if TYPE_CHECKING:
    from .main_dialog import SecInterpDialog

logger = get_logger(__name__)


class PreviewManager:
    """Manages preview generation and rendering for the dialog.

    This class encapsulates all preview-related logic, including data
    generation, rendering, and updates based on user interactions.
    """

    def __init__(self, dialog: "SecInterpDialog"):
        """Initialize preview manager with reference to parent dialog.

        Args:
            dialog: The SecInterpDialog instance
        """
        self.dialog = dialog
        self.cached_data: dict[str, Any] = {"topo": None, "geol": None, "struct": None, "drillhole": None}
        self.metrics = MetricsCollector()

        # Initialize parallel service
        self.async_service = ParallelGeologyService()
        self.async_service.all_finished.connect(self._on_geology_finished)
        self.async_service.batch_progress.connect(self._on_geology_progress)
        self.async_service.error_occurred.connect(self._on_geology_error)

        # Initialize zoom debounce timer
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._update_lod_for_zoom)

        # Connect extents changed signal
        # We need to do this carefully to avoid signal loops
        # Initial connection is safe
        self.dialog.preview_widget.canvas.extentsChanged.connect(self._on_extents_changed)

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

                self.dialog.preview_widget.results_text.setPlainText("Generating preview...")

                # 2. Data Generation
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".csv", delete=False
                ) as tmp:
                    tmp_path = Path(tmp.name)

                try:
                    # Generate topography
                    with PerformanceTimer("Topography Generation", self.metrics):
                        profile_data = self.generate_topography(
                            line_layer, raster_layer, band_num
                        )

                    if not profile_data or len(profile_data) < 2:
                        return (
                            False,
                            "No profile data generated. Check that the line intersects the raster.",
                        )

                    self.metrics.record_count("Topography Points", len(profile_data))
 
                    # Generate geology (optional)
                    geol_data = None
                    if self.dialog.page_geology.is_complete():
                         self._start_async_geology(line_layer, raster_layer, band_num)
                         # geol_data remains None for now, will receive via signal

                    # Generate structures (optional)
                    struct_data = None
                    buffer_dist = 100.0
                    with PerformanceTimer("Structure Generation", self.metrics):
                        buffer_dist = self._get_buffer_distance()
                        struct_data = self.generate_structures(
                            line_layer, raster_layer, band_num, buffer_dist
                        )

                    if struct_data:
                        self.metrics.record_count("Structure Points", len(struct_data))

                    # Generate drillholes (Phase 2/3)
                    drillhole_data = None
                    if self.dialog.page_drillhole.is_complete():
                         drillhole_data = self.generate_drillholes(raster_layer)
                    
                    if drillhole_data:
                        # drillhole_data is a dictionary or list of traces? 
                        # Controller returns (hole_id, traces, segments)
                        # We should store it.
                        self.metrics.record_count("Drillholes", len(drillhole_data))

                    # Cache the data
                    self.cached_data["topo"] = profile_data
                    self.cached_data["geol"] = geol_data
                    self.cached_data["struct"] = struct_data
                    self.cached_data["drillhole"] = drillhole_data

                finally:
                    if tmp_path.exists():
                        tmp_path.unlink()

                # 3. Visualization
                try:
                    if not self.dialog.plugin_instance or not hasattr(
                        self.dialog.plugin_instance, "draw_preview"
                    ):
                        raise AttributeError(
                            "Plugin instance or draw_preview method not available"
                        )

                    with PerformanceTimer("Rendering", self.metrics):
                        preview_options = self.dialog.get_preview_options()
                        max_points_setting = preview_options["max_points"]
                        auto_lod_enabled = preview_options["auto_lod"]
                        use_adaptive_sampling = preview_options["use_adaptive_sampling"]

                        # Calculate max_points dynamically if auto_lod is enabled
                        if auto_lod_enabled:
                            canvas_width = self.dialog.preview_widget.canvas.width()
                            max_points_for_render = int(canvas_width * 1.5)
                            max_points_for_render = max(100, min(10000, max_points_for_render))
                        else:
                            max_points_for_render = max_points_setting

                        self.dialog.plugin_instance.draw_preview(
                            profile_data,
                            geol_data,
                            struct_data,
                            drillhole_data=drillhole_data,
                            max_points=max_points_for_render,
                            use_adaptive_sampling=use_adaptive_sampling,
                        )
                except Exception as e:
                    logger.error(f"Error drawing preview: {e}", exc_info=True)
                    raise ValueError(f"Failed to render preview: {e!s}")

                # 4. Results Reporting
                result_msg = self._format_results_message(
                    profile_data, geol_data, struct_data, buffer_dist
                )
                self.dialog.preview_widget.results_text.setPlainText(result_msg)

                if DialogConfig.LOG_DETAILED_METRICS:
                    logger.info(f"Preview Performance: {self.metrics.get_summary()}")

            return True, "Preview generated successfully"

        except ValueError as e:
            error_msg = f"⚠ {e!s}"
            self.dialog.preview_widget.results_text.setPlainText(error_msg)
            return False, str(e)
        except Exception as e:
            error_details = traceback.format_exc()
            error_msg = (
                f"⚠ Error generating preview: {e!s}\\n\\nDetails:\\n{error_details}"
            )
            self.dialog.preview_widget.results_text.setPlainText(error_msg)
            logger.error(f"Preview generation failed: {e}", exc_info=True)
            return False, str(e)

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
            max_points_setting = preview_options["max_points"]
            auto_lod_enabled = preview_options["auto_lod"]
            use_adaptive_sampling = preview_options["use_adaptive_sampling"]

            # Calculate max_points dynamically if auto_lod is enabled
            if auto_lod_enabled:
                canvas_width = self.dialog.preview_widget.canvas.width()
                max_points_for_render = int(canvas_width * 1.5)
                max_points_for_render = max(100, min(10000, max_points_for_render))
            else:
                max_points_for_render = max_points_setting

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

    def generate_topography(
        self, line_layer: QgsVectorLayer, raster_layer: QgsRasterLayer, band_num: int
    ) -> ProfileData | None:
        """Generate topographic profile data.

        Args:
            line_layer: Cross-section line layer
            raster_layer: DEM raster layer
            band_num: Raster band number

        Returns:
            List of (distance, elevation) tuples or None if failed
        """
        try:
            return self.dialog.plugin_instance.controller.profile_service.generate_topographic_profile(
                line_layer, raster_layer, band_num
            )
        except Exception as e:
            logger.error(f"Error generating topography: {e}", exc_info=True)
            return None

    def generate_geology(
        self, line_layer: QgsVectorLayer, raster_layer: QgsRasterLayer, band_num: int
    ) -> GeologyData | None:
        """Generate geological profile data if outcrop layer is selected.

        Args:
            line_layer: Cross-section line layer
            raster_layer: DEM raster layer
            band_num: Raster band number

        Returns:
            List of (distance, elevation, geology_name) tuples or None
        """
        outcrop_layer = self.dialog.page_geology.layer_combo.currentLayer()
        if not outcrop_layer:
            logger.debug("No outcrop layer selected")
            return None

        outcrop_name_field = self.dialog.page_geology.field_combo.currentField()
        if not outcrop_name_field:
            logger.debug("No outcrop name field selected")
            return None

        try:
            logger.info(
                f"Generating geological profile with field: {outcrop_name_field}"
            )
            result = (
                self.dialog.plugin_instance.controller.geology_service.generate_geological_profile(
                    line_layer,
                    raster_layer,
                    outcrop_layer,
                    outcrop_name_field,
                    band_num,
                )
            )
            logger.info(
                f"Geological profile result: {len(result) if result else 0} segments"
            )
            return result
        except Exception as e:
            logger.error(f"Error generating geological profile: {e}", exc_info=True)
            return None

    def generate_structures(
        self,
        line_layer: QgsVectorLayer,
        raster_layer: QgsRasterLayer,
        band_num: int,
        buffer_dist: float,
    ) -> StructureData | None:
        """Generate structural data if structural layer is selected.

        Args:
            line_layer: Cross-section line layer
            buffer_dist: Buffer distance in meters

        Returns:
            List of (distance, apparent_dip) tuples or None
        """
        structural_layer = self.dialog.page_struct.layer_combo.currentLayer()
        if not structural_layer:
            return None

        dip_field = self.dialog.page_struct.dip_combo.currentField()
        strike_field = self.dialog.page_struct.strike_combo.currentField()

        if not dip_field or not strike_field:
            return None

        try:
            # Get line azimuth
            if not line_layer or not line_layer.isValid():
                logger.warning("Invalid line layer for structure generation")
                return None

            line_feat = next(line_layer.getFeatures(), None)
            if not line_feat:
                logger.warning("No features found in line layer")
                return None

            line_geom = line_feat.geometry()
            if not line_geom or line_geom.isNull():
                logger.warning("Invalid geometry in line feature")
                return None

            line_azimuth = scu.calculate_line_azimuth(line_geom)

            return self.dialog.plugin_instance.controller.structure_service.project_structures(
                line_lyr=line_layer,
                raster_lyr=raster_layer,
                struct_lyr=structural_layer,
                buffer_m=buffer_dist,
                line_az=line_azimuth,
                dip_field=dip_field,
                strike_field=strike_field,
                band_number=band_num,
            )
        except Exception as e:
            logger.error(f"Error generating structures: {e}", exc_info=True)
            return None

    def generate_drillholes(self, raster_layer: QgsRasterLayer):
        """Generate drillhole data for preview."""
        try:
            # We need to construct the 'values' dict expected by DrillholeService
            # or call controller.drillhole_service methods directly?
            # Controller.generate_profile_data builds 'values' from dialog.
            # Here we can reuse dialog.get_selected_values() which we updated!
            
            values = self.dialog.get_selected_values()
            
            # Additional required values that might not be in get_selected_values if they come from other pages
            # But get_selected_values aggregates everything.
            
            # However, DrillholeService.process_intervals needs projected traces first.
            # Controller logic:
            # 1. Project Collars
            # 2. Process Intervals
            
            dh_service = self.dialog.plugin_instance.controller.drillhole_service
            
            # Prepare arguments for project_collars
            # values dict has keys like 'collar_layer_obj'
           
            # Prepare geometry arguments
            line_layer = self.dialog.page_section.line_combo.currentLayer()
            if not line_layer:
                return []
                
            line_feat = next(line_layer.getFeatures(), None)
            if not line_feat:
                return []
                
            line_geom = line_feat.geometry()
            
            # Handle MultiLineString vs LineString
            if line_geom.isMultipart():
                lines = line_geom.asMultiPolyline()
                if not lines:
                    logger.warning("generate_drillholes: Empty MultiLineString")
                    return []
                # Use the first line segment of the multiline
                # Ideally sections are single lines, but sometimes they come as MultiLine
                points = lines[0]
            else:
                points = line_geom.asPolyline()
                
            if not points:
                logger.warning("generate_drillholes: Empty geometry points")
                return []
                
            line_start = points[0]
            
            # Create distance area
            from qgis.core import QgsDistanceArea
            distance_area = QgsDistanceArea()
            distance_area.setSourceCrs(line_layer.crs(), self.dialog.plugin_instance.iface.mapCanvas().mapSettings().transformContext())
            
            logger.info("generate_drillholes: Starting drillhole generation...")
            
            projected_collars = dh_service.project_collars(
                collar_layer=values.get("collar_layer_obj"),
                line_geom=line_geom,
                line_start=line_start,
                distance_area=distance_area,
                buffer_width=self.dialog.page_section.buffer_spin.value(),
                collar_id_field=values.get("collar_id_field"),
                use_geometry=values.get("collar_use_geometry", True),
                collar_x_field=values.get("collar_x_field"),
                collar_y_field=values.get("collar_y_field"),
                collar_z_field=values.get("collar_z_field"),
                collar_depth_field=values.get("collar_depth_field"),
                dem_layer=raster_layer
            )
            
            logger.info(f"generate_drillholes: Projected {len(projected_collars) if projected_collars else 0} collars.")
            
            if not projected_collars:
                return []
                
            # Prepare survey and interval fields dicts
            survey_fields = {
                "id": values.get("survey_id_field"),
                "depth": values.get("survey_depth_field"),
                "azim": values.get("survey_azim_field"),
                "incl": values.get("survey_incl_field")
            }
            
            interval_fields = {
                "id": values.get("interval_id_field"),
                "from": values.get("interval_from_field"),
                "to": values.get("interval_to_field"),
                "lith": values.get("interval_lith_field")
            }

            logger.info("generate_drillholes: Processing intervals...")
            # Process intervals
            # Note: process_intervals returns (geol_data, drillhole_data)
            # We are interested in drillhole_data (traces + segments) for visualization
            _, drillhole_data = dh_service.process_intervals(
                collar_points=projected_collars,
                collar_layer=values.get("collar_layer_obj"),
                survey_layer=values.get("survey_layer_obj"),
                interval_layer=values.get("interval_layer_obj"),
                collar_id_field=values.get("collar_id_field"),
                use_geometry=values.get("collar_use_geometry", True),
                collar_x_field=values.get("collar_x_field"),
                collar_y_field=values.get("collar_y_field"),
                line_geom=line_geom,
                line_start=line_start,
                distance_area=distance_area,
                buffer_width=self.dialog.page_section.buffer_spin.value(),
                section_azimuth=scu.calculate_line_azimuth(line_geom),
                survey_fields=survey_fields,
                interval_fields=interval_fields
            )
            
            logger.info(f"generate_drillholes: Processed {len(drillhole_data) if drillhole_data else 0} drillholes.")
            
            return drillhole_data
            
        except Exception as e:
            logger.error(f"Error generating drillholes: {e}", exc_info=True)
            return None

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

    def _format_results_message(
        self,
        profile_data: ProfileData,
        geol_data: GeologyData | None,
        struct_data: StructureData | None,
        buffer_dist: float,
    ) -> str:
        """Format results message for display.

        Args:
            profile_data: Topographic profile data
            geol_data: Geological profile data (optional)
            struct_data: Structural data (optional)
            buffer_dist: Buffer distance used

        Returns:
            Formatted message string
        """
        lines = [
            "✓ Preview generated!",
            "",
            f"Topography: {len(profile_data)} points",
        ]

        if geol_data:
            lines.append(f"Geology: {len(geol_data)} segments")
        else:
            lines.append("Geology: No intersections or layer not selected")

        if struct_data:
            lines.append(f"Structures: {len(struct_data)} measurements")
        else:
            lines.append(
                f"Structures: None in {buffer_dist}m buffer or layer not selected"
            )
            
        drillhole_data = self.cached_data.get("drillhole")
        if drillhole_data:
            lines.append(f"Drillholes: {len(drillhole_data)} holes/traces")
        else:
            lines.append("Drillholes: None or not configured")

        lines.extend(
            [
                "",
                f"Distance: {profile_data[0][0]:.1f} - {profile_data[-1][0]:.1f} m",
                f"Elevation: {min(p[1] for p in profile_data):.1f} - {max(p[1] for p in profile_data):.1f} m",
            ]
        )

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
                if "Geology Generation" in timings and geol_data:
                    lines.append(
                        f"  Geol: {format_duration(timings['Geology Generation'])}"
                    )
                if "Structure Generation" in timings and struct_data:
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
            
            # Base points (pixels * 1.5)
            base_points = canvas.width() * 1.5
            
            # Target points for the whole dataset to ensure current view has 'base_points' density
            new_max_points = int(base_points * ratio)
            
            # Clamp to safe limits (e.g. 50k points max)
            new_max_points = min(50000, new_max_points)
            new_max_points = max(100, new_max_points)

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
            band_num
        )
        
        self.dialog.preview_widget.results_text.setPlainText("Generating Geology in background...")
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
             # Since checkbox logic handles 'if show_geol -> use cached', we just need to force redraw
             # But first we might want to update the result text to say "Done"
             
             # Re-render
             self.update_from_checkboxes()
             
             # Update results text (we need to regenerate the whole message)
             # Note: This requires current state of other layers
             topo = self.cached_data["topo"]
             struct = self.cached_data["struct"]
             buffer_dist = self._get_buffer_distance()
             
             if topo: # Only valid if we have topo
                 msg = self._format_results_message(topo, final_geol_data, struct, buffer_dist)
                 self.dialog.preview_widget.results_text.setPlainText(msg)
                 
        except Exception as e:
            logger.error(f"Error updating UI after async geology: {e}", exc_info=True)

    def _on_geology_progress(self, progress):
        """Handle progress updates from parallel service."""
        # Optional: Update a progress bar if available
        # self.dialog.preview_widget.progressBar.setValue(progress)
        self.dialog.preview_widget.results_text.setPlainText(f"Generating Geology: {progress}%...")

    def _on_geology_error(self, error_msg):
        """Handle errors from parallel service."""
        logger.error(f"Async geology error: {error_msg}")
        self.dialog.preview_widget.results_text.append(f"\n⚠ Geology Error: {error_msg}")
