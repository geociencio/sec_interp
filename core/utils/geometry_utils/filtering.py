"""Geometry filtering and cleaning utilities."""

from __future__ import annotations

"""Geometry filtering utilities."""

from PyQt5.QtCore import QCoreApplication
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsFeatureRequest,
    QgsGeometry,
    QgsProject,
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
        List of QgsFeature objects that intersect the query buffer.

    """
    if not features_layer or not features_layer.isValid():
        raise ValueError(QCoreApplication.translate("GeometryFiltering", "Invalid features layer"))

    if not buffer_geometry or buffer_geometry.isNull():
        raise ValueError(QCoreApplication.translate("GeometryFiltering", "Invalid buffer geometry"))

    # 1. Transform buffer geometry if needed
    query_geom = buffer_geometry
    if buffer_crs and features_layer.crs() != buffer_crs:
        transform = QgsCoordinateTransform(buffer_crs, features_layer.crs(), QgsProject.instance())
        query_geom = QgsGeometry(buffer_geometry)
        query_geom.transform(transform)

    # 2. Get candidates using Bounding Box (Provider side filter)
    # This uses the provider's spatial index directly, avoiding O(N) index build
    request = QgsFeatureRequest().setFilterRect(query_geom.boundingBox())

    # 3. Precise filtering
    filtered_features = []
    for feature in features_layer.getFeatures(request):
        if feature.hasGeometry() and feature.geometry().intersects(query_geom):
            filtered_features.append(feature)

    logger.debug(f"Spatial Filter: confirmed {len(filtered_features)} features intersecting buffer")

    return filtered_features
