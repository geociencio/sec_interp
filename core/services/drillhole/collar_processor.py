"""Processing logic for Drillhole Collars."""

from __future__ import annotations

import contextlib
from typing import Any

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsDistanceArea,
    QgsFeature,
    QgsFeatureRequest,
    QgsGeometry,
    QgsPointXY,
    QgsRasterLayer,
    QgsVectorLayer,
)

from sec_interp.core import utils as scu
from sec_interp.core.domain import DrillholeProjection
from sec_interp.core.services.drillhole.projection_engine import ProjectionEngine


class CollarProcessor:
    """Handles extraction and projection of collar data."""

    DEFAULT_BUFFER_SEGMENTS = 8

    def detach_features(
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
        target_crs: QgsCoordinateReferenceSystem | None = None,
        transform_context: Any | None = None,
    ) -> tuple[set[Any], list[dict[str, Any]], dict[Any, float]]:
        """Detach collar features and pre-sample Z using WKT for decoupling."""
        line_buffer = self._create_line_buffer(line_geom, buffer_width)
        req = self._prepare_feature_request(
            line_geom, line_buffer, layer, target_crs, transform_context
        )

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
            attrs = scu.extract_feature_attributes(feat)

            collar_data.append({"wkt": wkt, "attributes": attrs, "id": hid})

            self._process_pre_sampled_z(
                feat, hid, dem_layer, z_field, use_geom, x_field, y_field, pre_sampled_z
            )

        return collar_ids, collar_data, pre_sampled_z

    def _create_line_buffer(
        self, line_geom: QgsGeometry, buffer_width: float
    ) -> QgsGeometry | None:
        try:
            return line_geom.buffer(buffer_width, self.DEFAULT_BUFFER_SEGMENTS)
        except (AttributeError, TypeError, ValueError):
            return None

    def _prepare_feature_request(
        self,
        line_geom: QgsGeometry,
        line_buffer: QgsGeometry | None,
        layer: QgsVectorLayer,
        target_crs: QgsCoordinateReferenceSystem | None,
        transform_context: Any | None,
    ) -> QgsFeatureRequest:
        collar_bbox = (
            line_buffer.boundingBox() if line_buffer else line_geom.boundingBox()
        )
        req = QgsFeatureRequest().setFilterRect(collar_bbox)

        if target_crs and target_crs.isValid() and layer.crs() != target_crs:
            if not transform_context:
                from qgis.core import QgsProject

                transform_context = QgsProject.instance().transformContext()
            req.setDestinationCrs(target_crs, transform_context)
        return req

    def _process_pre_sampled_z(
        self,
        feat: QgsFeature,
        hid: Any,
        dem_layer: QgsRasterLayer | None,
        z_field: str,
        use_geom: bool,
        x_field: str,
        y_field: str,
        pre_sampled_z: dict,
    ) -> None:
        if dem_layer:
            z = self.pre_sample_z(
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

    def pre_sample_z(
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
            pt = self.extract_point_agnostic(feat, False, use_geom, x_field, y_field)
            if pt:
                return scu.sample_point_elevation(dem_layer, pt)
        return None

    def extract_and_project_detached(
        self,
        collar_data: dict[str, Any] | QgsFeature,
        line_geom: QgsGeometry,
        line_start: QgsPointXY,
        da: QgsDistanceArea,
        buffer_width: float,
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        collar_z_field: str,
        collar_depth_field: str,
        pre_sampled_z: dict[Any, float] | None = None,
        dem_layer: QgsRasterLayer | None = None,
    ) -> DrillholeProjection | None:
        """Process and project a single collar from either dict or feature."""
        # 1. Extract Data agnosticly
        extracted = self.extract_attributes_agnostic(
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
        projection = ProjectionEngine.project_point_to_line(
            collar_pt, line_geom, line_start, da
        )
        dist_along, offset = projection

        # 3. Check if within buffer
        if offset <= buffer_width:
            return DrillholeProjection(
                hole_id=str(hole_id),
                distance=dist_along,
                elevation=z,
                offset=offset,
                total_depth=total_depth,
            )

        return None

    def extract_attributes_agnostic(
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
        collar_pt = self.extract_point_agnostic(
            data, is_dict, use_geometry, x_field, y_field
        )
        if not collar_pt:
            return None

        # Z
        z = self._extract_z_agnostic(
            data, is_dict, z_field, hole_id, collar_pt, pre_sampled_z, dem_layer
        )

        # Depth
        depth = self._extract_depth_agnostic(data, is_dict, depth_field)

        return hole_id, collar_pt, z, depth

    def extract_point_agnostic(
        self, data: Any, is_dict: bool, use_geom: bool, x_f: str, y_f: str
    ) -> QgsPointXY | None:
        """Extract point from geometry or fields agnosticly."""
        if use_geom:
            pt = self._extract_point_from_geom(data, is_dict)
            if pt:
                return pt

        # Fallback to fields
        return self._extract_point_from_fields(data, is_dict, x_f, y_f)

    def _extract_point_from_geom(self, data: Any, is_dict: bool) -> QgsPointXY | None:
        """Extract point from geometry."""
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
        return None

    def _extract_point_from_fields(
        self, data: Any, is_dict: bool, x_f: str, y_f: str
    ) -> QgsPointXY | None:
        """Extract point from coordinate fields."""
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
        z = self._get_z_from_field(data, is_dict, z_f)
        if z == 0.0:
            z = self._get_z_from_fallback(hole_id, pt, pre_sampled, dem)
        return z

    def _get_z_from_field(self, data: Any, is_dict: bool, z_f: str) -> float:
        """Get Z from attributes."""
        if not z_f:
            return 0.0
        attrs = data.get("attributes", {}) if is_dict else data
        with contextlib.suppress(ValueError, TypeError, KeyError):
            return float(attrs.get(z_f, 0.0)) if is_dict else float(attrs[z_f] or 0.0)
        return 0.0

    def _get_z_from_fallback(
        self,
        hole_id: Any,
        pt: QgsPointXY,
        pre_sampled: dict[Any, float] | None,
        dem: QgsRasterLayer | None,
    ) -> float:
        """Get Z from pre-sampled dict or DEM."""
        if pre_sampled and hole_id in pre_sampled:
            return pre_sampled[hole_id]
        if dem:
            return self._sample_dem(dem, pt)
        return 0.0

    def _extract_depth_agnostic(self, data: Any, is_dict: bool, depth_f: str) -> float:
        """Extract depth agnosticly."""
        attrs = data.get("attributes", {}) if is_dict else data
        depth = 0.0
        if depth_f:
            with contextlib.suppress(ValueError, TypeError, KeyError):
                depth = (
                    float(attrs.get(depth_f, 0.0))
                    if is_dict
                    else float(attrs[depth_f] or 0.0)
                )
        return depth

    def _sample_dem(self, dem: QgsRasterLayer, pt: QgsPointXY) -> float:
        """Sample elevation from DEM at point."""
        return scu.sample_point_elevation(dem, pt)

    def build_coordinate_map(
        self,
        collar_data: list[dict[str, Any]],
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
    ) -> dict[Any, QgsPointXY]:
        """Build a mapping of hole IDs to collar coordinates."""
        collar_coords = {}
        for item in collar_data:
            hid = item["id"]
            pt = self.extract_point_agnostic(
                item,
                True,  # is_dict
                use_geometry,
                collar_x_field,
                collar_y_field,
            )
            if pt:
                collar_coords[hid] = pt
        return collar_coords
