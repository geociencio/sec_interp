from __future__ import annotations


"""Sampling Utilities Module.

Elevation sampling and profile context preparation.
"""

from typing import Any, Optional

from qgis.core import (
    QgsDistanceArea,
    QgsGeometry,
    QgsPointXY,
    QgsRasterLayer,
    QgsVectorLayer,
)

from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


def sample_elevation_along_line(
    geometry: QgsGeometry,
    raster_layer: QgsRasterLayer,
    band_number: int,
    distance_area: QgsDistanceArea,
    reference_point: Optional[QgsPointXY] = None,
    interval: Optional[float] = None,
) -> list[QgsPointXY]:
    """Sample elevation values along a line geometry from a raster layer.

    Densifies the line at raster resolution and samples the elevation at each vertex.

    Args:
        geometry: The line geometry to sample along.
        raster_layer: The source DEM raster layer.
        band_number: The raster band index to sample.
        distance_area: Object for geodesic distance calculations.
        reference_point: Optional start point for distance measurements.
        interval: Optional sampling interval. If None, uses raster resolution.

    Returns:
        List[QgsPointXY]: A list where x is distance along section and y is elevation.
    """
    from .geometry import densify_line_by_interval

    # Use raster resolution if no interval provided
    if interval is None:
        interval = raster_layer.rasterUnitsPerPixelX()
    try:
        densified_geom = densify_line_by_interval(geometry, interval)
    except (ValueError, RuntimeError):
        # Fallback to original geometry if densification fails
        densified_geom = geometry

    # Get vertices from densified geometry using helper
    from .geometry import get_line_vertices

    vertices = get_line_vertices(densified_geom)

    points = []
    start_pt = reference_point if reference_point else vertices[0]

    # Sample elevation at each vertex
    for pt in vertices:
        # Calculate distance for X axis
        if reference_point:
            dist_from_start = distance_area.measureLine(reference_point, pt)
        else:
            dist_from_start = distance_area.measureLine(start_pt, pt)

        val, ok = raster_layer.dataProvider().sample(pt, band_number)
        elev = val if ok else 0.0
        points.append(QgsPointXY(dist_from_start, elev))

    return points


def prepare_profile_context(
    line_lyr: QgsVectorLayer,
) -> tuple[QgsGeometry, QgsPointXY, QgsDistanceArea]:
    """Prepare a common context for profile calculation operations.

    Args:
        line_lyr: The cross-section line vector layer.

    Returns:
        Tuple: (line_geom, line_start, distance_area)
            - line_geom (QgsGeometry): The geometry of the section line.
            - line_start (QgsPointXY): The starting point of the line.
            - distance_area (QgsDistanceArea): Fully configured distance object.

    Raises:
        ValueError: If the input layer is empty or has invalid geometry.
    """
    from .spatial import create_distance_area, get_line_start_point

    line_feat = next(line_lyr.getFeatures(), None)
    if not line_feat:
        raise ValueError("Line layer has no features")

    line_geom = line_feat.geometry()
    if not line_geom or line_geom.isNull():
        raise ValueError("Line geometry is not valid")

    line_start = get_line_start_point(line_geom)
    da = create_distance_area(line_lyr.crs())

    return line_geom, line_start, da


def interpolate_elevation(topo_data: list, distance: float) -> float:
    """Interpolate elevation at given distance.

    Args:
        topo_data: List of (distance, elevation) tuples.
        distance: Distance at which to interpolate elevation.

    Returns:
        float: Interpolated elevation value.
    """
    if not topo_data:
        return 0

    # Find nearest points
    for i in range(len(topo_data) - 1):
        dist1, elev1 = topo_data[i]
        dist2, elev2 = topo_data[i + 1]
        # Interpolate elevation
        if dist1 <= distance <= dist2:
            ratio = (distance - dist1) / (dist2 - dist1)
            return elev1 + (elev2 - elev1) * ratio
    # Return last elevation if distance is beyond last point
    return topo_data[-1][1] if topo_data else 0
