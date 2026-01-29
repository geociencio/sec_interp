from __future__ import annotations

"""Interface for Structure services."""

from abc import ABC, abstractmethod
from typing import Any

from qgis.core import QgsRasterLayer, QgsVectorLayer


class IStructureService(ABC):
    """Abstract interface for the Structural Projection Service."""

    @abstractmethod
    def detach_structures(
        self,
        struct_lyr: QgsVectorLayer,
        line_geom: QgsGeometry,
        buffer_m: float,
    ) -> list[dict[str, Any]]:
        """Extract structure features within buffer into detached dictionaries.

        Args:
            struct_lyr: Layer containing structural measurements.
            line_geom: Section line geometry.
            buffer_m: Buffer distance.

        Returns:
            List of feature data dictionaries (wkt, attributes).

        """
        pass

    @abstractmethod
    def project_structures(
        self,
        line_geom: QgsGeometry,
        line_start: Any,
        da: Any,
        raster_lyr: QgsRasterLayer,
        struct_data: list[dict[str, Any]],
        buffer_m: float,
        line_az: float,
        dip_field: str,
        strike_field: str,
        band_number: int = 1,
    ) -> Any:
        """Project detached structural measurements onto the section plane.

        Args:
            line_geom: The section line geometry.
            line_start: Start point of the line.
            da: Distance calculation object.
            raster_lyr: The DEM raster layer.
            struct_data: List of detached structure dictionaries.
            buffer_m: Search buffer distance.
            line_az: Azimuth of the section line.
            dip_field: Name of the dip field.
            strike_field: Name of the strike field.
            band_number: Raster band index.

        Returns:
            StructureData: List of StructureMeasurement objects.

        """
        pass
