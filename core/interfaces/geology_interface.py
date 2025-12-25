from abc import ABC, abstractmethod
from typing import Any

from qgis.core import QgsRasterLayer, QgsVectorLayer


class IGeologyService(ABC):
    """Abstract interface for the Geological Profiling Service."""

    @abstractmethod
    def generate_geological_profile(
        self,
        line_lyr: QgsVectorLayer,
        raster_lyr: QgsRasterLayer,
        outcrop_lyr: QgsVectorLayer,
        outcrop_name_field: str,
        band_number: int = 1,
    ) -> Any:
        """Generate geological profile data by intersecting the section line with outcrop polygons.

        Args:
            line_lyr: The cross-section line vector layer.
            raster_lyr: The DEM raster layer for elevation.
            outcrop_lyr: Vector layer containing geological outcrop polygons.
            outcrop_name_field: The field name for geological unit names.
            band_number: Raster band to use for elevation (default: 1).

        Returns:
            GeologyData: List of GeologySegment objects.
        """
        pass
