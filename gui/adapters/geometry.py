"""Geometry extraction adapter (Extract phase).

Collects the QGIS-dependent geometry helpers that were previously in
``core/utils``. These perform the "Extract" step of the Extract-then-Compute
pattern: creating distance areas, densifying lines, extracting vertices,
buffering/filtering, and sampling raster elevations. The core layer no longer
depends on QGIS for any of these operations.
"""

from __future__ import annotations

import math
from typing import Any

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsDistanceArea,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsRaster,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QCoreApplication

from sec_interp.core.exceptions import GeometryError


def create_distance_area(crs: QgsCoordinateReferenceSystem) -> QgsDistanceArea:
    """Create and configure a QgsDistanceArea object."""
    da = QgsDistanceArea()
    da.setSourceCrs(crs, QgsProject.instance().transformContext())
    da.setEllipsoid(crs.ellipsoidAcronym())
    return da


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
    densified = _densify_line_points(points, interval)
    return QgsGeometry.fromPolylineXY([QgsPointXY(x, y) for x, y in densified])


def _densify_line_points(
    points: list[tuple[float, float]], interval: float
) -> list[tuple[float, float]]:
    """Densify a polyline by inserting intermediate vertices (pure math)."""
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


def sample_point_elevation(raster_layer: QgsRasterLayer, point: Any, band_number: int = 1) -> float:
    """Sample elevation from a raster layer at a 2D coordinate.

    ``point`` may be a ``QgsPointXY`` or a ``(x, y)`` tuple.
    """
    if not raster_layer or not raster_layer.isValid():
        return 0.0

    try:
        pt = point if isinstance(point, QgsPointXY) else QgsPointXY(point[0], point[1])
        ident = raster_layer.dataProvider().identify(
            pt, QgsRaster.IdentifyFormat.IdentifyFormatValue
        )
        if ident.isValid():
            val = ident.results().get(band_number)
            if val is not None:
                return float(val)
    except (AttributeError, ValueError, TypeError):
        pass
    return 0.0


def sample_elevation_along_line(
    geometry: QgsGeometry,
    raster_layer: QgsRasterLayer,
    band_number: int,
    distance_area: QgsDistanceArea,
    reference_point: QgsPointXY | None = None,
    interval: float | None = None,
) -> list[QgsPointXY]:
    """Sample elevation values along a line geometry from a raster layer."""
    if interval is None:
        interval = raster_layer.rasterUnitsPerPixelX()
    try:
        densified_geom = densify_line_by_interval(geometry, interval)
    except (ValueError, RuntimeError):
        densified_geom = geometry

    vertices = get_line_vertices(densified_geom)

    points = []
    current_dist = 0.0
    if reference_point:
        current_dist = distance_area.measureLine(reference_point, vertices[0])

    for i, pt in enumerate(vertices):
        if i > 0:
            current_dist += distance_area.measureLine(vertices[i - 1], pt)

        val, ok = raster_layer.dataProvider().sample(pt, band_number)
        elev = val if ok else 0.0
        points.append(QgsPointXY(current_dist, elev))

    return points


def prepare_profile_context(
    line_lyr: QgsVectorLayer,
) -> tuple[QgsGeometry, QgsPointXY, QgsDistanceArea]:
    """Prepare a common context for profile calculation operations."""
    line_feat = next(line_lyr.getFeatures(), None)
    if not line_feat:
        raise GeometryError("Line layer has no features", {"layer": line_lyr.name()})

    line_geom = line_feat.geometry()
    if not line_geom or line_geom.isNull():
        raise GeometryError("Line geometry is not valid", {"layer": line_lyr.name()})

    try:
        if not get_line_vertices(line_geom):
            raise GeometryError("Line geometry has no vertices", {"layer": line_lyr.name()})
    except ValueError as e:
        raise GeometryError(str(e), {"layer": line_lyr.name()}) from e

    if line_geom.isMultipart():
        line_start = line_geom.asMultiPolyline()[0][0]
    else:
        polyline = line_geom.asPolyline()
        line_start = polyline[0] if polyline else QgsPointXY(0, 0)

    da = create_distance_area(line_lyr.crs())
    return line_geom, line_start, da


def line_length(line_lyr: QgsVectorLayer) -> float | None:
    """Return the length of the first feature's geometry in a line layer."""
    line_feat = next(line_lyr.getFeatures(), None)
    if not line_feat:
        return None
    line_geom = line_feat.geometry()
    if not line_geom or line_geom.isNull():
        return None
    return line_geom.length()
