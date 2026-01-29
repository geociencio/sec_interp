from __future__ import annotations

"""Core Utilities Package.

Organized by functionality:
- geometry: Spatial geometry operations
- spatial: Distance and azimuth calculations
- sampling: Elevation sampling and profiling
- parsing: Structural data parsing
- rendering: Visualization utilities
- io: File I/O and user messages
- geology: Geological calculations
"""

# Drillhole trajetory and projection
from .drillhole import (
    calculate_drillhole_trajectory,
    interpolate_intervals_on_trajectory,
    project_trajectory_to_section,
)

# Geological calculations
from .geology import (
    calculate_apparent_dip,
)

# Geometry operations and helpers
from .geometry import (
    create_buffer_geometry,
    create_memory_layer,
    densify_line_by_interval,
    filter_features_by_buffer,
    get_line_vertices,
)

# I/O utilities
from .io import (
    create_shapefile_writer,
)

# Structural data parsing and attribute extraction
from .parsing import (
    cardinal_to_azimuth,
    extract_feature_attributes,
    parse_dip,
    parse_strike,
)

# Rendering/Visualization utilities
from .rendering import (
    calculate_bounds,
    calculate_interval,
    create_coordinate_transform,
)

# Elevation Sampling and profiling
from .sampling import (
    interpolate_elevation,
    prepare_profile_context,
    sample_elevation_along_line,
    sample_point_elevation,
)

# Spatial calculations
from .spatial import (
    calculate_line_azimuth,
    calculate_step_size,
    create_distance_area,
    get_line_start_point,
)

__all__ = [
    # Geology
    "calculate_apparent_dip",
    # Rendering
    "calculate_bounds",
    # Drillhole
    "calculate_drillhole_trajectory",
    "calculate_interval",
    # Spatial
    "calculate_line_azimuth",
    "calculate_step_size",
    # Parsing
    "cardinal_to_azimuth",
    # Geometry
    "create_buffer_geometry",
    "create_coordinate_transform",
    "create_distance_area",
    "create_memory_layer",
    # I/O
    "create_shapefile_writer",
    "densify_line_by_interval",
    "extract_feature_attributes",
    "filter_features_by_buffer",
    "get_line_start_point",
    "get_line_vertices",
    # Sampling
    "interpolate_elevation",
    "interpolate_intervals_on_trajectory",
    "parse_dip",
    "parse_strike",
    "prepare_profile_context",
    "project_trajectory_to_section",
    "sample_elevation_along_line",
    "sample_point_elevation",
]
