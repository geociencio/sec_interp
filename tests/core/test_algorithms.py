"""
Unit tests for core algorithms.
"""

from tests.base_test import BaseTestCase
from sec_interp.core.utils import calculate_line_azimuth


class TestAlgorithms(BaseTestCase):
    def test_calculate_line_azimuth_horizontal(self):
        """Test azimuth calculation for a horizontal line (East)."""
        azimuth = calculate_line_azimuth([(0, 0), (10, 0)])
        self.assertEqual(azimuth, 90.0)

    def test_calculate_line_azimuth_vertical(self):
        """Test azimuth calculation for a vertical line (North)."""
        azimuth = calculate_line_azimuth([(0, 0), (0, 10)])
        self.assertEqual(azimuth, 0.0)

    def test_calculate_line_azimuth_point(self):
        """Test azimuth calculation for a point (should be 0)."""
        azimuth = calculate_line_azimuth([(0, 0)])
        self.assertEqual(azimuth, 0.0)
