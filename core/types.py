"""Common type aliases for SecInterp plugin.

This module defines type aliases used throughout the codebase to improve
type hint readability and maintainability.
"""

from typing import Any, Optional

from qgis.core import QgsPointXY, QgsRasterLayer, QgsVectorLayer


# Profile data types
ProfileData = list[tuple[float, float]]
"""List of (distance, elevation) tuples representing a topographic profile."""

GeologyData = list[tuple[float, float, str]]
"""List of (distance, elevation, unit_name) tuples representing geological intersections."""

StructureData = list[tuple[float, float]]
"""List of (distance, apparent_dip) tuples representing projected structural measurements."""

# Layer collections
LayerDict = dict[str, QgsVectorLayer]
"""Dictionary mapping layer names to QgsVectorLayer objects."""

# Settings and configuration
SettingsDict = dict[str, Any]
"""Dictionary of plugin settings and configuration values."""

ExportSettings = dict[str, Any]
"""Dictionary of export configuration parameters."""

# Validation results
ValidationResult = tuple[bool, str]
"""Tuple of (is_valid, error_message) from validation functions."""

# Point data
PointList = list[QgsPointXY]
"""List of QgsPointXY objects."""
