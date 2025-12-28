"""Interpretation exporters for SecInterp.

This module provides exporters for 2D interpretation data.
"""

from pathlib import Path
from typing import Any

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsPointXY,
    QgsVectorFileWriter,
    QgsVectorLayer,
    QgsWkbTypes,
    QgsProject,
)
from qgis.PyQt.QtCore import QMetaType, QVariant

from sec_interp.exporters.base_exporter import BaseExporter
from sec_interp.core.types import InterpretationPolygon
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class Interpretation2DExporter(BaseExporter):
    """Exports interpretations in 2D profile coordinates."""

    def __init__(self, settings: dict[str, Any]):
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
            bool: True if export was successful, False otherwise
        """
        interpretations = data.get("interpretations", [])
        if not interpretations:
            logger.warning("No interpretations to export.")
            return False

        # Create memory layer
        layer = QgsVectorLayer("Polygon?crs=", "interpretations_2d", "memory")

        # Define fields
        fields = QgsFields()
        fields.append(QgsField("id", QMetaType.Type.QString))
        fields.append(QgsField("name", QMetaType.Type.QString))
        fields.append(QgsField("type", QMetaType.Type.QString))
        fields.append(QgsField("color", QMetaType.Type.QString))
        fields.append(QgsField("created_at", QMetaType.Type.QString))

        layer.dataProvider().addAttributes(fields)
        layer.updateFields()

        # Add features
        features = []
        for interp in interpretations:
            # Create polygon geometry from 2D vertices
            points = [QgsPointXY(x, y) for x, y in interp.vertices_2d]

            # Ensure polygon is closed
            if points and points[0] != points[-1]:
                points.append(points[0])

            geom = QgsGeometry.fromPolygonXY([points])

            # Create feature
            feature = QgsFeature()
            feature.setGeometry(geom)
            feature.setAttributes([
                interp.id,
                interp.name,
                interp.type,
                interp.color,
                interp.created_at,
            ])
            features.append(feature)

        layer.dataProvider().addFeatures(features)

        # Write to Shapefile
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        options.fileEncoding = "UTF-8"

        # No CRS for 2D profile coordinates

        result, error_msg, _new_layer_id, _new_layer_path = QgsVectorFileWriter.writeAsVectorFormatV3(
            layer,
            str(output_path),
            QgsProject.instance().transformContext(),
            options
        )

        if result == QgsVectorFileWriter.NoError:
            logger.info(
                f"Successfully exported {len(interpretations)} interpretations to {output_path}"
            )
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
