"""Core module for SecInterp plugin.

Contains business logic, algorithms, and utilities.
"""

from .utils import (
    calculate_line_azimuth,
    calculate_step_size,
    sample_elevation_along_line,
)
from .validation import (
    validate_field_exists,
    validate_field_type,
    validate_layer_exists,
    validate_layer_geometry,
    validate_layer_has_features,
)


__all__ = [
    "calculate_line_azimuth",
    "calculate_step_size",
    "sample_elevation_along_line",
    "validate_field_exists",
    "validate_field_type",
    "validate_layer_exists",
    "validate_layer_geometry",
    "validate_layer_has_features",
]
