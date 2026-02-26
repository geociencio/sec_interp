"""Domain entities and basic aliases."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from qgis.core import QgsVectorLayer

# --- Aliases ---

# Profile data types (Initial aliases)
ProfilePoints = list[tuple[float, float]]
GeologyPoints = list[tuple[float, float, str]]
StructurePoints = list[tuple[float, float]]

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

# Point and Geometry Domain Types
Point2D = tuple[float, float]
"""A 2D point represented as (x, y) or (distance, elevation)."""

Point3D = tuple[float, float, float]
"""A 3D point represented as (x, y, z)."""

DomainGeometry = str
"""A geometry represented in WKT (Well-Known Text) format."""

PointList = list[Point2D]
"""List of 2D points."""


# --- Domain Models ---


@dataclass
class StructureMeasurement:
    """Represents a projected structural measurement on the section plane.

    Attributes:
        distance: Horizontal distance from the start of the profile.
        elevation: Elevation (Z) at the projected point.
        apparent_dip: Dip angle relative to the section plane.
        original_dip: True dip measured in the field.
        original_strike: True strike (azimuth) measured in the field.
        attributes: Dictionary containing original feature attributes.

    """

    distance: float
    elevation: float
    apparent_dip: float
    original_dip: float
    original_strike: float
    attributes: dict[str, Any]


@dataclass
class GeologySegment:
    """Represents a geological unit segment along the profile.

    Attributes:
        unit_name: Name of the geological unit.
        geometry_wkt: WKT representation of the segment geometry (optional).
        attributes: Dictionary containing original feature attributes.
        points: Sampled points (distance, elevation) representing the segment boundary.

    """

    unit_name: str
    geometry_wkt: DomainGeometry | None
    attributes: dict[str, Any]
    points: list[Point2D]
    points_3d: list[Point3D] = field(default_factory=list)
    points_3d_projected: list[Point3D] = field(default_factory=list)


@dataclass
class InterpretationPolygon:
    """Represents a 2D digitized interpretation polygon on the section profile.

    Attributes:
        id: Unique identifier for the polygon.
        name: User-defined name for the interpreted unit/feature.
        type: Classification (e.g., 'lithology', 'fault', 'alteration').
        vertices_2d: List of (distance, elevation) points defining the polygon.
        attributes: Metadata for the interpretation.
        color: Visual representation color (HEX).
        created_at: ISO timestamp of creation.

    """

    id: str
    name: str
    type: str
    vertices_2d: list[tuple[float, float]]
    attributes: dict[str, Any] = field(default_factory=dict)
    color: str = "#FF0000"
    created_at: str = ""


@dataclass
class InterpretationPolygon25D:
    """Represents a georeferenced 2.5D interpretation geometry (with M coordinates).

    Attributes:
        id: Inherited identifier.
        name: Inherited name.
        type: Inherited type.
        geometry_wkt: Domain Geometry in WKT format.
        attributes: Inherited and calculated attributes.
        crs_authid: CRS Auth ID (e.g. 'EPSG:4326').

    """

    id: str
    name: str
    type: str
    geometry_wkt: DomainGeometry
    attributes: dict[str, Any]
    crs_authid: str


# Final type aliases for processed data
StructureData = list[StructureMeasurement]
GeologyData = list[GeologySegment]
ProfileData = list[tuple[float, float]]
