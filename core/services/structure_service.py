# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SecInterp - StructureService
                                 A QGIS plugin
 Service for projecting structural measurements
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

from qgis.core import QgsVectorLayer

from .. import utils as scu
from .. import validation as vu
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
        struct_lyr: QgsVectorLayer,
        buffer_m: int,
        line_az: float,
        dip_field: str,
        strike_field: str,
    ):
        """Project structural measurements onto the cross-section plane.

        This function returns the profile data as a list of tuples.

        Filters structures within a buffer distance of the section line and calculates
        their apparent dip in the direction of the section.

        Args:
            line_lyr (QgsVectorLayer): The cross-section line layer.
            struct_lyr (QgsVectorLayer): The structural measurements layer (points).
            buffer_m (int): Buffer distance in meters to include structures.
            line_az (float): Azimuth of the section line in degrees.
            dip_field (str): Field name for dip angle.
            strike_field (str): Field name for strike angle.

        Returns:
            list: List of (distance, apparent_dip) tuples.

        Raises:
            ValueError: If line layer has no features or invalid geometry.
        """

        # Logging: Initial setup
        logger.info("=" * 60)
        logger.info("PROJECT_STRUCTURES - Starting analysis")
        logger.info("=" * 60)
        logger.info(f"Buffer distance: {buffer_m} (units depend on CRS)")
        logger.info(f"Line azimuth: {line_az:.2f}°")
        logger.info(f"Dip field: '{dip_field}'")
        logger.info(f"Strike field: '{strike_field}'")

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

        # Create buffer using native algorithm for better CRS handling
        try:
            buffer_geom = scu.create_buffer_geometry(
                line_geom, line_lyr.crs(), buffer_m, segments=25
            )
        except (ValueError, RuntimeError) as e:
            logger.error(f"Buffer creation failed: {e}")
            raise ValueError(f"Cannot create buffer zone: {e}") from e

        crs = struct_lyr.crs()

        # Logging: CRS information
        logger.info(f"Structural layer CRS: {crs.authid()} - {crs.description()}")
        logger.info(f"CRS units: {crs.mapUnits()}")
        if crs.isGeographic():
            logger.warning(
                "⚠️  CRS is GEOGRAPHIC (lat/lon) - buffer is in DEGREES, not meters!"
            )
            logger.warning(
                f"   A buffer of {buffer_m} degrees ≈ {buffer_m * 111} km at equator"
            )
        else:
            logger.info("✓ CRS is PROJECTED - buffer is in map units")

        da = scu.create_distance_area(crs)

        # Logging: Count total features
        total_features = struct_lyr.featureCount()
        logger.info(f"Total features in structural layer: {total_features}")

        projected_structs = []

        # Detailed counters for logging
        null_geom_count = 0
        missing_field_count = 0
        strike_parse_fail_count = 0
        dip_parse_fail_count = 0
        strike_range_fail_count = 0
        dip_range_fail_count = 0
        success_count = 0

        # Filter features spatially using optimized index-based method
        # Returns a list of features, not a layer
        try:
            filtered_features = scu.filter_features_by_buffer(
                struct_lyr, buffer_geom, line_lyr.crs()
            )
            filtered_count = len(filtered_features)
            outside_buffer_count = total_features - filtered_count

            logger.info(
                f"Spatial filter: {filtered_count} features in buffer, "
                f"{outside_buffer_count} outside"
            )
        except (ValueError, RuntimeError) as e:
            logger.error(f"Spatial filtering failed: {e}")
            raise ValueError(f"Cannot filter structures by buffer: {e}") from e

        # Process only filtered features (no need for intersects() check)
        for idx, f in enumerate(filtered_features):
            struct_geom = f.geometry()
            if not struct_geom or struct_geom.isNull():
                null_geom_count += 1
                continue

            # Feature is already inside buffer - no intersects() check needed
            p = struct_geom.asPoint()
            dist = da.measureLine(line_start, p)

            try:
                strike_raw = f[strike_field]
                dip_raw = f[dip_field]
            except KeyError as e:
                missing_field_count += 1
                logger.debug(f"Feature {idx}: Missing field {e}")
                continue

            # Parse strike (supports field notation like "N 15° W" or numeric)
            strike = scu.parse_strike(strike_raw)
            if strike is None:
                strike_parse_fail_count += 1
                logger.debug(
                    f"Feature {idx}: Failed to parse strike '{strike_raw}'"
                )
                continue

            # Parse dip (supports field notation like "22° SW" or numeric)
            dip_angle, dip_direction = scu.parse_dip(dip_raw)
            if dip_angle is None:
                dip_parse_fail_count += 1
                logger.debug(f"Feature {idx}: Failed to parse dip '{dip_raw}'")
                continue

            # Use dip_angle for calculations
            dip = dip_angle
            # Note: dip_direction could be used for additional validation if needed

            # Validate ranges
            is_valid, error_msg = vu.validate_angle_range(
                strike, "Strike", 0.0, 360.0
            )
            if not is_valid:
                strike_range_fail_count += 1
                logger.debug(
                    f"Feature {idx}: Strike validation failed - {error_msg} (value: {strike})"
                )
                continue

            is_valid, error_msg = vu.validate_angle_range(dip, "Dip", 0.0, 90.0)
            if not is_valid:
                dip_range_fail_count += 1
                logger.debug(
                    f"Feature {idx}: Dip validation failed - {error_msg} (value: {dip})"
                )
                continue

            app_dip = scu.calculate_apparent_dip(strike, dip, line_az)
            projected_structs.append((round(dist, 1), round(app_dip, 1)))
            success_count += 1
            logger.debug(
                f"Feature {idx}: ✓ Success - dist={dist:.1f}, strike={strike:.1f}°, dip={dip:.1f}°, app_dip={app_dip:.1f}°"
            )

        # Sort by distance
        projected_structs.sort(key=lambda x: x[0])

        # Logging: Summary
        logger.info("-" * 60)
        logger.info("FILTERING SUMMARY:")
        logger.info(f"  Total features processed: {total_features}")
        logger.info(f"  ✓ Successfully projected: {success_count}")
        logger.info(f"  ✗ Null/invalid geometry: {null_geom_count}")
        logger.info(f"  ✗ Outside buffer ({buffer_m} units): {outside_buffer_count}")
        logger.info(f"  ✗ Missing dip/strike fields: {missing_field_count}")
        logger.info(f"  ✗ Strike parsing failed: {strike_parse_fail_count}")
        logger.info(f"  ✗ Dip parsing failed: {dip_parse_fail_count}")
        logger.info(f"  ✗ Strike out of range: {strike_range_fail_count}")
        logger.info(f"  ✗ Dip out of range: {dip_range_fail_count}")
        logger.info("-" * 60)

        total_skipped = (
            null_geom_count
            + outside_buffer_count
            + missing_field_count
            + strike_parse_fail_count
            + dip_parse_fail_count
            + strike_range_fail_count
            + dip_range_fail_count
        )

        if total_skipped > 0:
            logger.warning(f"⚠️  Skipped {total_skipped} structural measurements")
            if outside_buffer_count == total_features - null_geom_count:
                logger.warning("⚠️  ALL valid features are outside the buffer!")
                logger.warning("   → Try increasing the buffer distance")
                logger.warning(
                    "   → Check that line and structural layers use the same CRS"
                )

        logger.info("=" * 60)

        return projected_structs
