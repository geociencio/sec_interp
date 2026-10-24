"""Line-geometry helpers for the Extract phase."""

from __future__ import annotations

import math

from qgis.core import QgsDistanceArea, QgsGeometry, QgsPointXY, QgsWkbTypes
from qgis.PyQt.QtCore import QCoreApplication

from sec_interp.core.utils.geometry_utils.processing import (
    MAX_DENSIFY_POINTS,
    densify_line_points,
)
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def extract_all_vertices(geometry: QgsGeometry) -> list[QgsPointXY]:
    """Extract all vertices from any QGIS geometry type."""
    if not geometry or geometry.isNull():
        return []
    return [QgsPointXY(v) for v in geometry.vertices()]


def get_line_vertices(geometry: QgsGeometry) -> list[QgsPointXY]:
    """Extract vertices specifically from a line or multiline geometry."""
    if not geometry or geometry.isNull():
        raise ValueError(
            QCoreApplication.translate("GeometryExtraction", "Geometry is null or invalid")
        )

    if geometry.type() != QgsWkbTypes.GeometryType.LineGeometry:
        raise ValueError(f"Expected LineGeometry, got {geometry.type()}")

    vertices = extract_all_vertices(geometry)
    if not vertices:
        raise ValueError(
            QCoreApplication.translate("GeometryExtraction", "Line geometry has no vertices")
        )
    return vertices


def extract_lines_from_geometry(geometry: QgsGeometry) -> list[QgsGeometry]:
    """Extract individual LineString geometries from a (possibly Multi) geometry."""
    geometries: list[QgsGeometry] = []
    if not geometry or geometry.isNull():
        return geometries

    if geometry.isMultipart():
        for part in geometry.asGeometryCollection():
            geometries.append(QgsGeometry(part))
    else:
        geometries.append(QgsGeometry(geometry))
    return geometries


def densify_line_by_interval(geometry: QgsGeometry, interval: float) -> QgsGeometry:
    """Densify a line geometry by a specific distance interval."""
    if not geometry or geometry.isNull():
        return QgsGeometry()

    verts = get_line_vertices(geometry)
    points = [(p.x(), p.y()) for p in verts]

    total_length = sum(
        math.hypot(points[i + 1][0] - points[i][0], points[i + 1][1] - points[i][1])
        for i in range(len(points) - 1)
    )
    if interval > 0 and total_length > 0:
        estimated = total_length / interval
        if estimated > MAX_DENSIFY_POINTS:
            logger.warning(
                "Densification capped: interval %.6g is too small for a %.3f-long "
                "line (requested ~%s points, cap %d). Check that the DEM and "
                "section line share a CRS.",
                interval,
                total_length,
                f"{estimated:.3g}",
                MAX_DENSIFY_POINTS,
            )

    densified = _densify_line_points(points, interval)
    return QgsGeometry.fromPolylineXY([QgsPointXY(x, y) for x, y in densified])


def _densify_line_points(
    points: list[tuple[float, float]], interval: float
) -> list[tuple[float, float]]:
    """Densify a polyline by inserting intermediate vertices (pure math).

    Delegates to the core implementation, which caps the number of generated
    vertices to protect against pathological intervals (e.g. a DEM pixel size
    expressed in a different CRS than the section line).
    """
    return densify_line_points(points, interval)


def calculate_segment_range(
    seg_geom: QgsGeometry,
    line_start: QgsPointXY,
    da: QgsDistanceArea,
) -> tuple[float, float] | None:
    """Calculate the start and end distance for a segment geometry along the line."""
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


def section_line_start_point(geometry: QgsGeometry) -> QgsPointXY:
    """Return the first vertex of a line geometry (start of the section)."""
    if not geometry or geometry.isNull():
        return QgsPointXY(0.0, 0.0)
    try:
        if geometry.isMultipart():
            parts = geometry.asMultiPolyline()
            if parts and parts[0]:
                return parts[0][0]
        else:
            polyline = geometry.asPolyline()
            if polyline:
                return polyline[0]
    except (AttributeError, RuntimeError):
        pass
    return QgsPointXY(0.0, 0.0)
