"""Specific exporters for profile data (Shapefiles)."""

import math
from pathlib import Path
from typing import Any, List, Dict, Optional, Union

from qgis.core import (
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsPointXY,
    QgsRaster,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QMetaType

from sec_interp.core import utils as scu
from sec_interp.logger_config import get_logger

from .base_exporter import BaseExporter


logger = get_logger(__name__)


class ProfileLineShpExporter(BaseExporter):
    """Exports the topographic profile line to a Shapefile."""

    def get_supported_extensions(self) -> List[str]:
        return [".shp"]

    def export(self, output_path: Path, data: Dict[str, Any]) -> bool:
        """Args:
        data (dict): Must contain 'profile_data' (list of tuples) and 'crs'.
        """
        profile_data = data.get("profile_data")
        crs = data.get("crs")
        if not profile_data or not crs:
            return False

        try:
            points = [QgsPointXY(d, e) for d, e in profile_data]
            geom = QgsGeometry.fromPolylineXY(points)
            if not geom or geom.isNull():
                return False

            fields = QgsFields()
            fields.append(QgsField("id", QMetaType.Type.Int))

            writer = scu.create_shapefile_writer(str(output_path), crs, fields)

            feat = QgsFeature()
            feat.setGeometry(geom)
            feat.setAttributes([1])
            writer.addFeature(feat)
            del writer
            return True
        except Exception:
            logger.exception(f"Failed to export profile line to {output_path}")
            return False


class GeologyShpExporter(BaseExporter):
    """Exports the geological profile to a Shapefile."""

    def get_supported_extensions(self) -> List[str]:
        return [".shp"]

    def export(self, output_path: Path, data: Dict[str, Any]) -> bool:
        """Args:
        data (dict): Must contain 'geology_data' (List[GeologySegment]) and 'crs'.
        """
        geology_data = data.get("geology_data")
        crs = data.get("crs")
        
        if not geology_data or not crs:
            return False

        try:
            fields = self._create_geology_fields(geology_data)
            writer = scu.create_shapefile_writer(str(output_path), crs, fields)

            for segment in geology_data:
                feat = self._create_geology_feature(segment, fields)
                if feat:
                    writer.addFeature(feat)

            del writer
            return True
        except Exception:
            logger.exception(f"Failed to export geology profile to {output_path}")
            return False

    def _create_geology_fields(self, geology_data: list) -> QgsFields:
        """Create fields from the first segment's attributes."""
        fields = QgsFields()
        if geology_data:
            # Use attributes from first segment as template
            first_attrs = geology_data[0].attributes
            for key in first_attrs.keys():
                fields.append(QgsField(key, QMetaType.Type.QString))
        return fields

    def _create_geology_feature(self, segment: Any, fields: QgsFields) -> Optional[QgsFeature]:
        """Create a feature for a geology segment."""
        if len(segment.points) < 2:
            return None
        
        points = [QgsPointXY(d, e) for d, e in segment.points]
        geom = QgsGeometry.fromPolylineXY(points)
        
        feat = QgsFeature(fields)
        feat.setGeometry(geom)
        
        # Set attributes
        for key, val in segment.attributes.items():
            idx = fields.indexOf(key)
            if idx >= 0:
                feat.setAttribute(idx, val)
        return feat


class StructureShpExporter(BaseExporter):
    """Exports the structural profile to a Shapefile."""

    def get_supported_extensions(self) -> List[str]:
        return [".shp"]

    def export(self, output_path: Path, data: Dict[str, Any]) -> bool:
        """Args:
        data (dict): Must contain 'structural_data' (List[StructureMeasurement]),
                     'crs', 'dip_scale_factor', 'raster_res'.
        """
        structural_data = data.get("structural_data")
        crs = data.get("crs")
        dip_scale_factor = data.get("dip_scale_factor", 4)
        raster_res = data.get("raster_res", 1.0)

        if not structural_data or not crs:
            return False

        try:
            line_length = raster_res * dip_scale_factor
            fields = self._create_structure_fields(structural_data)
            writer = scu.create_shapefile_writer(str(output_path), crs, fields)

            for m in structural_data:
                feat = self._create_structure_feature(m, fields, line_length)
                if feat:
                    writer.addFeature(feat)

            del writer
            return True
        except Exception:
            logger.exception(f"Failed to export structural profile to {output_path}")
            return False

    def _create_structure_fields(self, structural_data: list) -> QgsFields:
        """Create fields for structural data."""
        fields = QgsFields()
        if structural_data:
            first_attrs = structural_data[0].attributes
            for key in first_attrs.keys():
                fields.append(QgsField(key, QMetaType.Type.QString))
        
        fields.append(QgsField("app_dip", QMetaType.Type.Double))
        fields.append(QgsField("dist", QMetaType.Type.Double))
        fields.append(QgsField("elev", QMetaType.Type.Double))
        return fields

    def _create_structure_feature(self, m: Any, fields: QgsFields, line_length: float) -> QgsFeature:
        """Create a feature for a structural measurement."""
        geom = self._calculate_dip_geometry(m, line_length)
        
        feat = QgsFeature(fields)
        feat.setGeometry(geom)
        
        # Set attributes
        for key, val in m.attributes.items():
            idx = fields.indexOf(key)
            if idx >= 0:
                feat.setAttribute(idx, val)
        
        feat["app_dip"] = m.apparent_dip
        feat["dist"] = m.distance
        feat["elev"] = m.elevation
        return feat

    def _calculate_dip_geometry(self, m: Any, line_length: float) -> QgsGeometry:
        """Calculate the line geometry for a structural dip."""
        rad_dip = math.radians(m.apparent_dip)
        dy = -line_length * math.sin(abs(rad_dip))
        dx = line_length * math.cos(abs(rad_dip))
        if m.apparent_dip < 0:
            dx = -dx

        p1 = QgsPointXY(m.distance, m.elevation)
        p2 = QgsPointXY(m.distance + dx, m.elevation + dy)
        return QgsGeometry.fromPolylineXY([p1, p2])


class AxesShpExporter(BaseExporter):
    """Exports the profile axes to a Shapefile."""

    def get_supported_extensions(self) -> List[str]:
        return [".shp"]

    def export(self, output_path: Path, data: Dict[str, Any]) -> bool:
        """Args:
        data (dict): Must contain 'profile_data' and 'crs'.
        """
        profile_data = data.get("profile_data")
        crs = data.get("crs")
        if not profile_data or not crs:
            return False

        try:
            dists = [p[0] for p in profile_data]
            elevs = [p[1] for p in profile_data]

            min_d, max_d = min(dists), max(dists)
            min_e, max_e = min(elevs), max(elevs)

            if max_d == min_d:
                max_d = min_d + 100
            if max_e == min_e:
                max_e = min_e + 10

            e_range = max_e - min_e
            min_e_padded = min_e - e_range * 0.05
            max_e_padded = max_e + e_range * 0.05

            lines = [
                [QgsPointXY(min_d, min_e_padded), QgsPointXY(min_d, max_e_padded)],
                [QgsPointXY(max_d, min_e_padded), QgsPointXY(max_d, max_e_padded)],
                [QgsPointXY(min_d, min_e_padded), QgsPointXY(max_d, min_e_padded)],
            ]

            fields = QgsFields()
            fields.append(QgsField("axis", QMetaType.Type.QString))

            writer = scu.create_shapefile_writer(str(output_path), crs, fields)

            axis_names = ["Left", "Right", "Bottom"]
            for i, points in enumerate(lines):
                feat = QgsFeature()
                geom = QgsGeometry.fromPolylineXY(points)
                feat.setGeometry(geom)
                feat.setAttributes([axis_names[i]])
                writer.addFeature(feat)

            del writer
            return True
        except Exception:
            logger.exception(f"Failed to export axes to {output_path}")
            return False
