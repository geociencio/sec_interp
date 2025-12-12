"""/***************************************************************************
 SecInterp - StructureService
                                 A QGIS plugin
 Service for projecting structural measurements.
                              -------------------
        begin                : 2025-12-07
        copyright            : (C) 2025 by Juan M Bernales
        email                : juanbernales@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.core import QgsRaster, QgsRasterLayer, QgsVectorLayer

from sec_interp.core import utils as scu
from sec_interp.core import validation as vu
from sec_interp.core.types import StructureData
from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


class StructureService:
    """Service for projecting structural measurements onto cross-sections.

    This service handles the filtering and projection of structural measurements
    (dip/strike) onto a cross-section plane to calculate apparent dip.
    """

    def project_structures(
        self,
        line_lyr: QgsVectorLayer,
        raster_lyr: QgsRasterLayer,  # Added
        struct_lyr: QgsVectorLayer,
        buffer_m: int,
        line_az: float,
        dip_field: str,
        strike_field: str,
        band_number: int = 1,  # Added
    ) -> StructureData:
        """Project structural measurements onto the cross-section plane.

        This function returns the profile data as a list of StructureMeasurement objects.

        Filters structures within a buffer distance of the section line and calculates
        their apparent dip in the direction of the section.

        Args:
            line_lyr: The cross-section line layer.
            raster_lyr: The DEM raster layer for elevation sampling.
            struct_lyr: The structural measurements layer (points).
            buffer_m: Buffer distance in meters to include structures.
            line_az: Azimuth of the section line in degrees.
            dip_field: Field name for dip angle.
            strike_field: Field name for strike angle.
            band_number: Raster band to sample (default: 1).

        Returns:
            List of StructureMeasurement objects.

        Raises:
            ValueError: If line layer has no features or invalid geometry.
        """
        # Logging: Initial setup
        logger.info("=" * 60)
        logger.info("PROJECT_STRUCTURES - Starting analysis")
        logger.info("=" * 60)
        logger.info(f"Buffer distance: {buffer_m} (units depend on CRS)")
        logger.info(f"Line azimuth: {line_az:.2f}°")

        line_feat = next(line_lyr.getFeatures(), None)
        if not line_feat:
            raise ValueError("Line layer has no features")

        line_geom = line_feat.geometry()
        if not line_geom or line_geom.isNull():
            raise ValueError("Line geometry is not valid")

        if line_geom.isMultipart():
            line_start = line_geom.asMultiPolyline()[0][0]
        else:
            line_start = line_geom.asPolyline()[0]

        # Create buffer
        try:
            buffer_geom = scu.create_buffer_geometry(
                line_geom, line_lyr.crs(), buffer_m, segments=25
            )
        except (ValueError, RuntimeError) as e:
            logger.exception("Buffer creation failed")
            raise ValueError("Cannot create buffer zone") from e

        crs = struct_lyr.crs()
        da = scu.create_distance_area(crs)
        total_features = struct_lyr.featureCount()
        
        projected_structs = []

        try:
            filtered_features = scu.filter_features_by_buffer(
                struct_lyr, buffer_geom, line_lyr.crs()
            )
        except (ValueError, RuntimeError) as e:
            logger.exception("Spatial filtering failed")
            raise ValueError("Cannot filter structures by buffer") from e

        # Process filtered features
        from sec_interp.core.types import StructureMeasurement
        from qgis.core import QgsRaster

        for idx, f in enumerate(filtered_features):
            struct_geom = f.geometry()
            if not struct_geom or struct_geom.isNull():
                continue

            # Project point onto line to get true station distance
            if not struct_geom.intersects(buffer_geom): 
                # Should be caught by filter, but double check simple geom intersection
                # Actually filter_features checks bounding box then geometry, so safe.
                # But we need projected point on line for Distance calculation
                pass
            
            # Use geometry engine project (returns distance)
            proj_dist = line_geom.lineLocatePoint(struct_geom)
            if proj_dist < 0:
                continue

            # Interpolate point on line at that distance
            proj_pt = line_geom.interpolate(proj_dist).asPoint()
            
            # Measure geodesic distance from start if needed, or use proj_dist (Cartesian)
            # Standard is usually distance along line.
            # lineLocatePoint returns distance along geometry.
            dist = proj_dist 
            # Note: Previous code used da.measureLine(line_start, struct_geom.asPoint()) 
            # which is radial distance, not projected. Projected is better for sections.
            # Let's switch to projected distance as Exporter was doing?
            # Exporter used: proj_dist = line_geom.lineLocatePoint(struct_geom)
            # THEN: proj_pt = ... interpolate(proj_dist)
            # THEN: dist = da.measureLine(line_start, proj_pt)
            # This handles CRS differences better if da handles ellipsoids.
            
            dist = da.measureLine(line_start, proj_pt)

            # Sample Elevation
            res_val = (
                raster_lyr.dataProvider()
                .identify(proj_pt, QgsRaster.IdentifyFormatValue)
                .results()
            )
            elev = res_val.get(band_number, 0.0)

            try:
                strike_raw = f[strike_field]
                dip_raw = f[dip_field]
            except KeyError:
                continue

            strike = scu.parse_strike(strike_raw)
            dip_angle, _ = scu.parse_dip(dip_raw)

            if strike is None or dip_angle is None:
                continue
            
            # Validate ranges
            if not (0 <= strike <= 360) or not (0 <= dip_angle <= 90):
                continue

            app_dip = scu.calculate_apparent_dip(strike, dip_angle, line_az)
            
            # Create rich object
            measurement = StructureMeasurement(
                distance=round(dist, 1),
                elevation=round(elev, 1),
                apparent_dip=round(app_dip, 1),
                original_dip=dip_angle,
                original_strike=strike,
                attributes=dict(zip(f.fields().names(), f.attributes()))
            )
            projected_structs.append(measurement)

        # Sort by distance
        projected_structs.sort(key=lambda x: x.distance)
        
        logger.info(f"Processed {len(projected_structs)} structural measurements")
        return projected_structs
