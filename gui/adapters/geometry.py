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
    QgsCoordinateTransform,
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
from sec_interp.core.utils.geometry_utils.processing import (
    MAX_DENSIFY_POINTS,
    densify_line_points,
)
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

_DEFAULT_MAX_SAMPLES = 5_000
"""Fallback number of samples when the DEM resolution cannot be resolved."""


def create_distance_area(crs: QgsCoordinateReferenceSystem) -> QgsDistanceArea:
    """Create and configure a QgsDistanceArea object."""
    da = QgsDistanceArea()
    da.setSourceCrs(crs, QgsProject.instance().transformContext())
    da.setEllipsoid(crs.ellipsoidAcronym())
    return da


def _crs_equal(crs_a: Any, crs_b: Any) -> bool:
    """Compare two CRS objects defensively (mock/QGIS safe)."""
    if crs_a is None or crs_b is None:
        return False
    try:
        return bool(crs_a == crs_b)
    except (AttributeError, RuntimeError, TypeError):
        return False


def build_sampling_transform(
    line_crs: QgsCoordinateReferenceSystem | None,
    raster_layer: QgsRasterLayer,
) -> QgsCoordinateTransform | None:
    """Build a transform from the line CRS to the raster CRS, or ``None``.

    A transform is only needed when both CRSs are known and differ. Across
    different CRSs, sampling with raw layer coordinates reads the wrong pixels.

    Args:
        line_crs: CRS of the section line (``None`` if unknown).
        raster_layer: The DEM/raster layer being sampled.

    Returns:
        A ``QgsCoordinateTransform`` (line -> raster) or ``None`` when the CRSs
        match, are unknown, or the transform cannot be created.

    """
    if line_crs is None:
        return None
    try:
        raster_crs = raster_layer.crs()
    except (AttributeError, RuntimeError):
        return None
    if raster_crs is None or _crs_equal(line_crs, raster_crs):
        return None
    try:
        return QgsCoordinateTransform(
            line_crs, raster_crs, QgsProject.instance().transformContext()
        )
    except (AttributeError, RuntimeError, TypeError, ValueError):
        logger.warning(
            "Could not build line->raster CRS transform; sampling in line CRS.",
            exc_info=True,
        )
        return None


def raster_resolution_in_crs(
    raster_layer: QgsRasterLayer,
    target_crs: QgsCoordinateReferenceSystem | None,
) -> float | None:
    """Return the raster pixel size expressed in ``target_crs`` units.

    ``rasterUnitsPerPixelX()`` is expressed in the raster's own CRS. When the
    section line lives in a different CRS (on-the-fly reprojection), using that
    value directly as a sampling interval is meaningless and can densify the
    line into millions of vertices. This transforms a one-pixel-long segment
    from the raster CRS into ``target_crs`` to recover a usable interval.

    Args:
        raster_layer: The DEM/raster layer.
        target_crs: CRS in which to express the resolution (``None`` to return
            the raw value).

    Returns:
        Pixel size in ``target_crs`` units, or ``None`` if it cannot be
        determined.

    """
    try:
        res = raster_layer.rasterUnitsPerPixelX()
    except (AttributeError, RuntimeError):
        return None
    if res is None or res <= 0:
        return None

    if target_crs is None:
        return res

    try:
        raster_crs = raster_layer.crs()
    except (AttributeError, RuntimeError):
        return res
    if raster_crs is None or _crs_equal(raster_crs, target_crs):
        return res

    try:
        xform = QgsCoordinateTransform(
            raster_crs, target_crs, QgsProject.instance().transformContext()
        )
        center = raster_layer.extent().center()
        p_start = xform.transform(QgsPointXY(center.x(), center.y()))
        p_end = xform.transform(QgsPointXY(center.x() + res, center.y()))
        size = math.hypot(p_end.x() - p_start.x(), p_end.y() - p_start.y())
        return size if size > 0 else None
    except (AttributeError, RuntimeError, TypeError, ValueError):
        logger.warning(
            "Could not express raster resolution in the target CRS.",
            exc_info=True,
        )
        return None


def _fallback_interval(geometry: QgsGeometry) -> float | None:
    """Derive a bounded sampling interval from the geometry's own length."""
    try:
        length = float(geometry.length())
    except (AttributeError, RuntimeError, TypeError):
        return None
    if length <= 0:
        return None
    return length / _DEFAULT_MAX_SAMPLES


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
    """Sample elevation values along a line geometry from a raster layer.

    The sampling interval is the raster pixel size expressed in the section
    line's CRS. When the line and raster CRSs differ (on-the-fly reprojection),
    the pixel size is transformed before use and each sample point is
    reprojected into the raster CRS.
    """
    line_crs: QgsCoordinateReferenceSystem | None
    try:
        line_crs = distance_area.sourceCrs()
    except (AttributeError, RuntimeError):
        line_crs = None

    to_raster = build_sampling_transform(line_crs, raster_layer)

    if interval is None or interval <= 0:
        interval = raster_resolution_in_crs(raster_layer, line_crs)
    if interval is None or interval <= 0:
        interval = _fallback_interval(geometry)
    if interval is None or interval <= 0:
        interval = 1.0

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

        sample_pt = to_raster.transform(pt) if to_raster else pt
        val, ok = raster_layer.dataProvider().sample(sample_pt, band_number)
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
