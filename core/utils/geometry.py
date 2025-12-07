# -*- coding: utf-8 -*-
"""
Geometry Utilities Module

Spatial geometry operations using QGIS native algorithms.
"""

from qgis.core import (
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsVectorLayer,
    QgsFeature,
    QgsWkbTypes,
    QgsSpatialIndex,
    QgsFeatureRequest,
    QgsFields,
    QgsPointXY,
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
    fields: QgsFields = None,
) -> QgsVectorLayer:
    """Create a temporary memory layer with a single geometry feature.
    
    This is a reusable helper to avoid duplicating memory layer creation code.
    
    Args:
        geometry: Geometry to add to the layer
        crs: Coordinate reference system
        name: Layer name (default: "temp")
        fields: Optional fields definition
        
    Returns:
        QgsVectorLayer: Memory layer with the geometry
        
    Raises:
        ValueError: If geometry is invalid
        
    Example:
        >>> layer = create_memory_layer(line_geom, line_crs, "my_line")
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


def get_line_vertices(geometry: QgsGeometry) -> list[QgsPointXY]:
    """Extract vertices from a line geometry (handles multipart).
    
    This is a reusable helper to avoid duplicating multipart/singlepart logic.
    
    Args:
        geometry: Line geometry (LineString or MultiLineString)
        
    Returns:
        list[QgsPointXY]: List of vertices from the first part
        
    Raises:
        ValueError: If geometry is not a line or is invalid
        
    Example:
        >>> vertices = get_line_vertices(line_geom)
        >>> for pt in vertices:
        ...     print(pt.x(), pt.y())
    """
    if not geometry or geometry.isNull():
        raise ValueError("Geometry is null or invalid")
    
    if geometry.type() != QgsWkbTypes.LineGeometry:
        raise ValueError("Geometry must be a LineString or MultiLineString")
    
    # Handle multipart vs singlepart
    if geometry.isMultipart():
        parts = geometry.asMultiPolyline()
        if not parts:
            raise ValueError("MultiLineString has no parts")
        return parts[0]  # Return first part
    else:
        return geometry.asPolyline()


def run_processing_algorithm(
    algorithm: str,
    parameters: dict,
    silent: bool = True,
) -> dict:
    """Run a QGIS processing algorithm with consistent error handling.
    
    This is a reusable helper to avoid duplicating processing.run() boilerplate.
    
    Args:
        algorithm: Algorithm name (e.g., "native:buffer")
        parameters: Algorithm parameters dictionary
        silent: If True, suppress feedback output (default: True)
        
    Returns:
        dict: Algorithm result dictionary
        
    Raises:
        RuntimeError: If algorithm fails
        
    Example:
        >>> result = run_processing_algorithm(
        ...     "native:buffer",
        ...     {"INPUT": layer, "DISTANCE": 100, "OUTPUT": "memory:"}
        ... )
        >>> buffer_layer = result["OUTPUT"]
    """
    from qgis import processing
    from qgis.core import QgsProcessingFeedback
    
    try:
        feedback = QgsProcessingFeedback() if silent else None
        result = processing.run(algorithm, parameters, feedback=feedback)
        return result
    except Exception as e:
        error_msg = f"Processing algorithm '{algorithm}' failed: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


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

    Uses native:buffer for better CRS handling and robustness compared to
    the manual QgsGeometry.buffer() method.

    Args:
        geometry: Input geometry to buffer
        crs: Coordinate reference system of the geometry
        distance: Buffer distance in CRS units
        segments: Number of segments to approximate curves (default: 25)

    Returns:
        QgsGeometry: Buffered geometry

    Raises:
        ValueError: If buffer creation fails or geometry is invalid
        RuntimeError: If processing algorithm fails

    Example:
        >>> line_geom = line_layer.geometry()
        >>> buffer_geom = create_buffer_geometry(line_geom, line_layer.crs(), 100.0)
    """
    from qgis import processing
    from qgis.core import QgsProcessingFeedback

    if not geometry or geometry.isNull():
        raise ValueError("Input geometry is null or invalid")

    try:
        # Create temporary memory layer using helper
        temp_layer = create_memory_layer(geometry, crs, "temp_buffer")

        # Run native buffer algorithm using helper
        logger.debug(
            f"Creating buffer: distance={distance} {crs.mapUnits()}, segments={segments}"
        )

        result = run_processing_algorithm(
            "native:buffer",
            {
                "INPUT": temp_layer,
                "DISTANCE": distance,
                "SEGMENTS": segments,
                "END_CAP_STYLE": 0,  # Round
                "JOIN_STYLE": 0,  # Round
                "MITER_LIMIT": 2,
                "DISSOLVE": False,
                "OUTPUT": "memory:",
            },
        )

        # Extract buffer geometry from result
        buffer_layer = result["OUTPUT"]
        if buffer_layer.featureCount() == 0:
            raise ValueError("Buffer algorithm produced no features")

        # Get first feature's geometry
        buffer_feat = next(buffer_layer.getFeatures())
        buffer_geom = buffer_feat.geometry()

        if not buffer_geom or buffer_geom.isNull():
            raise ValueError("Buffer geometry is invalid")

        logger.debug("✓ Buffer created successfully using native algorithm")
        return buffer_geom

    except Exception as e:
        error_msg = f"Failed to create buffer using native algorithm: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def filter_features_by_buffer(
    features_layer: QgsVectorLayer,
    buffer_geometry: QgsGeometry,
    buffer_crs: QgsCoordinateReferenceSystem,
) -> list[QgsFeature]:
    """Filter features that intersect with buffer using native algorithm.

    Uses native:extractbylocation with spatial indexing for efficient filtering.
    This is much faster than manual iteration with intersects() for large datasets
    because it uses an R-tree spatial index.

    Args:
        features_layer: Layer containing features to filter
        buffer_geometry: Buffer geometry to use for spatial filter
        buffer_crs: CRS of the buffer geometry

    Returns:
        list[QgsFeature]: List of features that intersect the buffer
        
    Raises:
        ValueError: If inputs are invalid
    """
    if not features_layer or not features_layer.isValid():
        raise ValueError("Invalid features layer")
        
    if not buffer_geometry or buffer_geometry.isNull():
        raise ValueError("Invalid buffer geometry")

    # 1. Build Spatial Index 
    index = QgsSpatialIndex(features_layer.getFeatures())
    
    # 2. Get candidates using Bounding Box (Fast R-tree lookup)
    # intersects() returns list of feature IDs
    candidate_ids = index.intersects(buffer_geometry.boundingBox())
    
    # 3. Precise filtering
    filtered_features = []
    # Using QgsFeatureRequest with specific IDs is faster than iterating all
    if candidate_ids:
        request = QgsFeatureRequest().setFilterFids(candidate_ids)
        for feature in features_layer.getFeatures(request):
            if feature.geometry().intersects(buffer_geometry):
                filtered_features.append(feature)
            
    logger.debug(f"Spatial Index filtering: {len(candidate_ids)} candidates -> {len(filtered_features)} confirmed")
    
    return filtered_features


