from __future__ import annotations

"""Geometry extraction utilities."""

from qgis.core import QgsGeometry, QgsPointXY, QgsWkbTypes


def extract_all_vertices(geometry: QgsGeometry) -> list[QgsPointXY]:
    """Extract all vertices from any QGIS geometry type.

    Args:
        geometry: The input QGIS geometry.

    Returns:
        A flat list of all vertices found in the geometry.

    """
    if not geometry or geometry.isNull():
        return []

    return [QgsPointXY(v) for v in geometry.vertices()]


def get_line_vertices(geometry: QgsGeometry) -> list[QgsPointXY]:
    """Extract vertices specifically from a line or multiline geometry.

    Args:
        geometry: A QGIS geometry of type `LineGeometry`.

    Returns:
        A flat list of vertices.

    Raises:
        ValueError: If the geometry is null, not a line, or contains no vertices.

    """
    if not geometry or geometry.isNull():
        raise ValueError("Geometry is null or invalid")

    if geometry.type() != QgsWkbTypes.LineGeometry:
        raise ValueError(f"Expected LineGeometry, got {geometry.type()}")

    vertices = extract_all_vertices(geometry)
    if not vertices:
        raise ValueError("Line geometry has no vertices")

    return vertices


def extract_lines_from_geometry(geometry: QgsGeometry) -> list[QgsGeometry]:
    """Extract individual LineString geometries from a (possibly Multi) geometry.

    Args:
        geometry: Input geometry (LineString or MultiLineString).

    Returns:
        List of single LineString geometries.

    """
    geometries = []
    if not geometry or geometry.isNull():
        return geometries

    # MultiLineString handling
    if geometry.isMultipart():
        for part in geometry.asGeometryCollection():
            geometries.append(QgsGeometry(part))
    else:
        geometries.append(QgsGeometry(geometry))
    return geometries
