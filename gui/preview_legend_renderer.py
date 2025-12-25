"""Legend rendering logic for SecInterp preview.

Handles the drawing of the legend on a QPainter, including topography,
structures, and geological units.
"""

from __future__ import annotations

from typing import Optional

from qgis.PyQt.QtCore import QCoreApplication, QRectF, Qt
from qgis.PyQt.QtGui import QColor, QFont, QPainter, QPen

from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


class PreviewLegendRenderer:
    """Handles drawing the map legend for the profile preview."""

    @staticmethod
    def draw_legend(
        painter: QPainter,
        rect: QRectF,
        active_units: dict[str, QColor],
        has_topography: bool = False,
        has_structures: bool = False,
    ):
        """Draw legend on the given painter within the rect."""
        if not active_units and not has_topography and not has_structures:
            return

        # Configuration
        config = {
            "padding": 6,
            "item_height": 16,
            "symbol_size": 10,
            "line_width": 2,
            "margin": 20,
        }

        painter.save()
        painter.setFont(QFont("Arial", 8))

        legend_size, max_text_width = PreviewLegendRenderer._calculate_legend_size(
            painter, active_units, has_topography, has_structures, config
        )

        # Position: Top Right
        x = rect.width() - legend_size.width() - config["margin"]
        y = config["margin"]

        PreviewLegendRenderer._draw_legend_background(
            painter, x, y, legend_size.width(), legend_size.height()
        )

        # Draw items
        current_y = y + config["padding"]
        if has_topography:
            PreviewLegendRenderer._draw_line_item(
                painter, x, current_y, QCoreApplication.translate("PreviewLegendRenderer", "Topography"), QColor(0, 102, 204),
                max_text_width, config
            )
            current_y += config["item_height"]

        if has_structures:
            PreviewLegendRenderer._draw_line_item(
                painter, x, current_y, QCoreApplication.translate("PreviewLegendRenderer", "Structures"), QColor(204, 0, 0),
                max_text_width, config
            )
            current_y += config["item_height"]

        PreviewLegendRenderer._draw_geology_items(
            painter, x, current_y, active_units, max_text_width, config
        )

        painter.restore()

    @staticmethod
    def _calculate_legend_size(painter, active_units, has_topo, has_struct, config):
        """Calculate dimensions of the legend box."""
        fm = painter.fontMetrics()
        max_text_width = 0

        items = []
        if has_topo:
            items.append(QCoreApplication.translate("PreviewLegendRenderer", "Topography"))
        if has_struct:
            items.append(QCoreApplication.translate("PreviewLegendRenderer", "Structures"))
        items.extend(active_units.keys())

        for item in items:
            max_text_width = max(max_text_width, fm.boundingRect(item).width())

        width = max_text_width + config["symbol_size"] + config["padding"] * 3
        height = len(items) * config["item_height"] + config["padding"] * 2
        return QRectF(0, 0, width, height), max_text_width

    @staticmethod
    def _draw_legend_background(painter, x, y, width, height):
        """Draw the legend box background and border."""
        rect = QRectF(x, y, width, height)
        painter.setBrush(QColor(255, 255, 255, 200))
        painter.setPen(Qt.NoPen)
        painter.drawRect(rect)

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QColor(100, 100, 100))
        painter.drawRect(rect)

    @staticmethod
    def _draw_line_item(painter, x, y, label, color, max_width, config):
        """Draw a legend item with a line symbol."""
        p = config["padding"]
        ih = config["item_height"]
        ss = config["symbol_size"]

        painter.setPen(QPen(color, config["line_width"]))
        painter.drawLine(int(x + p), int(y + ih / 2), int(x + p + ss), int(y + ih / 2))

        painter.setPen(QColor(0, 0, 0))
        text_rect = QRectF(x + p * 2 + ss, y, max_width, ih)
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, label)

    @staticmethod
    def _draw_geology_items(painter, x, y, units, max_width, config):
        """Draw geological unit legend items."""
        p = config["padding"]
        ih = config["item_height"]
        ss = config["symbol_size"]

        for name, color in units.items():
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRect(QRectF(x + p, y + (ih - ss) / 2, ss, ss))

            painter.setPen(QColor(0, 0, 0))
            text_rect = QRectF(x + p * 2 + ss, y, max_width, ih)
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, name)
            y += ih

        painter.restore()
