"""Structural-measurement layer builder for the preview."""

from __future__ import annotations

import math
from typing import Any

from qgis.core import QgsFeature, QgsGeometry, QgsVectorLayer

from sec_interp.core.domain import ProfileData, StructureData


def create_struct_layer(
    factory: Any,
    struct_data: StructureData,
    reference_data: ProfileData,
    vert_exag: float = 1.0,
    dip_line_length: float | None = None,
    color: str | None = None,
    width: float | None = None,
) -> QgsVectorLayer | None:
    """Create a temporary layer for structural dips."""
    if not struct_data:
        return None

    layer, provider = factory.create_memory_layer("LineString", "Structures")
    if not layer:
        return None

    if dip_line_length is not None and dip_line_length > 0:
        line_length = dip_line_length
    else:
        if reference_data:
            elevs = [e for _, e in reference_data]
            e_range = max(elevs) - min(elevs)
        else:
            e_range = 100
        line_length = e_range * 0.1

    features = []
    for measurement in struct_data:
        elev = measurement.elevation
        dist = measurement.distance
        app_dip = measurement.apparent_dip
        rad_dip = math.radians(abs(app_dip))
        dx = line_length * math.cos(rad_dip)
        dy = line_length * math.sin(rad_dip)
        if app_dip < 0:
            dx = -dx

        points = [(dist, elev), (dist + dx, elev - dy)]
        line_points = factory._to_qgs_points(factory._apply_exaggeration(points, vert_exag))
        line_geom = QgsGeometry.fromPolylineXY(line_points)
        feat = QgsFeature()
        feat.setGeometry(line_geom)
        features.append(feat)

    provider.addFeatures(features)
    factory.struct_renderer.apply_style(layer, color=color, width=width)
    layer.updateExtents()
    return layer
