"""Tests for PreviewLegendRenderer."""

import unittest
from unittest.mock import MagicMock
from tests.base_test import BaseTestCase
from qgis.PyQt.QtCore import QRectF, Qt
from qgis.PyQt.QtGui import QColor, QFont
from sec_interp.gui.preview_legend_renderer import PreviewLegendRenderer


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

    def test_calculate_legend_size(self):
        """Test legend size calculation."""
        config = {"padding": 5, "item_height": 10, "symbol_size": 10}
        active_units = {"A": QColor(0, 0, 0)}

        size, max_w = PreviewLegendRenderer._calculate_legend_size(
            self.painter, active_units, True, True, config
        )

        # 3 items (Topo, Struct, A)
        self.assertEqual(max_w, 50)  # from fm mock
        self.assertEqual(size.height(), 3 * 10 + 2 * 5)
        self.assertEqual(size.width(), 50 + 10 + 3 * 5)


if __name__ == "__main__":
    unittest.main()
