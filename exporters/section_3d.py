"""QGIS 3D exporters for the section topography, geology and structures."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qgis.core import (
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsLineString,
    QgsPoint,
    QgsPolygon,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QMetaType

import sec_interp.exporters.qgis_io as scu_io
from sec_interp.core.domain.section_frame import SectionFrame
from sec_interp.logger_config import get_logger

from .base_exporter import BaseExporter

logger = get_logger(__name__)

MIN_LINE_POINTS = 2
MIN_POLYGON_POINTS = 3
DEFAULT_BASELINE_OFFSET = 1.0


class Topography3DExporter(BaseExporter):
    """Export the profile line as a georeferenced LineStringZ."""

    def get_supported_extensions(self) -> list[str]:
        """Return supported vector extensions."""
        return [".shp", ".gpkg", ".dxf"]

    def export(
        self,
        output_path: str | Path,
        data: dict[str, Any],
        layer_name: str | None = None,
    ) -> bool:
        """Write the 3D topography line."""
        profile_data = data.get("profile_data")
        frame: SectionFrame | None = data.get("frame")
        crs = data.get("crs")
        section_id = str(data.get("section_id", ""))
        if not profile_data or frame is None or not crs:
            return False
        if len(profile_data) < MIN_LINE_POINTS:
            return False

        try:
            points = [
                QgsPoint(*frame.to_map(distance, elevation)) for distance, elevation in profile_data
            ]
            fields = QgsFields()
            fields.append(QgsField("section_id", QMetaType.Type.QString))
            fields.append(QgsField("length", QMetaType.Type.Double))
            fields.append(QgsField("points", QMetaType.Type.Int))

            writer = scu_io.create_vector_writer(
                str(output_path),
                crs,
                fields,
                QgsWkbTypes.Type.LineStringZ,
                layer_name=layer_name,
            )
            feature = QgsFeature(fields)
            feature.setGeometry(QgsGeometry(QgsLineString(points)))
            feature.setAttribute("section_id", section_id)
            feature.setAttribute("length", frame.length)
            feature.setAttribute("points", len(points))
            writer.addFeature(feature)
            del writer
        except Exception:
            logger.exception(f"Failed to export 3D topography to {output_path}")
            return False
        return True


class Geology3DExporter(BaseExporter):
    """Export geology segments as georeferenced PolygonZ bands."""

    def get_supported_extensions(self) -> list[str]:
        """Return supported vector extensions."""
        return [".shp", ".gpkg", ".dxf"]

    def export(
        self,
        output_path: str | Path,
        data: dict[str, Any],
        layer_name: str | None = None,
    ) -> bool:
        """Write one 3D polygon per geology segment."""
        geology_data = data.get("geology_data")
        frame: SectionFrame | None = data.get("frame")
        crs = data.get("crs")
        section_id = str(data.get("section_id", ""))
        baseline_offset = float(data.get("baseline_offset", DEFAULT_BASELINE_OFFSET))
        if not geology_data or frame is None or not crs:
            return False

        try:
            fields = QgsFields()
            fields.append(QgsField("section_id", QMetaType.Type.QString))
            fields.append(QgsField("unit", QMetaType.Type.QString))
            fields.append(QgsField("unit_id", QMetaType.Type.QString))
            fields.append(QgsField("color", QMetaType.Type.QString))

            writer = scu_io.create_vector_writer(
                str(output_path),
                crs,
                fields,
                QgsWkbTypes.Type.PolygonZ,
                layer_name=layer_name,
            )
            written = 0
            for segment in geology_data:
                polygon = self._build_polygon(segment, frame, baseline_offset)
                if polygon is None:
                    continue
                feature = QgsFeature(fields)
                feature.setGeometry(QgsGeometry(polygon))
                feature.setAttribute("section_id", section_id)
                feature.setAttribute("unit", str(segment.unit_name))
                feature.setAttribute(
                    "unit_id", str(segment.attributes.get("id", segment.unit_name))
                )
                feature.setAttribute("color", str(segment.attributes.get("color", "#FF0000")))
                writer.addFeature(feature)
                written += 1
            del writer
            return written > 0
        except Exception:
            logger.exception(f"Failed to export 3D geology to {output_path}")
            return False

    def _build_polygon(
        self,
        segment: Any,
        frame: SectionFrame,
        baseline_offset: float,
    ) -> QgsPolygon | None:
        """Build a closed polygon from the segment top and a lower baseline."""
        if len(segment.points) < MIN_POLYGON_POINTS:
            return None

        top = [
            QgsPoint(*frame.to_map(distance, elevation)) for distance, elevation in segment.points
        ]
        baseline = min(point.z() for point in top) - baseline_offset
        bottom = [QgsPoint(point.x(), point.y(), baseline) for point in reversed(top)]
        ring = [*top, *bottom, top[0]]
        polygon = QgsPolygon()
        polygon.setExteriorRing(QgsLineString(ring))
        return polygon


class Structure3DExporter(BaseExporter):
    """Export structural measurements as georeferenced PointZ features."""

    def get_supported_extensions(self) -> list[str]:
        """Return supported vector extensions."""
        return [".shp", ".gpkg", ".dxf"]

    def export(
        self,
        output_path: str | Path,
        data: dict[str, Any],
        layer_name: str | None = None,
    ) -> bool:
        """Write structural measurements as 3D points."""
        structural_data = data.get("structural_data")
        frame: SectionFrame | None = data.get("frame")
        crs = data.get("crs")
        section_id = str(data.get("section_id", ""))
        if not structural_data or frame is None or not crs:
            return False

        try:
            fields = QgsFields()
            fields.append(QgsField("section_id", QMetaType.Type.QString))
            fields.append(QgsField("dip", QMetaType.Type.Double))
            fields.append(QgsField("strike", QMetaType.Type.Double))
            fields.append(QgsField("apparent_dip", QMetaType.Type.Double))
            fields.append(QgsField("type", QMetaType.Type.QString))

            writer = scu_io.create_vector_writer(
                str(output_path),
                crs,
                fields,
                QgsWkbTypes.Type.PointZ,
                layer_name=layer_name,
            )
            for measurement in structural_data:
                feature = QgsFeature(fields)
                feature.setGeometry(
                    QgsGeometry(
                        QgsPoint(*frame.to_map(measurement.distance, measurement.elevation))
                    )
                )
                feature.setAttribute("section_id", section_id)
                feature.setAttribute("dip", float(measurement.original_dip))
                feature.setAttribute("strike", float(measurement.original_strike))
                feature.setAttribute("apparent_dip", float(measurement.apparent_dip))
                feature.setAttribute("type", str(measurement.attributes.get("type", "")))
                writer.addFeature(feature)
            del writer
        except Exception:
            logger.exception(f"Failed to export 3D structures to {output_path}")
            return False
        return True
