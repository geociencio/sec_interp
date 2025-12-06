# -*- coding: utf-8 -*-
"""
Shapefile exporter module for vector data.
"""

from pathlib import Path
from typing import List, Dict, Any

from qgis.core import (
    QgsVectorFileWriter,
    QgsField,
    QgsFields,
    QgsFeature,
    QgsWkbTypes,
    QgsCoordinateReferenceSystem,
)
from qgis.PyQt.QtCore import QVariant

from .base_exporter import BaseExporter


class ShapefileExporter(BaseExporter):
    """Exporter for Shapefile and GeoPackage formats."""

    def get_supported_extensions(self) -> List[str]:
        """Get supported vector format extensions."""
        return ['.shp', '.gpkg']

    def export(self, output_path: Path, features_data: List[Dict[str, Any]]) -> bool:
        """Export features to shapefile or geopackage.
        
        Args:
            output_path: Output file path
            features_data: List of dicts with 'geometry' and 'attributes' keys
            
        Returns:
            True if export successful, False otherwise
        """
        if not features_data:
            return False

        try:
            # Get geometry type from settings or first feature
            geometry_type = self.get_setting('geometry_type', QgsWkbTypes.LineString)
            
            # Get CRS from settings
            crs = self.get_setting('crs', QgsCoordinateReferenceSystem('EPSG:4326'))
            
            # Define fields based on first feature's attributes
            fields = QgsFields()
            if features_data and 'attributes' in features_data[0]:
                first_attrs = features_data[0]['attributes']
                for key, value in first_attrs.items():
                    if isinstance(value, int):
                        fields.append(QgsField(key, QVariant.Int))
                    elif isinstance(value, float):
                        fields.append(QgsField(key, QVariant.Double))
                    else:
                        fields.append(QgsField(key, QVariant.String))

            # Determine driver
            ext = output_path.suffix.lower()
            driver = "GPKG" if ext == '.gpkg' else "ESRI Shapefile"

            # Create writer
            writer = QgsVectorFileWriter(
                str(output_path),
                "UTF-8",
                fields,
                geometry_type,
                crs,
                driver
            )

            if writer.hasError() != QgsVectorFileWriter.NoError:
                return False

            # Write features
            for data in features_data:
                feature = QgsFeature(fields)
                
                if 'geometry' in data:
                    feature.setGeometry(data['geometry'])
                
                if 'attributes' in data:
                    attrs = data['attributes']
                    feature.setAttributes([attrs.get(field.name()) for field in fields])
                
                writer.addFeature(feature)

            # Clean up
            del writer
            return True

        except Exception:
            return False
