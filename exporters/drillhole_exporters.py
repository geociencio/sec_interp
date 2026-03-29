"""Exporters for drillhole data (SHP, GPKG, DXF)."""

from __future__ import annotations

from typing import Any

from qgis.core import (
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsPointXY,
)
from qgis.PyQt.QtCore import QMetaType

import sec_interp.core.utils.io as scu_io
from sec_interp.core.domain import DrillholeProjection
from sec_interp.logger_config import get_logger

from .base_exporter import BaseExporter

logger = get_logger(__name__)

# Constants for drillhole data validation
MIN_REQUIRED_TRACE_POINTS = 2
LEGACY_DATA_LENGTH = 5
NEW_DATA_LENGTH = 3
MIN_POINTS_FOR_INTERVAL = 2
COORD_PAIR_LENGTH = 2


class DrillholeTraceVectorExporter(BaseExporter):
    """Exports drillhole traces to a vector file (SHP, GPKG, DXF)."""

    def get_supported_extensions(self) -> list[str]:
        """Get supported file extensions.

        Returns:
            List of supported extensions.

        """
        return [".shp", ".gpkg", ".dxf"]

    def export(self, output_path: Any, data: dict[str, Any], layer_name: str | None = None) -> bool:
        """Export drillhole traces to a vector file.

        Args:
            output_path: Path to the output file.
            data: Dictionary containing 'drillhole_data' and 'crs'.
            layer_name: Optional conceptual layer name.

        Returns:
            bool: True if export successful, False otherwise.

        """
        drillhole_data = data.get("drillhole_data")
        crs = data.get("crs")
        if not drillhole_data or not crs:
            return False

        try:
            fields = self._prepare_fields()
            writer = scu_io.create_vector_writer(
                str(output_path), crs, fields, layer_name=layer_name
            )

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
        for item in drillhole_data:
            if isinstance(item, DrillholeProjection):
                hole_id = item.hole_id
                traces = item.points_3d
            elif isinstance(item, list | tuple):
                # Handle variable tuple length (legacy 5 vs new 3)
                if len(item) == NEW_DATA_LENGTH:
                    hole_id, traces, _ = item
                elif len(item) >= LEGACY_DATA_LENGTH:
                    hole_id, traces, _traces_3d, _traces_3d_proj, _ = item
                else:
                    continue
            else:
                continue

            if not traces or len(traces) < MIN_REQUIRED_TRACE_POINTS:
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
        points = []
        for p in traces:
            # Handle SpatialMeta object or tuple/list
            if hasattr(p, "dist_along") and hasattr(p, "z"):
                points.append(QgsPointXY(p.dist_along, p.z))
            elif isinstance(p, list | tuple) and len(p) >= COORD_PAIR_LENGTH:
                points.append(QgsPointXY(p[0], p[1]))

        if not points:
            return None

        geom = QgsGeometry.fromPolylineXY(points)

        if not geom or geom.isNull():
            return None

        feat = QgsFeature(fields)
        feat.setGeometry(geom)
        feat.setAttribute("hole_id", hole_id)
        return feat


class DrillholeIntervalVectorExporter(BaseExporter):
    """Exports drillhole intervals to a vector file (SHP, GPKG, DXF)."""

    def get_supported_extensions(self) -> list[str]:
        """Get supported file extensions.

        Returns:
            List of supported extensions.

        """
        return [".shp", ".gpkg", ".dxf"]

    def export(self, output_path: Any, data: dict[str, Any], layer_name: str | None = None) -> bool:
        """Export drillhole intervals to a vector file.

        Args:
            output_path: Path to the output file.
            data: Dictionary containing 'drillhole_data' and 'crs'.
            layer_name: Optional conceptual layer name.

        Returns:
            bool: True if export successful, False otherwise.

        """
        drillhole_data = data.get("drillhole_data")
        crs = data.get("crs")
        if not drillhole_data or not crs:
            return False

        try:
            fields = self._prepare_fields()
            writer = scu_io.create_vector_writer(
                str(output_path), crs, fields, layer_name=layer_name
            )

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
        for item in drillhole_data:
            if isinstance(item, DrillholeProjection):
                hole_id = item.hole_id
                segments = item.segments
            elif isinstance(item, list | tuple):
                # Handle variable tuple length (legacy 5 vs new 3)
                # Segments are always the last element
                if len(item) == NEW_DATA_LENGTH or len(item) >= LEGACY_DATA_LENGTH:
                    hole_id = item[0]
                    segments = item[-1]
                else:
                    continue
            else:
                continue
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
        if not segment.points or len(segment.points) < MIN_POINTS_FOR_INTERVAL:
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
