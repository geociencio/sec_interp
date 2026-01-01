"""Tests for spatial utilities."""

import math
from unittest.mock import MagicMock
from tests.base_test import BaseTestCase
from qgis.core import QgsPointXY, QgsGeometry, QgsWkbTypes, QgsCoordinateReferenceSystem

from sec_interp.core.utils.spatial import (
    calculate_line_azimuth,
    calculate_step_size,
    get_line_start_point,
    create_distance_area,
)


class TestSpatialUtils(BaseTestCase):
    """Tests for spatial utility functions."""

    def test_calculate_line_azimuth_point(self):
        """Test azimuth calculation for a point (should return 0)."""
        geom = QgsGeometry.fromPointXY(QgsPointXY(0, 0))
        self.assertEqual(calculate_line_azimuth(geom), 0)

    def test_calculate_line_azimuth_line(self):
        """Test azimuth calculation for valid lines."""
        # North: (0,0) to (0,10) -> 0 degrees
        line_n = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(0, 10)])
        self.assertAlmostEqual(calculate_line_azimuth(line_n), 0)

        # East: (0,0) to (10,0) -> 90 degrees
        line_e = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(10, 0)])
        self.assertAlmostEqual(calculate_line_azimuth(line_e), 90)

        # South: (0,0) to (0,-10) -> 180 degrees
        line_s = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(0, -10)])
        self.assertAlmostEqual(calculate_line_azimuth(line_s), 180)

        # West: (0,0) to (-10,0) -> 270 degrees
        line_w = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(-10, 0)])
        self.assertAlmostEqual(calculate_line_azimuth(line_w), 270)

    def test_calculate_line_azimuth_unsupported(self):
        """Test azimuth for unsupported geometry types."""
        geom = QgsGeometry()
        geom._wkb_type = QgsWkbTypes.PolygonGeometry
        self.assertEqual(calculate_line_azimuth(geom), 0)

    def test_calculate_line_azimuth_short_line(self):
        """Test azimuth for line with less than 2 points."""
        geom = QgsGeometry()
        geom._wkb_type = QgsWkbTypes.LineString
        geom._polyline = [QgsPointXY(1, 1)]
        self.assertEqual(calculate_line_azimuth(geom), 0)

    def test_calculate_step_size_exception(self):
        """Test step size calculation when an exception occurs."""
        raster_lyr = MagicMock()
        raster_lyr.rasterUnitsPerPixelX.return_value = 2.0

        # Geometry that causes error in asPolyline
        geom = QgsGeometry()
        geom.asPolyline = MagicMock(side_effect=ValueError("Test error"))

        # Should fallback to resolution
        self.assertEqual(calculate_step_size(geom, raster_lyr), 2.0)

    def test_calculate_step_size(self):
        """Test step size calculation based on raster resolution."""
        raster_lyr = MagicMock()
        raster_lyr.rasterUnitsPerPixelX.return_value = 2.0

        # Horizontal line: dx=10, dy=0, length=10 -> step = 10 * 2 / 10 = 2
        line = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(10, 0)])
        self.assertAlmostEqual(calculate_step_size(line, raster_lyr), 2.0)

        # Diagonal line: dx=10, dy=10, length=sqrt(200)~14.14 -> step = 14.14 * 2 / 10 = 2.828
        line_diag = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(10, 10)])
        expected = math.sqrt(200) * 2 / 10
        self.assertAlmostEqual(calculate_step_size(line_diag, raster_lyr), expected)

    def test_calculate_step_size_multipart(self):
        """Test step size for multipart geometries."""
        raster_lyr = MagicMock()
        raster_lyr.rasterUnitsPerPixelX.return_value = 2.0

        line = QgsGeometry()
        line.isMultipart = MagicMock(return_value=True)
        line.asMultiPolyline = MagicMock(return_value=[[QgsPointXY(0, 0), QgsPointXY(10, 0)]])
        line.length = MagicMock(return_value=10.0)

        self.assertAlmostEqual(calculate_step_size(line, raster_lyr), 2.0)

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
        mline.asMultiPolyline = MagicMock(return_value=[[QgsPointXY(1, 2), QgsPointXY(3, 4)]])
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
