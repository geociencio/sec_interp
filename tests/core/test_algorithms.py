"""
Unit tests for core algorithms.
"""

from tests.base_test import BaseTestCase
from qgis.core import QgsGeometry, QgsPointXY
from sec_interp.core.utils import calculate_line_azimuth


class TestAlgorithms(BaseTestCase):
    def test_calculate_line_azimuth_horizontal(self):
        """Test azimuth calculation for a horizontal line (East)."""
        p1 = QgsPointXY(0, 0)
        p2 = QgsPointXY(10, 0)
        geom = QgsGeometry.fromPolylineXY([p1, p2])

        azimuth = calculate_line_azimuth(geom)
        self.assertEqual(azimuth, 90.0)


    def test_calculate_line_azimuth_vertical(self):
        """Test azimuth calculation for a vertical line (North)."""
        p1 = QgsPointXY(0, 0)
        p2 = QgsPointXY(0, 10)
        geom = QgsGeometry.fromPolylineXY([p1, p2])

        azimuth = calculate_line_azimuth(geom)
        self.assertEqual(azimuth, 0.0)


    def test_calculate_line_azimuth_point(self):
        """Test azimuth calculation for a point (should be 0)."""
        p1 = QgsPointXY(0, 0)
        geom = QgsGeometry.fromPointXY(p1)

        azimuth = calculate_line_azimuth(geom)
        self.assertEqual(azimuth, 0.0)
