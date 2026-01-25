from __future__ import annotations

"""Drillhole Data Processing Service.

This module provides services for processing and projecting drillhole data,
including collar projection, trajectory calculation, and interval interpolation.
"""

import contextlib
from typing import Any

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsDistanceArea,
    QgsFeature,
    QgsFeatureRequest,
    QgsGeometry,
    QgsPointXY,
    QgsRaster,
    QgsRasterLayer,
    QgsVectorLayer,
)

from sec_interp.core import utils as scu
from sec_interp.core.interfaces.drillhole_interface import IDrillholeService
from sec_interp.core.types import DrillholeTaskInput, GeologySegment
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class DrillholeService(IDrillholeService):
    """Service for processing drillhole data."""

    def project_collars(
        self,
        collar_data: list[dict[str, Any]],
        line_data: Any,
        distance_area: Any,
        buffer_width: float,
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        collar_z_field: str,
        collar_depth_field: str,
        pre_sampled_z: dict[Any, float] | None = None,
    ) -> list[tuple[Any, float, float, float, float]]:
        """Project collar points onto section line using detached domain data."""
        projected_collars = []

        # Get line start point
        line_start = QgsPointXY(line_data.vertexAt(0).x(), line_data.vertexAt(0).y())

        for c_item in collar_data:
            result = self._project_single_detached_collar(
                c_item,
                line_data,
                line_start,
                distance_area,
                buffer_width,
                collar_id_field,
                use_geometry,
                collar_x_field,
                collar_y_field,
                collar_z_field,
                collar_depth_field,
                pre_sampled_z,
            )
            if result:
                projected_collars.append(result)

        return projected_collars

    def _validate_project_collars_params(
        self,
        fields: Any,
        buffer_width: float,
        id_field: str,
        use_geom: bool,
        x_field: str,
        y_field: str,
    ) -> None:
        """Validate parameters for project_collars."""
        from sec_interp.core.exceptions import ValidationError

        if buffer_width <= 0:
            raise ValidationError(f"Buffer width must be positive, got {buffer_width}")

        if id_field and fields.indexFromName(id_field) == -1:
            raise ValidationError(f"Field '{id_field}' not found in collar data fields.")

        if not use_geom:
            for f_name in [x_field, y_field]:
                if f_name and fields.indexFromName(f_name) == -1:
                    raise ValidationError(f"Field '{f_name}' not found in collar data fields.")

    def prepare_task_input(
        self,
        line_layer: QgsVectorLayer,
        buffer_width: float,
        # Collar Params
        collar_layer: QgsVectorLayer,
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        collar_z_field: str,
        collar_depth_field: str,
        # Child Data params
        survey_layer: QgsVectorLayer,
        survey_fields: dict[str, str],
        interval_layer: QgsVectorLayer,
        interval_fields: dict[str, str],
        # Optional
        dem_layer: QgsRasterLayer | None = None,
        band_num: int = 1,
    ) -> DrillholeTaskInput:
        """Prepare detached domain data for async processing.

        This method centralizes the extraction of data from QGIS layers in the
        Main Thread, creating a detached DrillholeTaskInput DTO.
        """
        line_feat = next(line_layer.getFeatures(), None)
        if not line_feat:
            from sec_interp.core.exceptions import DataMissingError

            raise DataMissingError("Line layer has no features")

        line_geom = line_feat.geometry()
        line_crs = line_layer.crs()

        # Calculate line start and azimuth
        line_start = (
            line_geom.asPolyline()[0]
            if not line_geom.isMultipart()
            else line_geom.asMultiPolyline()[0][0]
        )

        p1 = line_start
        p2_vertex = line_geom.vertexAt(1)
        p2 = QgsPointXY(p2_vertex.x(), p2_vertex.y())
        section_azimuth = p1.azimuth(p2)
        if section_azimuth < 0:
            section_azimuth += 360

        self._validate_prepare_task_params(
            buffer_width,
            section_azimuth,
            collar_layer,
            collar_id_field,
            use_geometry,
            collar_x_field,
            collar_y_field,
        )

        # 1. Filter and Detach Collars
        collar_ids, collar_data, pre_sampled_z = self._detach_collar_features(
            collar_layer,
            line_geom,
            buffer_width,
            collar_id_field,
            use_geometry,
            collar_x_field,
            collar_y_field,
            collar_z_field,
            dem_layer,
        )

        # 2. Bulk Fetch Child Data (Sync)
        survey_map = self._fetch_bulk_data_detached(survey_layer, collar_ids, survey_fields)
        interval_map = self._fetch_bulk_data_detached(interval_layer, collar_ids, interval_fields)

        return DrillholeTaskInput(
            line_geometry_wkt=line_geom.asWkt(),
            line_start_x=line_start.x(),
            line_start_y=line_start.y(),
            line_crs_authid=line_crs.authid(),
            section_azimuth=section_azimuth,
            buffer_width=buffer_width,
            collar_id_field=collar_id_field,
            use_geometry=use_geometry,
            collar_x_field=collar_x_field,
            collar_y_field=collar_y_field,
            collar_z_field=collar_z_field,
            collar_depth_field=collar_depth_field,
            collar_data=collar_data,
            survey_data=survey_map,
            interval_data=interval_map,
            pre_sampled_z=pre_sampled_z,
        )

    def _validate_prepare_task_params(
        self,
        buffer_width: float,
        section_azimuth: float,
        collar_layer: QgsVectorLayer,
        id_field: str,
        use_geom: bool,
        x_field: str,
        y_field: str,
    ) -> None:
        """Validate parameters for prepare_task_input.

        Args:
            buffer_width: Buffer distance.
            section_azimuth: Section orientation.
            collar_layer: Layer to check.
            id_field: ID field name.
            use_geom: Whether geometric extraction is active.
            x_field: X field for fallback.
            y_field: Y field for fallback.

        Raises:
            ValidationError: If any constraint fails.

        """
        from sec_interp.core.exceptions import ValidationError
        from sec_interp.core.validation.validators import (
            validate_positive,
            validate_range,
        )

        validate_positive("Buffer width")(buffer_width)
        validate_range(0, 360, "Section azimuth")(section_azimuth)

        fields = collar_layer.fields()
        if id_field and fields.indexFromName(id_field) == -1:
            raise ValidationError(f"Collar ID field '{id_field}' not found.")

        if not use_geom:
            for f in [x_field, y_field]:
                if f and fields.indexFromName(f) == -1:
                    raise ValidationError(f"Field '{f}' not found for coordinate extraction.")
            if y_field and collar_layer.fields().indexFromName(y_field) == -1:
                raise ValidationError(f"Field '{y_field}' not found in collar layer.")

    def _detach_collar_features(
        self,
        layer: QgsVectorLayer,
        line_geom: QgsGeometry,
        buffer_width: float,
        id_field: str,
        use_geom: bool,
        x_field: str,
        y_field: str,
        z_field: str,
        dem_layer: QgsRasterLayer | None,
    ) -> tuple[set[Any], list[dict[str, Any]], dict[Any, float]]:
        """Detach collar features and pre-sample Z using WKT for decoupling."""
        try:
            line_buffer = line_geom.buffer(buffer_width, 8)
        except Exception:
            line_buffer = None

        collar_bbox = line_buffer.boundingBox() if line_buffer else line_geom.boundingBox()
        req = QgsFeatureRequest().setFilterRect(collar_bbox)

        collar_ids = set()
        collar_data = []
        pre_sampled_z = {}

        for feat in layer.getFeatures(req):
            if line_buffer and not feat.geometry().intersects(line_buffer):
                continue

            hid = feat[id_field]
            collar_ids.add(hid)

            # Detach geometry as WKT and attributes
            wkt = feat.geometry().asWkt() if feat.hasGeometry() else None
            attrs = dict(zip(feat.fields().names(), feat.attributes(), strict=False))

            collar_data.append({"wkt": wkt, "attributes": attrs, "id": hid})

            # Pre-sample Z
            if dem_layer:
                z = self._pre_sample_z_for_task(
                    feat,
                    hydro_id=hid,
                    dem_layer=dem_layer,
                    z_field=z_field,
                    use_geom=use_geom,
                    x_field=x_field,
                    y_field=y_field,
                )
                if z is not None:
                    pre_sampled_z[hid] = z

        return collar_ids, collar_data, pre_sampled_z

    def _pre_sample_z_for_task(
        self,
        feat: QgsFeature,
        hydro_id: Any,
        dem_layer: QgsRasterLayer,
        z_field: str,
        use_geom: bool,
        x_field: str,
        y_field: str,
    ) -> float | None:
        """Sample Z from DEM if missing in features."""
        z_val = 0.0
        try:
            if z_field:
                z_val = float(feat[z_field] or 0.0)
        except (ValueError, TypeError):
            z_val = 0.0

        if z_val == 0.0:
            pt = self._extract_point(feat, use_geom, x_field, y_field)
            if pt:
                return self._sample_dem(dem_layer, pt)
        return None

    def process_task_data(self, task_input: DrillholeTaskInput, feedback: Any | None = None) -> Any:
        """Process drillholes using detached domain data (Thread-Safe)."""
        # Reconstruct Objects
        line_crs = QgsCoordinateReferenceSystem(task_input.line_crs_authid)
        da = scu.create_distance_area(line_crs)
        line_geom = QgsGeometry.fromWkt(task_input.line_geometry_wkt)
        line_start = QgsPointXY(task_input.line_start_x, task_input.line_start_y)

        geol_data_all = []
        drillhole_data_all = []  # (hid, trace2d, trace3d, proj3d, geologic_segments)

        total = len(task_input.collar_data)

        for i, c_item in enumerate(task_input.collar_data):
            if feedback and feedback.isCanceled():
                return None

            # Process each collar and its associated data
            result = self._process_detached_collar_item(
                c_item, task_input, da, line_geom, line_start
            )
            if result:
                hole_geol, hole_tuple = result
                geol_data_all.extend(hole_geol)
                drillhole_data_all.append(hole_tuple)

            if feedback:
                feedback.setProgress((i / total) * 100)

        return geol_data_all, drillhole_data_all

    def _process_detached_collar_item(
        self,
        c_item: dict[str, Any],
        task_input: DrillholeTaskInput,
        da: QgsDistanceArea,
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
    ) -> tuple[list[GeologySegment], tuple] | None:
        """Process a single detached collar item."""
        # 1. Project collar using the common logic
        result = self._project_single_detached_collar(
            c_item,
            line_geom,
            line_start,
            da,
            task_input.buffer_width,
            task_input.collar_id_field,
            task_input.use_geometry,
            task_input.collar_x_field,
            task_input.collar_y_field,
            task_input.collar_z_field,
            task_input.collar_depth_field,
            task_input.pre_sampled_z,
        )

        if not result:
            return None

        hole_id, _dist, z, _offset, depth = result

        # 2. Extract point for single hole processing
        pt = self._extract_point_agnostic(
            c_item,
            True,  # it's a dict
            task_input.use_geometry,
            task_input.collar_x_field,
            task_input.collar_y_field,
        )

        if not pt:
            return None

        # 3. Full Processing
        surveys = task_input.survey_data.get(hole_id, [])
        intervals = task_input.interval_data.get(hole_id, [])

        return self._process_single_hole(
            hole_id=hole_id,
            collar_point=pt,
            collar_z=z,
            given_depth=depth,
            survey_data=surveys,
            intervals=intervals,
            line_geom=line_geom,
            line_start=line_start,
            distance_area=da,
            buffer_width=task_input.buffer_width,
            section_azimuth=task_input.section_azimuth,
        )

    def process_intervals(
        self,
        collar_points: list[tuple],
        collar_data: list[dict[str, Any]],
        survey_data: dict[Any, list[tuple]],
        interval_data: dict[Any, list[tuple]],
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        line_data: Any,
        distance_area: Any,
        buffer_width: float,
        section_azimuth: float,
        survey_fields: dict[str, str],
        interval_fields: dict[str, str],
    ) -> tuple[list, list]:
        """Process drillhole interval data using detached structures."""
        geol_data, drillhole_data = [], []

        # 1. Build collar coordinate map from detached data
        collar_coords = {}
        for item in collar_data:
            hid = item["id"]
            wkt = item.get("wkt")
            attrs = item["attributes"]
            pt = None
            if use_geometry and wkt:
                pt = QgsGeometry.fromWkt(wkt).asPoint()
            else:
                with contextlib.suppress(ValueError, TypeError, KeyError):
                    x, y = float(attrs.get(collar_x_field, 0)), float(attrs.get(collar_y_field, 0))
                    pt = QgsPointXY(x, y)
            if pt:
                collar_coords[hid] = pt

        for hole_id, _dist, collar_z, _off, given_depth in collar_points:
            collar_point = collar_coords.get(hole_id)
            if not collar_point:
                continue

            self._safe_process_single_hole(
                hole_id,
                collar_point,
                collar_z,
                given_depth,
                survey_data,
                interval_data,
                line_data,
                collar_point,  # Note: safe_process_single_hole signature might need line_start
                distance_area,
                buffer_width,
                section_azimuth,
                geol_data,
                drillhole_data,
            )

        return geol_data, drillhole_data

    def _fetch_bulk_data(
        self, layer: QgsVectorLayer, hole_ids: set[Any], fields: dict[str, str]
    ) -> dict[Any, list[tuple[Any, ...]]]:
        """Fetch data for multiple holes in a single pass."""
        if not self._validate_bulk_fetch_fields(layer, fields):
            return {}

        result_map: dict[Any, list[tuple]] = {}
        if not hole_ids:
            return {}

        id_f = fields["id"]
        is_survey = "depth" in fields

        ids_str = ", ".join([f"'{hid!s}'" for hid in hole_ids])
        request = QgsFeatureRequest().setFilterExpression(f'"{id_f}" IN ({ids_str})')

        for feat in layer.getFeatures(request):
            hole_id = feat[id_f]
            data = self._extract_data_tuple(feat, fields, is_survey)
            if data:
                result_map.setdefault(hole_id, []).append(data)

        # Sort surveys by depth
        if is_survey:
            for h_id in result_map:
                result_map[h_id].sort(key=lambda x: x[0])

        return result_map

    def _validate_bulk_fetch_fields(self, layer: QgsVectorLayer, fields: dict[str, str]) -> bool:
        """Validate fields for bulk fetching."""
        if not layer or not layer.isValid():
            return False

        id_f = fields.get("id")
        if not id_f or layer.fields().indexFromName(id_f) == -1:
            return False

        is_survey = "depth" in fields
        required = ["depth", "azim", "incl"] if is_survey else ["from", "to", "lith"]

        for field_key in required:
            f_name = fields.get(field_key)
            if not f_name or layer.fields().indexFromName(f_name) == -1:
                return False

        return True

    def _fetch_bulk_data_detached(
        self, layer: QgsVectorLayer, hole_ids: set[Any], fields: dict[str, str]
    ) -> dict[Any, list[tuple]]:
        """Fetch data into pure python structures (no QgsFeature dependency)."""
        # This is essentially the same as _fetch_bulk_data but guarantees primitive types
        # in the returned list, which _extract_data_tuple already does.
        # So we can reuse the logic but ensures it runs on Main Thread in prepare()
        return self._fetch_bulk_data(layer, hole_ids, fields)

    def _process_single_hole(
        self,
        hole_id: Any,
        collar_point: QgsPointXY,
        collar_z: float,
        given_depth: float,
        survey_data: list[tuple[float, float, float]],
        intervals: list[tuple[float, float, str]],
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        distance_area: QgsDistanceArea,
        buffer_width: float,
        section_azimuth: float,
    ) -> tuple[list[GeologySegment], tuple]:
        """Process a single drillhole's trajectory and intervals."""
        # 1. Determine Final Depth
        final_depth = self._determine_final_depth(given_depth, survey_data, intervals)

        # 2. Trajectory and Projection
        trajectory = scu.calculate_drillhole_trajectory(
            collar_point,
            collar_z,
            survey_data,
            section_azimuth,
            total_depth=final_depth,
        )
        projected_traj = scu.project_trajectory_to_section(
            trajectory, line_geom, line_start, distance_area
        )

        # 3. Interpolate Intervals
        hole_geol_data = self._interpolate_hole_intervals(projected_traj, intervals, buffer_width)

        # 4. Generate trace results
        hole_tuple = self._create_drillhole_result_tuple(hole_id, projected_traj, hole_geol_data)

        return hole_geol_data, hole_tuple

    def _determine_final_depth(
        self, given_depth: float, survey_data: list[tuple], intervals: list[tuple]
    ) -> float:
        """Determine final depth from given depth, surveys and intervals."""
        max_s_depth = max([s[0] for s in survey_data]) if survey_data else 0.0
        max_i_depth = max([i[1] for i in intervals]) if intervals else 0.0
        return max(given_depth, max_s_depth, max_i_depth)

    def _create_drillhole_result_tuple(
        self,
        hole_id: Any,
        projected_traj: list[tuple],
        hole_geol_data: list[GeologySegment],
    ) -> tuple:
        """Create the final result tuple for a drillhole."""
        traj_points_2d = [(p[4], p[3]) for p in projected_traj]
        traj_points_3d = [(p[1], p[2], p[3]) for p in projected_traj]
        traj_points_3d_proj = [(p[6], p[7], p[3]) for p in projected_traj]

        return (
            hole_id,
            traj_points_2d,
            traj_points_3d,
            traj_points_3d_proj,
            hole_geol_data,
        )

    def _build_collar_coord_map(
        self,
        layer: QgsVectorLayer,
        id_field: str,
        use_geom: bool,
        x_field: str,
        y_field: str,
    ) -> dict[Any, QgsPointXY]:
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

    def _get_survey_data(
        self, layer: QgsVectorLayer, hole_id: Any, fields: dict[str, str]
    ) -> list[tuple[Any, ...]]:
        """Legacy support - redirected to bulk fetch if needed."""
        res = self._fetch_bulk_data(layer, {hole_id}, fields)
        return res.get(hole_id, [])

    def _get_interval_data(
        self, layer: QgsVectorLayer, hole_id: Any, fields: dict[str, str]
    ) -> list[tuple[Any, ...]]:
        """Legacy support - redirected to bulk fetch if needed."""
        res = self._fetch_bulk_data(layer, {hole_id}, fields)
        return res.get(hole_id, [])

    def _interpolate_hole_intervals(
        self,
        traj: list[tuple[float, float, float, float, float]],
        intervals: list[tuple[float, float, str]],
        buffer_width: float,
    ) -> list[GeologySegment]:
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
        # Scu returns (attr, points_2d, points_3d, points_3d_proj)
        tuples = scu.interpolate_intervals_on_trajectory(traj, rich_intervals, buffer_width)

        segments = []
        for attr, points_2d, points_3d, points_3d_proj in tuples:
            segments.append(
                GeologySegment(
                    unit_name=str(attr.get("unit", "Unknown")),
                    geometry_wkt=None,
                    attributes=attr,
                    points=points_2d,
                    points_3d=points_3d,
                    points_3d_projected=points_3d_proj,
                )
            )
        return segments

    def _project_single_detached_collar(
        self,
        collar_data: dict[str, Any] | QgsFeature,
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
        pre_sampled_z: dict[Any, float] | None = None,
        dem_layer: QgsRasterLayer | None = None,
    ) -> tuple[Any, float, float, float, float] | None:
        """Process and project a single collar from either dict or feature."""
        # 1. Extract Data agnosticly
        extracted = self._extract_attributes_agnostic(
            collar_data,
            collar_id_field,
            use_geometry,
            collar_x_field,
            collar_y_field,
            collar_z_field,
            collar_depth_field,
            pre_sampled_z,
            dem_layer,
        )

        if not extracted:
            return None

        hole_id, collar_pt, z, total_depth = extracted

        # 2. Project to section line
        projection = self._project_point_to_line(collar_pt, line_geom, line_start, distance_area)
        dist_along, offset = projection

        # 3. Check if within buffer
        if offset <= buffer_width:
            return (hole_id, dist_along, z, offset, total_depth)

        return None

    def _extract_attributes_agnostic(
        self,
        data: dict[str, Any] | QgsFeature,
        id_field: str,
        use_geometry: bool,
        x_field: str,
        y_field: str,
        z_field: str,
        depth_field: str,
        pre_sampled_z: dict[Any, float] | None = None,
        dem_layer: QgsRasterLayer | None = None,
    ) -> tuple[Any, QgsPointXY, float, float] | None:
        """Extract collar ID, coordinate, Z and depth agnosticly from dict or feature."""
        is_dict = isinstance(data, dict)
        attrs = data.get("attributes", {}) if is_dict else data

        # ID
        try:
            hole_id = attrs.get(id_field) if is_dict else attrs[id_field]
        except (KeyError, AttributeError):
            return None
        if not hole_id:
            return None

        # Point
        collar_pt = self._extract_point_agnostic(data, is_dict, use_geometry, x_field, y_field)
        if not collar_pt:
            return None

        # Z
        z = self._extract_z_agnostic(
            data, is_dict, z_field, hole_id, collar_pt, pre_sampled_z, dem_layer
        )

        # Depth
        depth = self._extract_depth_agnostic(data, is_dict, depth_field)

        return hole_id, collar_pt, z, depth

    def _extract_point_agnostic(
        self, data: Any, is_dict: bool, use_geom: bool, x_f: str, y_f: str
    ) -> QgsPointXY | None:
        """Extract point from geometry or fields agnosticly."""
        if use_geom:
            if is_dict:
                wkt = data.get("wkt", "")
                if wkt:
                    geom = QgsGeometry.fromWkt(wkt)
                    if not geom.isNull() and not geom.isEmpty():
                        pt = geom.asPoint()
                        return QgsPointXY(pt.x(), pt.y())
            else:
                geom = data.geometry()
                if not geom.isNull() and not geom.isEmpty():
                    pt = geom.asPoint()
                    return QgsPointXY(pt.x(), pt.y())

        # Fallback to fields
        attrs = data.get("attributes", {}) if is_dict else data
        try:
            x = float(attrs.get(x_f, 0.0)) if is_dict else float(attrs[x_f] or 0.0)
            y = float(attrs.get(y_f, 0.0)) if is_dict else float(attrs[y_f] or 0.0)
            return QgsPointXY(x, y)
        except (ValueError, TypeError, KeyError):
            return None

    def _extract_z_agnostic(
        self,
        data: Any,
        is_dict: bool,
        z_f: str,
        hole_id: Any,
        pt: QgsPointXY,
        pre_sampled: dict[Any, float] | None,
        dem: QgsRasterLayer | None,
    ) -> float:
        """Extract Z with fallbacks agnosticly."""
        attrs = data.get("attributes", {}) if is_dict else data
        z = 0.0
        if z_f:
            with contextlib.suppress(ValueError, TypeError, KeyError):
                z = float(attrs.get(z_f, 0.0)) if is_dict else float(attrs[z_f] or 0.0)

        if z == 0.0:
            if pre_sampled and hole_id in pre_sampled:
                z = pre_sampled[hole_id]
            elif dem:
                z = self._sample_dem(dem, pt)
        return z

    def _extract_depth_agnostic(self, data: Any, is_dict: bool, depth_f: str) -> float:
        """Extract depth agnosticly."""
        attrs = data.get("attributes", {}) if is_dict else data
        depth = 0.0
        if depth_f:
            with contextlib.suppress(ValueError, TypeError, KeyError):
                depth = float(attrs.get(depth_f, 0.0)) if is_dict else float(attrs[depth_f] or 0.0)
        return depth

    def _project_point_to_line(
        self,
        pt: QgsPointXY,
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
    ) -> tuple[float, float]:
        """Project point to line and return (dist_along, offset)."""
        collar_geom_pt = QgsGeometry.fromPointXY(pt)
        nearest_point_geom = line_geom.nearestPoint(collar_geom_pt)
        nearest_point = nearest_point_geom.asPoint()
        nearest_point_xy = QgsPointXY(nearest_point.x(), nearest_point.y())

        dist_along = da.measureLine(line_start, nearest_point_xy)
        offset = da.measureLine(pt, nearest_point_xy)
        return dist_along, offset

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
        """Extract collar ID, coordinate, Z and depth from a feature."""
        if not id_field:
            return None
        hole_id = feat[id_field]

        # Point extraction
        pt = self._extract_point(feat, use_geom, x_field, y_field)
        if not pt:
            return None

        z = self._extract_collar_z(feat, z_field, pt, dem_layer)
        depth = self._extract_collar_depth(feat, depth_field)

        return hole_id, pt, z, depth

    def _extract_collar_z(
        self,
        feat: QgsFeature,
        z_field: str,
        pt: QgsPointXY,
        dem_layer: QgsRasterLayer | None,
    ) -> float:
        """Extract collar Z with DEM fallback."""
        z = 0.0
        if z_field:
            with contextlib.suppress(ValueError, TypeError):
                z = float(feat[z_field])

        if z == 0.0 and dem_layer:
            z = self._sample_dem(dem_layer, pt)
        return z

    def _extract_collar_depth(self, feat: QgsFeature, depth_field: str) -> float:
        """Extract collar depth."""
        depth = 0.0
        if depth_field:
            with contextlib.suppress(ValueError, TypeError):
                depth = float(feat[depth_field])
        return depth

    def _sample_dem(self, dem_layer: QgsRasterLayer, pt: QgsPointXY) -> float:
        """Sample elevation at point from DEM."""
        ident = dem_layer.dataProvider().identify(pt, QgsRaster.IdentifyFormatValue)
        if ident.isValid():
            val = ident.results().get(1)
            if val is not None:
                return float(val)
        return 0.0

    def _safe_process_single_hole(
        self,
        hole_id: Any,
        collar_point: QgsPointXY,
        collar_z: float,
        given_depth: float,
        surveys_map: dict[Any, list[tuple[float, float, float]]],
        intervals_map: dict[Any, list[tuple[float, float, str]]],
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        distance_area: QgsDistanceArea,
        buffer_width: float,
        section_azimuth: float,
        geol_data: list[GeologySegment],
        drillhole_data: list[tuple[Any, list[tuple[float, float]], list[GeologySegment]]],
    ) -> None:
        """Safely process a single hole with error logging."""
        try:
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

    def _extract_data_tuple(
        self, feat: QgsFeature, fields: dict[str, str], is_survey: bool
    ) -> tuple[float, float, Any] | None:
        """Extract a data tuple from a feature based on its role."""
        try:
            if is_survey:
                return (
                    float(feat[fields["depth"]]),
                    float(feat[fields["azim"]]),
                    float(feat[fields["incl"]]),
                )
            else:
                return (
                    float(feat[fields["from"]]),
                    float(feat[fields["to"]]),
                    str(feat[fields["lith"]]),
                )
        except (ValueError, TypeError, KeyError):
            return None
