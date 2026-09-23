"""Side panel shown beside the preview canvas (legend + interpretations)."""

from __future__ import annotations

from typing import Any

from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from qgis.PyQt.QtWidgets import (
    QGroupBox,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

_ICON_SIZE = 12


class PreviewSidePanel(QWidget):
    """Legend and interpretations panel docked next to the preview canvas."""

    unit_visibility_changed = pyqtSignal(str, bool)
    unit_color_changed = pyqtSignal(str, QColor)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the side panel.

        Args:
            parent: Optional parent widget.

        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Build the legend and interpretations sections."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        self.legend_group = QGroupBox(self.tr("Legend"))
        legend_layout = QVBoxLayout(self.legend_group)
        self.legend_list = QListWidget()
        self.legend_list.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.legend_list.setWordWrap(False)
        self.legend_list.setUniformItemSizes(True)
        self.legend_list.setToolTip(self.tr("Legend of the current preview"))
        legend_layout.addWidget(self.legend_list)
        layout.addWidget(self.legend_group)

        self.interp_group = QGroupBox(self.tr("Interpretations"))
        interp_layout = QVBoxLayout(self.interp_group)
        self.interp_list = QListWidget()
        self.interp_list.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.interp_list.setWordWrap(False)
        self.interp_list.setUniformItemSizes(True)
        self.interp_list.setToolTip(self.tr("Interpretation polygons drawn on the section"))
        interp_layout.addWidget(self.interp_list)
        layout.addWidget(self.interp_group)

        layout.addStretch(1)

    # --- Legend ---

    def update_legend(self, renderer: Any, visible: bool = True) -> None:
        """Refresh the legend list from a preview renderer."""
        self.set_legend_visible(visible)
        self.legend_list.clear()
        if not visible or renderer is None:
            return

        if getattr(renderer, "has_topography", False):
            self._add_legend_item(self.tr("Topography"), self._line_icon(QColor(0, 102, 204)))
        if getattr(renderer, "has_structures", False):
            self._add_legend_item(self.tr("Structures"), self._line_icon(QColor(204, 0, 0)))

        units = getattr(renderer, "active_units", None) or {}
        for name in sorted(units):
            color = units[name]
            self._add_legend_item(str(name), self._color_icon(color))

    def set_legend_visible(self, visible: bool) -> None:
        """Show or hide the legend section."""
        self.legend_group.setVisible(bool(visible))

    def _add_legend_item(self, name: str, icon: QIcon) -> None:
        """Add a labeled, icon-decorated item to the legend list."""
        item = QListWidgetItem(name)
        item.setIcon(icon)
        item.setToolTip(name)
        self.legend_list.addItem(item)

    # --- Interpretations ---

    def update_interpretations(self, interpretations: list | None) -> None:
        """Refresh the interpretations list (read-only)."""
        self.interp_list.clear()
        for interp in interpretations or []:
            name = getattr(interp, "name", "") or getattr(interp, "type", "")
            label = str(name) if name else self.tr("(unnamed)")
            color = QColor(str(getattr(interp, "color", "") or "#FF0000"))
            item = QListWidgetItem(label)
            item.setIcon(self._color_icon(color))
            item.setToolTip(label)
            self.interp_list.addItem(item)

    # --- Icon helpers ---

    @staticmethod
    def _color_icon(color: QColor) -> QIcon:
        """Return a small filled square icon for a geological unit color."""
        pixmap = QPixmap(_ICON_SIZE, _ICON_SIZE)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawRect(1, 1, _ICON_SIZE - 2, _ICON_SIZE - 2)
        painter.end()
        return QIcon(pixmap)

    @staticmethod
    def _line_icon(color: QColor) -> QIcon:
        """Return a small horizontal-line icon."""
        pixmap = QPixmap(_ICON_SIZE, _ICON_SIZE)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setPen(QPen(color, 2))
        painter.drawLine(0, _ICON_SIZE // 2, _ICON_SIZE, _ICON_SIZE // 2)
        painter.end()
        return QIcon(pixmap)
