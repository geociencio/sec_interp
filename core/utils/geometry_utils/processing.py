"""Geometry processing utilities."""

from __future__ import annotations

import math
from typing import Any

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsDistanceArea,
    QgsGeometry,
    QgsPointXY,
)
from qgis.PyQt.QtCore import QCoreApplication

from sec_interp.core.utils.geometry_utils.extraction import get_line_vertices
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def create_buffer_geometry(
    geometry: QgsGeometry,
    crs: QgsCoordinateReferenceSystem,
    distance: float,
    segments: int = 5,
) -> QgsGeometry:
    """Create a buffer around a geometry.

    Args:
        geometry: Input geometry.
        crs: Coordinate Reference System of the geometry.
        distance: Buffer distance in layer units.
        segments: Number of segments for the buffer approximation.

    Returns:
        The buffered geometry.

    """
    if not geometry or geometry.isNull():
        raise ValueError(
            QCoreApplication.translate("GeometryProcessing", "Geometry is null or invalid")
        )
    return geometry.buffer(distance, segments)


def densify_line_points(
    points: list[tuple[float, float]], interval: float
) -> list[tuple[float, float]]:
    """Densify a polyline by inserting intermediate vertices.

    Ensures no segment is longer than ``interval``. Returns the input unchanged
    if it has fewer than two points or the interval is non-positive.

    Args:
        points: List of (x, y) tuples.
        interval: Maximum segment length (in the same units as the points).

    Returns:
        Densified list of (x, y) tuples.

    """
    if not points or interval <= 0:
        return points

    result = [points[0]]
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]

        seg_len = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        if seg_len == 0:
            continue

        num_segments = max(1, math.ceil(seg_len / interval))
        for j in range(1, num_segments):
            t = j / num_segments
            result.append((p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1])))
        result.append(p2)

    return result


def densify_line_by_interval(geometry: QgsGeometry, interval: float) -> QgsGeometry:
    """Densify a line geometry by a specific distance interval.

    Adds intermediate vertices to ensure segments are no longer than the interval.

    Args:
        geometry: Line geometry to densify.
        interval: Maximum distance between vertices (in CRS units).

    Returns:
        The densified QgsGeometry.

    """
    if not geometry or geometry.isNull():
        return QgsGeometry()

    verts = get_line_vertices(geometry)
    points = [(p.x(), p.y()) for p in verts]
    densified = densify_line_points(points, interval)
    return QgsGeometry.fromPolylineXY([QgsPointXY(x, y) for x, y in densified])


def calculate_segment_range(
    seg_geom: QgsGeometry,
    line_start: QgsPointXY,
    da: QgsDistanceArea,
) -> tuple[float, float] | None:
    """Calculate the start and end distance for a segment geometry along the line.

    Args:
        seg_geom: Segment geometry (LineString).
        line_start: Start point of the main section line.
        da: QgsDistanceArea object.

    Returns:
        Tuple of (dist_start, dist_end) or None if invalid.

    """
    try:
        verts = get_line_vertices(seg_geom)
        if not verts:
            return None

        start_pt, end_pt = verts[0], verts[-1]
        dist_start = da.measureLine(line_start, start_pt)
        dist_end = da.measureLine(line_start, end_pt)

        if dist_start > dist_end:
            dist_start, dist_end = dist_end, dist_start

        return dist_start, dist_end
    except ValueError:
        return None


def interpolate_segment_points(
    dist_start: float,
    dist_end: float,
    master_grid_dists: list[tuple[float, Any, float]],  # (dist, point, elev)
    master_profile_data: list[tuple[float, float]],  # (dist, elev)
    tolerance: float,
) -> list[tuple[float, float]]:
    """Convert boundary distances into a list of points with sampled elevations.

    Includes the start/end points and any intermediate grid points from the
    master profile that fall within the specified distance range.

    Args:
        dist_start: Start distance along section.
        dist_end: End distance along section.
        master_grid_dists: Full grid of coordinates and elevations.
        master_profile_data: Topography profile (dist, elevation).
        tolerance: Distance tolerance for grid inclusions.

    Returns:
        List of (distance, elevation) tuples defining the segment profile.

    """
    from sec_interp.core.utils.sampling import interpolate_elevation

    # Get Inner Grid Points
    inner_points = [
        (d, e) for d, _, e in master_grid_dists if dist_start + tolerance < d < dist_end - tolerance
    ]

    # Interpolate Boundary Elevations
    elev_start = interpolate_elevation(master_profile_data, dist_start)
    elev_end = interpolate_elevation(master_profile_data, dist_end)

    return [(dist_start, elev_start), *inner_points, (dist_end, elev_end)]
