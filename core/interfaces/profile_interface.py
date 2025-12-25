from abc import ABC, abstractmethod
from typing import Any, Optional
from qgis.core import QgsRasterLayer, QgsVectorLayer


class IProfileService(ABC):
    """Abstract interface for the Topographic Profile Service."""

    @abstractmethod
    def generate_topographic_profile(
        self,
        line_lyr: QgsVectorLayer,
        raster_lyr: QgsRasterLayer,
        band_number: int = 1,
        interval: Optional[float] = None,
    ) -> Any:
        """Generate topographic profile data by sampling elevation along a section line.

        Args:
            line_lyr: The cross-section line vector layer.
            raster_lyr: The DEM raster layer for elevation.
            band_number: Raster band to sample (default: 1).
            interval: Optional sampling interval. If None, uses raster resolution.

        Returns:
            ProfileData: List of (distance, elevation) tuples.
        """
        pass