def densify_line_by_interval(
    geometry: QgsGeometry,
    interval: float,
) -> QgsGeometry:
    """Densify line geometry by adding vertices at regular intervals.

    Uses native:densifygeometriesgivenaninterval for precise vertex placement.
    This is simpler and more accurate than manual interpolation loops.

    Args:
        geometry: Line geometry to densify
        interval: Distance between vertices in geometry units

    Returns:
        QgsGeometry: Densified line geometry with vertices at regular intervals

    Raises:
        ValueError: If geometry is invalid or not a line
        RuntimeError: If densification algorithm fails

    Example:
        >>> line_geom = line_layer.geometry()
        >>> interval = raster_layer.rasterUnitsPerPixelX()
        >>> densified = densify_line_by_interval(line_geom, interval)
        >>> points = densified.asPolyline()  # Now has vertices at regular intervals
    """
    from qgis import processing
    from qgis.core import QgsProcessingFeedback

    if not geometry or geometry.isNull():
        raise ValueError("Input geometry is null or invalid")

    if geometry.type() != QgsWkbTypes.LineGeometry:
        raise ValueError("Geometry must be a LineString")

    try:
        # Create temporary layer using helper
        temp_layer = create_memory_layer(geometry, QgsCoordinateReferenceSystem(), "temp_densify")

        logger.debug(f"Densifying line with interval={interval:.2f}")

        # Run densification algorithm using helper
        result = run_processing_algorithm(
            "native:densifygeometriesgivenaninterval",
            {
                "INPUT": temp_layer,
                "INTERVAL": interval,
                "OUTPUT": "memory:",
            },
        )

        # Extract densified geometry
        densified_layer = result["OUTPUT"]
        if densified_layer.featureCount() == 0:
            raise ValueError("Densification produced no features")

        densified_feat = next(densified_layer.getFeatures())
        densified_geom = densified_feat.geometry()

        if not densified_geom or densified_geom.isNull():
            raise ValueError("Densified geometry is invalid")

        # Get vertex count for logging
        if densified_geom.isMultipart():
            vertex_count = sum(len(part) for part in densified_geom.asMultiPolyline())
        else:
            vertex_count = len(densified_geom.asPolyline())

        logger.debug(f"✓ Densification complete: {vertex_count} vertices")
        return densified_geom

    except Exception as e:
        error_msg = f"Failed to densify line: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
