"""Legend rendering logic for SecInterp preview.

Handles the drawing of the legend on a QPainter, including topography,
structures, and geological units.
"""

from __future__ import annotations

from typing import Any

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
        has_drillholes: bool = False,
        labels: dict[str, str] | None = None,
        drill_units: dict[str, QColor] | None = None,
    ) -> None:
        """Draw legend on the given painter within the rect.

        ``active_units`` are the geology units; ``drill_units`` (when given) are
        the drillhole lithologies, drawn under their own header.
        """
        if (
            not active_units
            and not drill_units
            and not has_topography
            and not has_structures
            and not has_drillholes
        ):
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
            painter,
            active_units,
            has_topography,
            has_structures,
            has_drillholes,
            config,
            labels,
            drill_units,
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
                painter,
                x,
                current_y,
                QCoreApplication.translate("PreviewLegendRenderer", "Topography"),
                QColor(0, 102, 204),
                max_text_width,
                config,
            )
            current_y += config["item_height"]

        if has_structures:
            PreviewLegendRenderer._draw_line_item(
                painter,
                x,
                current_y,
                QCoreApplication.translate("PreviewLegendRenderer", "Structures"),
                QColor(204, 0, 0),
                max_text_width,
                config,
            )
            current_y += config["item_height"]

        if has_drillholes:
            PreviewLegendRenderer._draw_line_item(
                painter,
                x,
                current_y,
                QCoreApplication.translate("PreviewLegendRenderer", "Drillholes"),
                QColor(50, 50, 50),
                max_text_width,
                config,
            )
            current_y += config["item_height"]

        if drill_units:
            current_y = PreviewLegendRenderer._draw_header(
                painter,
                x,
                current_y,
                QCoreApplication.translate("PreviewLegendRenderer", "Geology"),
                config,
            )
            current_y = PreviewLegendRenderer._draw_geology_items(
                painter, x, current_y, active_units, max_text_width, config, labels
            )
            current_y = PreviewLegendRenderer._draw_header(
                painter,
                x,
                current_y,
                QCoreApplication.translate("PreviewLegendRenderer", "Drillhole lithologies"),
                config,
            )
            PreviewLegendRenderer._draw_geology_items(
                painter, x, current_y, drill_units, max_text_width, config, labels
            )
        else:
            PreviewLegendRenderer._draw_geology_items(
                painter, x, current_y, active_units, max_text_width, config, labels
            )

        painter.restore()

    @staticmethod
    def _calculate_legend_size(
        painter: QPainter,
        active_units: dict[str, QColor],
        has_topo: bool,
        has_struct: bool,
        has_drill: bool,
        config: dict[str, Any],
        labels: dict[str, str] | None = None,
        drill_units: dict[str, QColor] | None = None,
    ) -> tuple[QRectF, float]:
        """Calculate dimensions of the legend box."""
        fm = painter.fontMetrics()
        max_text_width = 0
        labels = labels or {}

        items = []
        if has_topo:
            items.append(QCoreApplication.translate("PreviewLegendRenderer", "Topography"))
        if has_struct:
            items.append(QCoreApplication.translate("PreviewLegendRenderer", "Structures"))
        if has_drill:
            items.append(QCoreApplication.translate("PreviewLegendRenderer", "Drillholes"))
        if drill_units:
            items.append(QCoreApplication.translate("PreviewLegendRenderer", "Geology"))
        items.extend(labels.get(name, name) for name in active_units)
        if drill_units:
            items.append(
                QCoreApplication.translate("PreviewLegendRenderer", "Drillhole lithologies")
            )
            items.extend(labels.get(name, name) for name in drill_units)

        for item in items:
            max_text_width = max(max_text_width, fm.boundingRect(item).width())

        width = max_text_width + config["symbol_size"] + config["padding"] * 3
        height = len(items) * config["item_height"] + config["padding"] * 2
        return QRectF(0, 0, width, height), max_text_width

    @staticmethod
    def _draw_legend_background(
        painter: QPainter, x: float, y: float, width: float, height: float
    ) -> None:
        """Draw the legend box background and border."""
        rect = QRectF(x, y, width, height)
        painter.setBrush(QColor(255, 255, 255, 200))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(rect)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QColor(100, 100, 100))
        painter.drawRect(rect)

    @staticmethod
    def _draw_line_item(
        painter: QPainter,
        x: float,
        y: float,
        label: str,
        color: QColor,
        max_width: float,
        config: dict[str, Any],
    ) -> None:
        """Draw a legend item with a line symbol."""
        p = config["padding"]
        ih = config["item_height"]
        ss = config["symbol_size"]

        painter.setPen(QPen(color, config["line_width"]))
        painter.drawLine(int(x + p), int(y + ih / 2), int(x + p + ss), int(y + ih / 2))

        painter.setPen(QColor(0, 0, 0))
        text_rect = QRectF(x + p * 2 + ss, y, max_width, ih)
        painter.drawText(
            text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, label
        )

    @staticmethod
    def _draw_header(
        painter: QPainter,
        x: float,
        y: float,
        text: str,
        config: dict[str, Any],
    ) -> float:
        """Draw a bold section header and return the next y position."""
        p = config["padding"]
        ih = config["item_height"]
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(
            QRectF(x + p, y, 1000, ih),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            text,
        )
        font.setBold(False)
        painter.setFont(font)
        return y + ih

    @staticmethod
    def _draw_geology_items(
        painter: QPainter,
        x: float,
        y: float,
        units: dict[str, QColor],
        max_width: float,
        config: dict[str, Any],
        labels: dict[str, str] | None = None,
    ) -> float:
        """Draw geological unit legend items and return the next y position."""
        p = config["padding"]
        ih = config["item_height"]
        ss = config["symbol_size"]
        labels = labels or {}

        for name, color in units.items():
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(QRectF(x + p, y + (ih - ss) / 2, ss, ss))

            painter.setPen(QColor(0, 0, 0))
            text_rect = QRectF(x + p * 2 + ss, y, max_width, ih)
            painter.drawText(
                text_rect,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                labels.get(name, name),
            )
            y += ih

        return y
