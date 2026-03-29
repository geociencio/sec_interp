"""I/O Utilities Module.

File I/O operations and user messaging.
"""

from __future__ import annotations

from pathlib import Path

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFields,
    QgsProject,
    QgsVectorFileWriter,
    QgsWkbTypes,
)


def create_vector_writer(
    output_path: str | Path,
    crs: QgsCoordinateReferenceSystem,
    fields: QgsFields,
    geometry_type: QgsWkbTypes.GeometryType = QgsWkbTypes.LineString,
    layer_name: str | None = None,
    overwrite_layer: bool = True,
    symbology_export: QgsVectorFileWriter.SymbologyExport = QgsVectorFileWriter.NoSymbology,
) -> QgsVectorFileWriter:
    """Create and initialize a QgsVectorFileWriter for various vector formats.

    Supports Shapefile (.shp), GeoPackage (.gpkg), and DXF (.dxf) based on extension.

    Args:
        output_path: File system path for the new file.
        crs: The Coordinate Reference System.
        fields: The attribute fields definition.
        geometry_type: The mapping geometry type (default: LineString).
        layer_name: Optional conceptual layer name.
        overwrite_layer: Whether to overwrite existing layers.
        symbology_export: Symbology export mode (default: NoSymbology).

    Returns:
        An initialized writer object.

    """
    path = Path(output_path)
    ext = path.suffix.lower()

    drivers = {
        ".shp": "ESRI Shapefile",
        ".gpkg": "GPKG",
        ".dxf": "DXF",
    }

    if ext not in drivers:
        raise ValueError(f"Unsupported vector extension: {ext}")

    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = drivers[ext]
    options.fileEncoding = "UTF-8"
    options.symbologyExport = symbology_export

    if layer_name:
        options.layerName = layer_name

    # Specific handling for GeoPackage appending
    if ext == ".gpkg" and path.exists() and layer_name:
        if overwrite_layer:
            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
        else:
            options.actionOnExistingFile = QgsVectorFileWriter.AppendToLayerAddFields

    # Specific handling for DXF (CAD)
    effective_fields = fields
    if ext == ".dxf":
        # DXF driver in QGIS typically doesn't use standard attributes unless specified,
        # but we use an empty fields set to avoid conflicts with reserved CAD names
        # unless we explicitly want CAD attributes (like 'Layer').
        effective_fields = QgsFields()

    writer = QgsVectorFileWriter.create(
        str(path),
        effective_fields,
        geometry_type,
        crs,
        QgsProject.instance().transformContext(),
        options,
    )

    if writer.hasError() != QgsVectorFileWriter.NoError:
        raise OSError(f"Error creating vector file {path}: {writer.errorMessage()}")

    return writer


def create_shapefile_writer(*args, **kwargs) -> QgsVectorFileWriter:
    """Delegate to create_vector_writer (deprecated shim)."""
    return create_vector_writer(*args, **kwargs)
