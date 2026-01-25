from __future__ import annotations

"""Data Transfer Objects for async task inputs."""

from dataclasses import dataclass, field
from typing import Any

from .domain_types import DomainGeometry, Point2D


@dataclass
class GeologyTaskInput:
    """Data Transfer Object for GeologyGenerationTask.

    Contains all necessary data to process geological profiles
    without accessing QGIS layers directly.
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
