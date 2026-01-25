from __future__ import annotations

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

from typing import Any

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsDistanceArea,
    QgsFeatureRequest,
    QgsGeometry,
    QgsPointXY,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsWkbTypes,
)

from sec_interp.core import utils as scu
from sec_interp.core.exceptions import DataMissingError, GeometryError
from sec_interp.core.interfaces.geology_interface import IGeologyService
from sec_interp.core.performance_metrics import performance_monitor
from sec_interp.core.types import GeologyData, GeologySegment, GeologyTaskInput
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
        task_input = self.prepare_task_input(
            line_lyr, raster_lyr, outcrop_lyr, outcrop_name_field, band_number
        )
        return self.process_task_data(task_input)

    def prepare_task_input(
        self,
        line_lyr: QgsVectorLayer,
        raster_lyr: QgsRasterLayer,
        outcrop_lyr: QgsVectorLayer,
        outcrop_name_field: str,
        band_number: int = 1,
    ) -> GeologyTaskInput:
        """Prepare detached domain data for background task."""
        self._validate_inputs(line_lyr, raster_lyr, outcrop_lyr, outcrop_name_field, band_number)

        line_geom, line_start = self._extract_line_info(line_lyr)
        crs = line_lyr.crs()
        da = scu.create_distance_area(crs)

        # 1. Generate Master Profile Data (needs Raster access)
        master_profile_data, master_grid_dists_raw = self._generate_master_profile_data(
            line_geom, raster_lyr, band_number, da, line_start
        )

        # Convert master_grid_dists to domain types (dist, (x, y), elev)
        master_grid_dists = [(d, (pt.x(), pt.y()), e) for d, pt, e in master_grid_dists_raw]

        # 2. Extract Outcrop Data (needs Vector access)
        # This already returns detached dicts with WKT
        outcrop_data = self._extract_outcrop_data(line_geom, outcrop_lyr, outcrop_name_field)

        return GeologyTaskInput(
            line_geometry_wkt=line_geom.asWkt(),
            line_start_x=line_start.x(),
            line_start_y=line_start.y(),
            crs_authid=crs.authid(),
            master_profile_data=master_profile_data,
            master_grid_dists=master_grid_dists,
            outcrop_data=outcrop_data,
            outcrop_name_field=outcrop_name_field,
        )

    def _validate_inputs(
        self,
        line_lyr: QgsVectorLayer,
        raster_lyr: QgsRasterLayer,
        outcrop_lyr: QgsVectorLayer,
        outcrop_name_field: str,
        band_number: int,
    ) -> None:
        """Validate input layers and parameters."""
        from sec_interp.core.exceptions import ValidationError

        # 1. Layer Validity
        for lyr, name in [
            (line_lyr, "Line layer"),
            (raster_lyr, "Raster layer"),
            (outcrop_lyr, "Outcrop layer"),
        ]:
            if not lyr or not lyr.isValid():
                raise DataMissingError(
                    f"Invalid layer: {name}. Please check input layers.",
                    {"layer": name},
                )

        # 2. Band Validation
        if band_number < 1:
            raise ValidationError("Band number must be positive.")

        if band_number > raster_lyr.bandCount():
            raise ValidationError(
                f"Band number {band_number} exceeds raster band count ({raster_lyr.bandCount()})."
            )

        # 3. Field Validation
        idx = outcrop_lyr.fields().indexFromName(outcrop_name_field)
        if idx == -1:
            raise ValidationError(f"Field '{outcrop_name_field}' not found in outcrop layer.")

    def _extract_outcrop_data(
        self,
        line_geom: QgsGeometry,
        outcrop_lyr: QgsVectorLayer,
        outcrop_name_field: str,
    ) -> list[dict[str, Any]]:
        """Extract outcrop features intersecting the line bounding box.

        Returns a list of dictionaries with WKT geometry and attributes,
        completely detached from QGIS objects.
        """
        outcrop_data = []
        line_bbox = line_geom.boundingBox()
        request = QgsFeatureRequest().setFilterRect(line_bbox)

        for feature in outcrop_lyr.getFeatures(request):
            if not feature.hasGeometry():
                continue

            # Copy attributes and geometry to detached structures
            attrs = dict(zip(feature.fields().names(), feature.attributes(), strict=False))
            try:
                # Ensure we handle potential attribute read errors safely
                unit_name = str(feature[outcrop_name_field])
            except KeyError:
                unit_name = "Unknown"

            outcrop_data.append(
                {
                    "wkt": feature.geometry().asWkt(),  # Store as WKT immediately
                    "attrs": attrs,
                    "unit_name": unit_name,
                }
            )
        return outcrop_data

    def process_task_data(
        self, task_input: GeologyTaskInput, feedback: Any | None = None
    ) -> GeologyData:
        """Process geological data in a thread-safe way (Domain-Pure logic)."""
        # Reconstruct necessary tools from IDs/Strings
        crs = QgsCoordinateReferenceSystem(task_input.crs_authid)
        da = scu.create_distance_area(crs)
        line_geom = QgsGeometry.fromWkt(task_input.line_geometry_wkt)
        line_start = QgsPointXY(task_input.line_start_x, task_input.line_start_y)

        segments = []
        total = len(task_input.outcrop_data)

        for i, item in enumerate(task_input.outcrop_data):
            if feedback and feedback.isCanceled():
                return []

            outcrop_geom = QgsGeometry.fromWkt(item["wkt"])
            intersection = line_geom.intersection(outcrop_geom)

            if intersection.isEmpty():
                continue

            new_segments = self._process_detached_intersection(
                intersection,
                item["attrs"],
                item["unit_name"],
                line_start,
                da,
                task_input.master_grid_dists,
                task_input.master_profile_data,
                task_input.tolerance,
            )
            segments.extend(new_segments)

            if feedback:
                feedback.setProgress((i / total) * 100)

        # Sort by start distance
        segments.sort(key=lambda x: x.points[0][0] if x.points else 0)
        return segments

    def _process_detached_intersection(
        self,
        geom: QgsGeometry,
        attributes: dict[str, Any],
        unit_name: str,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
        master_grid_dists: list[tuple[float, QgsPointXY, float]],
        master_profile_data: list[tuple[float, float]],
        tolerance: float,
    ) -> list[GeologySegment]:
        """Variant of _process_intersection_geometry for detached data."""
        if not geom or geom.isNull():
            return []

        geometries = self._extract_geometries(geom)
        segments = []
        for seg_geom in geometries:
            segment = self._create_segment_from_detached(
                seg_geom,
                attributes,
                unit_name,
                line_start,
                da,
                master_grid_dists,
                master_profile_data,
                tolerance,
            )
            if segment:
                segments.append(segment)
        return segments

    def _extract_geometries(self, geom: QgsGeometry) -> list[QgsGeometry]:
        """Extract individual LineString geometries from a (possibly Multi) geometry."""
        geometries = []
        if geom.wkbType() in [QgsWkbTypes.LineString, QgsWkbTypes.LineString25D]:
            geometries.append(geom)
        elif geom.wkbType() in [
            QgsWkbTypes.MultiLineString,
            QgsWkbTypes.MultiLineString25D,
        ]:
            for part in geom.asMultiPolyline():
                geometries.append(QgsGeometry.fromPolylineXY(part))
        return geometries

    def _create_segment_from_detached(
        self,
        seg_geom: QgsGeometry,
        attributes: dict[str, Any],
        glg_val: str,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
        master_grid_dists: list[tuple[float, QgsPointXY, float]],
        master_profile_data: list[tuple[float, float]],
        tolerance: float,
    ) -> GeologySegment | None:
        """Create segment from detached data."""
        rng = self._calculate_segment_range(seg_geom, line_start, da)
        if not rng:
            return None

        dist_start, dist_end = rng
        segment_points = self._convert_to_segment_points(
            dist_start, dist_end, master_grid_dists, master_profile_data, tolerance
        )

        return GeologySegment(
            unit_name=glg_val,
            geometry_wkt=(seg_geom.asWkt() if seg_geom and not seg_geom.isNull() else None),
            attributes=attributes,
            points=[(round(d, 1), round(e, 1)) for d, e in segment_points],
        )

    def _calculate_segment_range(
        self,
        seg_geom: QgsGeometry,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
    ) -> tuple[float, float] | None:
        """Calculate the start and end distance for a segment geometry."""
        verts = scu.get_line_vertices(seg_geom)
        if not verts:
            return None

        start_pt, end_pt = verts[0], verts[-1]
        dist_start = da.measureLine(line_start, start_pt)
        dist_end = da.measureLine(line_start, end_pt)

        if dist_start > dist_end:
            dist_start, dist_end = dist_end, dist_start

        return dist_start, dist_end

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

    def _process_detached_intersection(
        self,
        geom: QgsGeometry,
        attrs: dict[str, Any],
        unit_name: str,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
        master_grid_dists: list[tuple[float, tuple[float, float], float]],
        master_profile_data: list[tuple[float, float]],
        tolerance: float,
    ) -> list[GeologySegment]:
        """Process a detached intersection geometry to extract geology segments."""
        if not geom or geom.isNull():
            return []

        geometries = self._extract_geometries(geom)
        if not geometries:
            return []

        segments = []
        for seg_geom in geometries:
            segment = self._create_segment_from_geometry(
                seg_geom,
                attrs,
                unit_name,
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
        attrs: dict[str, Any],
        unit_name: str,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
        master_grid_dists: list[tuple[float, tuple[float, float], float]],
        master_profile_data: list[tuple[float, float]],
        tolerance: float,
    ) -> GeologySegment | None:
        """Create a GeologySegment from a geometry part by sampling elevations."""
        rng = self._calculate_segment_range(seg_geom, line_start, da)
        if not rng:
            return None

        dist_start, dist_end = rng
        segment_points = self._convert_to_segment_points(
            dist_start, dist_end, master_grid_dists, master_profile_data, tolerance
        )

        return GeologySegment(
            unit_name=unit_name,
            geometry_wkt=(seg_geom.asWkt() if seg_geom and not seg_geom.isNull() else None),
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
        master_grid_dists: list[tuple[float, tuple[float, float], float]],
        master_profile_data: list[tuple[float, float]],
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
