"""Tests for the preview side panel (legend + interpretations)."""

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from qgis.PyQt.QtWidgets import QApplication

from sec_interp.gui.preview_side_panel import PreviewSidePanel
from tests.base_test import BaseTestCase


def _renderer():
    return SimpleNamespace(
        has_topography=True,
        has_structures=True,
        has_drillholes=True,
        legend_units=lambda: [
            ("UnitA", "Unit A", MagicMock(), False, "geology"),
            ("UnitB", "Unit B", MagicMock(), True, "drillholes"),
        ],
    )


class TestPreviewSidePanel(BaseTestCase):
    """Legend rows and interpretations list rendering."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure a QApplication exists for widget construction."""
        super().setUpClass()
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        super().setUp()
        self.panel = PreviewSidePanel()

    def test_update_legend_populates_rows(self) -> None:
        """Topography, structures and units become rows (units interactive)."""
        self.panel.update_legend(_renderer(), visible=True)

        names = [
            row.unit_name
            for row in self.panel._legend_rows
            if getattr(row, "unit_name", None)
        ]
        self.assertEqual(
            names, ["Topography", "Structures", "Drillhole traces", "UnitA", "UnitB"]
        )
        unit_rows = [r for r in self.panel._legend_rows if getattr(r, "check", None) is not None]
        self.assertEqual([r.unit_name for r in unit_rows], ["UnitA", "UnitB"])
        self.assertTrue(unit_rows[0].check.isChecked())  # UnitA visible
        self.assertFalse(unit_rows[1].check.isChecked())  # UnitB hidden

    def test_update_legend_hidden_clears_and_hides(self) -> None:
        """Hiding the legend clears the rows and hides the group."""
        with patch.object(self.panel.legend_group, "setVisible") as set_visible:
            self.panel.update_legend(_renderer(), visible=False)

        self.assertEqual(self.panel._legend_rows, [])
        set_visible.assert_called_with(False)

    def test_rerender_destroys_previous_rows(self) -> None:
        """Re-rendering replaces rows and destroys the old ones (no orphans)."""
        self.panel.update_legend(_renderer(), visible=True)
        first_rows = list(self.panel._legend_rows)

        self.panel.update_legend(_renderer(), visible=True)

        self.assertEqual(len(self.panel._legend_rows), 7)
        self.assertTrue(all(getattr(row, "_deleted", False) for row in first_rows))

    def test_visibility_toggle_emits(self) -> None:
        """Toggling a unit row forwards the visibility change."""
        handler = MagicMock()
        self.panel.unit_visibility_changed.connect(handler)
        self.panel.update_legend(_renderer(), visible=True)
        row = next(
            r for r in self.panel._legend_rows if getattr(r, "unit_name", None) == "UnitA"
        )

        row.check.setChecked(False)

        handler.assert_called_with("UnitA", False)

    def test_color_request_emits(self) -> None:
        """Clicking a unit color button forwards the request."""
        handler = MagicMock()
        self.panel.unit_color_requested.connect(handler)
        self.panel.update_legend(_renderer(), visible=True)
        row = next(
            r for r in self.panel._legend_rows if getattr(r, "unit_name", None) == "UnitA"
        )

        row.color_requested.emit("UnitA")

        handler.assert_called_with("UnitA")

    def test_unit_editor_rename_emits(self) -> None:
        """Editing the name emits label_changed with the unit identity."""
        from sec_interp.gui.preview_side_panel import UnitStyleEditor

        row = UnitStyleEditor("A", MagicMock(), with_rename=True, with_reorder=True)
        handler = MagicMock()
        row.label_changed.connect(handler)

        row.name_edit.setText("Alias")
        row.name_edit.editingFinished.emit()

        handler.assert_called_with("A", "Alias")

    def test_interpretations_added_to_legend(self) -> None:
        """Interpretations appear as a section inside the legend."""
        self.panel.update_legend(_renderer(), visible=True)
        self.panel.update_interpretations(
            [SimpleNamespace(name="chito", color="#ff0000", type="lithology")]
        )

        unit_names = [getattr(row, "unit_name", None) for row in self.panel._legend_rows]
        headers = [row.text() for row in self.panel._legend_rows if hasattr(row, "text")]
        self.assertIn("chito", unit_names)
        self.assertIn("Interpretations", headers)

    def test_interpretations_empty_not_shown(self) -> None:
        """No Interpretations section when there are none."""
        self.panel.update_legend(_renderer(), visible=True)
        self.panel.update_interpretations([])

        headers = [row.text() for row in self.panel._legend_rows if hasattr(row, "text")]
        self.assertNotIn("Interpretations", headers)
