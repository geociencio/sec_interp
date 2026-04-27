"""Service for managing preview generation and rendering.

This module provides a service to orchestrate the generation of all
preview components, including topography, structures, and drillholes.
It remains decoupled from the GUI layer.
"""

from __future__ import annotations

import math
from typing import Any

from sec_interp.core import utils as scu
from sec_interp.core.domain import (
    PreviewParams,
    PreviewResult,
)
from sec_interp.core.exceptions import (
    ProcessingError,
    SecInterpError,
)
from sec_interp.core.performance_metrics import PerformanceTimer
from sec_interp.core.utils.qgis import LayerResolver
from sec_interp.core.utils.sampling import prepare_profile_context
from sec_interp.core.utils.spatial import calculate_line_azimuth
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class PreviewService:
    """Orchestrates preview data generation."""

    def __init__(self, controller: Any) -> None:
        """Initialize with plugin controller to access other services.

        Args:
            controller: The SecInterpController instance.

        """
        self.controller = controller

    @property
    def drillhole_orchestrator(self) -> Any:
        """Expose drillhole orchestrator from controller."""
        return self.controller.drillhole_orchestrator

    @property
    def geology_service(self) -> Any:
        """Expose geology service from controller."""
        return self.controller.geology_service

    @property
    def structure_service(self) -> Any:
        """Expose structure service from controller."""
        return self.controller.structure_service

    @property
    def profile_service(self) -> Any:
        """Expose profile service from controller."""
        return self.controller.profile_service

    @staticmethod
    def calculate_max_points(
        canvas_width: int,
        manual_max: int = 1000,
        auto_lod: bool = True,
        ratio: float = 1.0,
    ) -> int:
        """Calculate the optimal number of points for rendering.

        Args:
            canvas_width: Current width of the preview canvas in pixels.
            manual_max: User-specified maximum points for plotting.
            auto_lod: Whether to use automatic level of detail (LOD).
            ratio: Current zoom ratio (full_extent / current_extent).

        Returns:
            The optimal number of points to use for 2D rendering.

        """
        if auto_lod:
            # Optimal points is roughly 2x the pixel width for high quality rendering
            base_points = max(200, int(canvas_width * 2))

            # Apply zoom boost if ratio is significant
            ZOOM_DETAIL_BOOST_THRESHOLD = 1.1
            if ratio > ZOOM_DETAIL_BOOST_THRESHOLD:
                # Slight detail boost as we zoom in
                detail_boost = 1.0 + (math.log10(ratio) * 0.5)
                return int(base_points * detail_boost)

            return base_points
        return manual_max

    def generate_all(
        self,
        params: PreviewParams,
        transform_context: Any,
        skip_drillholes: bool = False,
    ) -> PreviewResult:
        """Generate all preview components in a consolidated result.

        Args:
            params: Validated parameters for preview generation.
            transform_context: QgsCoordinateTransformContext for CRS operations.
            skip_drillholes: If True, skips synchronous drillhole generation.

        Returns:
            A consolidated object containing all generated preview data.

        """
        # Phase 5: Native validation
        params.validate()

        result = PreviewResult(buffer_dist=params.buffer_dist)
        self.transform_context = transform_context

        # 1. Topography & Context Extraction
        line_geom, line_start, raster_lyr = self._generate_topography_step(params, result)

        # 2. Structures (Now using detached flow)
        self._generate_structures_step(params, result, line_geom, line_start, raster_lyr)

        # 3. Drillholes
        if params.collar_layer and not skip_drillholes:
            with PerformanceTimer("Drillhole Generation", result.metrics):
                result.drillhole = self._generate_drillholes(params)
                if result.drillhole:
                    result.metrics.record_count("Drillholes", len(result.drillhole))

        return result

    def _generate_topography_step(
        self, params: PreviewParams, result: PreviewResult
    ) -> tuple[Any, Any, Any]:
        """Step 1: Topography & Context Extraction."""
        with PerformanceTimer("Topography Generation", result.metrics):
            line_lyr = LayerResolver.resolve(params.line_layer)
            raster_lyr = LayerResolver.resolve(params.raster_layer)

            if not line_lyr or not raster_lyr:
                raise ProcessingError("Required layers for topography are missing.")

            line_geom, line_start, distance_area = prepare_profile_context(line_lyr)
            self.distance_area = distance_area  # Store for other layers

            # Calculate LOD interval
            interval = None
            if params.auto_lod:
                line_len = line_geom.length()
                max_pts = self.calculate_max_points(params.canvas_width, params.max_points, True)
                interval = line_len / max_pts if max_pts > 0 else None

            result.topo = self.controller.profile_service.generate_topographic_profile(
                line_lyr,
                raster_lyr,
                params.band_num,
                interval=interval,
            )
            if result.topo:
                result.metrics.record_count("Topography Points", len(result.topo))
        return line_geom, line_start, raster_lyr

    def _generate_structures_step(
        self,
        params: PreviewParams,
        result: PreviewResult,
        line_geom: Any,
        line_start: Any,
        raster_lyr: Any,
    ) -> None:
        """Step 2: Structures (Now using detached flow)."""
        if params.struct_layer and params.dip_field and params.strike_field:
            with PerformanceTimer("Structure Generation", result.metrics):
                struct_lyr = LayerResolver.resolve(params.struct_layer)
                if not struct_lyr:
                    return

                line_azimuth = calculate_line_azimuth(line_geom)

                # Detach
                struct_data = self.controller.structure_service.detach_structures(
                    struct_lyr, line_geom, params.buffer_dist
                )

                # Project
                result.struct = self.controller.structure_service.project_structures(
                    line_geom=line_geom,
                    line_start=line_start,
                    da=self.distance_area,
                    raster_lyr=raster_lyr,  # Already resolved above
                    struct_data=struct_data,
                    buffer_m=params.buffer_dist,
                    line_az=line_azimuth,
                    dip_field=params.dip_field,
                    strike_field=params.strike_field,
                    band_number=params.band_num,
                )
                if result.struct:
                    result.metrics.record_count("Structure Points", len(result.struct))

    def _generate_drillholes(self, params: PreviewParams) -> Any | None:
        """Generate drillhole trace and interval data."""
        # Validation: Ensure critical drillhole fields are selected
        if not params.collar_id_field:
            logger.info("Drillhole preview skipped: No Collar ID field selected.")
            return None

        line_lyr = LayerResolver.resolve(params.line_layer)
        raster_lyr = LayerResolver.resolve(params.raster_layer)
        collar_lyr = LayerResolver.resolve(params.collar_layer)

        if not line_lyr or not collar_lyr:
            return None

        line_geom, line_start, distance_area = prepare_profile_context(line_lyr)

        # 1. Detach Data
        collar_ids, collar_data, pre_sampled_z = (
            self.controller.drillhole_service.collar_processor.detach_features(
                collar_lyr,
                line_geom,
                params.buffer_dist,
                params.collar_id_field,
                params.collar_use_geometry,
                params.collar_x_field,
                params.collar_y_field,
                params.collar_z_field,
                raster_lyr,
                target_crs=line_lyr.crs(),
            )
        )

        if not collar_data:
            return None

        # 2. Project Collars
        try:
            projected_collars = self.controller.drillhole_service.project_collars(
                collar_data=collar_data,
                line_data=line_geom,
                distance_area=distance_area,
                buffer_width=params.buffer_dist,
                collar_id_field=params.collar_id_field,
                use_geometry=params.collar_use_geometry,
                collar_x_field=params.collar_x_field,
                collar_y_field=params.collar_y_field,
                collar_z_field=params.collar_z_field,
                collar_depth_field=params.collar_depth_field,
                pre_sampled_z=pre_sampled_z,
            )
        except (ValueError, TypeError, SecInterpError) as e:
            raise ProcessingError(f"Failed to project drillhole collars: {e}") from e

        if not projected_collars:
            return None

        # 3. Fetch Child Data
        survey_lyr = LayerResolver.resolve(params.survey_layer)
        interval_lyr = LayerResolver.resolve(params.interval_layer)

        survey_map = {}
        if survey_lyr:
            survey_map = self.controller.drillhole_service._fetch_bulk_data(
                survey_lyr,
                collar_ids,
                {
                    "id": params.survey_id_field,
                    "depth": params.survey_depth_field,
                    "azim": params.survey_azim_field,
                    "incl": params.survey_incl_field,
                },
            )

        interval_map = {}
        if interval_lyr:
            interval_map = self.controller.drillhole_service._fetch_bulk_data(
                interval_lyr,
                collar_ids,
                {
                    "id": params.interval_id_field,
                    "from": params.interval_from_field,
                    "to": params.interval_to_field,
                    "lith": params.interval_lith_field,
                },
            )

        # 4. Process Intervals
        try:
            _, drillhole_data = self.controller.drillhole_service.process_intervals(
                collar_points=projected_collars,
                collar_data=collar_data,
                survey_data=survey_map,
                interval_data=interval_map,
                collar_id_field=params.collar_id_field,
                use_geometry=params.collar_use_geometry,
                collar_x_field=params.collar_x_field,
                collar_y_field=params.collar_y_field,
                line_geom=line_geom,
                line_start=line_start,
                distance_area=distance_area,
                buffer_width=params.buffer_dist,
                section_azimuth=scu.calculate_line_azimuth(line_geom),
                survey_fields={},
                interval_fields={},
            )
        except (ValueError, TypeError, SecInterpError) as e:
            logger.exception(f"Failed to process drillhole intervals: {e}")
            raise ProcessingError(f"Failed to process drillhole intervals: {e}") from e
        except Exception as e:
            logger.exception("Unexpected error during drillhole processing")
            raise ProcessingError("Unexpected error during drillhole processing") from e

        logger.info(f"Generated {len(drillhole_data) if drillhole_data else 0} drillhole traces")
        return drillhole_data
