"""Drillhole Data Processing Service.

This module provides services for processing and projecting drillhole data,
including collar projection, trajectory calculation, and interval interpolation.
"""

from __future__ import annotations

import contextlib
from typing import Any, Optional

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsDistanceArea,
    QgsFeature,
    QgsFeatureRequest,
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
        dem_layer: QgsRasterLayer | None,
        line_crs: QgsCoordinateReferenceSystem | None = None,
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
            raise GeometryError(
                "Failed to create section line buffer", {"buffer_width": buffer_width}
            ) from e

        # Use centralized filtering utility which handles CRS transformation
        candidate_features = scu.filter_features_by_buffer(collar_layer, line_buffer, line_crs)

        if not candidate_features:
            logger.info("No collars found within buffer area.")
            return []

        for collar_feat in candidate_features:
            result = self._project_single_collar(
                collar_feat,
                line_geom,
                line_start,
                distance_area,
                buffer_width,
                collar_id_field,
                use_geometry,
                collar_x_field,
                collar_y_field,
                collar_z_field,
                collar_depth_field,
                dem_layer,
            )
            if result:
                projected_collars.append(result)

        logger.info(
            f"DrillholeService.project_collars END: Found {len(projected_collars)} collars."
        )
        return projected_collars

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
        """Generate drillhole trace and interval data and project onto the section.

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

        # 2. Bulk fetch survey and interval data for all relevant holes
        hole_ids = {cp[0] for cp in collar_points}
        surveys_map = self._fetch_bulk_data(survey_layer, hole_ids, survey_fields)
        intervals_map = self._fetch_bulk_data(interval_layer, hole_ids, interval_fields)

        for hole_id, _dist, collar_z, _off, given_depth in collar_points:
            collar_point = collar_coords.get(hole_id)
            if not collar_point:
                continue

            try:
                # 3. Process individual hole
                hole_geol, hole_drill = self._process_single_hole(
                    hole_id=hole_id,
                    collar_point=collar_point,
                    collar_z=collar_z,
                    given_depth=given_depth,
                    survey_data=surveys_map.get(hole_id, []),
                    intervals=intervals_map.get(hole_id, []),
                    line_geom=line_geom,
                    line_start=line_start,
                    distance_area=distance_area,
                    buffer_width=buffer_width,
                    section_azimuth=section_azimuth,
                )

                if hole_geol:
                    geol_data.extend(hole_geol)
                drillhole_data.append(hole_drill)
            except Exception as e:
                logger.exception(f"Failed to process hole {hole_id}: {type(e).__name__}: {e}")
                import traceback

                logger.exception(traceback.format_exc())
                raise

        return geol_data, drillhole_data

    def _fetch_bulk_data(
        self, layer: QgsVectorLayer, hole_ids: set[Any], fields: dict[str, str]
    ) -> dict[Any, list[tuple]]:
        """Fetch data for multiple holes in a single pass.

        Args:
            layer: Vector layer to fetch from.
            hole_ids: Set of hole IDs to filter.
            fields: Field mapping.

        Returns:
            A dictionary mapping hole_id to list of data tuples.

        """
        if not layer or not layer.isValid():
            return {}

        id_f = fields.get("id")
        if not id_f:
            return {}

        # Determine data tuple structure based on context (survey vs interval)
        is_survey = "depth" in fields

        # Validate all required fields are present
        required = ["depth", "azim", "incl"] if is_survey else ["from", "to", "lith"]

        for field_key in required:
            if not fields.get(field_key):
                return {}

        result_map: dict[Any, list[tuple]] = {}
        if not hole_ids:
            return {}

        # Use QgsFeatureRequest for efficient filtering
        ids_str = ", ".join([f"'{hid!s}'" for hid in hole_ids])
        request = QgsFeatureRequest().setFilterExpression(f'"{id_f}" IN ({ids_str})')

        for feat in layer.getFeatures(request):
            hole_id = feat[id_f]

            try:
                if is_survey:
                    data = (
                        float(feat[fields["depth"]]),
                        float(feat[fields["azim"]]),
                        float(feat[fields["incl"]]),
                    )
                else:
                    data = (
                        float(feat[fields["from"]]),
                        float(feat[fields["to"]]),
                        str(feat[fields["lith"]]),
                    )

                if hole_id not in result_map:
                    result_map[hole_id] = []
                result_map[hole_id].append(data)
            except (ValueError, TypeError, KeyError):
                continue

        # Sort surveys by depth
        if is_survey:
            for h_id in result_map:
                result_map[h_id].sort(key=lambda x: x[0])

        return result_map

    def _process_single_hole(
        self,
        hole_id: Any,
        collar_point: QgsPointXY,
        collar_z: float,
        given_depth: float,
        survey_data: list[tuple],
        intervals: list[tuple],
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        distance_area: QgsDistanceArea,
        buffer_width: float,
        section_azimuth: float,
    ) -> tuple[list[GeologySegment], tuple]:
        """Process a single drillhole's trajectory and intervals.

        Returns:
            A tuple of (hole_geol_data, drillhole_tuple).

        """
        # 1. Determine Final Depth
        max_s_depth = max([s[0] for s in survey_data]) if survey_data else 0.0
        max_i_depth = max([i[1] for i in intervals]) if intervals else 0.0
        final_depth = max(given_depth, max_s_depth, max_i_depth)

        # 2. Trajectory and Projection
        trajectory = scu.calculate_drillhole_trajectory(
            collar_point, collar_z, survey_data, section_azimuth, total_depth=final_depth
        )
        projected_traj = scu.project_trajectory_to_section(
            trajectory, line_geom, line_start, distance_area
        )

        # 3. Interpolate Intervals
        hole_geol_data = self._interpolate_hole_intervals(projected_traj, intervals, buffer_width)

        # 4. Store trace
        traj_points = [(p[4], p[3]) for p in projected_traj]

        return hole_geol_data, (hole_id, traj_points, hole_geol_data)

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

        # Fetch only necessary attributes and geometry
        if use_geom:
            # Need geometry and id_field only
            request = QgsFeatureRequest().setSubsetOfAttributes([id_field], layer.fields())
        else:
            # Need id_field, x_field, y_field but no geometry
            request = QgsFeatureRequest().setSubsetOfAttributes(
                [id_field, x_field, y_field], layer.fields()
            )
            request.setFlags(QgsFeatureRequest.NoGeometry)

        for feat in layer.getFeatures(request):
            hole_id = feat[id_field]
            pt = self._extract_point(feat, use_geom, x_field, y_field)
            if pt:
                coords[hole_id] = pt
        return coords

    def _extract_point(
        self, feat: QgsFeature, use_geom: bool, x_f: str, y_f: str
    ) -> QgsPointXY | None:
        """Extract point from feature geometry or fields."""
        if use_geom:
            geom = feat.geometry()
            if geom:
                pt = geom.asPoint()
                if pt.x() != 0 or pt.y() != 0:
                    return pt
        else:
            try:
                x, y = float(feat[x_f]), float(feat[y_f])
                if x != 0 or y != 0:
                    return QgsPointXY(x, y)
            except (ValueError, TypeError, KeyError):
                pass
        return None

    def _get_survey_data(self, layer, hole_id, fields):
        """Legacy support - redirected to bulk fetch if needed."""
        res = self._fetch_bulk_data(layer, {hole_id}, fields)
        return res.get(hole_id, [])

    def _get_interval_data(self, layer, hole_id, fields):
        """Legacy support - redirected to bulk fetch if needed."""
        res = self._fetch_bulk_data(layer, {hole_id}, fields)
        return res.get(hole_id, [])

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
            (fd, td, {"unit": lith, "from": fd, "to": td}) for fd, td, lith in intervals
        ]
        tuples = scu.interpolate_intervals_on_trajectory(traj, rich_intervals, buffer_width)

        segments = []
        for attr, points in tuples:
            segments.append(
                GeologySegment(
                    unit_name=str(attr.get("unit", "Unknown")),
                    geometry=None,
                    attributes=attr,
                    points=points,
                )
            )
        return segments

    def _project_single_collar(
        self,
        collar_feat: QgsFeature,
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
        dem_layer: QgsRasterLayer | None,
    ) -> tuple[Any, float, float, float, float] | None:
        """Process and project a single collar feature.

        Args:
            collar_feat: The collar feature to process.
            line_geom: Section line geometry.
            line_start: Start point of the section line.
            distance_area: Distance calculation object.
            buffer_width: Buffer width for filtering.
            collar_id_field: Field for ID.
            use_geometry: Whether to use geometry for coords.
            collar_x_field: Field for X.
            collar_y_field: Field for Y.
            collar_z_field: Field for Z.
            collar_depth_field: Field for depth.
            dem_layer: Optional DEM layer.

        Returns:
            Tuple of (hole_id, dist_along, z, offset, total_depth) or None.

        """
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
            return None

        hole_id, collar_point, z, depth = collar_info

        # 2. Project to section line
        collar_geom_pt = QgsGeometry.fromPointXY(collar_point)
        nearest_point = line_geom.nearestPoint(collar_geom_pt).asPoint()

        # Calculate distances
        dist_along = distance_area.measureLine(line_start, nearest_point)
        offset = distance_area.measureLine(collar_point, nearest_point)

        # Check if within buffer
        if offset <= buffer_width:
            return (hole_id, dist_along, z, offset, depth)

        return None

    def _get_collar_info(
        self,
        feat: QgsFeature,
        id_field: str,
        use_geom: bool,
        x_field: str,
        y_field: str,
        z_field: str,
        depth_field: str,
        dem_layer: QgsRasterLayer | None = None,
    ) -> tuple[Any, QgsPointXY, float, float] | None:
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

        # Point extraction
        pt = self._extract_point(feat, use_geom, x_field, y_field)
        if not pt:
            return None

        # Z logic
        z = 0.0
        if z_field:
            with contextlib.suppress(ValueError, TypeError):
                z = float(feat[z_field])

        if z == 0.0 and dem_layer:
            z = self._sample_dem(dem_layer, pt)

        # Depth
        depth = 0.0
        if depth_field:
            with contextlib.suppress(ValueError, TypeError):
                depth = float(feat[depth_field])

        return hole_id, pt, z, depth

    def _sample_dem(self, dem_layer: QgsRasterLayer, pt: QgsPointXY) -> float:
        """Sample elevation at point from DEM."""
        ident = dem_layer.dataProvider().identify(pt, QgsRaster.IdentifyFormatValue)
        if ident.isValid():
            val = ident.results().get(1)
            if val is not None:
                return float(val)
        return 0.0
