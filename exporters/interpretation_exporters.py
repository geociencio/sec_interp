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
    QgsProject,
    QgsVectorFileWriter,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QMetaType

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
    ) -> bool:
        """Export interpretations to Shapefile.

        Args:
            output_path: Path to the output Shapefile (.shp)
            data: Dictionary containing:
                - interpretations: List of InterpretationPolygon objects

        Returns:
            bool: True if export successful, False otherwise

        """
        interpretations = data.get("interpretations", [])
        if not interpretations:
            logger.warning("No interpretations to export.")
            return False

        try:
            fields, sorted_keys = self._prepare_fields(interpretations)
            layer = QgsVectorLayer("Polygon?crs=", "interpretations_2d", "memory")
            layer.dataProvider().addAttributes(fields)
            layer.updateFields()

            features = []
            for interp in interpretations:
                feat = self._create_feature(interp, fields, sorted_keys)
                if feat:
                    features.append(feat)

            layer.dataProvider().addFeatures(features)

            return self._write_to_file(layer, output_path)

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

    def _write_to_file(self, layer: QgsVectorLayer, output_path: Path) -> bool:
        """Write the vector layer to a Shapefile on disk."""
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        options.fileEncoding = "UTF-8"

        result, error_msg, _new_layer_id, _new_layer_path = (
            QgsVectorFileWriter.writeAsVectorFormatV3(
                layer,
                str(output_path),
                QgsProject.instance().transformContext(),
                options,
            )
        )

        if result == QgsVectorFileWriter.NoError:
            logger.info(f"Successfully exported to {output_path}")
            return True
        else:
            logger.error(f"Failed to export interpretations: {error_msg}")
            return False

    def get_supported_extensions(self) -> list[str]:
        """Get list of supported file extensions.

        Returns:
            List of supported extensions.

        """
        return [".shp"]
