"""Vector data export utilities."""

from __future__ import annotations

"""Vector exporter module for Shapefile, GeoPackage and DXF data."""

from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

from qgis.core import (  # noqa: E402
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsVectorFileWriter,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QMetaType  # noqa: E402

from sec_interp.core.utils import io as scu_io  # noqa: E402
from sec_interp.logger_config import get_logger  # noqa: E402

from .base_exporter import BaseExporter  # noqa: E402

logger = get_logger(__name__)


class VectorExporter(BaseExporter):
    """Generic exporter for vector formats (SHP, GPKG, DXF)."""

    def get_supported_extensions(self) -> list[str]:
        """Get supported vector format extensions."""
        return [".shp", ".gpkg", ".dxf"]

    def export(
        self,
        output_path: Path,
        features_data: list[dict[str, Any]],
        layer_name: str | None = None,
    ) -> bool:
        """Export features to a vector file.

        Args:
            output_path: Output file path.
            features_data: List of dicts with 'geometry' and 'attributes' keys.
            layer_name: Optional layer name for multi-layer containers (GeoPackage).

        Returns:
            True if export successful, False otherwise.

        """
        if not features_data:
            return False

        try:
            geometry_type = self.get_setting("geometry_type", QgsWkbTypes.LineString)
            crs = self.get_setting("crs", QgsCoordinateReferenceSystem("EPSG:4326"))
            symb_mode = self.get_setting(
                "symbology_export", QgsVectorFileWriter.NoSymbology
            )

            fields = self._prepare_fields(features_data)
            writer = scu_io.create_vector_writer(
                output_path,
                crs,
                fields,
                geometry_type,
                layer_name=layer_name,
                symbology_export=symb_mode,
            )

            if writer.hasError() != QgsVectorFileWriter.NoError:
                logger.error(f"Failed to create writer: {writer.errorMessage()}")
                return False

            self._write_features(writer, features_data, fields)

            # Note: writer is closed when object is deleted or goes out of scope
            del writer

        except Exception:
            logger.exception(f"Vector export failed for {output_path}")
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
