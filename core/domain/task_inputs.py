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
class DrillholeTaskInput:
    """Data Transfer Object for DrillholeGenerationTask.

    Encapsulates all data required to project and process drillholes
    in a background thread without accessing QGIS API objects.

    Attributes:
        line_geometry_wkt: Section geometry in WKT.
        line_start_x: Start vertex X.
        line_start_y: Start vertex Y.
        line_crs_authid: CRS of the section line.
        section_azimuth: Azimuth orientation in degrees.
        buffer_width: Maximum horizontal projection buffer.
        collar_id_field: ID field name.
        use_geometry: Whether to use geometric coordinates for collars.
        collar_x_field: Fallback X field name.
        collar_y_field: Fallback Y field name.
        collar_z_field: Collar elevation field.
        collar_depth_field: Total depth field.
        collar_data: List of detached features.
        survey_data: Dictionary mapping hole IDs to survey readings.
        interval_data: Dictionary mapping hole IDs to geological logs.
        pre_sampled_z: Dictionary of pre-calculated collar elevations.

    """

    # Section Line Info
    line_geometry_wkt: DomainGeometry
    line_start_x: float
    line_start_y: float
    line_crs_authid: str
    section_azimuth: float

    # Parameters
    buffer_width: float
    collar_id_field: str
    use_geometry: bool
    collar_x_field: str
    collar_y_field: str
    collar_z_field: str
    collar_depth_field: str

    # Detached Data
    collar_data: list[dict[str, Any]]  # List of dicts with attrs and geometry
    survey_data: dict[Any, list[tuple[float, float, float]]]  # hole_id -> [(depth, azim, incl)]
    interval_data: dict[Any, list[tuple[float, float, str]]]  # hole_id -> [(from, to, lith)]

    # Optional DEM data for fallback elevation
    pre_sampled_z: dict[Any, float] = field(default_factory=dict)
