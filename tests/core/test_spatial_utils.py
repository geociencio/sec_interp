"""Tests for spatial utilities (pure math)."""

from tests.base_test import BaseTestCase

from sec_interp.core.utils.spatial import calculate_line_azimuth


class TestSpatialUtils(BaseTestCase):
    """Tests for spatial utility functions."""

    def test_calculate_line_azimuth_point(self):
        """Test azimuth calculation for a point (should return 0)."""
        self.assertEqual(calculate_line_azimuth([(0, 0)]), 0)

    def test_calculate_line_azimuth_line(self):
        """Test azimuth calculation for valid lines."""
        # North: (0,0) to (0,10) -> 0 degrees
        self.assertAlmostEqual(calculate_line_azimuth([(0, 0), (0, 10)]), 0)

        # East: (0,0) to (10,0) -> 90 degrees
        self.assertAlmostEqual(calculate_line_azimuth([(0, 0), (10, 0)]), 90)

        # South: (0,0) to (0,-10) -> 180 degrees
        self.assertAlmostEqual(calculate_line_azimuth([(0, 0), (0, -10)]), 180)

        # West: (0,0) to (-10,0) -> 270 degrees
        self.assertAlmostEqual(calculate_line_azimuth([(0, 0), (-10, 0)]), 270)

    def test_calculate_line_azimuth_unsupported(self):
        """Test azimuth for unsupported geometry types (empty points)."""
        self.assertEqual(calculate_line_azimuth([]), 0)

    def test_calculate_line_azimuth_short_line(self):
        """Test azimuth for line with less than 2 points."""
        self.assertEqual(calculate_line_azimuth([(1, 1)]), 0)
