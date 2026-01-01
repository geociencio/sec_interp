"""Tests for Drillhole Service."""

from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from qgis.core import (
    QgsPointXY,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsVectorLayer
)

from sec_interp.core.services.drillhole_service import DrillholeService
from sec_interp.core.exceptions import DataMissingError


class TestDrillholeService(BaseTestCase):
    """Tests for DrillholeService."""

    def setUp(self):
        super().setUp()
        self.service = DrillholeService()

        # Common mocks
        self.mock_line_geom = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(100, 0)])
        self.mock_line_start = QgsPointXY(0, 0)
        self.mock_da = MagicMock()
        self.mock_da.measureLine.return_value = 10.0

        self.mock_layer = MagicMock()
        self.mock_layer.name.return_value = "Test Layer"
        self.mock_layer.isValid.return_value = True

    def test_project_collars_no_layer(self):
        """Test project_collars with missing layer."""
        with self.assertRaises(DataMissingError):
            self.service.project_collars(
                None, self.mock_line_geom, self.mock_line_start,
                self.mock_da, 50.0, "id", True, "", "", "", "", None
            )

    @patch("sec_interp.core.services.drillhole_service.scu.filter_features_by_buffer")
    def test_project_collars_success(self, mock_filter):
        """Test successful collar projection."""
        # Setup mock features
        feat = QgsFeature()
        feat["id"] = "DH01"
        feat["depth"] = 100.0
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(10, 5)))

        mock_filter.return_value = [feat]

        # We need to mock _project_single_collar to simplify or test it integrated
        # Let's test integrated. _project_single_collar calls _get_collar_info

        results = self.service.project_collars(
            self.mock_layer, self.mock_line_geom, self.mock_line_start,
            self.mock_da, 50.0, "id", True, "x", "y", "z", "depth", None
        )

        self.assertEqual(len(results), 1)
        hole_id, dist, z, offset, depth = results[0]
        self.assertEqual(hole_id, "DH01")
        self.assertEqual(depth, 100.0)

    def test_get_collar_info_geom(self):
        """Test extracting collar info from geometry."""
        feat = QgsFeature()
        feat["id"] = "DH01"
        feat["z"] = 50.0
        feat["depth"] = 200.0
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(10, 20)))

        info = self.service._get_collar_info(
            feat, "id", True, "", "", "z", "depth", None
        )

        self.assertIsNotNone(info)
        hole_id, pt, z, depth = info
        self.assertEqual(hole_id, "DH01")
        self.assertEqual(pt.x(), 10.0)
        self.assertEqual(pt.y(), 20.0)
        self.assertEqual(z, 50.0)
        self.assertEqual(depth, 200.0)

    def test_get_collar_info_fields(self):
        """Test extracting collar info from fields."""
        feat = QgsFeature()
        feat["id"] = "DH01"
        feat["X"] = 15.0
        feat["Y"] = 25.0
        feat["depth"] = 150.0

        info = self.service._get_collar_info(
            feat, "id", False, "X", "Y", "", "depth", None
        )

        self.assertIsNotNone(info)
        hole_id, pt, z, depth = info
        self.assertEqual(pt.x(), 15.0)
        self.assertEqual(pt.y(), 25.0)
        self.assertEqual(z, 0.0) # No z field provided

    @patch("sec_interp.core.services.drillhole_service.scu.filter_features_by_buffer")
    def test_project_collars_empty(self, mock_filter):
        """Test project_collars with no features found."""
        mock_filter.return_value = []
        results = self.service.project_collars(
            self.mock_layer, self.mock_line_geom, self.mock_line_start,
            self.mock_da, 50.0, "id", True, "", "", "", "", None
        )
        self.assertEqual(len(results), 0)

    def test_get_collar_info_dem(self):
        """Test collar info with DEM elevation fallback."""
        feat = QgsFeature()
        feat["id"] = "DH01"
        feat["z"] = 0.0 # Force DEM fallback
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(10, 20)))

        dem_layer = MagicMock()
        dem_provider = MagicMock()
        dem_layer.dataProvider.return_value = dem_provider

        ident = MagicMock()
        ident.isValid.return_value = True
        ident.results.return_value = {1: 123.4}
        dem_provider.identify.return_value = ident

        info = self.service._get_collar_info(
            feat, "id", True, "", "", "z", "", dem_layer
        )

        self.assertIsNotNone(info)
        self.assertEqual(info[2], 123.4)

    def test_fetch_bulk_data_interval(self):
        """Test bulk fetching interval data."""
        interval_layer = MagicMock()
        interval_layer.isValid.return_value = True

        feat = QgsFeature()
        feat["hole_id"] = "DH01"
        feat["from"] = 0.0
        feat["to"] = 20.0
        feat["lith"] = "Sand"

        interval_layer.getFeatures.return_value = [feat]

        fields = {"id": "hole_id", "from": "from", "to": "to", "lith": "lith"}
        res = self.service._fetch_bulk_data(interval_layer, {"DH01"}, fields)

    def test_fetch_bulk_data_survey(self):
        """Test bulk fetching survey data."""
        survey_layer = MagicMock()
        survey_layer.isValid.return_value = True

        feat = QgsFeature()
        feat["hole_id"] = "DH01"
        feat["depth"] = 10.0
        feat["azim"] = 180.0
        feat["incl"] = -45.0

        survey_layer.getFeatures.return_value = [feat]

        fields = {"id": "hole_id", "depth": "depth", "azim": "azim", "incl": "incl"}
        res = self.service._fetch_bulk_data(survey_layer, {"DH01"}, fields)

        self.assertIn("DH01", res)
        self.assertEqual(len(res["DH01"]), 1)
        self.assertEqual(res["DH01"][0], (10.0, 180.0, -45.0))

    @patch("sec_interp.core.services.drillhole_service.scu.calculate_drillhole_trajectory")
    @patch("sec_interp.core.services.drillhole_service.scu.project_trajectory_to_section")
    @patch("sec_interp.core.services.drillhole_service.scu.interpolate_intervals_on_trajectory")
    def test_process_intervals(self, mock_interp, mock_proj, mock_calc):
        """Test processing intervals for multiple holes."""
        collar_points = [("DH01", 10.0, 50.0, 2.0, 100.0)]

        # Mock dependencies
        mock_calc.return_value = []
        mock_proj.return_value = []
        mock_interp.return_value = []

        # Mock building collar map
        self.service._build_collar_coord_map = MagicMock(return_value={"DH01": QgsPointXY(10, 10)})
        self.service._fetch_bulk_data = MagicMock(return_value={})

        geol, dh = self.service.process_intervals(
            collar_points, MagicMock(), MagicMock(), MagicMock(),
            "id", True, "", "", self.mock_line_geom, self.mock_line_start,
            self.mock_da, 50.0, 0.0, {}, {}
        )

        self.assertEqual(len(dh), 1)
        self.assertEqual(dh[0][0], "DH01")
