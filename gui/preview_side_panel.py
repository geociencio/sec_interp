"""Side panel shown beside the preview canvas (legend + interpretations)."""

from __future__ import annotations

from typing import Any

from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QIcon, QPainter, QPixmap
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

_ICON_SIZE = 12
_SWATCH_STYLE = "border: 1px solid #888;"


def _swatch_stylesheet(color: QColor) -> str:
    """Return a stylesheet painting a small color swatch."""
    return f"background-color: {color.name()}; {_SWATCH_STYLE}"


class LegendRow(QWidget):
    """A single legend row (optional visibility toggle + color swatch)."""

    visibility_changed = pyqtSignal(str, bool)
    color_requested = pyqtSignal(str)

    def __init__(
        self,
        name: str,
        color: QColor,
        hidden: bool = False,
        interactive: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the legend row.

        Args:
            name: Unit label.
            color: Swatch color.
            hidden: Whether the unit is currently hidden.
            interactive: Whether to show the visibility/color controls.
            parent: Optional parent widget.

        """
        super().__init__(parent)
        self.unit_name = name
        self.check: QCheckBox | None = None
        self.color_button: QWidget | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 1, 2, 1)
        layout.setSpacing(4)

        if interactive:
            self.check = QCheckBox()
            self.check.setChecked(not hidden)
            self.check.setToolTip(self.tr("Show/hide this unit"))
            self.check.toggled.connect(
                lambda checked: self.visibility_changed.emit(self.unit_name, checked)
            )
            layout.addWidget(self.check)

            button = QToolButton()
            button.setFixedSize(14, 14)
            button.setStyleSheet(_swatch_stylesheet(color))
            button.setToolTip(self.tr("Change this unit color"))
            button.clicked.connect(lambda: self.color_requested.emit(self.unit_name))
            self.color_button = button
            layout.addWidget(button)
        else:
            swatch = QLabel()
            swatch.setFixedSize(12, 12)
            swatch.setStyleSheet(_swatch_stylesheet(color))
            layout.addWidget(swatch)

        label = QLabel(str(name))
        label.setToolTip(str(name))
        layout.addWidget(label, stretch=1)


class PreviewSidePanel(QWidget):
    """Legend and interpretations panel docked next to the preview canvas."""

    unit_visibility_changed = pyqtSignal(str, bool)
    unit_color_requested = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the side panel.

        Args:
            parent: Optional parent widget.

        """
        super().__init__(parent)
        self._legend_rows: list[LegendRow] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Build the legend and interpretations sections."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        self.legend_group = QGroupBox(self.tr("Legend"))
        legend_layout = QVBoxLayout(self.legend_group)
        self.legend_scroll = QScrollArea()
        self.legend_scroll.setWidgetResizable(True)
        self.legend_container = QWidget()
        self.legend_layout = QVBoxLayout(self.legend_container)
        self.legend_layout.setContentsMargins(0, 0, 0, 0)
        self.legend_layout.setSpacing(1)
        self.legend_scroll.setWidget(self.legend_container)
        legend_layout.addWidget(self.legend_scroll)
        layout.addWidget(self.legend_group, stretch=2)

        self.interp_group = QGroupBox(self.tr("Interpretations"))
        interp_layout = QVBoxLayout(self.interp_group)
        self.interp_list = QListWidget()
        self.interp_list.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.interp_list.setWordWrap(False)
        self.interp_list.setUniformItemSizes(True)
        self.interp_list.setToolTip(self.tr("Interpretation polygons drawn on the section"))
        interp_layout.addWidget(self.interp_list)
        layout.addWidget(self.interp_group, stretch=1)

        self.legend_layout.addStretch(1)

    # --- Legend ---

    def update_legend(self, renderer: Any, visible: bool = True) -> None:
        """Rebuild the legend rows from a preview renderer."""
        self.set_legend_visible(visible)
        self._clear_legend_rows()
        if not visible or renderer is None:
            return

        if getattr(renderer, "has_topography", False):
            self._add_row(self.tr("Topography"), QColor(0, 102, 204), interactive=False)
        if getattr(renderer, "has_structures", False):
            self._add_row(self.tr("Structures"), QColor(204, 0, 0), interactive=False)

        for name, color, hidden in self._unit_entries(renderer):
            self._add_row(name, color, hidden=hidden, interactive=True)

    def _unit_entries(self, renderer: Any) -> list[tuple[str, QColor, bool]]:
        """Return unit entries from the renderer (known units + hidden flag)."""
        if hasattr(renderer, "legend_units"):
            return list(renderer.legend_units())
        units = getattr(renderer, "active_units", None) or {}
        return [(str(name), color, False) for name, color in sorted(units.items())]

    def _add_row(
        self, name: str, color: QColor, hidden: bool = False, interactive: bool = True
    ) -> None:
        """Create and wire a legend row widget."""
        row = LegendRow(name, color, hidden=hidden, interactive=interactive)
        if interactive:
            row.visibility_changed.connect(self.unit_visibility_changed.emit)
            row.color_requested.connect(self.unit_color_requested.emit)
        self.legend_layout.insertWidget(len(self._legend_rows), row)
        self._legend_rows.append(row)

    def _clear_legend_rows(self) -> None:
        """Remove all legend rows."""
        for row in self._legend_rows:
            self.legend_layout.removeWidget(row)
            row.setParent(None)
        self._legend_rows = []

    def set_legend_visible(self, visible: bool) -> None:
        """Show or hide the legend section."""
        self.legend_group.setVisible(bool(visible))

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
