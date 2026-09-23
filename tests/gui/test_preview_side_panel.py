"""Tests for the preview side panel (legend + interpretations)."""

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from qgis.PyQt.QtWidgets import QApplication

from sec_interp.gui.preview_side_panel import PreviewSidePanel
from tests.base_test import BaseTestCase


class TestPreviewSidePanel(BaseTestCase):
    """Legend and interpretations list rendering."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure a QApplication exists for widget construction."""
        super().setUpClass()
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        super().setUp()
        self.panel = PreviewSidePanel()

    def _renderer(self):
        renderer = MagicMock()
        renderer.has_topography = True
        renderer.has_structures = True
        renderer.active_units = {"UnitA": MagicMock(), "UnitB": MagicMock()}
        return renderer

    def test_update_legend_populates_items(self) -> None:
        """Topography, structures and units become legend rows."""
        self.panel.update_legend(self._renderer(), visible=True)

        self.assertEqual(self.panel.legend_list.count(), 4)
        texts = [self.panel.legend_list.item(i).text() for i in range(4)]
        self.assertIn("Topography", texts)
        self.assertIn("Structures", texts)
        self.assertIn("UnitA", texts)
        self.assertIn("UnitB", texts)

    def test_update_legend_hidden_clears_and_hides(self) -> None:
        """Hiding the legend clears the list and hides the group."""
        with patch.object(self.panel.legend_group, "setVisible") as set_visible:
            self.panel.update_legend(self._renderer(), visible=False)

        self.assertEqual(self.panel.legend_list.count(), 0)
        set_visible.assert_called_with(False)

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
