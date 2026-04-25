"""Sampling Utilities Module.

This module provides elevation sampling and profile context preparation tools.
"""

from __future__ import annotations

from qgis.core import (
    QgsDistanceArea,
    QgsGeometry,
    QgsPointXY,
    QgsRasterLayer,
    QgsVectorLayer,
)

from sec_interp.core.exceptions import GeometryError
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def sample_elevation_along_line(
    geometry: QgsGeometry,
    raster_layer: QgsRasterLayer,
    band_number: int,
    distance_area: QgsDistanceArea,
    reference_point: QgsPointXY | None = None,
    interval: float | None = None,
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
        A list of QgsPointXY objects where x is horizontal distance and y is elevation.

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
    current_dist = 0.0

    # Optional: If we have a reference point, calculate its distance to the first vertex
    if reference_point:
        current_dist = distance_area.measureLine(reference_point, vertices[0])

    # Sample elevation at each vertex
    for i, pt in enumerate(vertices):
        # Calculate incremental distance
        if i > 0:
            # For densified points, Euclidean distance is sufficient and MUCH faster
            # than geodesic measureLine calls, especially since they are very close.
            segment_len = distance_area.measureLine(vertices[i - 1], pt)
            current_dist += segment_len

        val, ok = raster_layer.dataProvider().sample(pt, band_number)
        elev = val if ok else 0.0
        points.append(QgsPointXY(current_dist, elev))

    return points


def prepare_profile_context(
    line_lyr: QgsVectorLayer,
) -> tuple[QgsGeometry, QgsPointXY, QgsDistanceArea]:
    """Prepare a common context for profile calculation operations.

    Args:
        line_lyr: The cross-section line vector layer.

    Returns:
        A tuple containing:
            - line_geom: The geometry of the section line.
            - line_start: The starting point of the line.
            - distance_area: Fully configured geodesic distance object.

    Raises:
        ValueError: If the input layer is empty or has invalid geometry.

    """
    from .spatial import create_distance_area, get_line_start_point

    line_feat = next(line_lyr.getFeatures(), None)
    if not line_feat:
        raise GeometryError("Line layer has no features", {"layer": line_lyr.name()})

    line_geom = line_feat.geometry()
    if not line_geom or line_geom.isNull():
        raise GeometryError("Line geometry is not valid", {"layer": line_lyr.name()})

    from .geometry import get_line_vertices

    try:
        if not get_line_vertices(line_geom):
            raise GeometryError("Line geometry has no vertices", {"layer": line_lyr.name()})
    except ValueError as e:
        raise GeometryError(str(e), {"layer": line_lyr.name()}) from e

    line_start = get_line_start_point(line_geom)
    da = create_distance_area(line_lyr.crs())

    return line_geom, line_start, da


def interpolate_elevation(topo_data: list[tuple[float, float]], distance: float) -> float:
    """Interpolate elevation at a given distance along the topography profile.

    Uses linear interpolation between the two nearest sampled points.

    Args:
        topo_data: List of (distance, elevation) tuples.
        distance: Horizontal distance along the section.

    Returns:
        The interpolated elevation value (Z) at that distance.

    """
    if not topo_data:
        return 0.0

    import bisect

    # Extract distances for bisect
    distances = [pt[0] for pt in topo_data]

    # Find the insertion point
    idx = bisect.bisect_left(distances, distance)

    if idx == 0:
        return topo_data[0][1]
    if idx >= len(topo_data):
        return topo_data[-1][1]

    # Interpolate
    dist1, elev1 = topo_data[idx - 1]
    dist2, elev2 = topo_data[idx]

    if dist2 == dist1:
        return elev1

    ratio = (distance - dist1) / (dist2 - dist1)
    return elev1 + (elev2 - elev1) * ratio


def sample_point_elevation(
    raster_layer: QgsRasterLayer, point: QgsPointXY, band_number: int = 1
) -> float:
    """Sample elevation from a raster layer at a specific 2D coordinate.

    Args:
        raster_layer: The DEM raster layer.
        point: The coordinate point (X, Y) to sample.
        band_number: The raster band index (default 1).

    Returns:
        The sampled elevation value (Z) or 0.0 if the point is out of bounds.

    """
    if not raster_layer or not raster_layer.isValid():
        return 0.0

    try:
        # identify() is more robust across different raster types than sample()
        # for single point access when speed is not the primary constraint.
        from qgis.core import QgsRaster

        ident = raster_layer.dataProvider().identify(point, QgsRaster.IdentifyFormatValue)
        if ident.isValid():
            val = ident.results().get(band_number)
            if val is not None:
                return float(val)
    except (AttributeError, ValueError, TypeError):
        pass
    return 0.0
