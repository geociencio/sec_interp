from __future__ import annotations

"""Core Utilities Package.

Organized by functionality:
- drillhole: Trajectory and projection calculations (pure)
- geology: Geological calculations (pure)
- io: File I/O and vector writing
- parsing: Structural data parsing (pure)
- rendering: Visualization utilities (pure)
- sampling: Elevation interpolation (pure)
- spatial: Distance and azimuth calculations (pure)
"""

# Drillhole trajectory and projection
from .drillhole import (
    calculate_drillhole_trajectory,
    interpolate_intervals_on_trajectory,
    project_trajectory_to_section,
)

# Geological calculations
from .geology import (
    calculate_apparent_dip,
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

# Elevation interpolation (pure)
from .sampling import (
    interpolate_elevation,
)

# Spatial calculations (pure)
from .spatial import (
    calculate_line_azimuth,
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
    # Parsing
    "cardinal_to_azimuth",
    # Rendering
    "create_coordinate_transform",
    # I/O
    "create_shapefile_writer",
    # Parsing
    "extract_feature_attributes",
    # Sampling
    "interpolate_elevation",
    # Drillhole
    "interpolate_intervals_on_trajectory",
    "parse_dip",
    "parse_strike",
    "project_trajectory_to_section",
]
