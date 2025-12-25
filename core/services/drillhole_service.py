from __future__ import annotations


"""Drillhole Data Processing Service.

This module provides services for processing and projecting drillhole data,
including collar projection, trajectory calculation, and interval interpolation.
"""

import contextlib
from typing import Any, Optional

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsDistanceArea,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsRaster,
    QgsRasterLayer,
    QgsSpatialIndex,
    QgsVectorLayer,
)

from sec_interp.core import utils as scu
from sec_interp.core.exceptions import DataMissingError, GeometryError, ProcessingError
from sec_interp.core.interfaces.drillhole_interface import IDrillholeService
from sec_interp.core.types import GeologySegment
from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


class DrillholeService(IDrillholeService):
    """Service for processing drillhole data."""

    def project_collars(
        self,
        collar_layer: QgsVectorLayer,
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        distance_area: QgsDistanceArea,
        buffer_width: float,
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        collar_z_field: str,
        collar_depth_field: str,
        dem_layer: Optional[QgsRasterLayer],
        line_crs: Optional[QgsCoordinateReferenceSystem] = None,
    ) -> list[tuple[Any, float, float, float, float]]:
        """Project collar points onto section line using spatial optimization.

        Args:
            collar_layer: Vector layer containing drillhole collars.
            line_geom: Geometry of the cross-section line.
            line_start: Start point of the section line.
            distance_area: Distance calculation object.
            buffer_width: Search buffer distance in meters.
            collar_id_field: Field name for unique drillhole ID.
            use_geometry: Whether to use feature geometry for X/Y coordinates.
            collar_x_field: Field name for X coordinate (if not using geometry).
            collar_y_field: Field name for Y coordinate (if not using geometry).
            collar_z_field: Field name for collar elevation.
            collar_depth_field: Field name for total drillhole depth.
            dem_layer: Optional DEM layer for elevation if Z field is missing/zero.
            line_crs: CRS of the section line for spatial filtering.

        Returns:
            A list of tuples (hole_id, dist_along, z, offset, total_depth).
        """
        if not collar_layer:
            raise DataMissingError("Collar layer is not provided")

        projected_collars = []
        logger.info(f"Projecting collars from {collar_layer.name()} with buffer {buffer_width}m")

        # 1. Spatial Filtering
        # Create buffer zone around section line
        try:
            line_buffer = line_geom.buffer(buffer_width, 8)
        except Exception as e:
            raise GeometryError("Failed to create section line buffer", {"buffer_width": buffer_width}) from e

        # Use centralized filtering utility which handles CRS transformation
        candidate_features = scu.filter_features_by_buffer(
            collar_layer, line_buffer, line_crs
        )

        if not candidate_features:
            logger.info("No collars found within buffer area.")
            return []

        for collar_feat in candidate_features:
            # 1. Get Collar Info
            collar_info = self._get_collar_info(
                collar_feat,
                collar_id_field,
                use_geometry,
                collar_x_field,
                collar_y_field,
                collar_z_field,
                collar_depth_field,
                dem_layer,
            )
            if not collar_info:
                continue

            hole_id, collar_point, z, depth = collar_info

            # 2. Project to section line
            collar_geom_pt = QgsGeometry.fromPointXY(collar_point)
            nearest_point = line_geom.nearestPoint(collar_geom_pt).asPoint()

            # Calculate distances
            dist_along = distance_area.measureLine(line_start, nearest_point)
            offset = distance_area.measureLine(collar_point, nearest_point)

            # Check if within buffer
            if offset <= buffer_width:
                projected_collars.append((hole_id, dist_along, z, offset, depth))

        logger.info(
            f"DrillholeService.project_collars END: Found {len(projected_collars)} collars."
        )
        return projected_collars

    def _get_collar_info(
        self,
        feat: QgsFeature,
        id_field: str,
        use_geom: bool,
        x_field: str,
        y_field: str,
        z_field: str,
        depth_field: str,
        dem_layer: Optional[QgsRasterLayer] = None,
    ) -> Optional[tuple[Any, QgsPointXY, float, float]]:
        """Extract collar ID, coordinate, Z and depth from a feature.

        Args:
            feat: The collar feature to parse.
            id_field: Field name for hole ID.
            use_geom: Whether to use geometry for coordinates.
            x_field: Field name for X coordinate.
            y_field: Field name for Y coordinate.
            z_field: Field name for Z coordinate.
            depth_field: Field name for total depth.
            dem_layer: Optional DEM layer for fallback elevation.

        Returns:
            A tuple of (hole_id, point, elevation, total_depth) or None if invalid.
        """
        if not id_field:
            return None
        hole_id = feat[id_field]
        x, y, z, depth = 0.0, 0.0, 0.0, 0.0

        if use_geom:
            geom = feat.geometry()
            if not geom:
                return None
            pt = geom.asPoint()
            x, y = pt.x(), pt.y()
        else:
            try:
                x = float(feat[x_field])
                y = float(feat[y_field])
            except (ValueError, TypeError):
                return None

        if x == 0.0 and y == 0.0:
            return None

        # Z
        if z_field:
            with contextlib.suppress(ValueError, TypeError):
                z = float(feat[z_field])

        if z == 0.0 and dem_layer:
            ident = dem_layer.dataProvider().identify(
                QgsPointXY(x, y), QgsRaster.IdentifyFormatValue
            )
            if ident.isValid():
                val = ident.results().get(1)
                if val is not None:
                    z = val

        # Depth
        if depth_field:
            with contextlib.suppress(ValueError, TypeError):
                depth = float(feat[depth_field])

        return hole_id, QgsPointXY(x, y), z, depth

    def process_intervals(
        self,
        collar_points: list[tuple],
        collar_layer: QgsVectorLayer,
        survey_layer: QgsVectorLayer,
        interval_layer: QgsVectorLayer,
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        distance_area: QgsDistanceArea,
        buffer_width: float,
        section_azimuth: float,
        survey_fields: dict[str, str],
        interval_fields: dict[str, str],
    ) -> tuple[
        list[GeologySegment],
        list[tuple[Any, list[tuple[float, float]], list[GeologySegment]]],
    ]:
        """Process drillhole interval data and project onto the section.

        Args:
            collar_points: List of projected collar tuples from `project_collars`.
            collar_layer: The collar vector layer.
            survey_layer: The survey vector layer.
            interval_layer: The interval/geology vector layer.
            collar_id_field: Field name for hole ID in collar layer.
            use_geometry: Use geometry for collar coordinates.
            collar_x_field: Field name for X in collar layer.
            collar_y_field: Field name for Y in collar layer.
            line_geom: Section line geometry.
            line_start: Section line start point.
            distance_area: Distance calculation object.
            buffer_width: Section buffer width in meters.
            section_azimuth: Azimuth of the section line.
            survey_fields: Mapping of survey field roles to field names.
            interval_fields: Mapping of interval field roles to field names.

        Returns:
            A tuple of (geol_data, drillhole_data).
        """
        geol_data, drillhole_data = [], []

        # 1. Build collar coordinate map
        collar_coords = self._build_collar_coord_map(
            collar_layer, collar_id_field, use_geometry, collar_x_field, collar_y_field
        )

        for hole_id, _dist, collar_z, _off, given_depth in collar_points:
            collar_point = collar_coords.get(hole_id)
            if not collar_point:
                continue

            # 2. Get Data
            survey_data = self._get_survey_data(survey_layer, hole_id, survey_fields)
            intervals = self._get_interval_data(interval_layer, hole_id, interval_fields)

            # 3. Determine Final Depth
            max_survey_depth = max([s[0] for s in survey_data]) if survey_data else 0.0
            max_interval_depth = max([i[1] for i in intervals]) if intervals else 0.0
            final_depth = max(given_depth, max_survey_depth, max_interval_depth)

            # 4. Trajectory and Projection
            trajectory = scu.calculate_drillhole_trajectory(
                collar_point, collar_z, survey_data, section_azimuth, total_depth=final_depth
            )
            projected_traj = scu.project_trajectory_to_section(
                trajectory, line_geom, line_start, distance_area
            )

            # 5. Interpolate Intervals
            hole_geol_data = self._interpolate_hole_intervals(
                projected_traj, intervals, buffer_width
            )

            if hole_geol_data:
                geol_data.extend(hole_geol_data)

            # 6. Store trace
            traj_points = [(p[4], p[3]) for p in projected_traj]
            drillhole_data.append((hole_id, traj_points, hole_geol_data))

        return geol_data, drillhole_data

    def _build_collar_coord_map(self, layer, id_field, use_geom, x_field, y_field):
        """Build a lookup map for collar coordinates.

        Args:
            layer: The collar vector layer.
            id_field: Field name for hole ID.
            use_geom: Whether to use feature geometry.
            x_field: Field name for X.
            y_field: Field name for Y.

        Returns:
            A dictionary mapping hole_id to QgsPointXY.
        """
        if not layer or not id_field:
            return {}
        coords = {}
        for feat in layer.getFeatures():
            hole_id = feat[id_field]
            if use_geom:
                geom = feat.geometry()
                if geom:
                    pt = geom.asPoint()
                    if pt.x() != 0 and pt.y() != 0:
                        coords[hole_id] = pt
            else:
                try:
                    x, y = float(feat[x_field]), float(feat[y_field])
                    if x != 0 and y != 0:
                        coords[hole_id] = QgsPointXY(x, y)
                except (ValueError, TypeError):
                    continue
        return coords

    def _get_survey_data(self, layer, hole_id, fields):
        """Fetch survey data for a specific hole from a survey layer.

        Args:
            layer: The survey vector layer.
            hole_id: The ID of the drillhole.
            fields: Mapping of field roles (id, depth, azim, incl).

        Returns:
            A list of (depth, azimuth, inclination) tuples sorted by depth.
        """
        if not layer or not fields.get("id"):
            return []
        data = []
        for feat in layer.getFeatures():
            if feat[fields["id"]] == hole_id:
                try:
                    d = float(feat[fields["depth"]])
                    a = float(feat[fields["azim"]])
                    i = float(feat[fields["incl"]])
                    data.append((d, a, i))
                except (ValueError, TypeError):
                    continue
        data.sort(key=lambda x: x[0])
        return data

    def _get_interval_data(self, layer, hole_id, fields):
        """Fetch interval data for a specific hole from an interval layer.

        Args:
            layer: The interval vector layer.
            hole_id: The ID of the drillhole.
            fields: Mapping of field roles (id, from, to, lith).

        Returns:
            A list of (from_depth, to_depth, lithology) tuples.
        """
        if not layer or not fields.get("id"):
            return []
        data = []
        for feat in layer.getFeatures():
            if feat[fields["id"]] == hole_id:
                try:
                    fd = float(feat[fields["from"]])
                    td = float(feat[fields["to"]])
                    lith = str(feat[fields["lith"]])
                    data.append((fd, td, lith))
                except (ValueError, TypeError):
                    continue
        return data

    def _interpolate_hole_intervals(self, traj, intervals, buffer_width):
        """Interpolate intervals along a trajectory and return GeologySegments.

        Args:
            traj: The projected trajectory tuples.
            intervals: List of (from, to, lith) tuples.
            buffer_width: Section buffer width.

        Returns:
            A list of GeologySegment objects.
        """
        if not intervals:
            return []

        rich_intervals = [
            (fd, td, {"unit": lith, "from": fd, "to": td})
            for fd, td, lith in intervals
        ]
        tuples = scu.interpolate_intervals_on_trajectory(traj, rich_intervals, buffer_width)

        segments = []
        for attr, points in tuples:
            segments.append(GeologySegment(
                unit_name=str(attr.get("unit", "Unknown")),
                geometry=None,
                attributes=attr,
                points=points,
            ))
        return segments
