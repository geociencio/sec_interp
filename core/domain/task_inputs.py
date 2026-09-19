"""Data Transfer Objects for async task inputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .entities import DomainGeometry, Point2D


@dataclass
class OutcropSegments:
    """Detached intersection segments for a single outcrop feature.

    Attributes:
        unit_name: Geological unit name.
        attributes: Original feature attributes.
        segments: List of ``(dist_start, dist_end, wkt)`` tuples, one per
            intersection segment along the section line.

    """

    unit_name: str
    attributes: dict[str, Any]
    segments: list[tuple[float, float, DomainGeometry]]


@dataclass
class GeologyContext:
    """Fully-detached geology data (Extract output) for pure computation.

    Produced by the GUI ``GeologyExtractor`` adapter and consumed by the
    QGIS-agnostic ``GeologyService``. Contains no live QGIS objects.

    Attributes:
        master_profile_data: Sampled topography elevations ``(dist, elev)``.
        master_grid_dists: Grid ``(dist, (x, y), elev)`` for interpolation.
        outcrops: Detached outcrop intersection segments.
        tolerance: Distance tolerance for intersection sampling.

    """

    master_profile_data: list[Point2D]
    master_grid_dists: list[tuple[float, Point2D, float]]
    outcrops: list[OutcropSegments]
    tolerance: float = 0.001


@dataclass
class DrillholeContext:
    """Fully-detached drillhole data (Extract output) for pure computation.

    Produced by the GUI ``DrillholeExtractor`` adapter and consumed by the
    QGIS-agnostic ``DrillholeService``. Contains no live QGIS objects.

    Attributes:
        line_points: Section line vertices as ``(x, y)`` tuples.
        section_azimuth: Section orientation in degrees.
        buffer_width: Maximum horizontal projection buffer.
        collar_id_field: ID field name.
        collar_z_field: Collar elevation field.
        collar_depth_field: Total depth field.
        collar_data: Detached collars (``{"id", "point", "attributes"}``).
        survey_data: hole_id -> [(depth, azim, incl)].
        interval_data: hole_id -> [(from, to, lith)].
        pre_sampled_z: hole_id -> pre-sampled collar elevation.

    """

    line_points: list[Point2D]
    section_azimuth: float
    buffer_width: float
    collar_id_field: str
    collar_z_field: str
    collar_depth_field: str
    collar_data: list[dict[str, Any]]
    survey_data: dict[Any, list[tuple[float, float, float]]]
    interval_data: dict[Any, list[tuple[float, float, str]]]
    pre_sampled_z: dict[Any, float] = field(default_factory=dict)
