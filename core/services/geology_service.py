# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SecInterp - GeologyService
                                 A QGIS plugin
 Service for generating geological profiles
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

from qgis import processing
from qgis.core import (
    QgsVectorLayer,
    QgsRasterLayer,
    QgsProcessingFeedback,
    QgsWkbTypes,
    QgsGeometry,
    QgsRaster,
)

from .. import utils as scu
from ..types import GeologyData
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class GeologyService:
    """Service for generating geological profiles.
    
    This service handles the extraction of geological unit intersections
    along a cross-section line.
    """

    def generate_geological_profile(
        self,
        line_lyr: QgsVectorLayer,
        raster_lyr: QgsRasterLayer,
        outcrop_lyr: QgsVectorLayer,
        outcrop_name_field: str,
        band_number: int = 1,
    ) -> GeologyData:
        """Generate geological profile data by intersecting the section line with outcrop polygons.

        This function returns the profile data as a list of tuples.

        Args:
            line_lyr (QgsVectorLayer): The cross-section line layer.
            raster_lyr (QgsRasterLayer): The DEM/raster layer for elevation.
            outcrop_lyr (QgsVectorLayer): The geological outcrop layer (polygons).
            glg_field (str): The field name in outcrop_lyr containing unit names.
            band_number (int): Raster band to sample (default: 1).

        Returns:
            list: List of (distance, elevation, unit_name) tuples.

        Raises:
            ValueError: If line layer has no features or invalid geometry.
            RuntimeError: If intersection algorithm fails.
        """
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

        crs = line_lyr.crs()
        da = scu.create_distance_area(crs)

        values = []

        # Use native intersection algorithm for better geometry handling
        try:
            feedback = QgsProcessingFeedback()

            # Log input information for debugging
            logger.info(
                f"Computing intersection: line CRS={line_lyr.crs().authid()}, "
                f"outcrop CRS={outcrop_lyr.crs().authid()}"
            )
            logger.debug(
                f"Line features: {line_lyr.featureCount()}, "
                f"Outcrop features: {outcrop_lyr.featureCount()}"
            )

            result = processing.run(
                "native:intersection",
                {
                    "INPUT": line_lyr,
                    "OVERLAY": outcrop_lyr,
                    "INPUT_FIELDS": [],  # Don't need line fields
                    "OVERLAY_FIELDS": [],  # Empty list = keep ALL geology fields
                    "OVERLAY_FIELDS_PREFIX": "",
                    "OUTPUT": "memory:",
                },
                feedback=feedback,
            )

            intersection_layer = result["OUTPUT"]
            intersection_count = intersection_layer.featureCount()
            
            logger.info(
                f"✓ Intersection complete: {intersection_count} segments found"
            )
            
            if intersection_count == 0:
                logger.warning(
                    "No intersections found. Check that line and outcrops overlap "
                    "and have compatible CRS."
                )

        except Exception as e:
            logger.error(f"Geological intersection failed: {e}")
            raise RuntimeError(f"Cannot compute geological intersection: {e}") from e

        # Process intersection results
        # TODO: Investigate why densify_line_by_interval() doesn't work here
        # Temporarily using manual interpolation as fallback
        processed_segments = 0
        total_points = 0
        
        for feature in intersection_layer.getFeatures():
            geom = feature.geometry()
            if not geom or geom.isNull():
                logger.debug("Skipping null geometry")
                continue

            # Log geometry type for debugging
            geom_type = geom.wkbType()
            geom_type_name = QgsWkbTypes.displayString(geom_type)
            logger.debug(f"Intersection segment geometry type: {geom_type_name} ({geom_type})")

            # Handle both LineString and MultiLineString geometries
            geometries_to_process = []
            
            if geom.wkbType() in [
                QgsWkbTypes.LineString,
                QgsWkbTypes.LineString25D,
            ]:
                # Single LineString
                geometries_to_process.append(geom)
            elif geom.wkbType() in [
                QgsWkbTypes.MultiLineString,
                QgsWkbTypes.MultiLineString25D,
            ]:
                # MultiLineString - extract individual parts
                multi_geom = geom.asMultiPolyline()
                for part in multi_geom:
                    # Create a new LineString geometry from each part
                    line_geom = QgsGeometry.fromPolylineXY(part)
                    geometries_to_process.append(line_geom)
                logger.debug(f"Extracted {len(multi_geom)} parts from MultiLineString")
            else:
                logger.warning(f"Skipping unsupported geometry type: {geom_type_name}")
                continue

            # Process each geometry (LineString or part of MultiLineString)
            for process_geom in geometries_to_process:
                # Use manual interpolation (original method) as temporary fallback
                dist_step = scu.calculate_step_size(process_geom, raster_lyr)
                length = process_geom.length()
                current_dist = 0.0
                
                logger.debug(f"Processing segment: length={length:.2f}, step={dist_step:.2f}")
                processed_segments += 1

                while current_dist <= length:
                    pt = process_geom.interpolate(current_dist).asPoint()

                    # Calculate distance from the start of the original section line
                    dist_from_start = da.measureLine(line_start, pt)

                    # Get elevation
                    res = (
                        raster_lyr.dataProvider()
                        .identify(pt, QgsRaster.IdentifyFormatValue)
                        .results()
                    )
                    elev = res.get(band_number, 0.0)

                    # Get geology (attribute preserved automatically by intersection)
                    glg_val = feature[glg_field]

                    values.append((round(dist_from_start, 1), round(elev, 1), glg_val))
                    total_points += 1

                    current_dist += dist_step
        
        logger.info(f"Processed {processed_segments} segments, generated {total_points} points")

        # Sort values by distance
        values.sort(key=lambda x: x[0])

        return values
