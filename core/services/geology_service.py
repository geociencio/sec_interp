"""/***************************************************************************
 SecInterp - GeologyService
                                 A QGIS plugin
 Service for generating geological profiles.
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
    QgsGeometry,
    QgsProcessingFeedback,
    QgsRaster,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsWkbTypes,
)

from sec_interp.core import utils as scu
from sec_interp.core.types import GeologyData
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

        # 1. Generate Master Profile Data (Grid Points + Elevations)
        # This acts as the "Ground Truth Surface" for alignment
        interval = raster_lyr.rasterUnitsPerPixelX()
        logger.debug(f"Generating master profile with interval={interval:.2f}")

        try:
            # Densify original line
            master_densified = scu.densify_line_by_interval(line_geom, interval)
            master_grid_points = scu.get_line_vertices(master_densified)
        except Exception as e:
            logger.warning(f"Failed to generate master grid: {e}")
            master_grid_points = scu.get_line_vertices(line_geom)

        # Calculate distances & sample elevations for master profile
        master_profile_data = [] # List of (dist, elev)
        master_grid_dists = []   # List of (dist, point, elev) for fast lookup
        
        for pt in master_grid_points:
            d = da.measureLine(line_start, pt)
            res = raster_lyr.dataProvider().identify(pt, QgsRaster.IdentifyFormatValue).results()
            elev = res.get(band_number, 0.0)
            
            master_profile_data.append((d, elev))
            master_grid_dists.append((d, pt, elev))

        values = []

        # 2. Run Intersection on Original Line
        try:
            feedback = QgsProcessingFeedback()
            result = processing.run(
                "native:intersection",
                {
                    "INPUT": line_lyr,
                    "OVERLAY": outcrop_lyr,
                    "INPUT_FIELDS": [], 
                    "OVERLAY_FIELDS": [], 
                    "OVERLAY_FIELDS_PREFIX": "",
                    "OUTPUT": "memory:",
                },
                feedback=feedback,
            )
            intersection_layer = result["OUTPUT"]
            intersection_count = intersection_layer.featureCount()
            logger.info(f"✓ Intersection: {intersection_count} segments")
        
        except Exception as e:
            logger.exception("Geological intersection failed")
            raise RuntimeError("Cannot compute geological intersection") from e

        # Import interpolation helper
        from sec_interp.core.utils.sampling import interpolate_elevation

        # Process intersection results
        processed_segments = 0
        total_points = 0
        tolerance = 0.001

        for feature in intersection_layer.getFeatures():
            geom = feature.geometry()
            if not geom or geom.isNull():
                continue

            # Handle geometries
            geometries = []
            if geom.wkbType() in [QgsWkbTypes.LineString, QgsWkbTypes.LineString25D]:
                geometries.append(geom)
            elif geom.wkbType() in [QgsWkbTypes.MultiLineString, QgsWkbTypes.MultiLineString25D]:
                for part in geom.asMultiPolyline():
                    geometries.append(QgsGeometry.fromPolylineXY(part))
            else:
                continue

            glg_val = feature[outcrop_name_field]

            for seg_geom in geometries:
                verts = scu.get_line_vertices(seg_geom)
                if not verts: continue
                
                # Get start/end distances
                start_pt, end_pt = verts[0], verts[-1]
                dist_start = da.measureLine(line_start, start_pt)
                dist_end = da.measureLine(line_start, end_pt)
                
                if dist_start > dist_end:
                    dist_start, dist_end = dist_end, dist_start

                # 3. Get Inner Grid Points (Pre-calculated elevations)
                inner_points = [
                    (d, e) for d, _, e in master_grid_dists 
                    if dist_start + tolerance < d < dist_end - tolerance
                ]

                # 4. Interpolate Boundary Elevations
                # Snap start/end to the topographic surface logic
                elev_start = interpolate_elevation(master_profile_data, dist_start)
                elev_end = interpolate_elevation(master_profile_data, dist_end)

                # Combine: [Start] + [Inner] + [End]
                segment_points = [(dist_start, elev_start)] + inner_points + [(dist_end, elev_end)]

                processed_segments += 1
                for d, e in segment_points:
                    values.append((round(d, 1), round(e, 1), glg_val))
                    total_points += 1

        logger.info(f"Processed {processed_segments} segments, generated {total_points} points (snapped)")
        values.sort(key=lambda x: x[0])
        return values
