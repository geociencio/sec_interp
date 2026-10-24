"""Field definitions and vector writing for 3D interpretation exports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qgis.core import QgsField, QgsFields, QgsVectorFileWriter
from qgis.PyQt.QtCore import QMetaType

import sec_interp.core.utils.io as scu_io
from sec_interp.core.exceptions import ExportError


def make_fields_obj(fields_list: list[QgsField]) -> QgsFields:
    """Build a ``QgsFields`` container from a field list."""
    qfields = QgsFields()
    for field in fields_list:
        qfields.append(field)
    return qfields


def prepare_fields(interpretations: list[Any]) -> tuple[list[QgsField], list[str]]:
    """Prepare the fixed and custom attribute fields for the export."""
    all_attr_keys = set()
    for interp in interpretations:
        if interp.attributes:
            all_attr_keys.update(interp.attributes.keys())
    sorted_keys = sorted(all_attr_keys)

    fields = [
        QgsField("id", QMetaType.Type.QString, len=50),
        QgsField("name", QMetaType.Type.QString, len=100),
        QgsField("type", QMetaType.Type.QString, len=50),
        QgsField("color", QMetaType.Type.QString, len=10),
        QgsField("created_at", QMetaType.Type.QString, len=30),
    ]
    for key in sorted_keys:
        fields.append(QgsField(key, QMetaType.Type.QString, len=255))
    return fields, sorted_keys


def write_shapefile(
    path: str | Path,
    features: list[Any],
    fields: list[QgsField],
    wkb_type: Any,
    crs: Any,
    layer_name: str | None = None,
) -> bool:
    """Write the projected features to a vector file."""
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "ESRI Shapefile"  # no-i18n
    options.fileEncoding = "UTF-8"
    qgs_fields = make_fields_obj(fields)

    writer = scu_io.create_vector_writer(
        str(path), crs, qgs_fields, wkb_type, layer_name=layer_name
    )
    if writer.hasError() != QgsVectorFileWriter.WriterError.NoError:
        raise ExportError(writer.errorMessage())

    for feature in features:
        writer.addFeature(feature)

    del writer
    return True
