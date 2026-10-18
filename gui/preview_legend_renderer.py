"""Legend rendering logic for SecInterp preview.

Handles the drawing of the legend on a QPainter with configurable position,
font size and item limit.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from qgis.PyQt.QtCore import QCoreApplication, QRectF, Qt
from qgis.PyQt.QtGui import QColor, QFont, QPainter, QPen

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

# Row kinds
_LINE = "line"
_SWATCH = "swatch"
_HEADER = "header"

_VALID_POSITIONS = ("top-right", "top-left", "bottom-right", "bottom-left")


def _translator() -> Callable[[str], str]:
    """Return a translator bound to this renderer's i18n context."""
    return lambda text: QCoreApplication.translate("PreviewLegendRenderer", text)


def _interpretation_label(interp: Any) -> str:
    """Return the display label for an interpretation."""
    name = getattr(interp, "name", "") or getattr(interp, "type", "") or "?"
    return str(name)


def _interpretation_color(interp: Any) -> QColor:
    """Return the swatch color for an interpretation."""
    return QColor(str(getattr(interp, "color", "") or "#FF0000"))


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
        interpretations: list | None = None,
        layout: dict[str, Any] | None = None,
        layer_colors: dict[str, QColor] | None = None,
    ) -> None:
        """Build the legend rows from data and draw them."""
        rows = PreviewLegendRenderer._build_rows(
            active_units=active_units,
            has_topography=has_topography,
            has_structures=has_structures,
            has_drillholes=has_drillholes,
            labels=labels or {},
            drill_units=drill_units or {},
            interpretations=interpretations or [],
            layer_colors=layer_colors or {},
        )
        PreviewLegendRenderer.draw_rows(painter, rect, rows, layout)

    @staticmethod
    def _build_rows(
        active_units: dict[str, QColor],
        has_topography: bool,
        has_structures: bool,
        has_drillholes: bool,
        labels: dict[str, str],
        drill_units: dict[str, QColor],
        interpretations: list,
        layer_colors: dict[str, QColor],
    ) -> list[tuple[str, str, QColor | None]]:
        """Collect every legend row (layers, units and interpretations)."""
        tr = _translator()
        rows: list[tuple[str, str, QColor | None]] = []
        rows.extend(
            PreviewLegendRenderer._layer_rows(
                has_topography, has_structures, has_drillholes, layer_colors, tr
            )
        )
        rows.extend(PreviewLegendRenderer._unit_rows(active_units, drill_units, labels, tr))
        rows.extend(PreviewLegendRenderer._interpretation_rows(interpretations, tr))
        return rows

    @staticmethod
    def _layer_rows(
        has_topography: bool,
        has_structures: bool,
        has_drillholes: bool,
        layer_colors: dict[str, QColor],
        tr: Callable[[str], str],
    ) -> list[tuple[str, str, QColor | None]]:
        """Return the topography/structures/drillhole trace rows."""
        rows: list[tuple[str, str, QColor | None]] = []
        if has_topography:
            color = layer_colors.get("topography") or QColor(0, 102, 204)
            rows.append((_LINE, tr("Topography"), color))
        if has_structures:
            color = layer_colors.get("structures") or QColor(204, 0, 0)
            rows.append((_LINE, tr("Structures"), color))
        if has_drillholes:
            color = layer_colors.get("drillholes") or QColor(50, 50, 50)
            rows.append((_LINE, tr("Drillhole traces"), color))
        return rows

    @staticmethod
    def _unit_rows(
        active_units: dict[str, QColor],
        drill_units: dict[str, QColor],
        labels: dict[str, str],
        tr: Callable[[str], str],
    ) -> list[tuple[str, str, QColor | None]]:
        """Return the geology and drillhole lithology unit rows."""
        swatches = [
            (_SWATCH, labels.get(name, name), color) for name, color in active_units.items()
        ]
        if not drill_units:
            return swatches

        rows: list[tuple[str, str, QColor | None]] = [(_HEADER, tr("Geology"), None)]
        rows.extend(swatches)
        rows.append((_HEADER, tr("Drillhole lithologies"), None))
        rows.extend((_SWATCH, labels.get(name, name), color) for name, color in drill_units.items())
        return rows

    @staticmethod
    def _interpretation_rows(
        interpretations: list, tr: Any
    ) -> list[tuple[str, str, QColor | None]]:
        """Return the interpretation rows (header plus one row each)."""
        if not interpretations:
            return []
        rows: list[tuple[str, str, QColor | None]] = [(_HEADER, tr("Interpretations"), None)]
        for interp in interpretations:
            rows.append((_SWATCH, _interpretation_label(interp), _interpretation_color(interp)))
        return rows

    @staticmethod
    def draw_rows(
        painter: QPainter,
        rect: QRectF,
        rows: list[tuple[str, str, QColor | None]],
        layout: dict[str, Any] | None = None,
    ) -> None:
        """Draw legend rows within ``rect`` honoring the layout options."""
        if not rows:
            return

        layout = layout or {}
        font_size = int(layout.get("font_size") or 8)
        position = layout.get("position") or "top-right"
        if position not in _VALID_POSITIONS:
            position = "top-right"
        max_items = int(layout.get("max_items") or 0)

        config = {
            "padding": 6,
            "item_height": max(12, font_size + 6),
            "symbol_size": max(8, font_size + 2),
            "line_width": 2,
            "margin": 20,
        }

        if max_items > 0 and len(rows) > max_items:
            hidden = len(rows) - max_items
            rows = rows[:max_items]
            rows.append((_HEADER, f"+{hidden} more", None))

        painter.save()
        painter.setFont(QFont("Arial", font_size))

        legend_size, max_text_width = PreviewLegendRenderer._measure(painter, rows, config)
        x, y = PreviewLegendRenderer._position(rect, legend_size, position, config["margin"])

        PreviewLegendRenderer._draw_legend_background(
            painter, x, y, legend_size.width(), legend_size.height()
        )

        current_y = y + config["padding"]
        for kind, label, color in rows:
            current_y = PreviewLegendRenderer._draw_row(
                painter, x, current_y, kind, label, color, max_text_width, config
            )

        painter.restore()

    @staticmethod
    def _position(rect: QRectF, size: QRectF, position: str, margin: float) -> tuple[float, float]:
        """Return the top-left corner for the legend box."""
        x = rect.width() - size.width() - margin if position.endswith("right") else margin
        y = rect.height() - size.height() - margin if position.startswith("bottom") else margin
        return x, y

    @staticmethod
    def _measure(
        painter: QPainter,
        rows: list[tuple[str, str, QColor | None]],
        config: dict[str, Any],
    ) -> tuple[QRectF, float]:
        """Measure the legend box size and the widest label."""
        fm = painter.fontMetrics()
        max_text_width = 0
        for _kind, label, _color in rows:
            max_text_width = max(max_text_width, fm.boundingRect(label).width())

        width = max_text_width + config["symbol_size"] + config["padding"] * 3
        height = len(rows) * config["item_height"] + config["padding"] * 2
        return QRectF(0, 0, width, height), max_text_width

    @staticmethod
    def _draw_row(
        painter: QPainter,
        x: float,
        y: float,
        kind: str,
        label: str,
        color: QColor | None,
        max_width: float,
        config: dict[str, Any],
    ) -> float:
        """Draw a single legend row and return the next y position."""
        p = config["padding"]
        ih = config["item_height"]
        ss = config["symbol_size"]

        if kind == _HEADER:
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(
                QRectF(x + p, y, max_width + ss, ih),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                label,
            )
            font.setBold(False)
            painter.setFont(font)
            return y + ih

        if kind == _LINE and color is not None:
            painter.setPen(QPen(color, config["line_width"]))
            painter.drawLine(int(x + p), int(y + ih / 2), int(x + p + ss), int(y + ih / 2))
        elif color is not None:
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(QRectF(x + p, y + (ih - ss) / 2, ss, ss))

        painter.setPen(QColor(0, 0, 0))
        painter.drawText(
            QRectF(x + p * 2 + ss, y, max_width, ih),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            label,
        )
        return y + ih

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
