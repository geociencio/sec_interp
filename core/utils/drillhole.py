from __future__ import annotations

"""Drillhole Utilities Module.

Calculations for drillhole geometry and projection.
"""

import math
from typing import Any

from qgis.core import QgsDistanceArea, QgsGeometry, QgsPointXY


def calculate_drillhole_trajectory(
    collar_point: Any,
    collar_z: float,
    survey_data: list[tuple[float, float, float]],
    section_azimuth: float,
    densify_step: float = 1.0,
    total_depth: float = 0.0,
) -> list[tuple[float, float, float, float, float, float]]:
    """Calculate 3D trajectory of a drillhole using survey data."""
    if not survey_data:
        if total_depth <= 0:
            return []
        survey_data = [(0.0, 0.0, -90.0)]

    trajectory = []
    try:
        x = collar_point.x() if hasattr(collar_point, "x") else collar_point[0]
        y = collar_point.y() if hasattr(collar_point, "y") else collar_point[1]
    except (AttributeError, TypeError, IndexError):
        x, y = 0.0, 0.0

    z = collar_z
    prev_depth = 0.0
    trajectory.append((0.0, x, y, z, 0.0, 0.0))

    last_azim = 0.0
    last_incl = 0.0
    last_survey_depth = 0.0

    for depth, azimuth, inclination in survey_data:
        last_azim, last_incl, last_survey_depth = azimuth, inclination, depth
        if depth <= prev_depth:
            continue

        interval = depth - prev_depth
        total_dx, total_dy, total_dz = _calculate_segment_delta(interval, azimuth, inclination)

        trajectory.extend(
            _calculate_segment_points(
                x,
                y,
                z,
                prev_depth,
                total_dx,
                total_dy,
                total_dz,
                interval,
                densify_step,
            )
        )

        x, y, z = x + total_dx, y + total_dy, z + total_dz
        prev_depth = depth

    if total_depth > last_survey_depth:
        trajectory.extend(
            _extrapolate_trajectory(
                x,
                y,
                z,
                last_survey_depth,
                total_depth,
                last_azim,
                last_incl,
                densify_step,
            )
        )

    return trajectory


def _calculate_segment_delta(
    interval: float, azimuth: float, inclination: float
) -> tuple[float, float, float]:
    """Calculate X, Y, Z deltas for a survey segment."""
    azim_rad = math.radians(azimuth)
    standard_incl_rad = math.radians(90 + inclination)
    dz = -interval * math.cos(standard_incl_rad)
    dx = interval * math.sin(standard_incl_rad) * math.sin(azim_rad)
    dy = interval * math.sin(standard_incl_rad) * math.cos(azim_rad)
    return dx, dy, dz


def _calculate_segment_points(
    x: float,
    y: float,
    z: float,
    prev_depth: float,
    dx: float,
    dy: float,
    dz: float,
    interval: float,
    step: float,
) -> list[tuple[float, float, float, float, float, float]]:
    """Generate densified points for a single segment."""
    points = []
    num_steps = max(1, int(interval / step))
    for i in range(1, num_steps + 1):
        frac = i / num_steps
        points.append(
            (
                prev_depth + interval * frac,
                x + dx * frac,
                y + dy * frac,
                z + dz * frac,
                0.0,
                0.0,
            )
        )
    return points


def _extrapolate_trajectory(
    x: float,
    y: float,
    z: float,
    last_depth: float,
    total_depth: float,
    azim: float,
    incl: float,
    step: float,
) -> list[tuple[float, float, float, float, float, float]]:
    """Extrapolate trajectory from last known survey point."""
    interval = total_depth - last_depth
    dx, dy, dz = _calculate_segment_delta(interval, azim, incl)
    return _calculate_segment_points(x, y, z, last_depth, dx, dy, dz, interval, step)


def project_trajectory_to_section(
    trajectory: list[tuple],
    line_geom: QgsGeometry,
    line_start: Any,  # Point2D or QgsPointXY
    distance_area: QgsDistanceArea,
) -> list[tuple[float, float, float, float, float, float, float, float]]:
    """Project drillhole trajectory points onto section line."""
    projected = []

    # Ensure line_start is QgsPointXY
    start_pt = line_start if hasattr(line_start, "x") else QgsPointXY(line_start[0], line_start[1])

    for depth, x, y, z, _, _ in trajectory:
        point = QgsPointXY(x, y)
        point_geom = QgsGeometry.fromPointXY(point)

        # Find nearest point on line
        nearest_point = line_geom.nearestPoint(point_geom)
        nearest_pt_xy = nearest_point.asPoint()

        # Calculate distance along section
        dist_along = distance_area.measureLine(start_pt, nearest_pt_xy)

        # Calculate offset from section
        offset = distance_area.measureLine(point, nearest_pt_xy)

        projected.append((depth, x, y, z, dist_along, offset, nearest_pt_xy.x(), nearest_pt_xy.y()))

    return projected


def interpolate_intervals_on_trajectory(
    trajectory: list[tuple],
    intervals: list[tuple[float, float, Any]],
    buffer_width: float,
) -> list[tuple[Any, list[tuple[float, float]], list[tuple[float, float, float]]]]:
    """Interpolate interval attributes along drillhole trajectory.

    Filters and maps geological intervals onto the 3D trajectory points
    that fall within the specified section buffer.

    Args:
        trajectory: List of (depth, x, y, z, dist_along, offset) tuples.
        intervals: List of (from_depth, to_depth, attribute) tuples.
        buffer_width: Maximum perpendicular offset to include a point.

    Returns:
        List of tuples containing:
            - attribute: The metadata/geology associated with the interval.
            - points_2d: List of (distance, elevation) coordinates for rendering.
            - points_3d: List of (x, y, z) original coordinates for 3D export.

    """
    geol_segments = []

    for from_depth, to_depth, attribute in intervals:
        # Find trajectory points within this interval
        interval_points_2d = []
        interval_points_3d = []
        interval_points_3d_proj = []

        for depth, x, y, z, dist_along, offset, nx, ny in trajectory:
            # Check if point is within interval and buffer
            if from_depth <= depth <= to_depth and offset <= buffer_width:
                interval_points_2d.append((dist_along, z))
                interval_points_3d.append((x, y, z))
                interval_points_3d_proj.append((nx, ny, z))

        # Add segment if we have points
        if interval_points_2d:
            geol_segments.append(
                (
                    attribute,
                    interval_points_2d,
                    interval_points_3d,
                    interval_points_3d_proj,
                )
            )

    return geol_segments
