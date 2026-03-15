"""DXF exporter for vector data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsProject,
    QgsVectorFileWriter,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QMetaType

from sec_interp.logger_config import get_logger

from .base_exporter import BaseExporter

logger = get_logger(__name__)


class DXFExporter(BaseExporter):
    """Exporter for DXF format."""

    def get_supported_extensions(self) -> list[str]:
        """Get supported vector format extensions."""
        return [".dxf"]

    def export(self, output_path: Path, features_data: list[dict[str, Any]]) -> bool:
        """Export features to DXF.

        Args:
            output_path: Output file path
            features_data: List of dicts with 'geometry' and 'attributes' keys

        Returns:
            True if export successful, False otherwise

        """
        if not features_data:
            return False

        try:
            geometry_type = self.get_setting("geometry_type", QgsWkbTypes.LineString)
            crs = self.get_setting("crs", QgsCoordinateReferenceSystem("EPSG:4326"))

            fields = self._prepare_fields(features_data)
            writer = self._create_writer(output_path, fields, geometry_type, crs)

            if writer.hasError() != QgsVectorFileWriter.NoError:
                logger.error(f"Failed to create DXF writer: {writer.errorMessage()}")
                return False

            self._write_features(writer, features_data, fields)

            # Note: writer is closed when object is deleted or goes out of scope
            del writer

        except Exception:
            logger.exception(f"DXF export failed for {output_path}")
            return False
        else:
            return True

    def _write_features(
        self,
        writer: QgsVectorFileWriter,
        features_data: list[dict[str, Any]],
        fields: QgsFields,
    ) -> None:
        """Process and write features to the vector writer.

        Args:
            writer: The QGIS vector file writer instance.
            features_data: List of feature data dictionaries.
            fields: The QGIS field collection for the layer.

        """
        for data in features_data:
            feature = QgsFeature(fields)
            if "geometry" in data:
                feature.setGeometry(data["geometry"])
            if "attributes" in data:
                attrs = data["attributes"]
                feature.setAttributes([attrs.get(field.name()) for field in fields])
            writer.addFeature(feature)

    def _prepare_fields(self, features_data: list[dict[str, Any]]) -> QgsFields:
        """Create fields based on first feature's attributes."""
        fields = QgsFields()
        if features_data and "attributes" in features_data[0]:
            first_attrs = features_data[0]["attributes"]
            for key, value in first_attrs.items():
                if isinstance(value, int):
                    fields.append(QgsField(key, QMetaType.Type.Int))
                elif isinstance(value, float):
                    fields.append(QgsField(key, QMetaType.Type.Double))
                else:
                    fields.append(QgsField(key, QMetaType.Type.QString))
        return fields

    def _create_writer(
        self,
        output_path: Path,
        fields: QgsFields,
        geometry_type: QgsWkbTypes,
        crs: QgsCoordinateReferenceSystem,
    ) -> QgsVectorFileWriter:
        """Create a QgsVectorFileWriter for the given path."""
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "DXF"
        options.fileEncoding = "UTF-8"
        # Optional: DXF specific options could be added here if needed in the future
        # e.g. options.symbologyExport = QgsVectorFileWriter.NoSymbology

        return QgsVectorFileWriter.create(
            str(output_path),
            fields,
            geometry_type,
            crs,
            QgsProject.instance().transformContext(),
            options,
        )
