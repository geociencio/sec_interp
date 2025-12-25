"""Geometry processing utilities."""

from __future__ import annotations

from typing import Any, Optional

from qgis import processing
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsProject,
    QgsVectorLayer,
    QgsWkbTypes,
)

from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


def create_buffer_geometry(
    geometry: QgsGeometry,
    crs: QgsCoordinateReferenceSystem,
    distance: float,
    segments: int = 5,
) -> QgsGeometry:
    """Create a buffer around a geometry.

    Args:
        geometry: Input geometry.
        crs: Coordinate Reference System of the geometry.
        distance: Buffer distance in layer units.
        segments: Number of segments for the buffer approximation.

    Returns:
        QgsGeometry: The buffered geometry.
    """
    if not geometry or geometry.isNull():
        raise ValueError("Geometry is null or invalid")
    return geometry.buffer(distance, segments)


def create_memory_layer(
    layer_name: str,
    layer_type: str,
    crs: QgsCoordinateReferenceSystem,
    fields: list[QgsField],
) -> QgsVectorLayer:
    """Create a temporary memory (scratch) layer.

    Args:
        layer_name: Name for the layer.
        layer_type: QGIS geometry type string (e.g., 'Point', 'LineString').
        crs: Coordinate reference system.
        fields: List of fields for the layer.

    Returns:
        QgsVectorLayer: The created memory layer.
    """
    uri = f"{layer_type}?crs={crs.authid()}"
    layer = QgsVectorLayer(uri, layer_name, "memory")
    if not layer.isValid():
        logger.error(f"Failed to create memory layer: {layer_name}")
        return None

    pr = layer.dataProvider()
    pr.addAttributes(fields)
    layer.updateFields()
    return layer


def densify_line_by_interval(geometry: QgsGeometry, interval: float) -> QgsGeometry:
    """Densify a line geometry by a specific distance interval.

    Args:
        geometry: Line geometry to densify.
        interval: Maximum distance between vertices.

    Returns:
        QgsGeometry: The densified geometry.
    """
    if not geometry or geometry.isNull():
        return QgsGeometry()
    return geometry.densifyByDistance(interval)


def run_geometry_operation(operation: str, *args, **kwargs) -> Any:
    """Generic wrapper for geometry operations.

    Args:
        operation: Name of the operation to perform.
        *args: Positional arguments for the operation.
        **kwargs: Keyword arguments for the operation.

    Returns:
        Any: Result of the operation.
    """
    # This is a placeholder for more complex logic if needed
    # For now it just logs and performs the op if possible
    logger.debug(f"Running geometry operation: {operation}")
    return None


def run_processing_algorithm(algorithm_id: str, parameters: dict[str, Any]) -> dict[str, Any]:
    """Execute a QGIS processing algorithm.

    Args:
        algorithm_id: The ID of the algorithm to run.
        parameters: A dictionary of parameters for the algorithm.

    Returns:
        dict[str, Any]: The algorithm results.
    """
    try:
        return processing.run(algorithm_id, parameters)
    except Exception:
        logger.exception(f"Error running processing algorithm {algorithm_id}")
        return {}
