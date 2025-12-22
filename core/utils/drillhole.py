"""Drillhole Utilities Module.

Calculations for drillhole geometry and projection.
"""

import math
from typing import List, Tuple, Any

from qgis.core import QgsPointXY, QgsGeometry, QgsDistanceArea


def calculate_drillhole_trajectory(
    collar_point: QgsPointXY, 
    collar_z: float, 
    survey_data: List[Tuple[float, float, float]], 
    section_azimuth: float, 
    densify_step: float = 1.0,
    total_depth: float = 0.0
) -> List[Tuple[float, float, float, float, float, float]]:
    """Calculate 3D trajectory of a drillhole using survey data.

    Uses the tangential method for trajectory calculation with densification
    to generate intermediate points for continuous interval projection.

    Args:
        collar_point: QgsPointXY of collar location (X, Y).
        collar_z: Elevation of collar (Z).
        survey_data: List of tuples (depth, azimuth, inclination) sorted by depth.
        section_azimuth: Azimuth of the section line in degrees.
        densify_step: Distance in meters between interpolated points (default 1.0m).
        total_depth: Optional total depth. If greater than last survey depth,
                     trajectory will be extrapolated using last orientation.

    Returns:
        List of tuples (depth, x, y, z, dist_along_section, offset_from_section):
            - depth: Depth along the hole.
            - x, y, z: 3D coordinates.
            - dist_along_section: Distance along the section line (initialized to 0.0).
            - offset_from_section: Perpendicular distance from section line (initialized to 0.0).
    """
    if not survey_data:
        if total_depth > 0:
            # No survey but depth provided: assume vertical hole
            # Add a dummy survey point at surface with vertical inclination (-90)
            survey_data = [(0.0, 0.0, -90.0)]
        else:
            return []

    trajectory = []

    # Start at collar
    x, y, z = collar_point.x(), collar_point.y(), collar_z
    prev_depth = 0.0

    # Add collar point
    trajectory.append((0.0, x, y, z, 0.0, 0.0))

    last_azimuth = 0.0
    last_inclination = 0.0
    last_survey_depth = 0.0

    for depth, azimuth, inclination in survey_data:
        # Keep track of last orientation for extrapolation
        last_azimuth = azimuth
        last_inclination = inclination
        last_survey_depth = depth

        if depth <= prev_depth:
            continue

        # Calculate interval
        interval = depth - prev_depth

        # Convert angles to radians
        azim_rad = math.radians(azimuth)
        
        # Inclination convention: -90° = vertical down, 0° = horizontal
        # We need to convert to standard convention where 0° = vertical down
        # Standard: 0° down, 90° horizontal
        standard_incl_rad = math.radians(90 + inclination)

        # Vertical component (negative because Z decreases downward)
        total_dz = -interval * math.cos(standard_incl_rad)

        # Horizontal components (East, North)
        total_dx = interval * math.sin(standard_incl_rad) * math.sin(azim_rad)
        total_dy = interval * math.sin(standard_incl_rad) * math.cos(azim_rad)

        # Densify: generate intermediate points along this segment
        num_steps = max(1, int(interval / densify_step))

        for i in range(1, num_steps + 1):
            # Calculate fraction of segment
            fraction = i / num_steps

            # Interpolate depth
            interp_depth = prev_depth + interval * fraction

            # Interpolate position (linear interpolation along segment)
            interp_x = x + total_dx * fraction
            interp_y = y + total_dy * fraction
            interp_z = z + total_dz * fraction

            # Add interpolated point
            trajectory.append((interp_depth, interp_x, interp_y, interp_z, 0.0, 0.0))

        # Update position to end of segment
        x += total_dx
        y += total_dy
        z += total_dz

        prev_depth = depth

    # Extrapolate if total_depth is provided and greater than last survey
    if total_depth > last_survey_depth:
        # Calculate interval
        interval = total_depth - last_survey_depth
        
        # Use last known orientation
        azim_rad = math.radians(last_azimuth)
        standard_incl_rad = math.radians(90 + last_inclination)

        # Vertical component
        total_dz = -interval * math.cos(standard_incl_rad)

        # Horizontal components
        total_dx = interval * math.sin(standard_incl_rad) * math.sin(azim_rad)
        total_dy = interval * math.sin(standard_incl_rad) * math.cos(azim_rad)

        # Densify extrapolation
        num_steps = max(1, int(interval / densify_step))

        for i in range(1, num_steps + 1):
            fraction = i / num_steps
            interp_depth = last_survey_depth + interval * fraction
            interp_x = x + total_dx * fraction
            interp_y = y + total_dy * fraction
            interp_z = z + total_dz * fraction
            trajectory.append((interp_depth, interp_x, interp_y, interp_z, 0.0, 0.0))

    return trajectory


def project_trajectory_to_section(
    trajectory: List[Tuple], 
    line_geom: QgsGeometry, 
    line_start: QgsPointXY, 
    distance_area: QgsDistanceArea
) -> List[Tuple[float, float, float, float, float, float]]:
    """Project drillhole trajectory points onto section line.

    Args:
        trajectory: List of (depth, x, y, z, _, _) from `calculate_drillhole_trajectory`.
        line_geom: QgsGeometry of the section line.
        line_start: QgsPointXY of the section line start.
        distance_area: QgsDistanceArea for geodesic measurements.

    Returns:
        List of tuples (depth, x, y, z, dist_along, offset):
            - depth: Original depth.
            - x, y, z: Original 3D coordinates.
            - dist_along: Projected distance along the section line.
            - offset: Perpendicular offset from the section line.
    """
    projected = []

    for depth, x, y, z, _, _ in trajectory:
        point = QgsPointXY(x, y)
        point_geom = QgsGeometry.fromPointXY(point)

        # Find nearest point on line
        nearest_point = line_geom.nearestPoint(point_geom)
        nearest_pt_xy = nearest_point.asPoint()

        # Calculate distance along section
        dist_along = distance_area.measureLine(line_start, nearest_pt_xy)

        # Calculate offset from section
        offset = distance_area.measureLine(point, nearest_pt_xy)

        projected.append((depth, x, y, z, dist_along, offset))

    return projected


def interpolate_intervals_on_trajectory(
    trajectory: List[Tuple], 
    intervals: List[Tuple[float, float, Any]], 
    buffer_width: float
) -> List[Tuple[Any, List[Tuple[float, float]]]]:
    """Interpolate interval attributes along drillhole trajectory.

    Filters and maps geological intervals onto the 3D trajectory points
    that fall within the specified section buffer.

    Args:
        trajectory: List of (depth, x, y, z, dist_along, offset) tuples.
        intervals: List of (from_depth, to_depth, attribute) tuples.
        buffer_width: Maximum perpendicular offset to include a point.

    Returns:
        List of (attribute, list of (dist_along, elevation)) tuples:
            - attribute: The metadata/geology associated with the interval.
            - points: List of (distance, Z) coordinates for rendering.
    """
    geol_segments = []

    for from_depth, to_depth, attribute in intervals:
        # Find trajectory points within this interval
        interval_points = []

        for depth, x, y, z, dist_along, offset in trajectory:
            # Check if point is within interval and buffer
            if from_depth <= depth <= to_depth and offset <= buffer_width:
                interval_points.append((dist_along, z))

        # Add segment if we have points
        if interval_points:
            geol_segments.append((attribute, interval_points))

    return geol_segments
