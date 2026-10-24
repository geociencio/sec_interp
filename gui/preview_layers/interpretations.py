"""Interpretation polygon layer builder for the preview."""

from __future__ import annotations

from typing import Any

from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer

from sec_interp.core.domain.entities import InterpretationPolygon


def create_interp_layer(
    factory: Any,
    interp_data: list[InterpretationPolygon],
    vert_exag: float = 1.0,
    default_color: str | None = None,
    hidden_ids: set[str] | None = None,
) -> QgsVectorLayer | None:
    """Create a memory layer for interpretation polygons (hidden ones skipped)."""
    if not interp_data:
        return None
    hidden = {str(i) for i in (hidden_ids or set())}
    visible = [i for i in interp_data if str(getattr(i, "id", "")) not in hidden]
    if not visible:
        return None
    interp_data = visible

    layer, provider = factory.create_memory_layer(
        "Polygon", "Interpretations", "field=id:string&field=name:string"
    )
    if not layer:
        return None

    features = []
    min_polygon_points = 3
    for interp in interp_data:
        if not interp.vertices_2d or len(interp.vertices_2d) < min_polygon_points:
            continue

        points = [QgsPointXY(x, y * vert_exag) for x, y in interp.vertices_2d]
        if points[0] != points[-1]:
            points.append(points[0])

        geom = QgsGeometry.fromPolygonXY([points])
        feat = QgsFeature(layer.fields())
        feat.setGeometry(geom)
        feat.setAttribute("id", interp.id)
        feat.setAttribute("name", interp.name)
        features.append(feat)

    if not features:
        return None

    provider.addFeatures(features)
    factory.interp_renderer.apply_style(layer, interp_data=interp_data, default_color=default_color)
    layer.updateExtents()
    return layer
