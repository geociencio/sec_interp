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
        legend_units=lambda: [
            ("UnitA", MagicMock(), False),
            ("UnitB", MagicMock(), True),
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

        names = [row.unit_name for row in self.panel._legend_rows]
        self.assertEqual(names, ["Topography", "Structures", "UnitA", "UnitB"])
        unit_rows = [r for r in self.panel._legend_rows if r.check is not None]
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

        self.assertEqual(len(self.panel._legend_rows), 4)
        self.assertTrue(all(getattr(row, "_deleted", False) for row in first_rows))

    def test_visibility_toggle_emits(self) -> None:
        """Toggling a unit row forwards the visibility change."""
        handler = MagicMock()
        self.panel.unit_visibility_changed.connect(handler)
        self.panel.update_legend(_renderer(), visible=True)
        row = next(r for r in self.panel._legend_rows if r.unit_name == "UnitA")

        row.check.setChecked(False)

        handler.assert_called_with("UnitA", False)

    def test_color_request_emits(self) -> None:
        """Clicking a unit color button forwards the request."""
        handler = MagicMock()
        self.panel.unit_color_requested.connect(handler)
        self.panel.update_legend(_renderer(), visible=True)
        row = next(r for r in self.panel._legend_rows if r.unit_name == "UnitA")

        row.color_requested.emit("UnitA")

        handler.assert_called_with("UnitA")

    def test_update_interpretations(self) -> None:
        """Interpretation polygons become labelled rows."""
        items = [
            SimpleNamespace(name="chito", color="#ff0000", type="lithology"),
            SimpleNamespace(name="angie", color="#00ff00", type="fault"),
        ]

        self.panel.update_interpretations(items)

        self.assertEqual(self.panel.interp_list.count(), 2)
        self.assertEqual(self.panel.interp_list.item(0).text(), "chito")

    def test_update_interpretations_empty(self) -> None:
        """An empty list leaves the interpretations list empty."""
        self.panel.update_interpretations([])

        self.assertEqual(self.panel.interp_list.count(), 0)
