# -*- coding: utf-8 -*-
"""
Core Utilities Package

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
from .geometry import (
    create_buffer_geometry,
    filter_features_by_buffer,
    densify_line_by_interval,
    # Helper functions
    create_memory_layer,
    get_line_vertices,
    run_processing_algorithm,
)

# Spatial calculations
from .spatial import (
    calculate_line_azimuth,
    calculate_step_size,
    get_line_start_point,
    create_distance_area,
)

# Sampling and profiling
from .sampling import (
    sample_elevation_along_line,
    prepare_profile_context,
    interpolate_elevation,
)

# Structural data parsing
from .parsing import (
    parse_strike,
    parse_dip,
    cardinal_to_azimuth,
)

# Rendering utilities
from .rendering import (
    calculate_bounds,
    create_coordinate_transform,
    calculate_interval,
)

# I/O utilities
from .io import (
    create_shapefile_writer,
    show_user_message,
)

# Geological calculations
from .geology import (
    calculate_apparent_dip,
)

__all__ = [
    # Geometry
    'create_buffer_geometry',
    'filter_features_by_buffer',
    'densify_line_by_interval',
    # Geometry helpers
    'create_memory_layer',
    'get_line_vertices',
    'run_processing_algorithm',
    # Spatial
    'calculate_line_azimuth',
    'calculate_step_size',
    'get_line_start_point',
    'create_distance_area',
    # Sampling
    'sample_elevation_along_line',
    'prepare_profile_context',
    'interpolate_elevation',
    # Parsing
    'parse_strike',
    'parse_dip',
    'cardinal_to_azimuth',
    # Rendering
    'calculate_bounds',
    'create_coordinate_transform',
    'calculate_interval',
    # I/O
    'create_shapefile_writer',
    'show_user_message',
    # Geology
    'calculate_apparent_dip',
]
