from __future__ import annotations

"""Geometry Utilities Facade.

Spatial geometry operations using QGIS native algorithms.
This module now serves as a facade for modularized sub-submodules.
"""

from .geometry_utils.extraction import (
    extract_all_vertices,
    get_line_vertices,
)
from .geometry_utils.filtering import (
    filter_features_by_buffer,
)
from .geometry_utils.processing import (
    create_buffer_geometry,
    create_memory_layer,
    densify_line_by_interval,
    run_geometry_operation,
)

__all__ = [
    "create_buffer_geometry",
    "create_memory_layer",
    "densify_line_by_interval",
    "extract_all_vertices",
    "filter_features_by_buffer",
    "get_line_vertices",
    "run_geometry_operation",
    "run_geometry_operation",
]
