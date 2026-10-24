"""Geometry extraction adapter (Extract phase).

Compatibility facade for the QGIS-dependent geometry helpers. The
implementation is split by concern:

- ``geometry_crs``: distance area, CRS transforms and sampling intervals.
- ``geometry_lines``: vertex extraction, densification and segment ranges.
- ``geometry_sampling``: point and line raster sampling.
- ``geometry_stats``: per-cell profile statistics.
- ``geometry_sections``: section-feature resolution and profile context.

These perform the "Extract" step of the Extract-then-Compute pattern; the core
layer stays QGIS-agnostic.
"""

from __future__ import annotations

from qgis.core import QgsPointXY

from sec_interp.gui.adapters.geometry_crs import (
    build_sampling_transform,
    create_distance_area,
    raster_resolution_in_crs,
    resolve_sampling_interval,
)
from sec_interp.gui.adapters.geometry_lines import (
    calculate_segment_range,
    densify_line_by_interval,
    extract_all_vertices,
    extract_lines_from_geometry,
    get_line_vertices,
    section_line_start_point,
)
from sec_interp.gui.adapters.geometry_sampling import (
    sample_elevation_along_line,
    sample_point_elevation,
)
from sec_interp.gui.adapters.geometry_sections import (
    line_length,
    prepare_profile_context,
    resolve_section_feature,
    resolve_section_geometry,
)
from sec_interp.gui.adapters.geometry_stats import (
    ProfileRasterStats,
    profile_raster_statistics,
)

__all__ = [
    "ProfileRasterStats",
    "QgsPointXY",
    "build_sampling_transform",
    "calculate_segment_range",
    "create_distance_area",
    "densify_line_by_interval",
    "extract_all_vertices",
    "extract_lines_from_geometry",
    "get_line_vertices",
    "line_length",
    "prepare_profile_context",
    "profile_raster_statistics",
    "raster_resolution_in_crs",
    "resolve_sampling_interval",
    "resolve_section_feature",
    "resolve_section_geometry",
    "sample_elevation_along_line",
    "sample_point_elevation",
    "section_line_start_point",
]
