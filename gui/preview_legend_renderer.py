"""Legend rendering logic for SecInterp preview.

Handles the drawing of the legend on a QPainter, including topography, 
structures, and geological units.
"""

from typing import Dict, Optional

from qgis.PyQt.QtCore import QRectF, Qt
from qgis.PyQt.QtGui import QColor, QFont, QPainter, QPen

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class PreviewLegendRenderer:
    """Handles drawing the map legend for the profile preview."""

    @staticmethod
    def draw_legend(
        painter: QPainter,
        rect: QRectF,
        active_units: Dict[str, QColor],
        has_topography: bool = False,
        has_structures: bool = False,
    ):
        """Draw legend on the given painter within the rect.

        Args:
            painter: QPainter instance
            rect: QRectF defining the drawing area
            active_units: Dictionary of unit names and their colors
            has_topography: Whether topography is present in the preview
            has_structures: Whether structures are present in the preview
        """
        # Check if we have anything to show
        if not active_units and not has_topography and not has_structures:
            return

        # Legend configuration
        padding = 6
        item_height = 16
        symbol_size = 10
        line_width = 2
        font_size = 8

        painter.save()
        font = QFont("Arial", font_size)
        painter.setFont(font)

        # Calculate legend size
        fm = painter.fontMetrics()
        max_width = 0

        if has_topography:
            max_width = max(max_width, fm.boundingRect("Topography").width())
        if has_structures:
            max_width = max(max_width, fm.boundingRect("Structures").width())
        for name in active_units:
            width = fm.boundingRect(name).width()
            max_width = max(max_width, width)

        total_items = len(active_units)
        if has_topography:
            total_items += 1
        if has_structures:
            total_items += 1

        legend_width = max_width + symbol_size + padding * 3
        legend_height = total_items * item_height + padding * 2

        # Position: Top Right with margin
        margin = 20
        x = rect.width() - legend_width - margin
        y = margin

        # Draw background
        bg_color = QColor(255, 255, 255, 200)
        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(QRectF(x, y, legend_width, legend_height))

        # Draw border
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QColor(100, 100, 100))
        painter.drawRect(QRectF(x, y, legend_width, legend_height))

        # Draw items
        current_y = y + padding

        # Draw topography
        if has_topography:
            painter.setPen(QPen(QColor(0, 102, 204), line_width))
            painter.drawLine(
                int(x + padding),
                int(current_y + item_height / 2),
                int(x + padding + symbol_size),
                int(current_y + item_height / 2),
            )
            painter.setPen(QColor(0, 0, 0))
            text_rect = QRectF(x + padding * 2 + symbol_size, current_y, max_width, item_height)
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, "Topography")
            current_y += item_height

        # Draw structures
        if has_structures:
            painter.setPen(QPen(QColor(204, 0, 0), line_width))
            painter.drawLine(
                int(x + padding),
                int(current_y + item_height / 2),
                int(x + padding + symbol_size),
                int(current_y + item_height / 2),
            )
            painter.setPen(QColor(0, 0, 0))
            text_rect = QRectF(x + padding * 2 + symbol_size, current_y, max_width, item_height)
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, "Structures")
            current_y += item_height

        # Draw geological units
        for name, color in active_units.items():
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            symbol_rect = QRectF(
                x + padding,
                current_y + (item_height - symbol_size) / 2,
                symbol_size,
                symbol_size,
            )
            painter.drawRect(symbol_rect)

            painter.setPen(QColor(0, 0, 0))
            text_rect = QRectF(x + padding * 2 + symbol_size, current_y, max_width, item_height)
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, name)
            current_y += item_height

        painter.restore()
