# -*- coding: utf-8 -*-
"""
Spatial Utilities Module

Distance calculations, azimuth, and basic spatial operations.
"""

import math
from qgis.core import (
    QgsDistanceArea,
    QgsProject,
    QgsPointXY,
    QgsGeometry,
    QgsWkbTypes,
)


def calculate_line_azimuth(line_geom: QgsGeometry) -> float:
    """Calculate the azimuth of a line.

    Args:
        line_geom: The line geometry to calculate azimuth for.

    Returns:
        float: Azimuth in degrees (0-360). Returns 0 for points or invalid lines.
    """
    if line_geom.wkbType() == QgsWkbTypes.Point:
        return 0  # Points have no azimuth
    elif line_geom.wkbType() == QgsWkbTypes.LineString:
        line = line_geom.asPolyline()
        if len(line) < 2:
            return 0
        # Calculate azimuth of first segment (from first to second point)
        p1 = line[0]
        p2 = line[1]
        azimuth = math.degrees(math.atan2(p2.x() - p1.x(), p2.y() - p1.y()))
        # Convert to compass bearing (0-360)
        if azimuth < 0:
            azimuth += 360
        return azimuth
    else:
        # For other geometry types, return a default value
        return 0


def calculate_step_size(geom: QgsGeometry, raster_lyr) -> float:
    """Calculate step size based on slope and raster resolution.

    .. deprecated::
        Use densify_line_by_interval() instead for better precision and simpler code.
        This function is kept for backward compatibility but may be removed in future versions.

    Ensures that sampling occurs at approximately one pixel intervals,
    accounting for the slope of the line relative to the raster grid.

    Args:
        geom: The geometry to sample along.
        raster_lyr: The raster layer being sampled.

    Returns:
        float: Calculated step size in map units.
    """
    # Get raster resolution
    res = raster_lyr.rasterUnitsPerPixelX()

    # Calculate step size based on slope to ensure 1 pixel sampling
    dist_step = res
    try:
        if geom.isMultipart():
            parts = geom.asMultiPolyline()
            line_pts = parts[0] if parts else []
        else:
            line_pts = geom.asPolyline()

        if line_pts and len(line_pts) >= 2:
            p1 = line_pts[0]
            p2 = line_pts[-1]
            dx = abs(p2.x() - p1.x())
            dy = abs(p2.y() - p1.y())
            if max(dx, dy) > 0:
                dist_step = geom.length() * res / max(dx, dy)
    except (ValueError, TypeError):
        # Fallback to simple resolution if geometry parsing fails
        pass
    return dist_step


def get_line_start_point(geometry: QgsGeometry) -> QgsPointXY:
    """Helper to get the start point of a line geometry.

    Args:
        geometry: The geometry to get start point from.

    Returns:
        QgsPointXY: The starting point of the line.
    """
    if geometry.isMultipart():
        return geometry.asMultiPolyline()[0][0]
    else:
        return geometry.asPolyline()[0]


def create_distance_area(crs):
    """Helper to create and configure QgsDistanceArea.

    Args:
        crs: The CRS to use for calculations.

    Returns:
        QgsDistanceArea: Configured distance area object.
    """
    da = QgsDistanceArea()
    da.setSourceCrs(crs, QgsProject.instance().transformContext())
    da.setEllipsoid(crs.ellipsoidAcronym())
    return da
