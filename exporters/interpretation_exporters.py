"""Interpretation export façade."""

from __future__ import annotations

"""Interpretation exporters for SecInterp.

This module provides exporters for 2D interpretation data.
"""

from pathlib import Path
from typing import Any

from qgis.core import (
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsPointXY,
    QgsVectorFileWriter,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QMetaType

import sec_interp.core.utils.io as scu_io
from sec_interp.exporters.base_exporter import BaseExporter
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class Interpretation2DExporter(BaseExporter):
    """Exports interpretations in 2D profile coordinates."""

    def __init__(self, settings: dict[str, Any]) -> None:
        """Initialize with settings.

        Args:
            settings: Dictionary of configuration settings.

        """
        super().__init__(settings)

    def export(
        self,
        output_path: Path,
        data: dict[str, Any],
        layer_name: str | None = None,
    ) -> bool:
        """Export interpretations to Shapefile.

        Args:
            output_path: Path to the output Shapefile (.shp)
            data: Dictionary containing:
                - interpretations: List of InterpretationPolygon objects
            layer_name: Optional conceptual name for the layer (e.g. inside a GeoPackage)

        Returns:
            bool: True if export successful, False otherwise

        """
        interpretations = data.get("interpretations", [])
        if not interpretations:
            logger.warning("No interpretations to export.")
            return False

        try:
            crs = data.get("crs")

            fields, sorted_keys = self._prepare_fields(interpretations)
            writer = scu_io.create_vector_writer(
                str(output_path),
                crs,
                fields,
                geometry_type=QgsWkbTypes.Polygon,
                layer_name=layer_name,
            )

            if writer.hasError() != QgsVectorFileWriter.NoError:
                logger.error(f"Failed to create writer for {output_path}: {writer.errorMessage()}")
                return False

            for interp in interpretations:
                feat = self._create_feature(interp, fields, sorted_keys)
                if feat:
                    writer.addFeature(feat)

            del writer  # Flushes and closes the file
            logger.info(f"Successfully exported to {output_path}")
            return True

        except Exception:
            logger.exception(f"Failed to export interpretations to {output_path}")
            return False

    def _prepare_fields(self, interpretations: list[Any]) -> tuple[QgsFields, list[str]]:
        """Identify custom attributes and create fields."""
        all_attr_keys = set()
        for interp in interpretations:
            if interp.attributes:
                all_attr_keys.update(interp.attributes.keys())

        sorted_keys = sorted(all_attr_keys)
        fields = QgsFields()
        fields.append(QgsField("id", QMetaType.Type.QString, len=50))
        fields.append(QgsField("name", QMetaType.Type.QString, len=100))
        fields.append(QgsField("type", QMetaType.Type.QString, len=50))
        fields.append(QgsField("color", QMetaType.Type.QString, len=10))
        fields.append(QgsField("created_at", QMetaType.Type.QString, len=30))

        for key in sorted_keys:
            fields.append(QgsField(key, QMetaType.Type.QString, len=255))
        return fields, sorted_keys

    def _create_feature(self, interp: Any, fields: QgsFields, sorted_keys: list[str]) -> QgsFeature:
        """Create a QgsFeature with geometry and attributes."""
        # Create polygon geometry from 2D vertices
        points = [QgsPointXY(x, y) for x, y in interp.vertices_2d]

        # Ensure polygon is closed
        if points and points[0] != points[-1]:
            points.append(points[0])

        geom = QgsGeometry.fromPolygonXY([points])

        feature = QgsFeature(fields)
        feature.setGeometry(geom)

        # Set attributes
        attrs = [
            interp.id,
            interp.name,
            interp.type,
            interp.color,
            interp.created_at,
        ]

        for key in sorted_keys:
            val = interp.attributes.get(key, "")
            attrs.append(str(val))

        feature.setAttributes(attrs)
        return feature

    def get_supported_extensions(self) -> list[str]:
        """Get supported file extensions."""
        return [".shp", ".gpkg", ".dxf"]
