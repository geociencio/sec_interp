"""Engine for calculating and projecting drillhole trajectories."""

from __future__ import annotations

from typing import Any

from qgis.core import QgsDistanceArea, QgsGeometry, QgsPointXY

from sec_interp.core import utils as scu
from sec_interp.core.domain import DrillholeProjection, GeologySegment, SpatialMeta
from sec_interp.core.services.drillhole.interval_processor import IntervalProcessor
from sec_interp.core.services.drillhole.survey_processor import SurveyProcessor


class TrajectoryEngine:
    """Orchestrates trajectory calculation and projection for individual drillholes."""

    def __init__(self) -> None:
        """Initialize the trajectory engine."""
        self.survey_processor = SurveyProcessor()
        self.interval_processor = IntervalProcessor()

    def process_single_hole(
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
        """Core logic for a single hole processing."""
        # 1. Determine Final Depth
        final_depth = self.survey_processor.determine_final_depth(
            given_depth, survey_data, intervals
        )

        # 2. Trajectory and Projection
        trajectory = scu.calculate_drillhole_trajectory(
            collar_point,
            collar_z,
            survey_data,
            section_azimuth,
            total_depth=final_depth,
        )
        projected_traj = scu.project_trajectory_to_section(
            trajectory, line_geom, line_start, distance_area
        )

        # 3. Interpolate Intervals
        hole_geol_data = self.interval_processor.interpolate_hole_intervals(
            projected_traj, intervals, buffer_width
        )

        # 4. Generate results
        hole_proj = self.create_drillhole_result(hole_id, projected_traj, hole_geol_data)

        return hole_geol_data, hole_proj

    def create_drillhole_result(
        self,
        hole_id: Any,
        projected_traj: list[tuple],
        hole_geol_data: list[GeologySegment],
        collar_proj: Any = None,
    ) -> DrillholeProjection:
        """Create the final DrillholeProjection for a drillhole."""
        spatial_points = []
        for p in projected_traj:
            spatial_points.append(
                SpatialMeta(
                    hole_id=str(hole_id),
                    dist_along=p[4],
                    offset=p[5],
                    z=p[3],
                    x_3d=p[1],
                    y_3d=p[2],
                    x_proj=p[6],
                    y_proj=p[7],
                )
            )

        # Basic projection info

        # Basic projection info from collar_proj or first point
        if collar_proj:
            dist = collar_proj.distance
            elev = collar_proj.elevation
            offset = collar_proj.offset
            depth = collar_proj.total_depth
        elif spatial_points:
            dist = spatial_points[0].dist_along
            elev = spatial_points[0].z
            offset = spatial_points[0].offset
            depth = 0.0  # Or infer from points if available
        else:
            # Fallback for completely empty trajectory and no collar projection
            dist = 0.0
            elev = 0.0
            offset = 0.0
            depth = 0.0

        return DrillholeProjection(
            hole_id=str(hole_id),
            distance=dist,
            elevation=elev,
            offset=offset,
            total_depth=depth,
            points_3d=spatial_points,
            segments=hole_geol_data,
        )
