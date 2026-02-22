"""Interface for Drillhole services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IDrillholeService(ABC):
    """Abstract interface for the Drillhole Processing Service."""

    @abstractmethod
    def project_collars(
        self,
        collar_data: list[dict[str, Any]],
        line_data: Any,
        distance_area: Any,
        buffer_width: float,
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        collar_z_field: str,
        collar_depth_field: str,
        pre_sampled_z: dict[Any, float] | None = None,
    ) -> list[tuple]:
        """Project collar points onto section line using detached data.

        Args:
            collar_data: List of detached collar entities (with geometry/attrs).
            line_data: Section line orientation data.
            distance_area: Calculation tool (or domain equivalent).
            buffer_width: Search buffer distance in meters.
            collar_id_field: Field name for unique drillhole ID.
            use_geometry: Whether to use geometry for coordinates.
            collar_x_field: Field for X.
            collar_y_field: Field for Y.
            collar_z_field: Field for elevation.
            collar_depth_field: Field for total depth.
            pre_sampled_z: Optional map of pre-sampled elevations.

        Returns:
            A list of tuples (hole_id, dist_along, z, offset, total_depth).

        """
        pass

    @abstractmethod
    def process_intervals(
        self,
        collar_points: list[tuple],
        collar_data: list[dict[str, Any]],
        survey_data: dict[Any, list[tuple]],
        interval_data: dict[Any, list[tuple]],
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        line_data: Any,
        distance_area: Any,
        buffer_width: float,
        section_azimuth: float,
        survey_fields: dict[str, str],
        interval_fields: dict[str, str],
    ) -> tuple[list, list]:
        """Process interval data using detached data structures.

        Args:
            collar_points: List of projected collar tuples.
            collar_data: List of detached collar entities.
            survey_data: Map of hole_id to list of survey tuples.
            interval_data: Map of hole_id to list of interval tuples.
            collar_id_field: Field name for ID.
            use_geometry: Use geometry for coordinates.
            collar_x_field: Field for X.
            collar_y_field: Field for Y.
            line_data: Line orientation data.
            distance_area: Distance calculation object.
            buffer_width: Buffer width.
            section_azimuth: Section azimuth.
            survey_fields: Survey field mapping.
            interval_fields: Interval field mapping.

        Returns:
            A tuple containing (geol_data, drillhole_data).

        """
        pass
