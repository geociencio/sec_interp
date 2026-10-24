"""Topography layer builders for the preview."""

from __future__ import annotations

from typing import Any

from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsLineSymbol,
    QgsPointXY,
    QgsSingleSymbolRenderer,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QColor

from sec_interp.core.domain import ProfileData
from sec_interp.core.utils.geometry_utils.optimization import PreviewOptimizer


def create_topo_layer(
    factory: Any,
    topo_data: ProfileData,
    vert_exag: float = 1.0,
    max_points: int = 1000,
    use_adaptive_sampling: bool = False,
    color_mode: str = "gradient",
    ramp_name: str | None = None,
    single_color: str | None = None,
    line_width: float | None = None,
) -> QgsVectorLayer | None:
    """Create a temporary layer for the topographic profile."""
    min_required_points = 2
    if not topo_data or len(topo_data) < min_required_points:
        return None

    if use_adaptive_sampling:
        render_data = PreviewOptimizer.adaptive_sample(topo_data, max_points=max_points)
    else:
        render_data = PreviewOptimizer.decimate(topo_data, max_points=max_points)

    layer, provider = factory.create_memory_layer("LineString", "Topography", "field=elev:double")
    if not layer:
        return None

    features = []
    for i in range(len(render_data) - 1):
        p1 = render_data[i]
        p2 = render_data[i + 1]
        line_points = factory._to_qgs_points(factory._apply_exaggeration([p1, p2], vert_exag))
        line_geom = QgsGeometry.fromPolylineXY(line_points)
        feat = QgsFeature(layer.fields())
        feat.setGeometry(line_geom)
        avg_elev = (p1[1] + p2[1]) / 2.0
        feat.setAttribute("elev", avg_elev)
        features.append(feat)

    if not features:
        return None

    provider.addFeatures(features)
    factory.topo_renderer.apply_style(
        layer,
        color_mode=color_mode,
        ramp_name=ramp_name,
        single_color=single_color,
        line_width=line_width,
    )
    layer.updateExtents()
    return layer


def create_smoothed_topo_layer(
    factory: Any,
    topo_data: ProfileData,
    vert_exag: float = 1.0,
    max_points: int = 1000,
    color: str = "#e57373",
) -> QgsVectorLayer | None:
    """Create a smoothed topography overlay line (soft red by default)."""
    min_required_points = 2
    if not topo_data or len(topo_data) < min_required_points:
        return None

    render_data = PreviewOptimizer.decimate(topo_data, max_points=max_points)
    layer, provider = factory.create_memory_layer("LineString", "Smoothed Topography")  # no-i18n
    if not layer:
        return None

    points = factory._to_qgs_points(factory._apply_exaggeration(render_data, vert_exag))
    geometry = QgsGeometry.fromPolylineXY(points)
    feature = QgsFeature(layer.fields())
    feature.setGeometry(geometry)
    provider.addFeatures([feature])

    symbol = QgsLineSymbol.createSimple({"width": "1.2", "capstyle": "round"})
    symbol.setColor(QColor(color))
    layer.setRenderer(QgsSingleSymbolRenderer(symbol))
    layer.updateExtents()
    return layer


def create_topo_fill_layer(
    factory: Any,
    topo_data: ProfileData,
    vert_exag: float = 1.0,
    max_points: int = 1000,
    base_elevation: float | None = None,
) -> QgsVectorLayer | None:
    """Create a solid curtain fill under the topography."""
    min_required_points = 2
    if not topo_data or len(topo_data) < min_required_points:
        return None

    render_data = PreviewOptimizer.decimate(topo_data, max_points=max_points)
    layer, provider = factory.create_memory_layer(
        "Polygon",
        QCoreApplication.translate("PreviewLayerFactory", "Topography Fill"),
    )
    if not layer:
        return None

    elevs = [p[1] for p in topo_data]
    if base_elevation is None:
        base_elevation = min(elevs) - (max(elevs) - min(elevs)) * 0.2

    base_y = base_elevation * vert_exag
    poly_points = [QgsPointXY(d, e * vert_exag) for d, e in render_data]
    poly_points.append(QgsPointXY(render_data[-1][0], base_y))
    poly_points.append(QgsPointXY(render_data[0][0], base_y))
    poly_points.append(QgsPointXY(render_data[0][0], render_data[0][1] * vert_exag))

    geom = QgsGeometry.fromPolygonXY([poly_points])
    feat = QgsFeature()
    feat.setGeometry(geom)
    provider.addFeatures([feat])
    factory.struct_renderer.apply_style(layer)
    layer.updateExtents()
    return layer
