"""I/O Utilities Module.

File I/O operations and user messaging.
"""

from pathlib import Path
from typing import Union

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFields,
    QgsProject,
    QgsVectorFileWriter,
    QgsWkbTypes,
)


def create_shapefile_writer(
    output_path: str | Path,
    crs: QgsCoordinateReferenceSystem,
    fields: QgsFields,
    geometry_type: QgsWkbTypes.GeometryType = QgsWkbTypes.LineString,
) -> QgsVectorFileWriter:
    """Helper to create and initialize a QgsVectorFileWriter for Shapefiles.

    Uses the modern `create` static method for QGIS 3.38+ compatibility.

    Args:
        output_path: File system path where the shapefile will be created.
        crs: The Coordinate Reference System for the new file.
        fields: The attribute fields definition.
        geometry_type: The mapping geometry type (default: LineString).

    Returns:
        QgsVectorFileWriter: An initialized writer object.

    Raises:
        OSError: If the writer cannot be created or has an initialization error.
    """
    # Use new static create method for QGIS 3.38+
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "ESRI Shapefile"
    options.fileEncoding = "UTF-8"

    writer = QgsVectorFileWriter.create(
        str(output_path),
        fields,
        geometry_type,
        crs,
        QgsProject.instance().transformContext(),
        options,
    )

    if writer.hasError() != QgsVectorFileWriter.NoError:
        raise OSError(
            f"Error creating shapefile {output_path}: {writer.errorMessage()}"
        )

    return writer
