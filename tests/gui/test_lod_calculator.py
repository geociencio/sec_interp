"""Tests for LODCalculator."""

import unittest
from unittest.mock import MagicMock

from sec_interp.tests.base_test import BaseTestCase
from sec_interp.gui.lod_calculator import LODCalculator


class TestLODCalculator(BaseTestCase):
    """Test suite for LODCalculator."""

    def setUp(self):
        super().setUp()
        self.mock_canvas = MagicMock()
        self.calculator = LODCalculator(self.mock_canvas)

    def test_calculate_max_points_low_res(self):
        """Test low resolution LOD (wide view)."""
        mock_extent = MagicMock()
        mock_extent.width.return_value = 3000
        mock_extent.height.return_value = 3000
        self.mock_canvas.extent.return_value = mock_extent

        # diag = 6000 > 5000
        self.assertEqual(self.calculator.calculate_max_points(), 500)

    def test_calculate_max_points_high_res(self):
        """Test high resolution LOD (close-up)."""
        mock_extent = MagicMock()
        mock_extent.width.return_value = 100
        mock_extent.height.return_value = 100
        self.mock_canvas.extent.return_value = mock_extent

        # diag = 200 < 500
        self.assertEqual(self.calculator.calculate_max_points(), 2000)

    def test_calculate_max_points_default(self):
        """Test default resolution LOD."""
        mock_extent = MagicMock()
        mock_extent.width.return_value = 1000
        mock_extent.height.return_value = 1000
        self.mock_canvas.extent.return_value = mock_extent

        # diag = 2000
        self.assertEqual(self.calculator.calculate_max_points(), 1000)

    def test_calculate_max_points_no_canvas(self):
        """Test fallback when no canvas is present."""
        calc = LODCalculator(None)
        self.assertEqual(calc.calculate_max_points(), 1000)


if __name__ == "__main__":
    unittest.main()
