"""Geometry filtering utilities."""

from __future__ import annotations

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsFeatureRequest,
    QgsGeometry,
    QgsProject,
    QgsSpatialIndex,
    QgsVectorLayer,
)

from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


def filter_features_by_buffer(
    features_layer: QgsVectorLayer,
    buffer_geometry: QgsGeometry,
    buffer_crs: QgsCoordinateReferenceSystem | None = None,
) -> list[QgsFeature]:
    """Filter features that intersect with buffer using spatial index.

    Args:
        features_layer: Layer containing features to filter.
        buffer_geometry: Buffer geometry to use for spatial filter.
        buffer_crs: CRS of the buffer geometry (optional).

    Returns:
        list[QgsFeature]: Features that intersect the buffer.
    """
    if not features_layer or not features_layer.isValid():
        raise ValueError("Invalid features layer")

    if not buffer_geometry or buffer_geometry.isNull():
        raise ValueError("Invalid buffer geometry")

    # 1. Transform buffer geometry if needed
    query_geom = buffer_geometry
    if buffer_crs and features_layer.crs() != buffer_crs:
        transform = QgsCoordinateTransform(
            buffer_crs, features_layer.crs(), QgsProject.instance()
        )
        query_geom = QgsGeometry(buffer_geometry)
        query_geom.transform(transform)

    # 2. Build Spatial Index (Optimized for repeated queries)
    index = QgsSpatialIndex(features_layer.getFeatures())

    # 3. Get candidates using Bounding Box (Fast R-tree lookup)
    candidate_ids = index.intersects(query_geom.boundingBox())

    # 4. Precise filtering
    filtered_features = []
    if candidate_ids:
        request = QgsFeatureRequest().setFilterFids(candidate_ids)
        for feature in features_layer.getFeatures(request):
            if feature.geometry().intersects(query_geom):
                filtered_features.append(feature)

    logger.debug(
        f"Spatial Index: {len(candidate_ids)} candidates -> {len(filtered_features)} confirmed"
    )

    return filtered_features
