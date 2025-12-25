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

# Geometry operations
# Geological calculations
from .drillhole import (
    calculate_drillhole_trajectory,
    interpolate_intervals_on_trajectory,
    project_trajectory_to_section,
)
from .geology import (
    calculate_apparent_dip,
)
from .geometry import (
    create_buffer_geometry,
    # Helper functions
    create_memory_layer,
    densify_line_by_interval,
    filter_features_by_buffer,
    get_line_vertices,
    run_processing_algorithm,
)

# I/O utilities
from .io import (
    create_shapefile_writer,
)

# Structural data parsing
from .parsing import (
    cardinal_to_azimuth,
    parse_dip,
    parse_strike,
)

# Rendering utilities
from .rendering import (
    calculate_bounds,
    calculate_interval,
    create_coordinate_transform,
)

# Sampling and profiling
from .sampling import (
    interpolate_elevation,
    prepare_profile_context,
    sample_elevation_along_line,
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
    "cardinal_to_azimuth",
    # Geometry
    "create_buffer_geometry",
    "create_coordinate_transform",
    "create_distance_area",
    # Geometry helpers
    "create_memory_layer",
    # I/O
    "create_shapefile_writer",
    "densify_line_by_interval",
    "filter_features_by_buffer",
    "get_line_start_point",
    "get_line_vertices",
    "interpolate_elevation",
    "interpolate_intervals_on_trajectory",
    "parse_dip",
    # Parsing
    "parse_strike",
    "prepare_profile_context",
    "project_trajectory_to_section",
    "run_processing_algorithm",
    # Sampling
    "sample_elevation_along_line",
]
