from __future__ import annotations

"""3D Drillhole Exporter.

This module provides exporters for 3D drillhole data (traces and intervals).
"""

from typing import Any

from qgis.core import (
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsPoint,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QMetaType

from sec_interp.core import utils as scu
from sec_interp.logger_config import get_logger

from .base_exporter import BaseExporter

logger = get_logger(__name__)


class DrillholeTrace3DExporter(BaseExporter):
    """Exports 3D drillhole traces to a Shapefile."""

    def get_supported_extensions(self) -> list[str]:
        """Get supported extensions."""
        return [".shp"]

    def export(self, output_path: Any, data: dict[str, Any]) -> bool:
        """Export 3D drillhole traces to a Shapefile.

        Args:
            output_path: Path to the output Shapefile.
            data: Dictionary containing 'drillhole_data' and 'crs'.
                  Can include 'use_projected' (bool).

        Returns:
            bool: True if export successful, False otherwise.

        """
        drillhole_data = data.get("drillhole_data")
        crs = data.get("crs")
        use_projected = data.get("use_projected", False)
        if not drillhole_data or not crs:
            return False

        try:
            fields = self._prepare_fields()
            writer = scu.create_shapefile_writer(
                str(output_path), crs, fields, QgsWkbTypes.LineStringZ
            )

            for hole_data in drillhole_data:
                self._process_hole_trace(writer, fields, hole_data, use_projected)

            del writer
        except Exception as e:
            logger.exception(f"Error exporting 3D traces to {output_path}: {e}")
            return False
        return True

    def _process_hole_trace(
        self, writer: Any, fields: QgsFields, hole_data: tuple, use_projected: bool
    ) -> None:
        """Process and write a single hole trace feature."""
        hole_id, _, traces_3d, traces_3d_proj, _ = hole_data
        points_source = traces_3d_proj if use_projected else traces_3d
        if not points_source or len(points_source) < 2:
            return

        points = [QgsPoint(x, y, z) for x, y, z in points_source]
        geom = QgsGeometry.fromPolyline(points)

        if geom and not geom.isNull():
            feat = QgsFeature(fields)
            feat.setGeometry(geom)
            feat.setAttribute("hole_id", str(hole_id))
            writer.addFeature(feat)

    def _prepare_fields(self) -> QgsFields:
        """Create standard fields for drillhole trace."""
        fields = QgsFields()
        fields.append(QgsField("hole_id", QMetaType.Type.QString))
        return fields


class DrillholeInterval3DExporter(BaseExporter):
    """Exports 3D drillhole intervals to a Shapefile."""

    def get_supported_extensions(self) -> list[str]:
        """Get supported extensions."""
        return [".shp"]

    def export(self, output_path: Any, data: dict[str, Any]) -> bool:
        """Export 3D drillhole intervals to a Shapefile.

        Args:
            output_path: Path to the output Shapefile.
            data: Dictionary containing 'drillhole_data' and 'crs'.
                  Can include 'use_projected' (bool).

        Returns:
            bool: True if export successful, False otherwise.

        """
        drillhole_data = data.get("drillhole_data")
        crs = data.get("crs")
        use_projected = data.get("use_projected", False)
        if not drillhole_data or not crs:
            return False

        try:
            fields = self._prepare_fields()
            writer = scu.create_shapefile_writer(
                str(output_path), crs, fields, QgsWkbTypes.LineStringZ
            )

            for hole_data in drillhole_data:
                self._process_hole_intervals(writer, fields, hole_data, use_projected)

            del writer
        except Exception as e:
            logger.exception(f"Error exporting 3D intervals to {output_path}: {e}")
            return False
        return True

    def _process_hole_intervals(
        self, writer: Any, fields: QgsFields, hole_data: tuple, use_projected: bool
    ) -> None:
        """Process and write intervals for a single hole."""
        hole_id, _, _, _, segments = hole_data
        if not segments:
            return

        for segment in segments:
            points_source = segment.points_3d_projected if use_projected else segment.points_3d
            if not points_source or len(points_source) < 2:
                continue

            points = [QgsPoint(x, y, z) for x, y, z in points_source]
            geom = QgsGeometry.fromPolyline(points)

            if geom and not geom.isNull():
                feat = QgsFeature(fields)
                feat.setGeometry(geom)
                feat.setAttribute("hole_id", str(hole_id))
                attrs = segment.attributes
                feat.setAttribute("from_depth", attrs.get("from", 0.0))
                feat.setAttribute("to_depth", attrs.get("to", 0.0))
                feat.setAttribute("unit", segment.unit_name)
                writer.addFeature(feat)

    def _prepare_fields(self) -> QgsFields:
        """Create fields for drillhole intervals."""
        fields = QgsFields()
        fields.append(QgsField("hole_id", QMetaType.Type.QString))
        fields.append(QgsField("from_depth", QMetaType.Type.Double))
        fields.append(QgsField("to_depth", QMetaType.Type.Double))
        fields.append(QgsField("unit", QMetaType.Type.QString))
        return fields
