"""Best-effort detection of mislabelled CRS from layer extent plausibility.

A wrong CRS label cannot be read from metadata (QGIS trusts the declaration),
but it is often visible in the coordinate values. These rules are intentionally
conservative: they only fire when the declared CRS is contradicted by an extent
(or raster pixel size) that could not plausibly belong to it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sec_interp.core.validation.layer_metadata import LayerMetadata

if TYPE_CHECKING:
    from .project_validator import ValidationParams

# Valid geographic coordinate bounds (degrees).
GEOGRAPHIC_X_LIMIT = 180.0
GEOGRAPHIC_Y_LIMIT = 90.0
# A projected extent spanning less than this (map units) is not believable.
MIN_PROJECTED_SPAN = 1.0
# A projected pixel smaller than this (map units) is not believable.
MIN_PROJECTED_PIXEL = 1e-3


def configured_layer_metadata(params: ValidationParams) -> list[LayerMetadata]:
    """Return the detached metadata of every configured layer."""
    candidates = (
        params.raster_layer,
        params.line_layer,
        params.outcrop_layer,
        params.struct_layer,
        params.collar_layer,
        params.survey_layer,
        params.interval_layer,
    )
    return [m for m in candidates if m is not None]


def _extent(metadata: LayerMetadata) -> tuple[float, float, float, float] | None:
    """Return the populated extent tuple, or None when incomplete."""
    xmin = metadata.extent_xmin
    ymin = metadata.extent_ymin
    xmax = metadata.extent_xmax
    ymax = metadata.extent_ymax
    if xmin is None or ymin is None or xmax is None or ymax is None:
        return None
    return xmin, ymin, xmax, ymax


def implausible_crs_reason(metadata: LayerMetadata | None) -> str:
    """Return a human-readable reason if the CRS looks mislabelled, else ``""``.

    Args:
        metadata: Detached layer metadata (extent populated by the GUI extractor).

    Returns:
        A message describing the mismatch, or an empty string when the CRS is
        plausible or cannot be judged.

    """
    if metadata is None or metadata.crs_is_geographic is None:
        return ""
    extent = _extent(metadata)
    if extent is None:
        return ""
    xmin, ymin, xmax, ymax = extent

    span_x = abs(xmax - xmin)
    span_y = abs(ymax - ymin)
    if span_x == 0 and span_y == 0:
        return ""

    max_x = max(abs(xmin), abs(xmax))
    max_y = max(abs(ymin), abs(ymax))
    within_geographic_bounds = max_x <= GEOGRAPHIC_X_LIMIT and max_y <= GEOGRAPHIC_Y_LIMIT

    if metadata.crs_is_geographic:
        if max_x > GEOGRAPHIC_X_LIMIT or max_y > GEOGRAPHIC_Y_LIMIT:
            return (
                f"Layer '{metadata.name}' is declared with a geographic CRS but its "
                f"coordinates exceed lon/lat bounds (x up to {max_x:.3g}, y up to "
                f"{max_y:.3g}); the data may actually be projected."
            )
        return ""

    tiny_span = max(span_x, span_y) < MIN_PROJECTED_SPAN
    tiny_pixel = (
        metadata.pixel_size_x is not None and 0 < metadata.pixel_size_x < MIN_PROJECTED_PIXEL
    )
    if within_geographic_bounds and (tiny_span or tiny_pixel):
        return (
            f"Layer '{metadata.name}' is declared with a projected CRS but its extent "
            f"({xmin:.4g}, {ymin:.4g} : {xmax:.4g}, {ymax:.4g}) looks like degrees; "
            "the data may be geographic (e.g. EPSG:4326) with a wrong CRS label. "
            "Fix it with 'Assign Projection' (not 'Reproject')."
        )
    return ""
