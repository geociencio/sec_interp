"""Geometry Utilities Module.

Spatial geometry operations using QGIS native algorithms.
"""

from __future__ import annotations

from typing import Any, List, Optional, Union

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsFeatureRequest,
    QgsFields,
    QgsGeometry,
    QgsPointXY,
    QgsProcessingFeedback,
    QgsSpatialIndex,
    QgsVectorLayer,
    QgsWkbTypes,
)

from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


# ============================================================================
# Helper Functions
# ============================================================================


def create_memory_layer(
    geometry: QgsGeometry,
    crs: QgsCoordinateReferenceSystem,
    name: str = "temp",
    fields: Optional[QgsFields] = None,
) -> QgsVectorLayer:
    """Create a temporary QGIS memory layer with a single geometry feature.

    Args:
        geometry: The QGIS geometry to add to the layer.
        crs: The Coordinate Reference System for the new layer.
        name: Internal name for the layer (default: "temp").
        fields: Optional field definitions for attributes.

    Returns:
        QgsVectorLayer: A valid (but potentially empty on failure) QGIS memory layer.

    Raises:
        ValueError: If the input geometry is null or invalid.
        RuntimeError: If the memory layer cannot be initialized.
    """
    if not geometry or geometry.isNull():
        raise ValueError("Geometry is null or invalid")

    # Determine geometry type
    geom_type_map = {
        QgsWkbTypes.PointGeometry: "Point",
        QgsWkbTypes.LineGeometry: "LineString",
        QgsWkbTypes.PolygonGeometry: "Polygon",
    }
    geom_type = geom_type_map.get(geometry.type(), "LineString")

    # Create memory layer
    layer = QgsVectorLayer(geom_type, name, "memory")
    if not layer.isValid():
        raise RuntimeError(f"Failed to create memory layer of type {geom_type}")

    layer.setCrs(crs)

    # Add fields if provided
    if fields:
        layer.dataProvider().addAttributes(fields.toList())
        layer.updateFields()

    # Add geometry feature
    feat = QgsFeature()
    feat.setGeometry(geometry)
    layer.dataProvider().addFeatures([feat])

    return layer


def extract_all_vertices(geometry: QgsGeometry) -> list[QgsPointXY]:
    """Extract all vertices from any QGIS geometry type.

    Handles points, lines, and polygons, including multipart geometries.

    Args:
        geometry: The input QGIS geometry.

    Returns:
        List[QgsPointXY]: A flat list of all vertices found in the geometry.
    """
    if not geometry or geometry.isNull():
        return []

    if geometry.isMultipart():
        vertices = []
        # MultiLineString -> list of lists of points
        if geometry.type() == QgsWkbTypes.LineGeometry:
            for part in geometry.asMultiPolyline():
                vertices.extend(part)
        # MultiPoint -> list of points
        elif geometry.type() == QgsWkbTypes.PointGeometry:
            vertices.extend(geometry.asMultiPoint())
        # MultiPolygon -> list of lists of lists of points (simplified)
        elif geometry.type() == QgsWkbTypes.PolygonGeometry:
            for part in geometry.asMultiPolygon():
                for ring in part:
                    vertices.extend(ring)
        return vertices

    # Singlepart
    if geometry.type() == QgsWkbTypes.LineGeometry:
        return geometry.asPolyline()
    if geometry.type() == QgsWkbTypes.PointGeometry:
        return [geometry.asPoint()]
    if geometry.type() == QgsWkbTypes.PolygonGeometry:
        vertices = []
        for ring in geometry.asPolygon():
            vertices.extend(ring)
        return vertices

    return []


def get_line_vertices(geometry: QgsGeometry) -> list[QgsPointXY]:
    """Extract vertices specifically from a line or multiline geometry.

    Args:
        geometry: A QGIS geometry of type `LineGeometry`.

    Returns:
        List[QgsPointXY]: A flat list of vertices.

    Raises:
        ValueError: If the geometry is null, not a line, or contains no vertices.
    """
    if not geometry or geometry.isNull():
        raise ValueError("Geometry is null or invalid")

    if geometry.type() != QgsWkbTypes.LineGeometry:
        raise ValueError(f"Expected LineGeometry, got {geometry.type()}")

    vertices = extract_all_vertices(geometry)
    if not vertices:
        raise ValueError("Line geometry has no vertices")

    return vertices


def run_processing_algorithm(
    algorithm: str,
    parameters: dict,
    silent: bool = True,
) -> dict:
    """Execute a QGIS processing algorithm with consistent error handling.

    Args:
        algorithm: The provider:algorithm ID (e.g., "native:buffer").
        parameters: A dictionary of algorithm parameters.
        silent: If True, uses a silent feedback object (default: True).

    Returns:
        dict: The result dictionary returned by `processing.run`.

    Raises:
        RuntimeError: If the algorithm fails to execute or returns an error.
    """
    from qgis import processing

    try:
        feedback = QgsProcessingFeedback() if silent else None
        result = processing.run(algorithm, parameters, feedback=feedback)
        return result
    except Exception as e:
        error_msg = f"Processing algorithm '{algorithm}' failed: {e!s}"
        logger.exception(error_msg)
        raise RuntimeError(error_msg) from e


