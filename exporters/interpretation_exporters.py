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
)
from qgis.PyQt.QtCore import QVariant

from sec_interp.core.types import InterpretationPolygon
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class Interpretation2DExporter:
    """Exports interpretations in 2D profile coordinates."""

    def export_interpretations(
        self,
        output_path: Path,
        interpretations: list[InterpretationPolygon],
    ) -> bool:
        """Export a list of InterpretationPolygon objects to Shapefile.

        Args:
            output_path: Path to the output Shapefile (.shp)
            interpretations: List of InterpretationPolygon objects

        Returns:
            bool: True if export was successful, False otherwise
        """
        if not interpretations:
            logger.warning("No interpretations to export.")
            return False

        # Create memory layer
        layer = QgsVectorLayer("Polygon?crs=", "interpretations_2d", "memory")

        # Define fields
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.String))
        fields.append(QgsField("name", QVariant.String))
        fields.append(QgsField("type", QVariant.String))
        fields.append(QgsField("color", QVariant.String))
        fields.append(QgsField("created_at", QVariant.String))

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
        error = QgsVectorFileWriter.writeAsVectorFormat(
            layer,
            str(output_path),
            "UTF-8",
            QgsCoordinateReferenceSystem(),  # No CRS for 2D profile coordinates
            "ESRI Shapefile",
        )

        if error[0] == QgsVectorFileWriter.NoError:
            logger.info(
                f"Successfully exported {len(interpretations)} interpretations to {output_path}"
            )
            return True
        else:
            logger.error(f"Failed to export interpretations: {error}")
            return False
