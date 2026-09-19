"""Interface for Structure services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any


class IStructureService(ABC):
    """Abstract interface for the Structural Projection Service."""

    @abstractmethod
    def project_structures(
        self,
        line_points: list[tuple[float, float]],
        struct_data: list[dict[str, Any]],
        elevation_sampler: Callable[[float, float], float],
        line_az: float,
        dip_field: str,
        strike_field: str,
    ) -> Any:
        """Project detached structural measurements onto the section plane.

        Args:
            line_points: Section line vertices as ``(x, y)`` tuples.
            struct_data: List of detached structures (``{"point", "attributes"}``).
            elevation_sampler: Callable sampling elevation at ``(x, y)``.
            line_az: Azimuth of the section line.
            dip_field: Name of the dip field.
            strike_field: Name of the strike field.

        Returns:
            StructureData: List of StructureMeasurement objects.

        """
        pass
