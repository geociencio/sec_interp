"""Drillhole layer builders for the preview."""

from __future__ import annotations

from typing import Any

from qgis.core import QgsFeature, QgsGeometry, QgsVectorLayer
from qgis.PyQt.QtCore import QCoreApplication

from sec_interp.core.domain import DrillholeProjection
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def create_drillhole_trace_layer(
    factory: Any,
    drillhole_data: list,
    vert_exag: float = 1.0,
    color: str | None = None,
    width: float | None = None,
    labels: bool = True,
) -> QgsVectorLayer | None:
    """Create a temporary layer for drillhole traces."""
    logger.debug(
        f"create_drillhole_trace_layer called with "
        f"{len(drillhole_data) if drillhole_data else 0} holes"
    )
    if not drillhole_data:
        logger.warning("No drillhole data provided for trace layer")
        return None

    layer, provider = factory.create_memory_layer(
        "LineString",
        QCoreApplication.translate("PreviewLayerFactory", "Drillhole Traces"),
        "field=hole_id:string",
    )
    if not layer:
        return None

    features = []
    for hole_data in drillhole_data:
        hole_id, trace_points = _extract_trace_data(hole_data)
        feat = _create_trace_feature(factory, hole_id, trace_points, layer.fields(), vert_exag)
        if feat:
            features.append(feat)

    logger.info(f"Adding {len(features)} drillhole trace features to layer")
    provider.addFeatures(features)
    factory.drill_renderer.apply_style(layer, role="trace", color=color, width=width, labels=labels)
    layer.updateExtents()
    return layer


def _extract_trace_data(hole_data: Any) -> tuple[Any, Any]:
    """Extract hole_id and trace_points from hole_data."""
    if isinstance(hole_data, DrillholeProjection):
        return hole_data.hole_id, hole_data.points_3d
    return hole_data[0], hole_data[1]


def _create_trace_feature(
    factory: Any,
    hole_id: Any,
    trace_points: Any,
    fields: Any,
    vert_exag: float,
) -> QgsFeature | None:
    """Create a single trace feature if enough points exist."""
    min_trace_points = 2
    if not trace_points or len(trace_points) < min_trace_points:
        return None

    render_points = []
    for point in trace_points:
        dist = getattr(point, "dist_along", point[0] if isinstance(point, (list, tuple)) else 0.0)
        z = getattr(point, "z", point[1] if isinstance(point, (list, tuple)) else 0.0)
        render_points.append((dist, z))

    line_points = factory._to_qgs_points(factory._apply_exaggeration(render_points, vert_exag))
    line_geom = QgsGeometry.fromPolylineXY(line_points)
    feat = QgsFeature(fields)
    feat.setGeometry(line_geom)
    feat.setAttribute("hole_id", hole_id)
    return feat


def create_drillhole_interval_layer(
    factory: Any,
    drillhole_data: list,
    vert_exag: float = 1.0,
) -> QgsVectorLayer | None:
    """Create a temporary layer for drillhole intervals."""
    if not drillhole_data:
        return None

    all_segments = _collect_all_segments(drillhole_data)
    if not all_segments:
        return None

    layer, provider = factory.create_memory_layer(
        "LineString",
        QCoreApplication.translate("PreviewLayerFactory", "Drillhole Intervals"),
        "field=unit:string",
    )
    if not layer:
        return None

    unique_units = set()
    features = _create_interval_features(
        factory, all_segments, layer.fields(), vert_exag, unique_units
    )

    provider.addFeatures(features)
    factory.color_manager.register_units(unique_units, source="drillholes")
    factory.drill_renderer.apply_style(layer, role="interval", unique_units=unique_units)
    layer.updateExtents()
    return layer


def _collect_all_segments(drillhole_data: list) -> list:
    """Collect all segments from a list of drillhole_data items."""
    all_segments = []
    for hole_data in drillhole_data:
        if isinstance(hole_data, DrillholeProjection):
            segments = hole_data.segments
        else:
            min_hole_data_for_segments = 3
            segments = hole_data[-1] if len(hole_data) >= min_hole_data_for_segments else []

        if segments and isinstance(segments, list):
            all_segments.extend(segments)
    return all_segments


def _create_interval_features(
    factory: Any,
    all_segments: list,
    fields: Any,
    vert_exag: float,
    unique_units: set,
) -> list[QgsFeature]:
    """Create QgsFeature objects for valid segments."""
    features = []
    min_segment_points = 2
    for segment in all_segments:
        if not segment.points or len(segment.points) < min_segment_points:
            continue

        unique_units.add(segment.unit_name)
        line_points = factory._to_qgs_points(factory._apply_exaggeration(segment.points, vert_exag))
        line_geom = QgsGeometry.fromPolylineXY(line_points)
        feat = QgsFeature(fields)
        feat.setGeometry(line_geom)
        feat.setAttribute("unit", segment.unit_name)
        features.append(feat)
    return features
