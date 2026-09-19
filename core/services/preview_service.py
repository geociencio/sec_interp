"""Service for managing preview generation and rendering.

This module provides a service to orchestrate the synchronous generation of
topography and structure preview components. Drillholes are generated
asynchronously via the GUI task orchestrator.
It remains decoupled from the GUI layer.
"""

from __future__ import annotations

import math
from typing import Any

from sec_interp.core.domain import (
    PreviewParams,
    PreviewResult,
)
from sec_interp.core.exceptions import ProcessingError
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
    ) -> PreviewResult:
        """Generate all preview components in a consolidated result.

        Args:
            params: Validated parameters for preview generation.
            transform_context: QgsCoordinateTransformContext for CRS operations.

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
