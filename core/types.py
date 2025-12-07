# -*- coding: utf-8 -*-
"""
Common type aliases for SecInterp plugin.

This module defines type aliases used throughout the codebase to improve
type hint readability and maintainability.
"""

from typing import List, Tuple, Dict, Any, Optional
from qgis.core import QgsVectorLayer, QgsRasterLayer, QgsPointXY

# Profile data types
ProfileData = List[Tuple[float, float]]
"""List of (distance, elevation) tuples representing a topographic profile."""

GeologyData = List[Tuple[float, float, str]]
"""List of (distance, elevation, unit_name) tuples representing geological intersections."""

StructureData = List[Tuple[float, float]]
"""List of (distance, apparent_dip) tuples representing projected structural measurements."""

# Layer collections
LayerDict = Dict[str, QgsVectorLayer]
"""Dictionary mapping layer names to QgsVectorLayer objects."""

# Settings and configuration
SettingsDict = Dict[str, Any]
"""Dictionary of plugin settings and configuration values."""

ExportSettings = Dict[str, Any]
"""Dictionary of export configuration parameters."""

# Validation results
ValidationResult = Tuple[bool, str]
"""Tuple of (is_valid, error_message) from validation functions."""

# Point data
PointList = List[QgsPointXY]
"""List of QgsPointXY objects."""
