"""Drillhole extraction adapter (Extract phase).

Bridges the QGIS object world and the QGIS-agnostic core layer for drillholes.
It reads the section line and collar layers, buffers the line, detaches collars,
pre-samples collar elevations from a DEM, and fetches survey/interval data —
returning a fully-detached :class:`DrillholeContext`.
"""

from __future__ import annotations

import math
from typing import Any

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFeatureRequest,
    QgsGeometry,
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QCoreApplication

from sec_interp.core import utils as scu
from sec_interp.core.domain.task_inputs import DrillholeContext
from sec_interp.core.exceptions import DataMissingError, ValidationError
from sec_interp.gui.adapters import geometry
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

DEFAULT_BUFFER_SEGMENTS = 8


class DrillholeExtractor:
    """Extract drillhole-related data from QGIS layers into primitives."""

    def __init__(self, data_fetcher: Any | None = None) -> None:
        """Initialize with an optional child-data fetcher.

        Args:
            data_fetcher: A ``DataFetcher`` adapter for survey/interval bulk reads.

        """
        self.data_fetcher = data_fetcher

    def tr(self, message: str) -> str:
        """Translate a message using QCoreApplication."""
        return QCoreApplication.translate("DrillholeExtractor", message)  # type: ignore[no-any-return]

    def extract_context(
        self,
        line_layer: QgsVectorLayer,
        buffer_width: float,
        collar_layer: QgsVectorLayer,
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        collar_z_field: str,
        collar_depth_field: str,
        survey_layer: QgsVectorLayer,
        survey_fields: dict[str, str],
        interval_layer: QgsVectorLayer,
        interval_fields: dict[str, str],
        dem_layer: QgsRasterLayer | None = None,
        band_num: int = 1,
    ) -> DrillholeContext | None:
        """Extract a fully-detached :class:`DrillholeContext`.

        Args:
            line_layer: The cross-section line layer.
            buffer_width: Buffer distance (line-layer units).
            collar_layer: Collar points layer.
            collar_id_field: ID field name.
            use_geometry: Whether to read collar coordinates from geometry.
            collar_x_field: Fallback X field.
            collar_y_field: Fallback Y field.
            collar_z_field: Collar elevation field.
            collar_depth_field: Total depth field.
            survey_layer: Survey readings layer.
            survey_fields: Survey field mapping.
            interval_layer: Interval layer.
            interval_fields: Interval field mapping.
            dem_layer: Optional DEM for fallback collar elevation.
            band_num: Raster band for elevation sampling.

        Returns:
            A detached :class:`DrillholeContext`, or None if no line geometry.

        """
        if buffer_width <= 0:
            raise ValidationError(self.tr("Buffer width must be positive"))

        self._validate_fields(
            collar_layer,
            collar_id_field,
            use_geometry,
            collar_x_field,
            collar_y_field,
            collar_z_field,
            collar_depth_field,
            survey_layer,
            survey_fields,
            interval_layer,
            interval_fields,
        )

        line_geom = self._read_line_geometry(line_layer)
        if line_geom is None:
            return None

        line_points = self._extract_line_points(line_geom)
        section_azimuth = self._calculate_azimuth(line_points)

        collar_ids: set[Any] = set()
        collar_data: list[dict[str, Any]] = []
        pre_sampled_z: dict[Any, float] = {}
        if collar_layer:
            collar_ids, collar_data, pre_sampled_z = self._detach_collars(
                collar_layer,
                line_geom,
                buffer_width,
                collar_id_field,
                use_geometry,
                collar_x_field,
                collar_y_field,
                collar_z_field,
                dem_layer,
                target_crs=line_layer.crs(),
            )

        survey_map: dict[Any, list[tuple]] = {}
        interval_map: dict[Any, list[tuple]] = {}
        if collar_ids and self.data_fetcher:
            if survey_layer:
                survey_map = self.data_fetcher.fetch_bulk_data(
                    survey_layer, collar_ids, survey_fields
                )
            if interval_layer:
                interval_map = self.data_fetcher.fetch_bulk_data(
                    interval_layer, collar_ids, interval_fields
                )

        return DrillholeContext(
            line_points=line_points,
            section_azimuth=section_azimuth,
            buffer_width=buffer_width,
            collar_id_field=collar_id_field,
            collar_z_field=collar_z_field,
            collar_depth_field=collar_depth_field,
            collar_data=collar_data,
            survey_data=survey_map,
            interval_data=interval_map,
            pre_sampled_z=pre_sampled_z,
        )

    def _read_line_geometry(self, line_lyr: QgsVectorLayer) -> QgsGeometry | None:
        """Read and validate the first feature geometry of the line layer."""
        line_feat = next(line_lyr.getFeatures(), None)
        if not line_feat:
            raise DataMissingError(self.tr("Line layer has no features"))

        line_geom = line_feat.geometry()
        if not line_geom or line_geom.isNull():
            return None
        return line_geom

    def _validate_fields(
        self,
        collar_layer: QgsVectorLayer,
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        collar_z_field: str,
        collar_depth_field: str,
        survey_layer: QgsVectorLayer,
        survey_fields: dict[str, str],
        interval_layer: QgsVectorLayer,
        interval_fields: dict[str, str],
    ) -> None:
        """Validate layer field mappings (Level 3 domain validation)."""
        if collar_layer:
            self._validate_collar_fields(
                collar_layer,
                collar_id_field,
                use_geometry,
                collar_x_field,
                collar_y_field,
                collar_z_field,
                collar_depth_field,
            )

        if survey_layer:
            self._validate_child_fields(survey_layer, survey_fields, "Survey")

        if interval_layer:
            self._validate_child_fields(interval_layer, interval_fields, "Interval")

    def _validate_collar_fields(
        self,
        collar_layer: QgsVectorLayer,
        collar_id_field: str,
        use_geometry: bool,
        collar_x_field: str,
        collar_y_field: str,
        collar_z_field: str,
        collar_depth_field: str,
    ) -> None:
        """Validate collar layer field mappings."""
        collar_names = [f.name() for f in collar_layer.fields()]
        self._check_field(collar_id_field, collar_names, "Collar ID")
        if not use_geometry:
            self._check_field(collar_x_field, collar_names, "Collar X")
            self._check_field(collar_y_field, collar_names, "Collar Y")
        if collar_z_field:
            self._check_field(collar_z_field, collar_names, "Collar Z")
        if collar_depth_field:
            self._check_field(collar_depth_field, collar_names, "Collar Depth")

    def _validate_child_fields(
        self, layer: QgsVectorLayer, fields: dict[str, str], label: str
    ) -> None:
        """Validate survey/interval layer field mappings."""
        layer_names = [f.name() for f in layer.fields()]
        for fname in fields.values():
            if fname and fname not in layer_names:
                raise ValidationError(self.tr("{0} field '{1}' not found").format(label, fname))

    def _check_field(self, field_name: str, fields: list[str], label: str) -> None:
        """Raise ValidationError if a field is missing."""
        if field_name and field_name not in fields:
            raise ValidationError(self.tr("{0} field '{1}' not found").format(label, field_name))

    def _extract_line_points(self, geometry: QgsGeometry) -> list[tuple[float, float]]:
        """Extract ``(x, y)`` tuples from a single/multi-part line geometry."""
        if geometry.isMultipart():
            parts = geometry.asMultiPolyline()
            polyline = parts[0] if parts else []
        else:
            polyline = geometry.asPolyline()
        return [(p.x(), p.y()) for p in polyline]

    def _calculate_azimuth(self, points: list[tuple[float, float]]) -> float:
        """Calculate the compass bearing from the first two vertices."""
        MIN_REQUIRED_POINTS = 2
        if len(points) < MIN_REQUIRED_POINTS:
            return 0.0
        p1, p2 = points[0], points[1]
        azimuth = math.degrees(math.atan2(p2[0] - p1[0], p2[1] - p1[1]))
        if azimuth < 0:
            azimuth += 360
        return azimuth

    def _detach_collars(
        self,
        collar_layer: QgsVectorLayer,
        line_geom: QgsGeometry,
        buffer_width: float,
        id_field: str,
        use_geom: bool,
        x_field: str,
        y_field: str,
        z_field: str,
        dem_layer: QgsRasterLayer | None,
        target_crs: QgsCoordinateReferenceSystem | None = None,
    ) -> tuple[set[Any], list[dict[str, Any]], dict[Any, float]]:
        """Buffer the line and detach collar features within it."""
        line_buffer = self._create_line_buffer(line_geom, buffer_width)
        req = self._prepare_feature_request(line_geom, line_buffer, collar_layer, target_crs)

        collar_ids: set[Any] = set()
        collar_data: list[dict[str, Any]] = []
        pre_sampled_z: dict[Any, float] = {}

        for feat in collar_layer.getFeatures(req):
            if line_buffer and not feat.geometry().intersects(line_buffer):
                continue

            hid = feat[id_field]
            collar_ids.add(hid)

            attrs = scu.extract_feature_attributes(feat)
            point = self._extract_point(feat, attrs, use_geom, x_field, y_field)
            if point is None:
                continue

            collar_data.append({"id": hid, "point": point, "attributes": attrs})

            z = self._pre_sample_z(feat, attrs, hid, z_field, point, dem_layer)
            if z is not None:
                pre_sampled_z[hid] = z

        return collar_ids, collar_data, pre_sampled_z

    def _create_line_buffer(
        self, line_geom: QgsGeometry, buffer_width: float
    ) -> QgsGeometry | None:
        try:
            return line_geom.buffer(buffer_width, DEFAULT_BUFFER_SEGMENTS)
        except (AttributeError, TypeError, ValueError):
            return None

    def _prepare_feature_request(
        self,
        line_geom: QgsGeometry,
        line_buffer: QgsGeometry | None,
        layer: QgsVectorLayer,
        target_crs: QgsCoordinateReferenceSystem | None,
    ) -> QgsFeatureRequest:
        bbox = line_buffer.boundingBox() if line_buffer else line_geom.boundingBox()
        req = QgsFeatureRequest().setFilterRect(bbox)

        if target_crs and target_crs.isValid() and layer.crs() != target_crs:
            transform_context = QgsProject.instance().transformContext()
            req.setDestinationCrs(target_crs, transform_context)
        return req

    def _extract_point(
        self,
        feat: Any,
        attrs: dict[str, Any],
        use_geom: bool,
        x_field: str,
        y_field: str,
    ) -> tuple[float, float] | None:
        """Extract a collar point from geometry or coordinate fields."""
        if use_geom:
            geom = feat.geometry()
            if geom and not geom.isNull() and not geom.isEmpty():
                pt = geom.asPoint()
                return (pt.x(), pt.y())

        try:
            x = float(attrs.get(x_field, 0.0))
            y = float(attrs.get(y_field, 0.0))
            return (x, y)
        except (ValueError, TypeError):
            return None

    def _pre_sample_z(
        self,
        feat: Any,
        attrs: dict[str, Any],
        hid: Any,
        z_field: str,
        point: tuple[float, float],
        dem_layer: QgsRasterLayer | None,
    ) -> float | None:
        """Sample collar Z from DEM if missing from the attribute field."""
        z_val = 0.0
        if z_field:
            try:
                z_val = float(attrs.get(z_field, 0.0) or 0.0)
            except (ValueError, TypeError):
                z_val = 0.0

        if z_val == 0.0 and dem_layer:
            elev = self._sample_elevation(dem_layer, point)
            if elev:
                return elev
        return None

    def _sample_elevation(self, dem_layer: QgsRasterLayer, point: tuple[float, float]) -> float:
        """Sample a single elevation value from a raster layer."""
        if not dem_layer or not dem_layer.isValid():
            return 0.0
        return geometry.sample_point_elevation(dem_layer, point)
