"""CRS, distance-area and sampling-interval helpers for geometry extraction."""

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
    QgsRasterLayer,
)

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

_DEFAULT_MAX_SAMPLES = 5_000
"""Fallback number of samples when the DEM resolution cannot be resolved."""  # no-i18n


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


def resolve_sampling_interval(
    geometry: QgsGeometry,
    raster_layer: QgsRasterLayer,
    line_crs: QgsCoordinateReferenceSystem | None,
) -> float:
    """Resolve a safe sampling interval for a raster profile.

    Prefers the DEM pixel size expressed in the line's CRS. Falls back to a
    length-derived interval when the resolution cannot be resolved, and always
    returns a strictly positive value.

    Args:
        geometry: The section line geometry (in ``line_crs`` units).
        raster_layer: The DEM/raster layer.
        line_crs: CRS of the section line (``None`` if unknown).

    Returns:
        A positive sampling interval in ``line_crs`` units.

    """
    interval = raster_resolution_in_crs(raster_layer, line_crs)
    if interval is None or interval <= 0:
        interval = _fallback_interval(geometry)
    if interval is None or interval <= 0:
        interval = 1.0
    return interval
