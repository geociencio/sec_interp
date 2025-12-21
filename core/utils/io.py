"""I/O Utilities Module.

File I/O operations and user messaging.
"""

from pathlib import Path

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFields,
    QgsProject,
    QgsVectorFileWriter,
    QgsWkbTypes,
)


def create_shapefile_writer(
    output_path,
    crs: QgsCoordinateReferenceSystem,
    fields: QgsFields,
    geometry_type=QgsWkbTypes.LineString,
):
    """Helper to create a QgsVectorFileWriter.

    Args:
        output_path: Path where shapefile will be created.
        crs: CRS for the shapefile.
        fields: Fields definition for the shapefile.
        geometry_type: Geometry type (default: LineString).

    Returns:
        QgsVectorFileWriter: Initialized writer object.

    Raises:
        IOError: If writer creation fails.
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


