from __future__ import annotations

"""Geometry processing utilities."""

from typing import Any

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsField,
    QgsGeometry,
    QgsVectorLayer,
)

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
        raise ValueError("Geometry is null or invalid")
    return geometry.buffer(distance, segments)


def create_memory_layer(
    layer_name: str,
    layer_type: str,
    crs: QgsCoordinateReferenceSystem,
    fields: list[QgsField],
) -> QgsVectorLayer:
    """Create a temporary memory (scratch) layer.

    Args:
        layer_name: Name for the layer.
        layer_type: QGIS geometry type string (e.g., 'Point', 'LineString').
        crs: Coordinate reference system.
        fields: List of fields for the layer.

    Returns:
        The created memory layer.

    """
    uri = f"{layer_type}?crs={crs.authid()}"
    layer = QgsVectorLayer(uri, layer_name, "memory")
    if not layer.isValid():
        logger.error(f"Failed to create memory layer: {layer_name}")
        return None

    pr = layer.dataProvider()
    pr.addAttributes(fields)
    layer.updateFields()
    return layer


def densify_line_by_interval(geometry: QgsGeometry, interval: float) -> QgsGeometry:
    """Densify a line geometry by a specific distance interval.

    Args:
        geometry: Line geometry to densify.
        interval: Maximum distance between vertices.

    Returns:
        The densified geometry.

    """
    if not geometry or geometry.isNull():
        return QgsGeometry()
    return geometry.densifyByDistance(interval)


def run_geometry_operation(operation: str, *args, **kwargs) -> Any:
    """Wrap generic geometry operations.

    Args:
        operation: Name of the operation to perform.
        *args: Positional arguments for the operation.
        **kwargs: Keyword arguments for the operation.

    Returns:
        Result of the operation.

    """
    # This is a placeholder for more complex logic if needed
    # For now it just logs and performs the op if possible
    logger.debug(f"Running geometry operation: {operation}")
    return None


def calculate_segment_range(
    seg_geom: QgsGeometry,
    line_start: QgsPointXY,
    da: Any,  # QgsDistanceArea
) -> tuple[float, float] | None:
    """Calculate the start and end distance for a segment geometry along the line.

    Args:
        seg_geom: Segment geometry (LineString).
        line_start: Start point of the main section line.
        da: QgsDistanceArea object.

    Returns:
        Tuple of (dist_start, dist_end) or None if invalid.

    """
    from sec_interp.core.utils.geometry_utils.extraction import get_line_vertices

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
    """Convert start/end distances to a list of segment points with interpolated elevations.

    Args:
        dist_start: Start distance of the segment.
        dist_end: End distance of the segment.
        master_grid_dists: Master grid elevation data (dist, point, elev).
        master_profile_data: Master profile topography data (dist, elev).
        tolerance: Tolerance for grid point inclusion.

    Returns:
        List of (distance, elevation) tuples.

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
