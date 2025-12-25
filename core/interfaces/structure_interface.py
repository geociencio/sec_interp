from abc import ABC, abstractmethod
from typing import Any
from qgis.core import QgsRasterLayer, QgsVectorLayer


class IStructureService(ABC):
    """Abstract interface for the Structural Projection Service."""

    @abstractmethod
    def project_structures(
        self,
        line_lyr: QgsVectorLayer,
        raster_lyr: QgsRasterLayer,
        struct_lyr: QgsVectorLayer,
        buffer_m: int,
        line_az: float,
        dip_field: str,
        strike_field: str,
        band_number: int = 1,
    ) -> Any:
        """Project structural measurements onto the cross-section plane.

        Args:
            line_lyr: The cross-section line vector layer.
            raster_lyr: The DEM raster layer for elevation sampling.
            struct_lyr: Vector layer containing structural measurements.
            buffer_m: Search buffer distance in meters.
            line_az: Azimuth of the section line in degrees.
            dip_field: Name of the field containing dip values.
            strike_field: Name of the field containing strike values.
            band_number: Raster band to use for elevation (default: 1).

        Returns:
            StructureData: List of StructureMeasurement objects.
        """
        pass
