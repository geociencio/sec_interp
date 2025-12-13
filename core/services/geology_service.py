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
from sec_interp.core.performance_metrics import performance_monitor
from sec_interp.core.types import GeologyData
from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


class GeologyService:
    """Service for generating geological profiles.

    This service handles the extraction of geological unit intersections
    along a cross-section line.
    """

    @performance_monitor
    def generate_geological_profile(
        self,
        line_lyr: QgsVectorLayer,
        raster_lyr: QgsRasterLayer,
        outcrop_lyr: QgsVectorLayer,
        outcrop_name_field: str,
        band_number: int = 1,
    ) -> GeologyData:
        """Generate geological profile data by intersecting the section line with outcrop polygons.

        Returns a list of GeologySegment objects.
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
        interval = raster_lyr.rasterUnitsPerPixelX()
        logger.debug(f"Generating master profile with interval={interval:.2f}")

        try:
            master_densified = scu.densify_line_by_interval(line_geom, interval)
            master_grid_points = scu.get_line_vertices(master_densified)
        except Exception as e:
            logger.warning(f"Failed to generate master grid: {e}")
            master_grid_points = scu.get_line_vertices(line_geom)

        master_profile_data = [] 
        master_grid_dists = []   
        
        for pt in master_grid_points:
            d = da.measureLine(line_start, pt)
            res = raster_lyr.dataProvider().identify(pt, QgsRaster.IdentifyFormatValue).results()
            elev = res.get(band_number, 0.0)
            
            master_profile_data.append((d, elev))
            master_grid_dists.append((d, pt, elev))

        segments = []

        # 2. Run Intersection
        try:
            feedback = QgsProcessingFeedback()
            result = processing.run(
                "native:intersection",
                {
                    "INPUT": line_lyr,
                    "OVERLAY": outcrop_lyr,
                    "OUTPUT": "memory:",
                },
                feedback=feedback,
            )
            intersection_layer = result["OUTPUT"]
        except Exception as e:
            logger.exception("Geological intersection failed")
            raise RuntimeError("Cannot compute geological intersection") from e

        from sec_interp.core.utils.sampling import interpolate_elevation
        from sec_interp.core.types import GeologySegment

        tolerance = 0.001

        for feature in intersection_layer.getFeatures():
            geom = feature.geometry()
            if not geom or geom.isNull():
                continue

            geometries = []
            if geom.wkbType() in [QgsWkbTypes.LineString, QgsWkbTypes.LineString25D]:
                geometries.append(geom)
            elif geom.wkbType() in [QgsWkbTypes.MultiLineString, QgsWkbTypes.MultiLineString25D]:
                for part in geom.asMultiPolyline():
                    geometries.append(QgsGeometry.fromPolylineXY(part))
            else:
                continue

            try:
                glg_val = feature[outcrop_name_field]
            except KeyError:
                glg_val = "Unknown"

            for seg_geom in geometries:
                verts = scu.get_line_vertices(seg_geom)
                if not verts: continue
                
                # Get start/end distances
                start_pt, end_pt = verts[0], verts[-1]
                dist_start = da.measureLine(line_start, start_pt)
                dist_end = da.measureLine(line_start, end_pt)
                
                if dist_start > dist_end:
                    dist_start, dist_end = dist_end, dist_start

                # 3. Get Inner Grid Points
                inner_points = [
                    (d, e) for d, _, e in master_grid_dists 
                    if dist_start + tolerance < d < dist_end - tolerance
                ]

                # 4. Interpolate Boundary Elevations
                elev_start = interpolate_elevation(master_profile_data, dist_start)
                elev_end = interpolate_elevation(master_profile_data, dist_end)

                # Combine
                segment_points = [(dist_start, elev_start)] + inner_points + [(dist_end, elev_end)]
                
                # Create GeometrySegment
                # Note: We store the intersection geometry but the points are what really matters for profile
                # Attributes from original feature
                attrs = dict(zip(feature.fields().names(), feature.attributes()))
                
                segment = GeologySegment(
                    unit_name=str(glg_val),
                    geometry=seg_geom, 
                    attributes=attrs,
                    points=[(round(d, 1), round(e, 1)) for d, e in segment_points]
                )
                segments.append(segment)

        logger.info(f"Generated {len(segments)} geological segments")
        # Sort by start distance
        segments.sort(key=lambda x: x.points[0][0] if x.points else 0)
        return segments
