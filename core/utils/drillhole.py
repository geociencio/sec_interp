"""Drillhole Utilities Module.

Calculations for drillhole geometry and projection.
"""

from __future__ import annotations

import math
from typing import Any

from qgis.core import QgsDistanceArea, QgsGeometry, QgsPointXY

# Constants for tolerance and validation
DEPTH_TOLERANCE = 1e-5
MIN_INTERVAL_POINTS = 2


def calculate_drillhole_trajectory(
    collar_point: Any,
    collar_z: float,
    survey_data: list[tuple[float, float, float]],
    section_azimuth: float,
    densify_step: float = 1.0,
    total_depth: float = 0.0,
) -> list[tuple[float, float, float, float, float, float]]:
    """Calculate the 3D trajectory of a drillhole using survey data.

    Calculates X, Y, Z positions along the hole using minimum curvature or
    tangential approximation based on survey readings (depth, azimuth, dip).

    Args:
        collar_point: Starting point (QgsPointXY or tuple).
        collar_z: Starting elevation.
        survey_data: List of (depth, azimuth, inclination) tuples.
        section_azimuth: Azimuth of the section line (for relative calcs).
        densify_step: Distance between interpolated points in meters.
        total_depth: Total depth of the hole.

    Returns:
        List of (depth, x, y, z, 0.0, 0.0) trajectory points.

    """
    if not survey_data:
        if total_depth <= 0:
            return []
        survey_data = [(0.0, 0.0, -90.0)]

    trajectory = []
    x, y = _initialize_start_point(collar_point)

    z = collar_z
    prev_depth = 0.0
    trajectory.append((0.0, x, y, z, 0.0, 0.0))

    last_azim = 0.0
    last_incl = 0.0
    last_survey_depth = 0.0

    for depth, azimuth, inclination in survey_data:
        x, y, z, prev_depth = _process_survey_segment(
            depth, azimuth, inclination, x, y, z, prev_depth, densify_step, trajectory
        )
        last_azim, last_incl, last_survey_depth = azimuth, inclination, depth

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


def _initialize_start_point(collar_point: Any) -> tuple[float, float]:
    """Extract X and Y coordinates from a point-like object."""
    try:
        x = collar_point.x() if hasattr(collar_point, "x") else collar_point[0]
        y = collar_point.y() if hasattr(collar_point, "y") else collar_point[1]
        return float(x), float(y)
    except (AttributeError, TypeError, IndexError):
        return 0.0, 0.0


def _process_survey_segment(
    depth: float,
    azimuth: float,
    inclination: float,
    x: float,
    y: float,
    z: float,
    prev_depth: float,
    densify_step: float,
    trajectory: list,
) -> tuple[float, float, float, float]:
    """Process a single survey segment and update coordinates."""
    if depth <= prev_depth:
        return x, y, z, prev_depth

    interval = depth - prev_depth
    dx, dy, dz = _calculate_segment_delta(interval, azimuth, inclination)

    trajectory.extend(
        _calculate_segment_points(x, y, z, prev_depth, dx, dy, dz, interval, densify_step)
    )

    return x + dx, y + dy, z + dz, depth


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
    """Project drillhole trajectory points onto the section line.

    Calculates the 2D projection (distance along section) and the offset
    (distance from section) for each point in a 3D trajectory.

    Args:
        trajectory: List of 3D trajectory points (depth, x, y, z, ...).
        line_geom: Section line geometry.
        line_start: Reference start point for distance calculation.
        distance_area: Distance calculation utility.

    Returns:
        List of (depth, x, y, z, dist_along, offset, proj_x, proj_y) tuples.

    """
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
) -> list[
    tuple[
        Any,
        list[tuple[float, float]],
        list[tuple[float, float, float]],
        list[tuple[float, float, float]],
    ]
]:
    """Interpolate interval attributes along drillhole trajectory.

    Ensures that even short intervals have at least two points by interpolating
    at the exact from/to depths on the trajectory segments.

    Args:
        trajectory: List of (depth, x, y, z, dist_along, offset, nx, ny) tuples.
        intervals: List of (from_depth, to_depth, attribute) tuples.
        buffer_width: Maximum perpendicular offset to include a point.

    Returns:
        List of tuples (attribute, points_2d, points_3d, points_3d_proj).

    """
    geol_segments = []
    if not trajectory or not intervals:
        return geol_segments

    # Sort trajectory by depth in case it's not (though it should be)
    traj = sorted(trajectory, key=lambda p: p[0])

    for from_val, to_val, attr in intervals:
        points_in_interval = _get_points_for_interval(traj, from_val, to_val, buffer_width)

        if len(points_in_interval) >= MIN_INTERVAL_POINTS:
            p_2d = [(p[4], p[3]) for p in points_in_interval]
            p_3d = [(p[1], p[2], p[3]) for p in points_in_interval]
            p_3d_proj = [(p[6], p[7], p[3]) for p in points_in_interval]
            geol_segments.append((attr, p_2d, p_3d, p_3d_proj))

    return geol_segments


def _get_points_for_interval(
    traj: list[tuple], from_val: float, to_val: float, buffer_width: float
) -> list[tuple]:
    """Get points belonging to a specific interval."""
    points = []

    # 1. Add interpolated point at from_val
    p_from = _interpolate_at_depth(traj, from_val)
    if p_from and p_from[5] <= buffer_width:
        points.append(p_from)

    # 2. Add all trajectory points strictly inside (from_val, to_val)
    for p in traj:
        if from_val < p[0] < to_val and p[5] <= buffer_width:
            points.append(p)

    # 3. Add interpolated point at to_val
    p_to = _interpolate_at_depth(traj, to_val)
    if p_to and p_to[5] <= buffer_width:
        # Avoid duplicate if to_val == from_val or coinciding with a traj point
        if not points or abs(points[-1][0] - p_to[0]) > DEPTH_TOLERANCE:
            points.append(p_to)

    return points


def _interpolate_at_depth(trajectory: list[tuple], target_depth: float) -> tuple | None:
    """Interpolate a trajectory point at a specific depth."""
    if not trajectory:
        return None

    # Exact match or boundary checks
    if abs(trajectory[0][0] - target_depth) < DEPTH_TOLERANCE:
        return trajectory[0]
    if abs(trajectory[-1][0] - target_depth) < DEPTH_TOLERANCE:
        return trajectory[-1]
    if target_depth < trajectory[0][0] or target_depth > trajectory[-1][0]:
        return None

    # Find the segment [p1, p2] containing target_depth
    for i in range(len(trajectory) - 1):
        p1, p2 = trajectory[i], trajectory[i + 1]
        if p1[0] <= target_depth <= p2[0]:
            d1, d2 = p1[0], p2[0]
            if abs(d2 - d1) < DEPTH_TOLERANCE:
                return p1
            frac = (target_depth - d1) / (d2 - d1)
            # Interpolate all fields (depth, x, y, z, dist, offset, nx, ny)
            return tuple(p1[j] + (p2[j] - p1[j]) * frac for j in range(len(p1)))

    return None
