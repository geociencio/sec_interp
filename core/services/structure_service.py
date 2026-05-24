"""Structure Data Processing Service.

This module handles the calculation of apparent dips and projection
of structural measurements (planes, lines) onto the section plane.
"""

# /***************************************************************************
#  SecInterp - StructureService
#                                  A QGIS plugin
#  Service for projecting structural measurements.
#                               -------------------
#         begin                : 2025-12-07
#         copyright            : (C) 2025 by Juan M Bernales
#         email                : juanbernales@gmail.com
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/
from __future__ import annotations

from typing import Any

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsDistanceArea,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsRasterLayer,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QCoreApplication

from sec_interp.core import utils as scu
from sec_interp.core.domain import StructureData, StructureMeasurement
from sec_interp.core.exceptions import ProcessingError
from sec_interp.core.interfaces.structure_interface import IStructureService
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class StructureService(IStructureService):
    """Service for projecting structural measurements onto cross-sections.

    This service handles the filtering and projection of structural measurements
    (dip/strike) onto a cross-section plane to calculate apparent dip.
    """

    def tr(self, message: str) -> str:
        """Translate a message using QCoreApplication."""
        return QCoreApplication.translate("StructureService", message)  # type: ignore[no-any-return]

    def detach_structures(
        self,
        struct_lyr: QgsVectorLayer,
        line_geom: QgsGeometry,
        buffer_m: float,
    ) -> list[dict[str, Any]]:
        """Extract structural features within buffer into detached dictionaries.

        Uses a spatial index filter via a buffer around the section line.

        Args:
            struct_lyr: Structural measurements vector layer.
            line_geom: Section line geometry.
            buffer_m: Buffer distance in meters.

        Returns:
            List of detached dictionaries containing WKT and attributes.

        """
        buffer_geom = self._create_buffer_zone(line_geom, struct_lyr.crs(), buffer_m)
        filtered_features = self._filter_structures(
            struct_lyr, buffer_geom, struct_lyr.crs()
        )

        detached_data = []
        for feat in filtered_features:
            detached_data.append(
                {
                    "wkt": feat.geometry().asWkt() if feat.hasGeometry() else None,
                    "attributes": scu.extract_feature_attributes(feat),
                }
            )
        return detached_data

    def project_structures(
        self,
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
        raster_lyr: QgsRasterLayer,
        struct_data: list[dict[str, Any]],
        buffer_m: float,
        line_az: float,
        dip_field: str,
        strike_field: str,
        band_number: int = 1,
    ) -> StructureData:
        """Project detached structural measurements onto the section plane.

        Calculates stations (distance along section), elevations from DEM,
        and apparent dips based on the section orientation.

        Args:
            line_geom: Section line geometry.
            line_start: Section start point.
            da: Distance calculator.
            raster_lyr: Elevation raster layer.
            struct_data: List of detached structural data.
            buffer_m: Projection buffer (m).
            line_az: Section azimuth in degrees.
            dip_field: Field name for dip angle.
            strike_field: Field name for strike azimuth.
            band_number: Raster band for elevation.

        Returns:
            StructureData: Sorted list of projected StructureMeasurement objects.

        """
        projected_structs = []

        for item in struct_data:
            measurement = self._process_single_structure(
                item,
                line_geom,
                line_start,
                da,
                raster_lyr,
                band_number,
                line_az,
                dip_field,
                strike_field,
            )
            if measurement:
                projected_structs.append(measurement)

        # Sort by distance
        projected_structs.sort(key=lambda x: x.distance)

        logger.info(
            self.tr("Processed {0} structural measurements").format(
                len(projected_structs)
            )
        )
        return projected_structs

    def _create_buffer_zone(
        self,
        line_geom: QgsGeometry,
        crs: QgsCoordinateReferenceSystem,
        buffer_m: float,
    ) -> QgsGeometry:
        """Create a buffer geometry around the section line.

        Args:
            line_geom: The section line geometry.
            crs: CRS of the line layer.
            buffer_m: Buffer distance in meters.

        Returns:
            The buffered area as a QgsGeometry.

        Raises:
            ProcessingError: If buffer creation fails.

        """
        try:
            return scu.create_buffer_geometry(line_geom, crs, buffer_m, segments=25)
        except (ValueError, RuntimeError) as e:
            logger.exception(self.tr("Buffer creation failed"))
            raise ProcessingError(
                self.tr("Cannot create buffer zone"),
                {"buffer_m": buffer_m, "crs": crs.authid()},
            ) from e

    def _filter_structures(
        self,
        struct_lyr: QgsVectorLayer,
        buffer_geom: QgsGeometry,
        target_crs: QgsCoordinateReferenceSystem,
    ) -> list[QgsFeature]:
        """Select structure features within the buffer using spatial indexing.

        Args:
            struct_lyr: The layer containing structural measurements.
            buffer_geom: The buffer area geometry.
            target_crs: CRS of the project/section line.

        Returns:
            An iterator over the filtered QgsFeature objects.

        Raises:
            ProcessingError: If spatial filtering fails.

        """
        try:
            return scu.filter_features_by_buffer(struct_lyr, buffer_geom, target_crs)
        except (ValueError, RuntimeError) as e:
            logger.exception(self.tr("Spatial filtering failed"))
            raise ProcessingError(
                self.tr("Cannot filter structures by buffer"),
                {"layer": struct_lyr.name()},
            ) from e

    def _process_single_structure(
        self,
        data: dict[str, Any],
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
        raster_lyr: QgsRasterLayer,
        band_number: int,
        line_az: float,
        dip_field: str,
        strike_field: str,
    ) -> StructureMeasurement | None:
        """Process a single structure from detached data.

        Projects the measurement point onto the section line and calculates
        geological properties.

        Args:
            data: Detached structure data.
            line_geom: Section line geometry.
            line_start: Start point.
            da: Distance measurer.
            raster_lyr: Elevation raster.
            band_number: Band num.
            line_az: Section azimuth.
            dip_field: Dip field.
            strike_field: Strike field.

        Returns:
            StructureMeasurement or None if projection fails.

        """
        wkt = data.get("wkt")
        if not wkt:
            return None

        struct_geom = QgsGeometry.fromWkt(wkt)
        if struct_geom.isNull():
            return None

        # Project point onto line to get true station distance
        proj_dist = line_geom.lineLocatePoint(struct_geom)
        if proj_dist < 0:
            return None

        # Interpolate point on line at that distance
        proj_pt = line_geom.interpolate(proj_dist).asPoint()

        # Measure geodesic distance from start
        dist = da.measureLine(line_start, proj_pt)

        elev = scu.sample_point_elevation(raster_lyr, proj_pt, band_number)

        parsed_data = self._parse_structural_data(
            data["attributes"], strike_field, dip_field, line_az
        )
        if not parsed_data:
            return None

        strike, dip_angle, app_dip = parsed_data

        # Create object
        return StructureMeasurement(
            distance=round(dist, 1),
            elevation=round(elev, 1),
            apparent_dip=round(app_dip, 1),
            original_dip=dip_angle,
            original_strike=strike,
            attributes=data["attributes"],
        )

    def _parse_structural_data(
        self,
        attributes: dict[str, Any],
        strike_field: str,
        dip_field: str,
        line_az: float,
    ) -> tuple[float, float, float] | None:
        """Parse strike and dip attributes and calculate apparent dip.

        Args:
            attributes: Feature attributes dictionary.
            strike_field: Name of the strike field.
            dip_field: Name of the dip field.
            line_az: Azimuth of the section line.

        Returns:
            Tuple (strike, dip, apparent_dip) or None if parsing fails.

        """
        try:
            strike_raw = attributes.get(strike_field)
            dip_raw = attributes.get(dip_field)
        except (AttributeError, KeyError):
            return None

        strike = scu.parse_strike(strike_raw)
        dip_angle, _ = scu.parse_dip(dip_raw)

        if strike is None or dip_angle is None:
            return None

        MAX_STRIKE = 360
        MAX_DIP_ANGLE = 90

        # Validate ranges
        if not (0 <= strike <= MAX_STRIKE) or not (0 <= dip_angle <= MAX_DIP_ANGLE):
            return None

        app_dip = scu.calculate_apparent_dip(strike, dip_angle, line_az)
        return strike, dip_angle, app_dip
