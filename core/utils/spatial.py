"""Spatial Utilities and layer querying Module.

Distance calculations, azimuth, and basic spatial operations.
"""

from __future__ import annotations

import math

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsDistanceArea,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
)


def extract_line_points(geometry: QgsGeometry) -> list[tuple[float, float]]:
    """Extract (x, y) tuples from a line geometry.

    Handles singlepart and multipart lines. Returns an empty list for
    non-line geometries or geometries without vertices.

    Args:
        geometry: The QGIS line geometry.

    Returns:
        List of (x, y) tuples.

    """
    if geometry.isMultipart():
        parts = geometry.asMultiPolyline()
        polyline = parts[0] if parts else []
    else:
        polyline = geometry.asPolyline()
    return [(p.x(), p.y()) for p in polyline]


def calculate_line_azimuth(points: list[tuple[float, float]]) -> float:
    """Calculate the azimuth (compass bearing) of a line.

    Calculates the azimuth based on the first two points of the line.
    Returns 0 for points or single-vertex lines.

    Args:
        points: List of (x, y) tuples defining the line.

    Returns:
        Azimuth in degrees (0-360).

    """
    MIN_REQUIRED_POINTS = 2
    if len(points) < MIN_REQUIRED_POINTS:
        return 0

    p1 = points[0]
    p2 = points[1]
    azimuth = math.degrees(math.atan2(p2[0] - p1[0], p2[1] - p1[1]))
    if azimuth < 0:
        azimuth += 360
    return azimuth


def get_line_start_point(geometry: QgsGeometry) -> QgsPointXY:
    """Get the start point of a line geometry.

    Handles both singlepart and multipart line geometries.

    Args:
        geometry: The line geometry.

    Returns:
        The first vertex of the first part of the geometry.

    """
    if geometry.isMultipart():
        return geometry.asMultiPolyline()[0][0]

    polyline = geometry.asPolyline()
    if not polyline:
        from sec_interp.core.exceptions import GeometryError

        raise GeometryError("Polyline has no vertices")
    return polyline[0]


def create_distance_area(crs: QgsCoordinateReferenceSystem) -> QgsDistanceArea:
    """Create and configure a QgsDistanceArea object.

    Configures the distance area with the provided CRS, project transform context,
    and associated ellipsoid for geodesic calculations.

    Args:
        crs: The Coordinate Reference System to use.

    Returns:
        The configured distance calculation object.

    """
    da = QgsDistanceArea()
    da.setSourceCrs(crs, QgsProject.instance().transformContext())
    da.setEllipsoid(crs.ellipsoidAcronym())
    return da
