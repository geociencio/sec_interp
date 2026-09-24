"""Side panel shown beside the preview canvas (legend with layers and units)."""

from __future__ import annotations

from typing import Any

from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

_SWATCH_STYLE = "border: 1px solid #888;"


def _swatch_stylesheet(color: QColor) -> str:
    """Return a stylesheet painting a small color swatch."""
    return f"background-color: {color.name()}; {_SWATCH_STYLE}"


class UnitStyleEditor(QWidget):
    """A row: visibility, color and (optionally) rename/reorder controls."""

    visibility_changed = pyqtSignal(str, bool)
    color_requested = pyqtSignal(str)
    label_changed = pyqtSignal(str, str)
    move_requested = pyqtSignal(str, int)

    def __init__(
        self,
        name: str,
        color: QColor,
        hidden: bool = False,
        label: str | None = None,
        interactive: bool = True,
        with_visibility: bool = True,
        with_color: bool = True,
        with_rename: bool = False,
        with_reorder: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the row.

        Args:
            name: Identity (unit name or entry key).
            color: Swatch color.
            hidden: Whether the entry is currently hidden.
            label: Display label (alias) or the name.
            interactive: Whether to show any control.
            with_visibility: Show the visibility checkbox (interactive).
            with_color: Show the color button (interactive).
            with_rename: Whether to show an editable name.
            with_reorder: Whether to show up/down buttons.
            parent: Optional parent widget.

        """
        super().__init__(parent)
        self.unit_name = name
        self.check: QCheckBox | None = None
        self.color_button: QWidget | None = None
        self.name_edit: QLineEdit | None = None
        display = label or name

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 1, 2, 1)
        layout.setSpacing(4)

        if interactive and with_visibility:
            self.check = QCheckBox()
            self.check.setChecked(not hidden)
            self.check.setToolTip(self.tr("Show/hide this layer"))
            self.check.toggled.connect(
                lambda checked: self.visibility_changed.emit(self.unit_name, checked)
            )
            layout.addWidget(self.check)

        if interactive and with_color:
            button = QToolButton()
            button.setFixedSize(14, 14)
            button.setStyleSheet(_swatch_stylesheet(color))
            button.setToolTip(self.tr("Change this color"))
            button.clicked.connect(lambda: self.color_requested.emit(self.unit_name))
            self.color_button = button
            layout.addWidget(button)
        elif not interactive:
            swatch = QLabel()
            swatch.setFixedSize(12, 12)
            swatch.setStyleSheet(_swatch_stylesheet(color))
            layout.addWidget(swatch)

        if with_reorder:
            layout.addWidget(self._reorder_button("▲", -1))
            layout.addWidget(self._reorder_button("▼", +1))

        if with_rename:
            self.name_edit = QLineEdit(display)
            self.name_edit.setToolTip(self.tr("Rename this unit"))
            self.name_edit.editingFinished.connect(
                lambda: self.label_changed.emit(self.unit_name, self.name_edit.text())
            )
            layout.addWidget(self.name_edit, stretch=1)
        else:
            label_widget = QLabel(display)
            label_widget.setToolTip(display)
            layout.addWidget(label_widget, stretch=1)

    def _reorder_button(self, text: str, delta: int) -> QToolButton:
        """Create a reorder button emitting ``move_requested``."""
        button = QToolButton()
        button.setText(text)
        button.setFixedWidth(18)
        button.clicked.connect(lambda: self.move_requested.emit(self.unit_name, delta))
        return button


class PreviewSidePanel(QWidget):
    """Legend panel (layers, units and interpretations) beside the canvas."""

    unit_visibility_changed = pyqtSignal(str, bool)
    unit_color_requested = pyqtSignal(str)
    layer_visibility_changed = pyqtSignal(str, bool)
    layer_color_requested = pyqtSignal(str)
    interpretation_visibility_changed = pyqtSignal(str, bool)
    interpretation_color_requested = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the side panel.

        Args:
            parent: Optional parent widget.

        """
        super().__init__(parent)
        self._legend_rows: list[QWidget] = []
        self._interpretations: list = []
        self._renderer: Any = None
        self._legend_style: dict = {}
        self._legend_visible = True
        self._layer_visibility: dict[str, bool] = {}
        self._hidden_interp_ids: set[str] = set()
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Build the legend section."""
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
        layout.addWidget(self.legend_group)

        self.legend_layout.addStretch(1)

    # --- Legend ---

    def update_legend(
        self,
        renderer: Any,
        visible: bool = True,
        style: dict | None = None,
        layer_visibility: dict[str, bool] | None = None,
        hidden_interp_ids: set[str] | None = None,
    ) -> None:
        """Rebuild all legend rows from a preview renderer and the active styles."""
        self._renderer = renderer
        self._legend_visible = visible
        self._legend_style = style or {}
        if layer_visibility is not None:
            self._layer_visibility = dict(layer_visibility)
        if hidden_interp_ids is not None:
            self._hidden_interp_ids = set(hidden_interp_ids)
        self.set_legend_visible(visible)
        self._rebuild_rows()

    def update_interpretations(self, interpretations: list | None) -> None:
        """Update the interpretations shown inside the legend."""
        self._interpretations = list(interpretations or [])
        if self._renderer is not None:
            self._rebuild_rows()

    def _rebuild_rows(self) -> None:
        """Rebuild the legend rows from the stored renderer/style/interpretations."""
        self._clear_legend_rows()
        renderer = self._renderer
        if not self._legend_visible or renderer is None:
            return
        style = self._legend_style

        if getattr(renderer, "has_topography", False):
            self._add_row(
                "topography",
                self._topo_color(style),
                hidden=not self._layer_visibility.get("topography", True),
                label=self.tr("Topography"),
                kind="layer",
            )
        if getattr(renderer, "has_structures", False):
            self._add_row(
                "structures",
                QColor(str(style.get("struct_color") or "#cc0000")),
                hidden=not self._layer_visibility.get("structures", True),
                label=self.tr("Structures"),
                kind="layer",
            )
        if getattr(renderer, "has_drillholes", False):
            self._add_row(
                "drillholes",
                QColor(str(style.get("drill_trace_color") or "#323232")),
                hidden=not self._layer_visibility.get("drillholes", True),
                label=self.tr("Drillhole traces"),
                kind="layer",
            )

        units = self._unit_entries(renderer)
        self._add_unit_group(self.tr("Geology"), [u for u in units if u[4] == "geology"])
        self._add_unit_group(
            self.tr("Drillhole lithologies"), [u for u in units if u[4] == "drillholes"]
        )
        self._add_interpretation_group()

    @staticmethod
    def _topo_color(style: dict) -> QColor:
        """Return the color representing the topography in the legend."""
        if style.get("color_mode") == "single":
            return QColor(str(style.get("single_color_hex") or "#1f77b4"))
        return QColor("#0066cc")

    def _add_unit_group(self, title: str, units: list[tuple]) -> None:
        """Add a section label and its unit rows."""
        if not units:
            return
        self._add_section_label(title)
        for name, label, color, hidden, _source in units:
            self._add_row(name, color, hidden=hidden, interactive=True, label=label)

    def _add_interpretation_group(self) -> None:
        """Add the interpretations as an editable legend section."""
        if not self._interpretations:
            return
        self._add_section_label(self.tr("Interpretations"))
        for interp in self._interpretations:
            iid = str(getattr(interp, "id", "") or getattr(interp, "name", ""))
            name = getattr(interp, "name", "") or getattr(interp, "type", "")
            label = str(name) if name else self.tr("(unnamed)")
            color = QColor(str(getattr(interp, "color", "") or "#FF0000"))
            self._add_row(
                iid,
                color,
                hidden=iid in self._hidden_interp_ids,
                label=label,
                kind="interpretation",
            )

    def _unit_entries(self, renderer: Any) -> list[tuple[str, str, Any, bool, str]]:
        """Return unit entries (name, label, color, hidden, source)."""
        if hasattr(renderer, "legend_units"):
            return list(renderer.legend_units())
        units = getattr(renderer, "active_units", None) or {}
        return [
            (str(name), str(name), color, False, "geology") for name, color in sorted(units.items())
        ]

    def _add_row(
        self,
        name: str,
        color: QColor,
        hidden: bool = False,
        interactive: bool = True,
        label: str | None = None,
        kind: str = "unit",
        with_visibility: bool = True,
        with_color: bool = True,
    ) -> None:
        """Create and wire a legend row widget."""
        row = UnitStyleEditor(
            name,
            color,
            hidden=hidden,
            label=label,
            interactive=interactive,
            with_visibility=with_visibility,
            with_color=with_color,
        )
        if kind == "layer":
            row.visibility_changed.connect(self.layer_visibility_changed.emit)
            row.color_requested.connect(self.layer_color_requested.emit)
        elif kind == "interpretation":
            row.visibility_changed.connect(self.interpretation_visibility_changed.emit)
            row.color_requested.connect(self.interpretation_color_requested.emit)
        elif interactive:
            row.visibility_changed.connect(self.unit_visibility_changed.emit)
            row.color_requested.connect(self.unit_color_requested.emit)
        self.legend_layout.insertWidget(len(self._legend_rows), row)
        self._legend_rows.append(row)

    def _add_section_label(self, text: str) -> None:
        """Add a bold section header to the legend."""
        label = QLabel()
        label.setText(text)
        label.setStyleSheet("font-weight: bold; padding-top: 4px;")
        self.legend_layout.insertWidget(len(self._legend_rows), label)
        self._legend_rows.append(label)

    def _clear_legend_rows(self) -> None:
        """Remove and destroy all legend rows.

        ``deleteLater`` is required: merely reparenting to ``None`` turns a
        previously visible widget into a top-level window (one orphan window
        per row on every re-render).
        """
        for row in self._legend_rows:
            self.legend_layout.removeWidget(row)
            row.deleteLater()
        self._legend_rows = []

    def set_legend_visible(self, visible: bool) -> None:
        """Show or hide the legend section."""
        self.legend_group.setVisible(bool(visible))
