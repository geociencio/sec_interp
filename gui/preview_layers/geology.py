"""Geology layer builder for the preview."""

from __future__ import annotations

from typing import Any

from qgis.core import QgsFeature, QgsGeometry, QgsVectorLayer

from sec_interp.core.domain import GeologyData
from sec_interp.core.utils.geometry_utils.optimization import PreviewOptimizer


def create_geol_layer(
    factory: Any,
    geol_data: GeologyData,
    vert_exag: float = 1.0,
    max_points: int = 1000,
) -> QgsVectorLayer | None:
    """Create a temporary layer for the geological profile."""
    if not geol_data:
        return None

    layer, provider = factory.create_memory_layer("LineString", "Geology", "field=unit:string")
    if not layer:
        return None

    unique_units = {s.unit_name for s in geol_data}
    factory.color_manager.register_units(unique_units)
    features = []
    min_required_points = 2
    for segment in geol_data:
        if not segment.points or len(segment.points) < min_required_points:
            continue

        render_points = PreviewOptimizer.decimate(segment.points, max_points=max_points)
        line_points = factory._to_qgs_points(factory._apply_exaggeration(render_points, vert_exag))
        line_geom = QgsGeometry.fromPolylineXY(line_points)
        feat = QgsFeature(layer.fields())
        feat.setGeometry(line_geom)
        feat.setAttribute("unit", segment.unit_name)
        features.append(feat)

    provider.addFeatures(features)
    factory.geol_renderer.apply_style(layer, unique_units=unique_units)
    layer.updateExtents()
    return layer
