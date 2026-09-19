"""Tests for spatial utilities."""

from unittest.mock import MagicMock
from tests.base_test import BaseTestCase
from qgis.core import QgsPointXY, QgsGeometry, QgsCoordinateReferenceSystem

from sec_interp.core.utils.spatial import (
    calculate_line_azimuth,
    get_line_start_point,
    create_distance_area,
)


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

    def test_get_line_start_point(self):
        """Test getting start point from single and multipart lines."""
        # Singlepart
        line = QgsGeometry.fromPolylineXY([QgsPointXY(5, 10), QgsPointXY(20, 30)])
        start = get_line_start_point(line)
        self.assertEqual(start.x(), 5)
        self.assertEqual(start.y(), 10)

        # Multipart
        mline = QgsGeometry()
        mline.isMultipart = MagicMock(return_value=True)
        mline.asMultiPolyline = MagicMock(
            return_value=[[QgsPointXY(1, 2), QgsPointXY(3, 4)]]
        )
        start_m = get_line_start_point(mline)
        self.assertEqual(start_m.x(), 1)
        self.assertEqual(start_m.y(), 2)

    def test_create_distance_area(self):
        """Test creation and configuration of QgsDistanceArea."""
        crs = QgsCoordinateReferenceSystem("EPSG:32633")
        da = create_distance_area(crs)

        self.assertIsNotNone(da)
        # Check that it supports the expected methods (handled by mock in base_test.py)
        da.setSourceCrs(crs, None)
        self.assertEqual(da.measureLine(QgsPointXY(0, 0), QgsPointXY(10, 0)), 10.0)
