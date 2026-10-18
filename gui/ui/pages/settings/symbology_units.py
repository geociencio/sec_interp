"""Per-unit editor section for the Symbology settings tab.

Kept separate from :mod:`symbology_tab` so that module stays within the size
gate. The mixin relies on the host widget providing ``tr``, ``changed`` and
``_collapsible_group``.
"""

from __future__ import annotations

from typing import Any

from qgis.gui import QgsCollapsibleGroupBox
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import (
    QColorDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from sec_interp.gui.preview_side_panel import UnitStyleEditor


class UnitsEditorMixin:
    """Build and manage the editable color/hide/rename/reorder unit rows."""

    def _build_units_group(self) -> QgsCollapsibleGroupBox:
        """Build the per-unit editor (color/hide/rename/reorder)."""
        group = self._collapsible_group(self.tr("Units"))
        layout = QVBoxLayout(group)
        layout.addWidget(
            QLabel(self.tr("<i>Hide, recolor, rename or reorder the geology/drillhole units.</i>"))
        )

        self.units_scroll = QScrollArea()
        self.units_scroll.setWidgetResizable(True)
        # Bound the height so a long unit list scrolls instead of forcing the
        # whole dialog to grow.
        self.units_scroll.setMinimumHeight(240)
        self.units_scroll.setMaximumHeight(340)
        self.units_container = QWidget()
        self.units_layout = QVBoxLayout(self.units_container)
        self.units_layout.setContentsMargins(0, 0, 0, 0)
        self.units_layout.setSpacing(1)
        self.units_scroll.setWidget(self.units_container)
        layout.addWidget(self.units_scroll)

        btn_layout = QHBoxLayout()
        self.btn_reset_units = QPushButton(self.tr("Reset unit styles"))
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_reset_units)
        layout.addLayout(btn_layout)
        return group

    def set_unit_manager(self, manager: Any) -> None:
        """Inject the ColorManager that backs the per-unit editor."""
        self._unit_manager = manager
        self.refresh_units(force=True)

    def refresh_units(self, force: bool = False) -> None:
        """Rebuild the unit rows when the underlying units change."""
        manager = self._unit_manager
        if manager is None:
            return
        entries = [
            (name, manager.label(name), manager.get_color(name).name(), manager.is_hidden(name))
            for name in manager.ordered_units()
        ]
        if not force and entries == self._unit_signature:
            return
        self._unit_signature = entries
        self._rebuild_unit_rows(manager, entries)

    def _rebuild_unit_rows(self, manager: Any, entries: list[tuple]) -> None:
        """Recreate the editable rows for the current units."""
        for row in self._unit_rows:
            self.units_layout.removeWidget(row)
            row.deleteLater()
        self._unit_rows = []

        for name, label, color_hex, hidden in entries:
            row = UnitStyleEditor(
                name,
                QColor(color_hex),
                hidden=hidden,
                label=label,
                with_rename=True,
                with_reorder=True,
            )
            row.visibility_changed.connect(self._on_unit_visibility)
            row.color_requested.connect(self._on_unit_color)
            row.label_changed.connect(self._on_unit_label)
            row.move_requested.connect(self._on_unit_move)
            self.units_layout.insertWidget(len(self._unit_rows), row)
            self._unit_rows.append(row)

    def _on_unit_visibility(self, name: str, visible: bool) -> None:
        """Hide/show a unit and refresh the preview."""
        self._unit_manager.set_hidden(name, not visible)
        self.changed.emit()

    def _on_unit_color(self, name: str) -> None:
        """Pick a new color for a unit and refresh the preview."""
        current = self._unit_manager.get_color(name)
        color = QColorDialog.getColor(current, self, self.tr("Select unit color"))
        if color is not None and color.isValid():
            self._unit_manager.set_color(name, color)
            self.refresh_units(force=True)
            self.changed.emit()

    def _on_unit_label(self, name: str, text: str) -> None:
        """Rename a unit and refresh the preview/legend."""
        self._unit_manager.set_label(name, text)
        self.changed.emit()

    def _on_unit_move(self, name: str, delta: int) -> None:
        """Reorder a unit and refresh the preview/legend."""
        self._unit_manager.move_unit(name, delta)
        self.refresh_units(force=True)
        self.changed.emit()

    def connect_unit_signals(self) -> None:
        """Connect the per-unit reset button."""
        self.btn_reset_units.clicked.connect(self.reset_units)

    def reset_units(self) -> None:
        """Clear all per-unit customization."""
        manager = self._unit_manager
        if manager is None:
            return
        for name in list(manager.known_units()):
            manager.set_hidden(name, False)
            manager.set_label(name, "")
        manager.set_order([])
        self.refresh_units(force=True)
        self.changed.emit()
