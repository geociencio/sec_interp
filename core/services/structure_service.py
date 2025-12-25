from __future__ import annotations

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
from collections.abc import Iterator
from typing import List, Optional

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsDistanceArea,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsRaster,
    QgsRasterLayer,
    QgsVectorLayer,
)

from sec_interp.core import utils as scu
from sec_interp.core.exceptions import DataMissingError, GeometryError, ProcessingError
from sec_interp.core import validation as vu
from sec_interp.core.interfaces.structure_interface import IStructureService
from sec_interp.core.types import StructureData, StructureMeasurement
from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


class StructureService(IStructureService):
    """Service for projecting structural measurements onto cross-sections.

    This service handles the filtering and projection of structural measurements
    (dip/strike) onto a cross-section plane to calculate apparent dip.
    """

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
    ) -> StructureData:
        """Project structural measurements onto the cross-section plane.

        Filters structures within a buffer, samples elevation, and calculates
        apparent dip for each measurement.

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
            A list of StructureMeasurement objects sorted by distance along section.

        Raises:
            DataMissingError: If line layer has no features.
            GeometryError: If line geometry is invalid.
        """
        # Logging: Initial setup
        logger.info(f"Analyzing structures in {struct_lyr.name()} with buffer {buffer_m}m")

        line_feat = next(line_lyr.getFeatures(), None)
        if not line_feat:
            raise DataMissingError("Line layer has no features", {"layer": line_lyr.name()})

        line_geom = line_feat.geometry()
        if not line_geom or line_geom.isNull():
            raise GeometryError("Line geometry is not valid", {"layer": line_lyr.name()})

        if line_geom.isMultipart():
            line_start = line_geom.asMultiPolyline()[0][0]
        else:
            line_start = line_geom.asPolyline()[0]

        # 1. Create Buffer
        buffer_geom = self._create_buffer_zone(line_geom, line_lyr.crs(), buffer_m)

        # 2. Filter Measures
        filtered_features = self._filter_structures(
            struct_lyr, buffer_geom, line_lyr.crs()
        )

        # 3. Process Features
        projected_structs = []
        crs = struct_lyr.crs()
        da = scu.create_distance_area(crs)

        for f in filtered_features:
            measurement = self._process_single_structure(
                f,
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

        logger.info(f"Processed {len(projected_structs)} structural measurements from {struct_lyr.name()}")
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
            logger.exception("Buffer creation failed")
            raise ProcessingError("Cannot create buffer zone", {"buffer_m": buffer_m, "crs": crs.authid()}) from e

    def _filter_structures(
        self,
        struct_lyr: QgsVectorLayer,
        buffer_geom: QgsGeometry,
        target_crs: QgsCoordinateReferenceSystem,
    ) -> Iterator[QgsFeature]:
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
            logger.exception("Spatial filtering failed")
            raise ProcessingError("Cannot filter structures by buffer", {"layer": struct_lyr.name()}) from e

    def _process_single_structure(
        self,
        feature: QgsFeature,
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
        raster_lyr: QgsRasterLayer,
        band_number: int,
        line_az: float,
        dip_field: str,
        strike_field: str,
    ) -> Optional[StructureMeasurement]:
        """Process a single structure feature to calculate its 2D coordinates and apparent dip.

        Args:
            feature: The source structural point feature.
            line_geom: The section line geometry.
            line_start: The start point of the section line.
            da: The distance calculation object.
            raster_lyr: The DEM layer for elevation sampling.
            band_number: The raster band index.
            line_az: The azimuth of the section line.
            dip_field: Field name for original dip.
            strike_field: Field name for original strike.

        Returns:
            The projected measurement object, or None if invalid or cannot be projected.
        """
        struct_geom = feature.geometry()
        if not struct_geom or struct_geom.isNull():
            return None

        # Project point onto line to get true station distance
        proj_dist = line_geom.lineLocatePoint(struct_geom)
        if proj_dist < 0:
            return None

        # Interpolate point on line at that distance
        proj_pt = line_geom.interpolate(proj_dist).asPoint()

        # Measure geodesic distance from start
        # Using measureLine ensures correct units (meters) even if CRS is geographic
        dist = da.measureLine(line_start, proj_pt)

        # Sample Elevation
        res_val = (
            raster_lyr.dataProvider()
            .identify(proj_pt, QgsRaster.IdentifyFormatValue)
            .results()
        )
        elev = res_val.get(band_number, 0.0)

        # Parse Attributes
        try:
            strike_raw = feature[strike_field]
            dip_raw = feature[dip_field]
        except KeyError:
            return None

        strike = scu.parse_strike(strike_raw)
        dip_angle, _ = scu.parse_dip(dip_raw)

        if strike is None or dip_angle is None:
            return None

        # Validate ranges
        if not (0 <= strike <= 360) or not (0 <= dip_angle <= 90):
            return None

        app_dip = scu.calculate_apparent_dip(strike, dip_angle, line_az)

        # Create object
        return StructureMeasurement(
            distance=round(dist, 1),
            elevation=round(elev, 1),
            apparent_dip=round(app_dip, 1),
            original_dip=dip_angle,
            original_strike=strike,
            attributes=dict(
                zip(feature.fields().names(), feature.attributes(), strict=False)
            ),
        )
