"""Raster-grid statistics for the profile over the DEM."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from qgis.core import (
    QgsCoordinateTransform,
    QgsDistanceArea,
    QgsGeometry,
    QgsPointXY,
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


@dataclass(frozen=True)
class ProfileRasterStats:
    """Read-only elevation statistics of the section over the DEM.

    Attributes:
        count: Number of distinct raster cells sampled.
        minimum: Minimum elevation (m).
        maximum: Maximum elevation (m).
        mean: Mean elevation (m).
        resolution: Sampling interval in line-CRS units (raster pixel size).
        length: Total sampled distance along the line (line-CRS units).

    """

    count: int
    minimum: float
    maximum: float
    mean: float
    resolution: float
    length: float


def _raster_grid(
    raster_layer: QgsRasterLayer,
) -> tuple[Any, float, float] | None:
    """Return ``(extent, pixel_x, pixel_y)`` or None when unavailable."""
    try:
        extent = raster_layer.extent()
        res_x = float(raster_layer.rasterUnitsPerPixelX())
        res_y = float(raster_layer.rasterUnitsPerPixelY())
    except (AttributeError, TypeError, RuntimeError):
        return None
    if res_x <= 0 or res_y <= 0:
        return None
    return extent, res_x, res_y


def _sample_unique_cells(
    vertices: list[QgsPointXY],
    to_raster: QgsCoordinateTransform | None,
    provider: Any,
    band_number: int,
    grid: tuple[Any, float, float],
    distance_area: QgsDistanceArea,
) -> tuple[list[float], float]:
    """Sample one elevation per raster cell along the densified vertices."""
    extent, res_x, res_y = grid
    last_cell: tuple[int, int] | None = None
    values: list[float] = []
    current_dist = 0.0

    for i, pt in enumerate(vertices):
        if i > 0:
            current_dist += distance_area.measureLine(vertices[i - 1], pt)

        sample_pt = to_raster.transform(pt) if to_raster else pt
        cell = (
            math.floor((sample_pt.x() - extent.xMinimum()) / res_x),
            math.floor((extent.yMaximum() - sample_pt.y()) / res_y),
        )
        if cell == last_cell:
            continue
        last_cell = cell

        val, ok = provider.sample(sample_pt, band_number)
        if ok and val is not None:
            values.append(float(val))

    return values, current_dist


def profile_raster_statistics(
    line_geom: QgsGeometry,
    raster_layer: QgsRasterLayer,
    band_number: int,
    distance_area: QgsDistanceArea,
) -> ProfileRasterStats | None:
    """Compute min/max/mean elevation over unique DEM cells along the line.

    Densifies at the CRS-aware raster resolution, reprojects each sample into
    the raster CRS and collapses samples that fall in the same pixel cell (so
    repeated cells from the densification do not bias min/max/mean). Returns
    ``None`` when there is nothing usable to sample.
    """
    if not line_geom or not raster_layer or not raster_layer.isValid():
        return None

    try:
        line_crs = distance_area.sourceCrs()
    except (AttributeError, RuntimeError):
        line_crs = None

    resolution = resolve_sampling_interval(line_geom, raster_layer, line_crs)
    if resolution <= 0:
        return None

    grid = _raster_grid(raster_layer)
    if grid is None:
        return None

    try:
        densified = densify_line_by_interval(line_geom, resolution)
        vertices = get_line_vertices(densified)
    except (ValueError, RuntimeError):
        return None

    values, length = _sample_unique_cells(
        vertices,
        build_sampling_transform(line_crs, raster_layer),
        raster_layer.dataProvider(),
        band_number,
        grid,
        distance_area,
    )
    if not values:
        return None

    return ProfileRasterStats(
        count=len(values),
        minimum=min(values),
        maximum=max(values),
        mean=sum(values) / len(values),
        resolution=resolution,
        length=length,
    )
