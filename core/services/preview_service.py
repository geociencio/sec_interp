"""Preview service for SecInterp.

This module provides a service to orchestrate the generation of all
preview components, including topography, structures, and drillholes.
It remains decoupled from the GUI layer.
"""

from __future__ import annotations

import math
import time
from typing import Any, Optional

from qgis.core import (
    QgsDistanceArea,
    QgsGeometry,
    QgsPointXY,
    QgsRasterLayer,
    QgsVectorLayer,
)

from sec_interp.core.exceptions import ProcessingError, GeometryError, DataMissingError
from sec_interp.core import utils as scu
from sec_interp.core.performance_metrics import MetricsCollector, PerformanceTimer
from sec_interp.core.types import GeologyData, ProfileData, StructureData, PreviewParams, PreviewResult
from sec_interp.logger_config import get_logger


logger = get_logger(__name__)






class PreviewService:
    """Orchestrates preview data generation."""

    def __init__(self, controller: Any):
        """Initialize with plugin controller to access other services.

        Args:
            controller: The SecInterpController instance.
        """
        self.controller = controller

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
            if ratio > 1.1:
                # Slight detail boost as we zoom in
                detail_boost = 1.0 + (math.log10(ratio) * 0.5)
                return int(base_points * detail_boost)

            return base_points
        return manual_max

    def generate_all(
        self, params: PreviewParams, transform_context: Any
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

        # 1. Topography
        with PerformanceTimer("Topography Generation", result.metrics):
            # Calculate LOD interval
            interval = None
            if params.auto_lod:
                # Get line length
                line_feat = next(params.line_layer.getFeatures(), None)
                if not line_feat:
                    raise GeometryError("Section line layer has no features", {"layer": params.line_layer.name()})
                
                line_len = line_feat.geometry().length()
                max_pts = self.calculate_max_points(
                    params.canvas_width, params.max_points, True
                )
                interval = line_len / max_pts if max_pts > 0 else None

            result.topo = self.controller.profile_service.generate_topographic_profile(
                params.line_layer, params.raster_layer, params.band_num, interval=interval
            )
            if result.topo:
                result.metrics.record_count("Topography Points", len(result.topo))

        # 2. Structures
        if params.struct_layer and params.dip_field and params.strike_field:
            with PerformanceTimer("Structure Generation", result.metrics):
                line_feat = next(params.line_layer.getFeatures(), None)
                if line_feat:
                    line_geom = line_feat.geometry()
                    line_azimuth = scu.calculate_line_azimuth(line_geom)

                    result.struct = (
                        self.controller.structure_service.project_structures(
                            line_lyr=params.line_layer,
                            raster_lyr=params.raster_layer,
                            struct_lyr=params.struct_layer,
                            buffer_m=params.buffer_dist,
                            line_az=line_azimuth,
                            dip_field=params.dip_field,
                            strike_field=params.strike_field,
                            band_number=params.band_num,
                        )
                    )
                    if result.struct:
                        result.metrics.record_count(
                            "Structure Points", len(result.struct)
                        )

        # 3. Drillholes
        if params.collar_layer:
            with PerformanceTimer("Drillhole Generation", result.metrics):
                result.drillhole = self._generate_drillholes(params)
                if result.drillhole:
                    result.metrics.record_count("Drillholes", len(result.drillhole))

        return result

    def _generate_drillholes(self, params: PreviewParams) -> Optional[Any]:
        """Internal helper for drillhole trace and interval generation.

        Args:
            params: Preview parameters containing drillhole layer and fields.

        Returns:
            A list of drillhole data tuples, or None if no collars found or skipped.
        """
        line_feat = next(params.line_layer.getFeatures(), None)
        if not line_feat:
            raise GeometryError("Section line layer has no features", {"layer": params.line_layer.name()})

        # Validation: Ensure critical drillhole fields are selected
        if not params.collar_id_field:
            logger.info("Drillhole preview skipped: No Collar ID field selected.")
            return None

        line_geom = line_feat.geometry()
        if line_geom.isMultipart():
            lines = line_geom.asMultiPolyline()
            points = lines[0] if lines else []
        else:
            points = line_geom.asPolyline()

        if not points:
            raise GeometryError("Section line has no vertices", {"layer": params.line_layer.name()})

        line_start = points[0]

        # Setup distance area
        distance_area = QgsDistanceArea()
        distance_area.setSourceCrs(params.line_layer.crs(), self.transform_context)

        try:
            projected_collars = self.controller.drillhole_service.project_collars(
                collar_layer=params.collar_layer,
                line_geom=line_geom,
                line_start=line_start,
                distance_area=distance_area,
                buffer_width=params.buffer_dist,
                collar_id_field=params.collar_id_field,
                use_geometry=params.collar_use_geometry,
                collar_x_field=params.collar_x_field,
                collar_y_field=params.collar_y_field,
                collar_z_field=params.collar_z_field,
                collar_depth_field=params.collar_depth_field,
                dem_layer=params.raster_layer,
                line_crs=params.line_layer.crs(),
            )
        except Exception as e:
            raise ProcessingError("Failed to project drillhole collars", {"hole_id_field": params.collar_id_field}) from e

        if not projected_collars:
            return None

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

        try:
            _, drillhole_data = self.controller.drillhole_service.process_intervals(
                collar_points=projected_collars,
                collar_layer=params.collar_layer,
                survey_layer=params.survey_layer,
                interval_layer=params.interval_layer,
                collar_id_field=params.collar_id_field,
                use_geometry=params.collar_use_geometry,
                collar_x_field=params.collar_x_field,
                collar_y_field=params.collar_y_field,
                line_geom=line_geom,
                line_start=line_start,
                distance_area=distance_area,
                buffer_width=params.buffer_dist,
                section_azimuth=scu.calculate_line_azimuth(line_geom),
                survey_fields=survey_fields,
                interval_fields=interval_fields,
            )
        except Exception as e:
            raise ProcessingError("Failed to process drillhole intervals") from e

        logger.info(f"Generated {len(drillhole_data) if drillhole_data else 0} drillhole traces")
        return drillhole_data
