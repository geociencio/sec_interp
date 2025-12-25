# /***************************************************************************
#  SecInterp - GeologyService
#                                  A QGIS plugin
#  Service for generating geological profiles.
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

import contextlib
from typing import List, Optional, Tuple
from collections.abc import Generator

from qgis import processing
from qgis.core import (
    QgsDistanceArea,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsProcessingFeedback,
    QgsRaster,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsWkbTypes,
)

from sec_interp.core import utils as scu
from sec_interp.core.exceptions import DataMissingError, GeometryError, ProcessingError
from sec_interp.core.performance_metrics import performance_monitor
from sec_interp.core.interfaces.geology_interface import IGeologyService
from sec_interp.core.types import GeologyData, GeologySegment
from sec_interp.core.utils.sampling import interpolate_elevation
from sec_interp.core.utils.resource_manager import temporary_memory_layer
from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


class GeologyService(IGeologyService):
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

        Extracts geological unit intersections along the cross-section line,
        calculates elevations from the DEM, and returns a list of segments.

        Args:
            line_lyr: The QGIS vector layer representing the cross-section line.
            raster_lyr: The Digital Elevation Model (DEM) raster layer.
            outcrop_lyr: The QGIS vector layer containing geological outcrop polygons.
            outcrop_name_field: The attribute field name for geological unit names.
            band_number: The raster band to use for elevation sampling (default 1).

        Returns:
            GeologyData: A list of `GeologySegment` objects, sorted by distance along the section.

        Raises:
            DataMissingError: If the line layer has no features.
            GeometryError: If the line geometry is invalid.
            ProcessingError: If the intersection processing fails.
        """
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

        crs = line_lyr.crs()
        da = scu.create_distance_area(crs)

        # 1. Generate Master Profile Data
        master_profile_data, master_grid_dists = self._generate_master_profile_data(
            line_geom, raster_lyr, band_number, da, line_start
        )

        # 2. Run Intersection & 3. Process Intersections
        segments = []
        tolerance = 0.001

        # Execute intersection and manage its lifecycle
        with self._intersect_to_temp_layer(line_lyr, outcrop_lyr) as intersection_layer:
            if not intersection_layer or not intersection_layer.isValid():
                logger.error("Intersection layer is invalid")
                return []

            for feature in intersection_layer.getFeatures():
                new_segments = self._process_intersection_feature(
                    feature,
                    outcrop_name_field,
                    line_start,
                    da,
                    master_grid_dists,
                    master_profile_data,
                    tolerance,
                )
                segments.extend(new_segments)

        logger.info(f"Generated {len(segments)} geological segments")
        # Sort by start distance
        segments.sort(key=lambda x: x.points[0][0] if x.points else 0)

        return segments

    def _generate_master_profile_data(
        self,
        line_geom: QgsGeometry,
        raster_lyr: QgsRasterLayer,
        band_number: int,
        da: QgsDistanceArea,
        line_start: QgsPointXY,
    ) -> tuple[list[tuple[float, float]], list[tuple[float, QgsPointXY, float]]]:
        """Generate the master profile data (grid points and elevations).

        Args:
            line_geom: The geometry of the cross-section line.
            raster_lyr: The DEM raster layer for elevation.
            band_number: The raster band to sample.
            da: The distance calculation object.
            line_start: The start point of the section line.

        Returns:
            A tuple containing:
                - master_profile_data: List of (distance, elevation) tuples.
                - master_grid_dists: List of (distance, point, elevation) tuples.
        """
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
        current_dist = 0.0

        for i, pt in enumerate(master_grid_points):
            if i > 0:
                segment_len = da.measureLine(master_grid_points[i - 1], pt)
                current_dist += segment_len
            
            # Use sample() for faster single band access
            val, ok = raster_lyr.dataProvider().sample(pt, band_number)
            elev = val if ok else 0.0

            master_profile_data.append((current_dist, elev))
            master_grid_dists.append((current_dist, pt, elev))

        return master_profile_data, master_grid_dists

    @contextlib.contextmanager
    def _intersect_to_temp_layer(
        self, line_lyr: QgsVectorLayer, outcrop_lyr: QgsVectorLayer
    ) -> Generator[QgsVectorLayer, None, None]:
        """Execute intersection and yield result as a managed temporary layer.

        Args:
            line_lyr: The section line vector layer.
            outcrop_lyr: The outcrop polygons vector layer.

        Yields:
            The intersection memory layer.

        Raises:
            ProcessingError: If the intersection calculation fails.
        """
        try:
            feedback = QgsProcessingFeedback()
            result = processing.run(
                "native:intersection",
                {
                    "INPUT": line_lyr,
                    "OVERLAY": outcrop_lyr,
                    "OUTPUT": "memory:intersection_temp",
                },
                feedback=feedback,
            )
            layer = result["OUTPUT"]
            
            # Use our resource manager to ensure cleanup
            with temporary_memory_layer(layer.source(), layer.name()) as managed_layer:
                # We need to manually copy features if it's a new instance, 
                # but 'memory:' layers from processing are already in memory.
                # Just yielding the result layer is enough if we wrap it.
                yield layer
                
        except Exception as e:
            logger.exception("Geological intersection failed")
            raise ProcessingError(
                "Cannot compute geological intersection", 
                {"line_layer": line_lyr.name(), "outcrop_layer": outcrop_lyr.name()}
            ) from e

    def _process_intersection_feature(
        self,
        feature: QgsFeature,
        outcrop_name_field: str,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
        master_grid_dists: list,
        master_profile_data: list,
        tolerance: float,
    ) -> list[GeologySegment]:
        """Process a single intersection feature to extract geology segments.

        Args:
            feature: The intersection result feature.
            outcrop_name_field: The field name for geological unit names.
            line_start: Start point of the section line.
            da: Geodesic distance calculation object.
            master_grid_dists: Master grid elevation data for sampling.
            master_profile_data: Master profile data for boundary interpolation.
            tolerance: Small distance tolerance for grid point inclusion.

        Returns:
            A list of GeologySegment objects extracted from the feature.
        """
        geom = feature.geometry()
        if not geom or geom.isNull():
            return []

        geometries = []
        if geom.wkbType() in [QgsWkbTypes.LineString, QgsWkbTypes.LineString25D]:
            geometries.append(geom)
        elif geom.wkbType() in [
            QgsWkbTypes.MultiLineString,
            QgsWkbTypes.MultiLineString25D,
        ]:
            for part in geom.asMultiPolyline():
                geometries.append(QgsGeometry.fromPolylineXY(part))
        else:
            return []

        try:
            glg_val = feature[outcrop_name_field]
        except KeyError:
            glg_val = "Unknown"

        segments = []
        for seg_geom in geometries:
            segment = self._create_segment_from_geometry(
                seg_geom,
                feature,
                str(glg_val),
                line_start,
                da,
                master_grid_dists,
                master_profile_data,
                tolerance,
            )
            if segment:
                segments.append(segment)

        return segments

    def _create_segment_from_geometry(
        self,
        seg_geom: QgsGeometry,
        feature: QgsFeature,
        glg_val: str,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
        master_grid_dists: list,
        master_profile_data: list,
        tolerance: float,
    ) -> Optional[GeologySegment]:
        """Create a GeologySegment from a geometry part by sampling elevations.

        Args:
            seg_geom: The part geometry to process.
            feature: Original source feature for attribute extraction.
            glg_val: The geology unit name for this segment.
            line_start: Start point of the section line.
            da: Geodesic distance calculation object.
            master_grid_dists: Master grid elevation data.
            master_profile_data: Master profile topography data.
            tolerance: Geometrical distance tolerance.

        Returns:
            A new GeologySegment object, or None if the geometry has no vertices.
        """
        verts = scu.get_line_vertices(seg_geom)
        if not verts:
            return None

        # Get start/end distances
        start_pt, end_pt = verts[0], verts[-1]
        dist_start = da.measureLine(line_start, start_pt)
        dist_end = da.measureLine(line_start, end_pt)

        if dist_start > dist_end:
            dist_start, dist_end = dist_end, dist_start

        # Get Inner Grid Points
        inner_points = [
            (d, e)
            for d, _, e in master_grid_dists
            if dist_start + tolerance < d < dist_end - tolerance
        ]

        # Interpolate Boundary Elevations
        elev_start = interpolate_elevation(master_profile_data, dist_start)
        elev_end = interpolate_elevation(master_profile_data, dist_end)

        # Combine
        segment_points = [(dist_start, elev_start), *inner_points, (dist_end, elev_end)]

        # Attributes from original feature
        attrs = dict(zip(feature.fields().names(), feature.attributes(), strict=False))

        return GeologySegment(
            unit_name=glg_val,
            geometry=seg_geom,
            attributes=attrs,
            points=[(round(d, 1), round(e, 1)) for d, e in segment_points],
        )
