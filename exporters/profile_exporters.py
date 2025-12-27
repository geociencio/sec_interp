"""Specific exporters for profile data (Shapefiles)."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Optional, Union

from qgis.core import (
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsPointXY,
    QgsRaster,
    QgsVectorFileWriter,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QMetaType

from sec_interp.core import utils as scu
from sec_interp.logger_config import get_logger

from .base_exporter import BaseExporter


logger = get_logger(__name__)


class ProfileLineShpExporter(BaseExporter):
    """Exports the topographic profile line to a Shapefile."""

    def get_supported_extensions(self) -> list[str]:
        return [".shp"]

    def export(self, output_path: Path, data: dict[str, Any]) -> bool:
        """Export the topographic profile line to a Shapefile.

        Args:
            output_path: Path to the output Shapefile.
            data: Dictionary containing 'profile_data' and 'crs'.
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
        except Exception:
            logger.exception(f"Failed to export profile line to {output_path}")
            return False
        else:
            return True


class GeologyShpExporter(BaseExporter):
    """Exports the geological profile to a Shapefile."""

    def get_supported_extensions(self) -> list[str]:
        return [".shp"]

    def export(self, output_path: Path, data: dict[str, Any]) -> bool:
        """Export the geological profile to a Shapefile.

        Args:
            output_path: Path to the output Shapefile.
            data: Dictionary containing 'geology_data' and 'crs'.
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

        except Exception:
            logger.exception(f"Failed to export geology profile to {output_path}")
            return False
        else:
            return True

    def _create_geology_fields(self, geology_data: list) -> QgsFields:
        """Create fields from the first segment's attributes."""
        fields = QgsFields()
        if geology_data:
            # Use attributes from first segment as template
            first_attrs = geology_data[0].attributes
            for key in first_attrs:
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

    def get_supported_extensions(self) -> list[str]:
        return [".shp"]

    def export(self, output_path: Path, data: dict[str, Any]) -> bool:
        """Export the structural profile to a Shapefile.

        Args:
            output_path: Path to the output Shapefile.
            data: Dictionary containing 'structural_data', 'crs', 'dip_scale_factor',
                and 'raster_res'.
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
        except Exception:
            logger.exception(f"Failed to export structural profile to {output_path}")
            return False
        else:
            return True

    def _create_structure_fields(self, structural_data: list) -> QgsFields:
        """Create fields for structural data."""
        fields = QgsFields()
        if structural_data:
            first_attrs = structural_data[0].attributes
            for key in first_attrs:
                fields.append(QgsField(key, QMetaType.Type.QString))

        fields.append(QgsField("app_dip", QMetaType.Type.Double))
        fields.append(QgsField("dist", QMetaType.Type.Double))
        fields.append(QgsField("elev", QMetaType.Type.Double))
        return fields

    def _create_structure_feature(
        self, m: Any, fields: QgsFields, line_length: float
    ) -> QgsFeature:
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

    def get_supported_extensions(self) -> list[str]:
        return [".shp"]

    def export(self, output_path: Path, data: dict[str, Any]) -> bool:
        """Export the profile axes to a Shapefile.

        Args:
            output_path: Path to the output Shapefile.
            data: Dictionary containing 'profile_data' and 'crs'.
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

        except Exception:
            logger.exception(f"Failed to export axes to {output_path}")
            return False
        else:
            return True


class Interpretation25DExporter(BaseExporter):
    """Exports 2.5D interpretation polygons to a Shapefile."""

    def get_supported_extensions(self) -> list[str]:
        return [".shp"]

    def export(self, output_path: Path, data: dict[str, Any]) -> bool:
        """Export interpretation polygons to a Shapefile.

        Args:
            output_path: Path to the output Shapefile.
            data: Dictionary containing 'interpretations' and 'crs'.
        """
        interpretations = data.get("interpretations")
        crs = data.get("crs")
        if not interpretations or not crs:
            logger.warning(f"Aborting export to {output_path}: missing interpretations or CRS")
            return False

        try:
            fields = QgsFields()
            fields.append(QgsField("id", QMetaType.Type.QString))
            fields.append(QgsField("name", QMetaType.Type.QString))
            fields.append(QgsField("type", QMetaType.Type.QString))

            writer = scu.create_shapefile_writer(
                str(output_path), crs, fields, QgsWkbTypes.PolygonZM
            )
            if not writer:
                logger.error(f"Failed to create shapefile writer for {output_path}")
                return False

            count = 0
            for interp in interpretations:
                # InterpretationPolygon25D has a geometry attribute
                if not hasattr(interp, "geometry") or not interp.geometry:
                    continue

                geom = interp.geometry

                # Validate geometry
                if not geom.isGeosValid():
                    logger.warning(
                        f"Invalid geometry for interpretation {interp.id}, attempting to fix"
                    )
                    geom = geom.makeValid()

                if not geom.isGeosValid() or geom.isEmpty():
                    logger.warning(f"Skipping interpretation {interp.id} due to invalid geometry")
                    continue

                # Check if geometry is still a polygon after makeValid
                # Accept all polygon variants (2D, Z, M, ZM)
                geom_type = geom.wkbType()

                # If it's a GeometryCollection (common after repair), extract only polygon parts
                if geom_type == QgsWkbTypes.GeometryCollection:
                    polygons = []
                    for part in geom.constGet():
                        if part.wkbType() in [
                            QgsWkbTypes.Polygon,
                            QgsWkbTypes.PolygonZ,
                            QgsWkbTypes.PolygonM,
                            QgsWkbTypes.PolygonZM,
                        ]:
                            polygons.append(QgsGeometry(part))

                    if polygons:
                        geom = QgsGeometry.collectGeometry(polygons)
                        geom_type = geom.wkbType()
                        logger.info(
                            f"Converted GeometryCollection to {QgsWkbTypes.displayString(geom_type)} for interpretation {interp.id}"
                        )
                    else:
                        logger.warning(
                            f"Skipping interpretation {interp.id}: GeometryCollection contains no polygons"
                        )
                        continue

                is_polygon = geom_type in [
                    QgsWkbTypes.Polygon,
                    QgsWkbTypes.PolygonZ,
                    QgsWkbTypes.PolygonM,
                    QgsWkbTypes.PolygonZM,
                    QgsWkbTypes.MultiPolygon,
                    QgsWkbTypes.MultiPolygonZ,
                    QgsWkbTypes.MultiPolygonM,
                    QgsWkbTypes.MultiPolygonZM,
                ]

                if not is_polygon:
                    logger.warning(
                        f"Skipping interpretation {interp.id}: geometry became {QgsWkbTypes.displayString(geom_type)} after validation"
                    )
                    continue

                feat = QgsFeature(fields)
                feat.setGeometry(geom)
                feat.setAttribute("id", interp.id)
                feat.setAttribute("name", interp.name)
                feat.setAttribute("type", interp.type)

                if writer.addFeature(feat):
                    count += 1

            error = writer.hasError()
            if error != QgsVectorFileWriter.NoError:
                logger.error(f"Error writing to shapefile: {writer.errorMessage()}")
                return False

            logger.info(f"Successfully exported {count} interpretations to {output_path}")
            del writer
            return True

        except Exception:
            logger.exception(f"Failed to export interpretations to {output_path}")
            return False