def run_geometry_operation(
    algorithm: str,
    geometry: QgsGeometry,
    crs: QgsCoordinateReferenceSystem,
    parameters: dict,
) -> QgsGeometry:
    """Run a processing algorithm on a single geometry by wrapping it in a memory layer.

    Args:
        algorithm: The algorithm ID to run.
        geometry: The input geometry.
        crs: The CRS of the input geometry.
        parameters: Additional parameters (INPUT and OUTPUT are automatically handled).

    Returns:
        QgsGeometry: The resulting geometry from the operation's output layer.

    Raises:
        ValueError: If the operation yields no features or an invalid geometry.
        RuntimeError: If the underlying processing algorithm fails.
    """
    # 1. Create temporary input
    temp_layer = create_memory_layer(geometry, crs, f"input_{algorithm.split(':')[-1]}")

    # 2. Prepare parameters
    full_params = parameters.copy()
    full_params["INPUT"] = temp_layer
    full_params["OUTPUT"] = "memory:"

    # 3. Run algorithm
    result = run_processing_algorithm(algorithm, full_params)

    # 4. Extract output
    out_layer = result.get("OUTPUT")
    if not out_layer or out_layer.featureCount() == 0:
        raise ValueError(f"Algorithm {algorithm} produced no results")

    feat = next(out_layer.getFeatures())
    out_geom = feat.geometry()

    if not out_geom or out_geom.isNull():
        raise ValueError(f"Resulting geometry from {algorithm} is null")

    return out_geom


# ============================================================================
# Main Functions
# ============================================================================


def create_buffer_geometry(
    geometry: QgsGeometry,
    crs: QgsCoordinateReferenceSystem,
    distance: float,
    segments: int = 25,
) -> QgsGeometry:
    """Create buffer geometry using native QGIS processing algorithm.

    Args:
        geometry: Input geometry to buffer.
        crs: Coordinate reference system.
        distance: Buffer distance in CRS units.
        segments: Number of segments for curves (default: 25).

    Returns:
        QgsGeometry: Buffered geometry.
    """
    logger.debug(f"Buffering geometry: distance={distance}, segments={segments}")

    return run_geometry_operation(
        "native:buffer",
        geometry,
        crs,
        {
            "DISTANCE": distance,
            "SEGMENTS": segments,
            "END_CAP_STYLE": 0,  # Round
            "JOIN_STYLE": 0,  # Round
            "MITER_LIMIT": 2,
            "DISSOLVE": False,
        },
    )


def filter_features_by_buffer(
    features_layer: QgsVectorLayer,
    buffer_geometry: QgsGeometry,
    buffer_crs: QgsCoordinateReferenceSystem | None = None,
) -> list[QgsFeature]:
    """Filter features that intersect with buffer using spatial index.

    Args:
        features_layer: Layer containing features to filter.
        buffer_geometry: Buffer geometry to use for spatial filter.
        buffer_crs: CRS of the buffer geometry (optional, for compatibility).

    Returns:
        List[QgsFeature]: Features that intersect the buffer.

    Raises:
        ValueError: If inputs are invalid.
    """
    if not features_layer or not features_layer.isValid():
        raise ValueError("Invalid features layer")

    if not buffer_geometry or buffer_geometry.isNull():
        raise ValueError("Invalid buffer geometry")

    # 1. Build Spatial Index (Optimized for repeated queries)
    index = QgsSpatialIndex(features_layer.getFeatures())

    # 2. Get candidates using Bounding Box (Fast R-tree lookup)
    candidate_ids = index.intersects(buffer_geometry.boundingBox())

    # 3. Precise filtering
    filtered_features = []
    if candidate_ids:
        request = QgsFeatureRequest().setFilterFids(candidate_ids)
        for feature in features_layer.getFeatures(request):
            if feature.geometry().intersects(buffer_geometry):
                filtered_features.append(feature)

    logger.debug(
        f"Spatial Index: {len(candidate_ids)} candidates -> {len(filtered_features)} confirmed"
    )

    return filtered_features


def densify_line_by_interval(
    geometry: QgsGeometry,
    interval: float,
) -> QgsGeometry:
    """Densify line geometry by adding vertices at regular intervals.

    Args:
        geometry: Line geometry to densify.
        interval: Distance between vertices in geometry units.

    Returns:
        QgsGeometry: Densified line geometry.

    Raises:
        ValueError: If geometry is not a line.
    """
    if not geometry or geometry.isNull():
        raise ValueError("Input geometry is null or invalid")

    if geometry.type() != QgsWkbTypes.LineGeometry:
        raise ValueError("Densification only supported for LineGeometry")

    logger.debug(f"Densifying line with interval={interval:.2f}")

    return run_geometry_operation(
        "native:densifygeometriesgivenaninterval",
        geometry,
        QgsCoordinateReferenceSystem(),  # Unused for densification
        {"INTERVAL": interval},
    )
