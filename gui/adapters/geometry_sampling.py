"""Raster point/line sampling helpers for the Extract phase."""

from __future__ import annotations

from typing import Any

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsDistanceArea,
    QgsGeometry,
    QgsPointXY,
    QgsRaster,
    QgsRasterLayer,
)

from sec_interp.gui.adapters.geometry_crs import (
    build_sampling_transform,
    resolve_sampling_interval,
)
from sec_interp.gui.adapters.geometry_lines import (
    densify_line_by_interval,
    get_line_vertices,
)


def sample_point_elevation(
    raster_layer: QgsRasterLayer,
    point: Any,
    band_number: int = 1,
    source_crs: QgsCoordinateReferenceSystem | None = None,
) -> float:
    """Sample elevation from a raster layer at a 2D coordinate.

    ``point`` may be a ``QgsPointXY`` or a ``(x, y)`` tuple. When ``source_crs``
    differs from the raster CRS, the point is reprojected before sampling.
    """
    if not raster_layer or not raster_layer.isValid():
        return 0.0

    try:
        pt = point if isinstance(point, QgsPointXY) else QgsPointXY(point[0], point[1])
        transform = build_sampling_transform(source_crs, raster_layer)
        if transform is not None:
            pt = transform.transform(pt)
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
        interval = resolve_sampling_interval(geometry, raster_layer, line_crs)

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
