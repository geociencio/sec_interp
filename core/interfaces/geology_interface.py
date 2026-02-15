"""Interface for Geology services."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IGeologyService(ABC):
    """Abstract interface for the Geological Profiling Service."""

    @abstractmethod
    def generate_geological_profile(
        self,
        line_data: Any,  # Will be refined to a DTO or specific params
        raster_data: Any,
        outcrop_data: list[dict[str, Any]],
        outcrop_name_field: str,
        band_number: int = 1,
    ) -> Any:
        """Generate geological profile data using detached structures.

        Args:
            line_data: Section line orientation data.
            raster_data: DEM elevation data.
            outcrop_data: List of detached outcrop entities.
            outcrop_name_field: Field name for unit names.
            band_number: Raster band to use.

        Returns:
            GeologyData: List of GeologySegment objects.

        """
        pass
