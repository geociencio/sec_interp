"""3D Drillhole Exporter.

This module provides exporters for 3D drillhole data (traces and intervals).
"""

from __future__ import annotations

from typing import Any

from qgis.core import (
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsLineString,
    QgsPoint,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QMetaType

import sec_interp.core.utils.io as scu_io
from sec_interp.core.domain import DrillholeProjection
from sec_interp.logger_config import get_logger

from .base_exporter import BaseExporter

logger = get_logger(__name__)

# Constants for drillhole data lengths
NEW_DATA_LENGTH = 3
LEGACY_DATA_LENGTH = 5
MIN_POINTS_FOR_INTERVAL = 2


class DrillholeTrace3DExporter(BaseExporter):
    """Exports 3D drillhole traces to a Shapefile."""

    def get_supported_extensions(self) -> list[str]:
        """Get supported extensions."""
        return [".shp", ".gpkg", ".dxf"]

    def export(self, output_path: Any, data: dict[str, Any], layer_name: str | None = None) -> bool:
        """Export 3D drillhole traces to a Shapefile.

        Args:
            output_path: Path to the output Shapefile.
            data: Dictionary containing 'drillhole_data' and 'crs'.
                  Can include 'use_projected' (bool).
            layer_name: Optional conceptual name for the layer.

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
            writer = scu_io.create_vector_writer(
                str(output_path),
                crs,
                fields,
                QgsWkbTypes.LineStringZ,
                layer_name=layer_name,
            )

            for hole_data in drillhole_data:
                self._process_hole_trace(writer, fields, hole_data, use_projected)

            del writer
        except Exception as e:
            logger.exception(f"Error exporting 3D traces to {output_path}: {e}")
            return False
        return True

    def _process_hole_trace(
        self, writer: Any, fields: QgsFields, hole_data: Any, use_projected: bool
    ) -> None:
        """Process and write a single hole trace feature."""
        extracted = self._extract_hole_spatial_data(hole_data)
        if not extracted:
            return

        hole_id, spatial_points = extracted
        points = self._get_trace_points(spatial_points, use_projected)

        if not points or len(points) < MIN_POINTS_FOR_INTERVAL:
            return

        geom = QgsGeometry(QgsLineString(points))
        if geom and not geom.isNull():
            feat = QgsFeature(fields)
            feat.setGeometry(geom)
            feat.setAttribute("hole_id", str(hole_id))
            writer.addFeature(feat)

    def _extract_hole_spatial_data(self, hole_data: Any) -> tuple[Any, Any] | None:
        """Extract hole ID and spatial points from various data formats."""
        if isinstance(hole_data, DrillholeProjection):
            return hole_data.hole_id, hole_data.points_3d

        if isinstance(hole_data, list | tuple):
            hole_id = hole_data[0]
            if len(hole_data) == NEW_DATA_LENGTH:
                # New format with SpatialMeta objects
                return hole_id, hole_data[1]
            if len(hole_data) == LEGACY_DATA_LENGTH:
                # Legacy/Integration Test format
                return hole_id, hole_data
            logger.warning(
                f"Unexpected hole data format (length {len(hole_data)}) for hole {hole_id}"
            )
        return None

    def _get_trace_points(self, spatial_data: Any, use_projected: bool) -> list[QgsPoint]:
        """Convert spatial data to QgsPoint list based on projection."""
        if isinstance(spatial_data, list | tuple) and len(spatial_data) == LEGACY_DATA_LENGTH:
            # Legacy/Integration Test format
            _, _, traces_3d, traces_3d_proj, _ = spatial_data
            points_source = traces_3d_proj if use_projected else traces_3d
            return [QgsPoint(x, y, z) for x, y, z in points_source]

        # Standard SpatialMeta objects
        if use_projected:
            return [
                QgsPoint(p.x_proj or 0.0, p.y_proj or 0.0, p.z)
                for p in spatial_data
                if p.x_proj is not None
            ]
        return [
            QgsPoint(p.x_3d or 0.0, p.y_3d or 0.0, p.z) for p in spatial_data if p.x_3d is not None
        ]

    def _prepare_fields(self) -> QgsFields:
        """Create standard fields for drillhole trace."""
        fields = QgsFields()
        fields.append(QgsField("hole_id", QMetaType.Type.QString))
        return fields


class DrillholeInterval3DExporter(BaseExporter):
    """Exports 3D drillhole intervals to a Shapefile."""

    def get_supported_extensions(self) -> list[str]:
        """Get supported extensions."""
        return [".shp", ".gpkg", ".dxf"]

    def export(self, output_path: Any, data: dict[str, Any], layer_name: str | None = None) -> bool:
        """Export 3D drillhole intervals to a Shapefile.

        Args:
            output_path: Path to the output Shapefile.
            data: Dictionary containing 'drillhole_data' and 'crs'.
                  Can include 'use_projected' (bool).
            layer_name: Optional conceptual layer name.

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
            writer = scu_io.create_vector_writer(
                str(output_path),
                crs,
                fields,
                QgsWkbTypes.LineStringZ,
                layer_name=layer_name,
            )

            for hole_data in drillhole_data:
                self._process_hole_intervals(writer, fields, hole_data, use_projected)

            del writer
        except Exception as e:
            logger.exception(f"Error exporting 3D intervals to {output_path}: {e}")
            return False
        return True

    def _process_hole_intervals(
        self, writer: Any, fields: QgsFields, hole_data: Any, use_projected: bool
    ) -> None:
        """Process and write intervals for a single hole."""
        if isinstance(hole_data, DrillholeProjection):
            hole_id = hole_data.hole_id
            segments = hole_data.segments
        elif isinstance(hole_data, list | tuple):
            # segments are always the last element in both 3 and 5 element formats
            hole_id = hole_data[0]
            segments = hole_data[-1]
        else:
            return

        if not segments or not isinstance(segments, list):
            return

        for segment in segments:
            points_source = segment.points_3d_projected if use_projected else segment.points_3d
            if not points_source or len(points_source) < MIN_POINTS_FOR_INTERVAL:
                continue

            points = [QgsPoint(x, y, z) for x, y, z in points_source]
            geom = QgsGeometry(QgsLineString(points))

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
