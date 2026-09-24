"""Tests for PreviewLegendRenderer."""

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from qgis.PyQt.QtCore import QRectF
from qgis.PyQt.QtGui import QColor

from sec_interp.gui.preview_legend_renderer import PreviewLegendRenderer
from tests.base_test import BaseTestCase


class TestPreviewLegendRenderer(BaseTestCase):
    """Tests for the PreviewLegendRenderer class."""

    def setUp(self):
        super().setUp()
        self.painter = MagicMock()
        # Mock fontMetrics for size calculation
        self.fm = MagicMock()
        self.fm.boundingRect.return_value = QRectF(0, 0, 50, 10)
        self.painter.fontMetrics.return_value = self.fm

    def test_draw_legend_empty(self):
        """Test drawing an empty legend (should return early)."""
        rect = QRectF(0, 0, 100, 100)
        PreviewLegendRenderer.draw_legend(self.painter, rect, {})
        self.painter.save.assert_not_called()

    def test_draw_legend_full(self):
        """Test drawing a full legend with all item types."""
        rect = QRectF(0, 0, 500, 500)
        active_units = {"Unit A": QColor(255, 0, 0), "Unit B": QColor(0, 255, 0)}

        PreviewLegendRenderer.draw_legend(
            self.painter, rect, active_units, has_topography=True, has_structures=True
        )

        self.painter.save.assert_called_once()
        self.painter.restore.assert_called_once()
        # Verify background was drawn
        self.painter.drawRect.assert_called()
        # Verify text was drawn (Topography, Structures, Unit A, Unit B)
        self.assertEqual(self.painter.drawText.call_count, 4)

    def test_draw_legend_with_drillholes(self):
        """Drillholes add a single labeled line item."""
        rect = QRectF(0, 0, 500, 500)

        PreviewLegendRenderer.draw_legend(self.painter, rect, {}, has_drillholes=True)

        self.painter.save.assert_called_once()
        self.assertEqual(self.painter.drawText.call_count, 1)

    def test_draw_legend_with_interpretations(self):
        """Interpretations add a section header plus one item each."""
        rect = QRectF(0, 0, 500, 500)
        interpretations = [
            SimpleNamespace(name="chito", color="#ff0000", type="lithology"),
            SimpleNamespace(name="angie", color="#00ff00", type="fault"),
        ]

        PreviewLegendRenderer.draw_legend(
            self.painter, rect, {}, interpretations=interpretations
        )

        self.painter.save.assert_called_once()
        # Header + 2 items
        self.assertEqual(self.painter.drawText.call_count, 3)

    def test_interpretations_header_follows_drill_items(self):
        """The Interpretations header must be below the last drill item."""
        rect = QRectF(0, 0, 500, 500)
        drill = {"D1": QColor(255, 0, 0), "D2": QColor(0, 255, 0)}
        interpretations = [SimpleNamespace(name="i1", color="#ff0000", type="lith")]

        PreviewLegendRenderer.draw_legend(
            self.painter,
            rect,
            {},
            drill_units=drill,
            interpretations=interpretations,
        )

        ys = {}
        for call in self.painter.drawText.call_args_list:
            text_rect = call.args[0]
            text = call.args[2]
            ys[text] = text_rect.y()

        self.assertGreater(ys["Interpretations"], ys["D2"])

    def test_calculate_legend_size(self):
        """Test legend size calculation."""
        config = {"padding": 5, "item_height": 10, "symbol_size": 10}
        active_units = {"A": QColor(0, 0, 0)}

        size, max_w = PreviewLegendRenderer._calculate_legend_size(
            self.painter, active_units, True, True, False, config
        )

        # 3 items (Topo, Struct, A)
        self.assertEqual(max_w, 50)  # from fm mock
        self.assertEqual(size.height(), 3 * 10 + 2 * 5)
        self.assertEqual(size.width(), 50 + 10 + 3 * 5)


if __name__ == "__main__":
    unittest.main()
