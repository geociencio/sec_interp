"""Drillhole Data Processing Service.

This module provides services for processing and projecting drillhole data,
including collar projection, trajectory calculation, and interval interpolation.
"""

from __future__ import annotations

from typing import Any

from qgis.core import (
    QgsDistanceArea,
    QgsGeometry,
    QgsPointXY,
)
from qgis.PyQt.QtCore import QCoreApplication

from sec_interp.core import utils as scu
from sec_interp.core.domain import DrillholeProjection, GeologySegment
from sec_interp.core.exceptions import (
    SecInterpError,
    ValidationError,
)
from sec_interp.core.interfaces.drillhole_interface import IDrillholeService
from sec_interp.core.services.drillhole.collar_processor import CollarProcessor
from sec_interp.core.services.drillhole.data_fetcher import DataFetcher
from sec_interp.core.services.drillhole.interval_processor import IntervalProcessor
from sec_interp.core.services.drillhole.survey_processor import SurveyProcessor
from sec_interp.core.services.drillhole.trajectory_engine import TrajectoryEngine
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class DrillholeService(IDrillholeService):
    """Service for processing and orchestrating drillhole data.

    This service handles the projection of collars onto a 2D section line,
    the calculation of 3D trajectories from survey data, and the interpolation
    of geological intervals along those trajectories. It leverages specialized
    processors to maintain a clean separation of concerns.
    """

    def __init__(
        self,
        collar_processor: CollarProcessor | None = None,
        survey_processor: SurveyProcessor | None = None,
        interval_processor: IntervalProcessor | None = None,
        data_fetcher: DataFetcher | None = None,
        trajectory_engine: TrajectoryEngine | None = None,
    ) -> None:
        """Initialize the service with specialized processors.

        Args:
            collar_processor: Optional collar processor.
            survey_processor: Optional survey processor.
            interval_processor: Optional interval processor.
            data_fetcher: Optional data fetcher.
            trajectory_engine: Optional trajectory engine.

        """
        self.collar_processor = collar_processor or CollarProcessor()
        self.survey_processor = survey_processor or SurveyProcessor()
        self.interval_processor = interval_processor or IntervalProcessor()
        self.data_fetcher = data_fetcher or DataFetcher()
        self.trajectory_engine = trajectory_engine or TrajectoryEngine()

    def tr(self, message: str) -> str:
        """Translate a message using QCoreApplication."""
        return QCoreApplication.translate("DrillholeService", message)  # type: ignore[no-any-return]

    def project_collars(
        self,
        collar_data: list[dict[str, Any]],
        line_data: Any,
        distance_area: QgsDistanceArea,
        buffer_width: float,
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        collar_z_field: str,
        collar_depth_field: str,
        pre_sampled_z: dict[Any, float] | None = None,
    ) -> list[DrillholeProjection]:
        """Project collar points onto section line using detached domain data.

        Args:
            collar_data: List of detached collar dictionaries.
            line_data: Section line geometry or feature.
            distance_area: QgsDistanceArea for measurements.
            buffer_width: Maximum distance from section for projection.
            collar_id_field: Name of the ID field.
            use_geometry: Whether to use geometric data for projection.
            collar_x_field: Field name for X coordinate (if not using geometry).
            collar_y_field: Field name for Y coordinate (if not using geometry).
            collar_z_field: Field name for Z coordinate.
            collar_depth_field: Field name for total depth.
            pre_sampled_z: Optional dict of pre-sampled elevations.

        Returns:
            List of projection tuples: (hole_id, dist_along, z, offset, total_depth).

        Raises:
            ValidationError: If parameters are invalid.

        """
        # Simple parameter validation
        if buffer_width <= 0:
            raise ValidationError(
                self.tr("Buffer width must be positive, got {0}").format(buffer_width)
            )

        da = distance_area
        line_geom = line_data.geometry() if hasattr(line_data, "geometry") else line_data
        try:
            line_start = scu.get_line_start_point(line_geom)
        except (AttributeError, TypeError, ValueError, SecInterpError):
            line_start = QgsPointXY(0, 0)  # Fallback

        results = []
        for c_item in collar_data:
            # Delegate to CollarProcessor
            res = self.collar_processor.extract_and_project_detached(
                c_item,
                line_geom,
                line_start,
                da,
                buffer_width,
                collar_id_field,
                use_geometry,
                collar_x_field,
                collar_y_field,
                collar_z_field,
                collar_depth_field,
                pre_sampled_z,
            )
            if res:
                results.append(res)

        return results

    def _build_collar_coordinate_map(
        self,
        collar_data: list[dict[str, Any]],
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
    ) -> dict[Any, QgsPointXY]:
        """Build a mapping of hole IDs to collar coordinates."""
        return self.collar_processor.build_coordinate_map(
            collar_data, use_geometry, collar_x_field, collar_y_field
        )

    def _extract_point_from_attrs(
        self, attrs: dict[str, Any], x_field: str, y_field: str
    ) -> QgsPointXY | None:
        """Safely extract a point from attribute dictionary."""
        return self.collar_processor.extract_point_agnostic(
            {"attributes": attrs}, True, False, x_field, y_field
        )

    def process_intervals(
        self,
        collar_points: list[DrillholeProjection],
        collar_data: list[dict[str, Any]],
        survey_data: dict[Any, list[tuple]],
        interval_data: dict[Any, list[tuple]],
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        distance_area: QgsDistanceArea,
        buffer_width: float,
        section_azimuth: float,
        survey_fields: dict[str, str],
        interval_fields: dict[str, str],
    ) -> tuple[list[GeologySegment], list[DrillholeProjection]]:
        """Process drillhole interval data using detached structures."""
        geol_data: list[GeologySegment] = []
        drillhole_data: list[DrillholeProjection] = []

        # 1. Build collar coordinate map from detached data
        collar_coords = self._build_collar_coordinate_map(
            collar_data, use_geometry, collar_x_field, collar_y_field
        )

        self._process_hole_batch(
            collar_points,
            collar_coords,
            survey_data,
            interval_data,
            line_geom,
            line_start,
            distance_area,
            buffer_width,
            section_azimuth,
            geol_data,
            drillhole_data,
        )

        return geol_data, drillhole_data

    def _process_hole_batch(
        self,
        collar_points: list[DrillholeProjection],
        collar_coords: dict[Any, QgsPointXY],
        survey_data: dict[Any, list[tuple]],
        interval_data: dict[Any, list[tuple]],
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        distance_area: QgsDistanceArea,
        buffer_width: float,
        section_azimuth: float,
        geol_data: list[GeologySegment],
        drillhole_data: list[DrillholeProjection],
    ) -> None:
        """Process a batch of holes sequentially."""
        for result in collar_points:
            hole_id = result.hole_id
            collar_z = result.elevation
            given_depth = result.total_depth

            collar_point = collar_coords.get(hole_id)
            if not collar_point:
                continue

            self._safe_process_single_hole(
                hole_id,
                collar_point,
                collar_z,
                given_depth,
                survey_data,
                interval_data,
                line_geom,
                line_start,
                distance_area,
                buffer_width,
                section_azimuth,
                geol_data,
                drillhole_data,
            )

    def _process_single_hole(
        self,
        hole_id: Any,
        collar_point: QgsPointXY,
        collar_z: float,
        given_depth: float,
        survey_data: list[tuple[float, float, float]],
        intervals: list[tuple[float, float, str]],
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        distance_area: QgsDistanceArea,
        buffer_width: float,
        section_azimuth: float,
    ) -> tuple[list[GeologySegment], DrillholeProjection]:
        """Process a single drillhole's trajectory and intervals."""
        return self.trajectory_engine.process_single_hole(
            hole_id,
            collar_point,
            collar_z,
            given_depth,
            survey_data,
            intervals,
            line_geom,
            line_start,
            distance_area,
            buffer_width,
            section_azimuth,
        )

    def _create_drillhole_result_tuple(
        self,
        hole_id: Any,
        projected_traj: list[tuple],
        hole_geol_data: list[GeologySegment],
    ) -> DrillholeProjection:
        """Create the final result tuple for a drillhole using SpatialMeta."""
        return self.trajectory_engine.create_drillhole_result(
            hole_id, projected_traj, hole_geol_data
        )

    def _safe_process_single_hole(
        self,
        hole_id: Any,
        collar_point: QgsPointXY,
        collar_z: float,
        given_depth: float,
        surveys_map: dict[Any, list[tuple[float, float, float]]],
        intervals_map: dict[Any, list[tuple[float, float, str]]],
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        distance_area: QgsDistanceArea,
        buffer_width: float,
        section_azimuth: float,
        geol_data: list[GeologySegment],
        drillhole_data: list[DrillholeProjection],
    ) -> None:
        """Safely process a single hole with error logging."""
        try:
            hole_geol, hole_drill = self._process_single_hole(
                hole_id=hole_id,
                collar_point=collar_point,
                collar_z=collar_z,
                given_depth=given_depth,
                survey_data=surveys_map.get(hole_id, []),
                intervals=intervals_map.get(hole_id, []),
                line_geom=line_geom,
                line_start=line_start,
                distance_area=distance_area,
                buffer_width=buffer_width,
                section_azimuth=section_azimuth,
            )

            if hole_geol:
                geol_data.extend(hole_geol)
            drillhole_data.append(hole_drill)
        except (ValueError, TypeError, KeyError) as e:
            logger.exception(self.tr("Data error in hole {0}: {1}").format(hole_id, e))
        except SecInterpError as e:
            logger.exception(self.tr("Processing error in hole {0}: {1}").format(hole_id, e))
        except (AttributeError, RuntimeError) as e:
            logger.exception(
                self.tr("Runtime or attribute error processing hole {0}").format(hole_id)
            )
            raise SecInterpError(self.tr("Unexpected processing error: {0}").format(e)) from e
        except Exception:
            logger.exception(
                self.tr("Critical unexpected error processing hole {0}").format(hole_id)
            )
            raise
