"""Exporters for drillhole data (Shapefiles)."""

from typing import Any

from qgis.core import (
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsPointXY,
)
from qgis.PyQt.QtCore import QMetaType

from sec_interp.core import utils as scu
from sec_interp.logger_config import get_logger

from .base_exporter import BaseExporter

logger = get_logger(__name__)


class DrillholeTraceShpExporter(BaseExporter):
    """Exports drillhole traces to a Shapefile."""

    def get_supported_extensions(self) -> list[str]:
        """Get supported file extensions.

        Returns:
            List of supported extensions.

        """
        return [".shp"]

    def export(self, output_path: Any, data: dict[str, Any]) -> bool:
        """Export drillhole traces to a Shapefile.

        Args:
            output_path: Path to the output Shapefile.
            data: Dictionary containing 'drillhole_data' and 'crs'.

        Returns:
            bool: True if export successful, False otherwise.

        """
        drillhole_data = data.get("drillhole_data")
        crs = data.get("crs")
        if not drillhole_data or not crs:
            return False

        try:
            fields = self._prepare_fields()
            writer = scu.create_shapefile_writer(str(output_path), crs, fields)

            self._write_traces(writer, drillhole_data, fields)
            del writer
        except Exception:
            logger.exception(f"Failed to export drillhole traces to {output_path}")
            return False
        else:
            return True

    def _write_traces(self, writer: Any, drillhole_data: list, fields: QgsFields) -> None:
        """Write drillhole traces to the writer.

        Args:
            writer: The vector file writer.
            drillhole_data: List of drillhole data.
            fields: The QGIS field collection.

        """
        for hole_id, traces, _ in drillhole_data:
            if not traces or len(traces) < 2:
                continue

            feat = self._create_feature(hole_id, traces, fields)
            if feat:
                writer.addFeature(feat)

    def _prepare_fields(self) -> QgsFields:
        """Create standard fields for drillhole trace."""
        fields = QgsFields()
        fields.append(QgsField("hole_id", QMetaType.Type.QString))
        return fields

    def _create_feature(self, hole_id: str, traces: list, fields: QgsFields) -> QgsFeature | None:
        """Create a trace feature from points."""
        points = [QgsPointXY(d, e) for d, e in traces]
        geom = QgsGeometry.fromPolylineXY(points)

        if not geom or geom.isNull():
            return None

        feat = QgsFeature(fields)
        feat.setGeometry(geom)
        feat.setAttribute("hole_id", hole_id)
        return feat


class DrillholeIntervalShpExporter(BaseExporter):
    """Exports drillhole intervals to a Shapefile."""

    def get_supported_extensions(self) -> list[str]:
        """Get supported file extensions.

        Returns:
            List of supported extensions.

        """
        return [".shp"]

    def export(self, output_path: Any, data: dict[str, Any]) -> bool:
        """Export drillhole intervals to a Shapefile.

        Args:
            output_path: Path to the output Shapefile.
            data: Dictionary containing 'drillhole_data' and 'crs'.

        Returns:
            bool: True if export successful, False otherwise.

        """
        drillhole_data = data.get("drillhole_data")
        crs = data.get("crs")
        if not drillhole_data or not crs:
            return False

        try:
            fields = self._prepare_fields()
            writer = scu.create_shapefile_writer(str(output_path), crs, fields)

            self._write_intervals(writer, drillhole_data, fields)
            del writer
        except Exception:
            logger.exception(f"Failed to export drillhole intervals to {output_path}")
            return False
        else:
            return True

    def _write_intervals(self, writer: Any, drillhole_data: list, fields: QgsFields) -> None:
        """Write drillhole intervals to the writer.

        Args:
            writer: The vector file writer.
            drillhole_data: List of drillhole data.
            fields: The QGIS field collection.

        """
        for hole_id, _, segments in drillhole_data:
            if not segments:
                continue

            for segment in segments:
                feat = self._create_feature(hole_id, segment, fields)
                if feat:
                    writer.addFeature(feat)

    def _prepare_fields(self) -> QgsFields:
        """Create fields for drillhole intervals."""
        fields = QgsFields()
        fields.append(QgsField("hole_id", QMetaType.Type.QString))
        fields.append(QgsField("from_depth", QMetaType.Type.Double))
        fields.append(QgsField("to_depth", QMetaType.Type.Double))
        fields.append(QgsField("unit", QMetaType.Type.QString))
        return fields

    def _create_feature(self, hole_id: str, segment: Any, fields: QgsFields) -> QgsFeature | None:
        """Create an interval feature from segment data."""
        if not segment.points or len(segment.points) < 2:
            return None

        points = [QgsPointXY(d, e) for d, e in segment.points]
        geom = QgsGeometry.fromPolylineXY(points)

        if not geom or geom.isNull():
            return None

        feat = QgsFeature(fields)
        feat.setGeometry(geom)
        feat.setAttribute("hole_id", hole_id)

        attrs = segment.attributes
        feat.setAttribute("from_depth", attrs.get("from", 0.0))
        feat.setAttribute("to_depth", attrs.get("to", 0.0))
        feat.setAttribute("unit", segment.unit_name)

        return feat
