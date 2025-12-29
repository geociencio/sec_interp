"""Geology Data Processing Service.

This module handles the extraction and projection of geological boundaries
and unit segments from map layers to the cross-section plane.
"""

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

from collections.abc import Generator
from typing import Optional

from qgis.core import (
    QgsDistanceArea,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsRaster,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsWkbTypes,
    QgsFeatureRequest,
)

from sec_interp.core import utils as scu
from sec_interp.core.exceptions import DataMissingError, GeometryError, ProcessingError
from sec_interp.core.interfaces.geology_interface import IGeologyService
from sec_interp.core.performance_metrics import performance_monitor
from sec_interp.core.types import GeologyData, GeologySegment
from sec_interp.core.utils.sampling import interpolate_elevation
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
        line_geom, line_start = self._extract_line_info(line_lyr)

        crs = line_lyr.crs()
        da = scu.create_distance_area(crs)

        # 1. Generate Master Profile Data
        master_profile_data, master_grid_dists = self._generate_master_profile_data(
            line_geom, raster_lyr, band_number, da, line_start
        )

        # 2. Optimized Spatial Filter & Intersection
        segments = []
        tolerance = 0.001

        # Spatial Filter: Use the line's bounding box to restrict the search
        line_bbox = line_geom.boundingBox()
        request = QgsFeatureRequest().setFilterRect(line_bbox)

        for feature in outcrop_lyr.getFeatures(request):
            if not feature.hasGeometry():
                continue

            outcrop_geom = feature.geometry()

            # Perform exact geometric intersection
            intersection = line_geom.intersection(outcrop_geom)

            if intersection.isEmpty():
                continue

            # Process the intersection geometry
            new_segments = self._process_intersection_geometry(
                intersection,
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

    def _process_intersection_geometry(
        self,
        geom: QgsGeometry,
        feature: QgsFeature,
        outcrop_name_field: str,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
        master_grid_dists: list,
        master_profile_data: list,
        tolerance: float,
    ) -> list[GeologySegment]:
        """Process an intersection geometry to extract geology segments.

        Args:
            geom: The intersection geometry (LineString or MultiLineString).
            feature: The original feature (for attributes).
            outcrop_name_field: The field name for geological unit names.
            line_start: Start point of the section line.
            da: Geodesic distance calculation object.
            master_grid_dists: Master grid elevation data for sampling.
            master_profile_data: Master profile data for boundary interpolation.
            tolerance: Small distance tolerance for grid point inclusion.

        Returns:
            A list of GeologySegment objects.

        """
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
            # Handle GeometryCollection if needed, or other types
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
    ) -> GeologySegment | None:
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

        # Convert to points
        segment_points = self._convert_to_segment_points(
            dist_start, dist_end, master_grid_dists, master_profile_data, tolerance
        )

        # Attributes from original feature
        attrs = dict(zip(feature.fields().names(), feature.attributes(), strict=False))

        return GeologySegment(
            unit_name=glg_val,
            geometry=seg_geom,
            attributes=attrs,
            points=[(round(d, 1), round(e, 1)) for d, e in segment_points],
        )

    def _extract_line_info(self, line_lyr: QgsVectorLayer) -> tuple[QgsGeometry, QgsPointXY]:
        """Extract geometry and start point from the line layer.

        Args:
            line_lyr: The vector layer containing the section line.

        Returns:
            A tuple containing (line_geometry, start_point).

        Raises:
            DataMissingError: If layer has no features.
            GeometryError: If geometry is invalid.

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

        return line_geom, line_start

    def _convert_to_segment_points(
        self,
        dist_start: float,
        dist_end: float,
        master_grid_dists: list,
        master_profile_data: list,
        tolerance: float,
    ) -> list[tuple[float, float]]:
        """Convert start/end distances to a list of segment points with elevations.

        Args:
            dist_start: Start distance of the segment.
            dist_end: End distance of the segment.
            master_grid_dists: Master grid elevation data.
            master_profile_data: Master profile topography data.
            tolerance: Tolerance for grid point inclusion.

        Returns:
            List of (distance, elevation) tuples.

        """
        # Get Inner Grid Points
        inner_points = [
            (d, e)
            for d, _, e in master_grid_dists
            if dist_start + tolerance < d < dist_end - tolerance
        ]

        # Interpolate Boundary Elevations
        elev_start = interpolate_elevation(master_profile_data, dist_start)
        elev_end = interpolate_elevation(master_profile_data, dist_end)

        return [(dist_start, elev_start), *inner_points, (dist_end, elev_end)]
