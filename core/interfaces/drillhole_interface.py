from abc import ABC, abstractmethod
from typing import Any, Optional

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsDistanceArea,
    QgsGeometry,
    QgsPointXY,
    QgsRasterLayer,
    QgsVectorLayer,
)


class IDrillholeService(ABC):
    """Abstract interface for the Drillhole Processing Service."""

    @abstractmethod
    def project_collars(
        self,
        collar_layer: QgsVectorLayer,
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        distance_area: QgsDistanceArea,
        buffer_width: float,
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        collar_z_field: str,
        collar_depth_field: str,
        dem_layer: Optional[QgsRasterLayer],
        line_crs: Optional[QgsCoordinateReferenceSystem] = None,
    ) -> list[tuple]:
        """Project collar points onto section line.

        Args:
            collar_layer: Vector layer containing drillhole collars.
            line_geom: Geometry of the cross-section line.
            line_start: Start point of the section line.
            distance_area: Distance calculation object.
            buffer_width: Search buffer distance in meters.
            collar_id_field: Field name for unique drillhole ID.
            use_geometry: Whether to use feature geometry for X/Y coordinates.
            collar_x_field: Field name for X coordinate (if not using geometry).
            collar_y_field: Field name for Y coordinate (if not using geometry).
            collar_z_field: Field name for collar elevation.
            collar_depth_field: Field name for total drillhole depth.
            dem_layer: Optional DEM layer for elevation if Z field is missing/zero.
            line_crs: CRS of the section line for spatial filtering.

        Returns:
            A list of tuples (hole_id, dist_along, z, offset, total_depth).
        """
        pass

    @abstractmethod
    def process_intervals(
        self,
        collar_points: list[tuple],
        collar_layer: QgsVectorLayer,
        survey_layer: QgsVectorLayer,
        interval_layer: QgsVectorLayer,
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        distance_area: QgsDistanceArea,
        buffer_width: float,
        section_azimuth: float,
        survey_fields: dict[str, str],
        interval_fields: dict[str, str],
    ) -> tuple[list, list]:
        """Process drillhole interval data and project onto the section.

        Args:
            collar_points: List of projected collar tuples from `project_collars`.
            collar_layer: The collar vector layer.
            survey_layer: The survey vector layer.
            interval_layer: The interval/geology vector layer.
            collar_id_field: Field name for hole ID in collar layer.
            use_geometry: Use geometry for collar coordinates.
            collar_x_field: Field name for X in collar layer.
            collar_y_field: Field name for Y in collar layer.
            line_geom: Section line geometry.
            line_start: Section line start point.
            distance_area: Distance calculation object.
            buffer_width: Section buffer width in meters.
            section_azimuth: Azimuth of the section line.
            survey_fields: Mapping of survey field roles to field names.
            interval_fields: Mapping of interval field roles to field names.

        Returns:
            A tuple containing (geol_data, drillhole_data).
        """
        pass
