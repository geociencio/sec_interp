"""Axes and grid management for SecInterp preview.

Handles the creation of grid lines and axes labels with nice intervals.
"""

from __future__ import annotations

import math
from typing import Optional

from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsLineString,
    QgsLineSymbol,
    QgsMarkerSymbol,
    QgsPalLayerSettings,
    QgsPointXY,
    QgsProject,
    QgsProperty,
    QgsPropertyCollection,
    QgsSingleSymbolRenderer,
    QgsTextFormat,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
)
from qgis.PyQt.QtGui import QColor

from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


class PreviewAxesManager:
    """Manages the creation and styling of axes and grid lines for the preview."""

    @staticmethod
    def get_nice_interval(target_step: float) -> float:
        """Calculate a nice interval for grid lines (1-2-5 sequence)."""
        if target_step <= 0:
            return 100.0

        exponent = math.floor(math.log10(target_step))
        fraction = target_step / (10**exponent)

        if fraction < 1.5:
            nice_fraction = 1.0
        elif fraction < 3.5:
            nice_fraction = 2.0
        elif fraction < 7.5:
            nice_fraction = 5.0
        else:
            nice_fraction = 10.0

        return nice_fraction * (10**exponent)

    @classmethod
    def create_axes_layer(
        cls, extent, vert_exag: float = 1.0
    ) -> Optional[QgsVectorLayer]:
        """Create temporary layer for axes and grid."""
        if not extent:
            return None

        layer = QgsVectorLayer("LineString", "Axes", "memory")

        # Ensure layer has a valid CRS (Project CRS)
        project_crs = QgsProject.instance().crs()
        if project_crs.isValid():
             layer.setCrs(project_crs)

        provider = layer.dataProvider()

        width = extent.width()
        height = extent.height()

        x_interval = cls.get_nice_interval(width / 5)
        y_interval = cls.get_nice_interval((height / vert_exag) / 5)

        x_start = math.floor(extent.xMinimum() / x_interval) * x_interval
        y_min_orig = extent.yMinimum() / vert_exag
        y_max_orig = extent.yMaximum() / vert_exag
        y_start = math.floor(y_min_orig / y_interval) * y_interval

        features = []

        # Vertical grid lines
        y_floor = y_start * vert_exag
        y_ceil = (math.ceil(y_max_orig / y_interval) * y_interval) * vert_exag

        x = x_start
        last_x = x_start
        while x <= extent.xMaximum() + 0.1:  # Small epsilon
            p1 = QgsPointXY(x, y_floor)
            p2 = QgsPointXY(x, y_ceil)
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry(QgsLineString([p1, p2])))
            features.append(feat)
            last_x = x
            x += x_interval

        # Horizontal grid lines
        y = y_start
        while y <= y_max_orig + 0.1:  # Small epsilon
            y_draw = y * vert_exag
            p1 = QgsPointXY(x_start, y_draw)
            p2 = QgsPointXY(last_x, y_draw)
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry(QgsLineString([p1, p2])))
            features.append(feat)
            y += y_interval

        provider.addFeatures(features)

        symbol = QgsLineSymbol.createSimple(
            {"color": "200,200,200", "width": "0.3", "line_style": "dash"}
        )
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        return layer

    @classmethod
    def create_axes_labels_layer(
        cls, extent, vert_exag: float = 1.0
    ) -> Optional[QgsVectorLayer]:
        """Create a point layer for axes labels."""
        if not extent:
            return None

        layer = QgsVectorLayer(
            "Point?field=label:string&field=quadrant:integer",
            "Axes Labels",
            "memory",
        )

        # Ensure layer has a valid CRS (Project CRS)
        project_crs = QgsProject.instance().crs()
        if project_crs.isValid():
             layer.setCrs(project_crs)

        provider = layer.dataProvider()

        width = extent.width()
        height = extent.height()

        x_interval = cls.get_nice_interval(width / 5)
        y_interval = cls.get_nice_interval((height / vert_exag) / 5)

        x_start = math.floor(extent.xMinimum() / x_interval) * x_interval
        y_min_orig = extent.yMinimum() / vert_exag
        y_max_orig = extent.yMaximum() / vert_exag
        y_start = math.floor(y_min_orig / y_interval) * y_interval
        y_floor = y_start * vert_exag

        features = []

        # X Axis Labels
        x = x_start
        while x <= extent.xMaximum() + 0.1:
            feat = QgsFeature(layer.fields())
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y_floor)))
            feat.setAttribute("label", f"{x:.0f}")
            feat.setAttribute("quadrant", 7)  # Below
            features.append(feat)
            x += x_interval

        # Y Axis Labels
        y = y_start
        while y <= y_max_orig + 0.1:
            y_draw = y * vert_exag
            feat = QgsFeature(layer.fields())
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x_start, y_draw)))
            feat.setAttribute("label", f"{y:.0f}")
            feat.setAttribute("quadrant", 3)  # Left
            features.append(feat)
            y += y_interval

        provider.addFeatures(features)

        settings = QgsPalLayerSettings()
        settings.fieldName = "label"
        settings.placement = QgsPalLayerSettings.Placement.OverPoint

        txt_format = QgsTextFormat()
        txt_format.setColor(QColor(0, 0, 0))
        txt_format.setSize(8)
        settings.setFormat(txt_format)

        props = QgsPropertyCollection()
        props.setProperty(
            QgsPalLayerSettings.Property.OffsetQuad, QgsProperty.fromField("quadrant")
        )
        # Significant distance for Y (quadrant 3) vs X (quadrant 7)
        props.setProperty(
            QgsPalLayerSettings.Property.LabelDistance,
            QgsProperty.fromExpression("IF(quadrant=3, 15, 8)"),
        )
        settings.setDataDefinedProperties(props)
        settings.dist = 8.0  # Fallback

        layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))
        layer.setLabelsEnabled(True)

        symbol = QgsMarkerSymbol.createSimple({"size": "0", "color": "0,0,0,0"})
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        return layer
