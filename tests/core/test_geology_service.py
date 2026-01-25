"""Tests for Geology Service."""

from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from qgis.core import (
    QgsPointXY,
    QgsGeometry,
    QgsFeature,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsCoordinateReferenceSystem,
)

from sec_interp.core.services.geology_service import GeologyService
from sec_interp.core.exceptions import DataMissingError, GeometryError


class TestGeologyService(BaseTestCase):
    """Tests for GeologyService."""

    def setUp(self):
        super().setUp()
        self.service = GeologyService()

        # Setup mock layers
        self.mock_line_lyr = MagicMock()
        self.mock_raster_lyr = MagicMock()
        self.mock_raster_lyr.bandCount.return_value = 1
        self.mock_outcrop_lyr = MagicMock()

        # Setup line geometry
        self.line_geom = QgsGeometry.fromPolylineXY(
            [QgsPointXY(0, 0), QgsPointXY(100, 0)]
        )
        self.line_feat = QgsFeature()
        self.line_feat.setGeometry(self.line_geom)

        self.mock_line_lyr.getFeatures.return_value = iter([self.line_feat])
        self.mock_line_lyr.crs.return_value = QgsCoordinateReferenceSystem("EPSG:32633")
        self.mock_line_lyr.name.return_value = "Line Layer"

    def test_extract_line_info_success(self):
        """Test line extraction from layer."""
        geom, start = self.service._extract_line_info(self.mock_line_lyr)
        self.assertIsNotNone(geom)
        self.assertEqual(start.x(), 0)
        self.assertEqual(start.y(), 0)

    def test_extract_line_info_no_features(self):
        """Test extraction from empty layer."""
        self.mock_line_lyr.getFeatures.return_value = iter([])
        with self.assertRaises(DataMissingError):
            self.service._extract_line_info(self.mock_line_lyr)

    @patch("sec_interp.core.services.geology_service.scu.create_distance_area")
    def test_generate_geological_profile(self, mock_da):
        """Test full profile generation."""
        # Setup DistanceArea mock
        da = MagicMock()
        da.measureLine.return_value = 10.0
        mock_da.return_value = da

        # Setup raster mock
        self.mock_raster_lyr.rasterUnitsPerPixelX.return_value = 10.0
        provider = MagicMock()
        provider.sample.return_value = (50.0, True)
        self.mock_raster_lyr.dataProvider.return_value = provider

        # Setup outcrop feature
        from qgis.core import QgsFields, QgsField, QMetaType

        fields = QgsFields()
        fields.append(QgsField("unit", QMetaType.Type.QString))

        outcrop_feat = QgsFeature(fields)
        outcrop_feat["unit"] = "Unit A"
        outcrop_feat.setGeometry(
            QgsGeometry.fromPolylineXY([QgsPointXY(20, -10), QgsPointXY(20, 10)])
        )
        self.mock_outcrop_lyr.getFeatures.return_value = [outcrop_feat]
        self.mock_outcrop_lyr.fields.return_value = fields

        segments = self.service.generate_geological_profile(
            self.mock_line_lyr, self.mock_raster_lyr, self.mock_outcrop_lyr, "unit"
        )

        self.assertIsInstance(segments, list)
        self.assertGreater(len(segments), 0)
        self.assertEqual(segments[0].unit_name, "Unit A")

    def test_generate_master_profile_data(self):
        """Test master profile generation logic."""
        da = MagicMock()
        da.measureLine.return_value = 10.0

        line_start = QgsPointXY(0, 0)

        # Mock raster
        self.mock_raster_lyr.rasterUnitsPerPixelX.return_value = (
            50.0  # 100/50 = 2 segments
        )
        provider = MagicMock()
        provider.sample.return_value = (100.0, True)
        self.mock_raster_lyr.dataProvider.return_value = provider

        profile, grid = self.service._generate_master_profile_data(
            self.line_geom, self.mock_raster_lyr, 1, da, line_start
        )

        self.assertEqual(len(profile), len(grid))
        self.assertGreater(len(profile), 1)
        self.assertEqual(profile[0][0], 0.0)  # Start distance
        self.assertEqual(profile[0][1], 100.0)  # Elevation

    def test_convert_to_segment_points(self):
        """Test distance to point conversion with interpolation."""
        grid = [(0.0, None, 100.0), (10.0, None, 110.0), (20.0, None, 120.0)]
        profile = [(0.0, 100.0), (10.0, 110.0), (20.0, 120.0)]

        # Segment from 5 to 15
        points = self.service._convert_to_segment_points(
            5.0, 15.0, grid, profile, 0.001
        )

        self.assertEqual(len(points), 3)  # (5, 105), (10, 110), (15, 115)
        self.assertAlmostEqual(points[0][0], 5.0)
        self.assertAlmostEqual(points[0][1], 105.0)
        self.assertAlmostEqual(points[2][0], 15.0)
        self.assertAlmostEqual(points[2][1], 115.0)
