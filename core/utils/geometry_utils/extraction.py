"""Geometry extraction utilities."""

from __future__ import annotations

from qgis.core import QgsGeometry, QgsPointXY, QgsWkbTypes


def extract_all_vertices(geometry: QgsGeometry) -> list[QgsPointXY]:
    """Extract all vertices from any QGIS geometry type.

    Args:
        geometry: The input QGIS geometry.

    Returns:
        list[QgsPointXY]: A flat list of all vertices found in the geometry.
    """
    if not geometry or geometry.isNull():
        return []

    return [QgsPointXY(v) for v in geometry.vertices()]


def get_line_vertices(geometry: QgsGeometry) -> list[QgsPointXY]:
    """Extract vertices specifically from a line or multiline geometry.

    Args:
        geometry: A QGIS geometry of type `LineGeometry`.

    Returns:
        list[QgsPointXY]: A flat list of vertices.

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
