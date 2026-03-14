"""Data Transfer Objects for async task inputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .entities import DomainGeometry, Point2D


@dataclass
class GeologyTaskInput:
    """Data Transfer Object for GeologyGenerationTask.

    Contains all necessary data to process geological profiles
    without accessing QGIS layers directly.

    Attributes:
        line_geometry_wkt: Section geometry in WKT format.
        line_start_x: X coordinate of section start vertex.
        line_start_y: Y coordinate of section start vertex.
        crs_authid: Authority ID for the CRS (e.g., 'EPSG:4326').
        master_profile_data: Sampled topography elevations.
        master_grid_dists: Grid distances for point sampling.
        outcrop_data: Detached outcrop features (geometries and attrs).
        outcrop_name_field: Name of the field containing unit info.
        tolerance: Distance tolerance for intersection sampling.

    """

    line_geometry_wkt: DomainGeometry
    line_start_x: float
    line_start_y: float
    crs_authid: str
    master_profile_data: list[Point2D]
    master_grid_dists: list[tuple[float, Point2D, float]]
    outcrop_data: list[dict[str, Any]]  # List of dicts with 'wkt', 'attrs', 'unit_name'
    outcrop_name_field: str
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
    survey_data: dict[
        Any, list[tuple[float, float, float]]
    ]  # hole_id -> [(depth, azim, incl)]
    interval_data: dict[
        Any, list[tuple[float, float, str]]
    ]  # hole_id -> [(from, to, lith)]

    # Optional DEM data for fallback elevation
    pre_sampled_z: dict[Any, float] = field(default_factory=dict)
