"""Tests for Drillhole Service."""

from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from qgis.core import (
    QgsPointXY,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsVectorLayer,
)

from sec_interp.core.services.drillhole_service import DrillholeService
from sec_interp.core.exceptions import DataMissingError
from sec_interp.core.types import DrillholeTaskInput


class TestDrillholeService(BaseTestCase):
    """Tests for DrillholeService."""

    def setUp(self):
        super().setUp()
        self.service = DrillholeService()

        # Common mocks
        self.mock_line_geom = QgsGeometry.fromPolylineXY(
            [QgsPointXY(0, 0), QgsPointXY(100, 0)]
        )
        # In the new service, we pass geometries directly
        self.mock_line_data = self.mock_line_geom

        self.mock_da = MagicMock()
        self.mock_da.measureLine.return_value = 10.0

    def test_project_collars_success(self):
        """Test successful collar projection with detached data."""
        # Setup mock detached collar data with proper structure
        collar_data = [
            {
                "attributes": {"id": "DH01", "depth": 100.0, "z": 50.0},
                "wkt": "POINT(10 5)",
            }
        ]

        results = self.service.project_collars(
            collar_data=collar_data,
            line_data=self.mock_line_data,
            distance_area=self.mock_da,
            buffer_width=50.0,
            collar_id_field="id",
            use_geometry=True,
            collar_x_field="x",
            collar_y_field="y",
            collar_z_field="z",
            collar_depth_field="depth",
            pre_sampled_z=None,
        )

        self.assertEqual(len(results), 1)
        hole_id, dist, z, offset, depth = results[0]
        self.assertEqual(hole_id, "DH01")
        self.assertEqual(depth, 100.0)

    def test_fetch_bulk_data_survey(self):
        """Test bulk fetching survey data."""
        survey_layer = MagicMock()
        survey_layer.isValid.return_value = True

        from qgis.core import QgsFields, QgsField
        from PyQt5.QtCore import QVariant

        fields_cfg = QgsFields()
        fields_cfg.append(QgsField("hole_id", QVariant.String))
        fields_cfg.append(QgsField("depth", QVariant.Double))
        fields_cfg.append(QgsField("azim", QVariant.Double))
        fields_cfg.append(QgsField("incl", QVariant.Double))

        feat = QgsFeature(fields_cfg)
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

    @patch(
        "sec_interp.core.services.drillhole_service.scu.calculate_drillhole_trajectory"
    )
    @patch(
        "sec_interp.core.services.drillhole_service.scu.project_trajectory_to_section"
    )
    @patch(
        "sec_interp.core.services.drillhole_service.scu.interpolate_intervals_on_trajectory"
    )
    def test_process_intervals(self, mock_interp, mock_proj, mock_calc):
        """Test processing intervals for multiple holes."""
        collar_points = [("DH01", 10.0, 50.0, 2.0, 100.0)]
        collar_data = [
            {"id": "DH01", "attributes": {"x": 10, "y": 10}, "wkt": "POINT(10 10)"}
        ]

        # Mock dependencies
        mock_calc.return_value = []
        mock_proj.return_value = []
        mock_interp.return_value = []

        geol, dh = self.service.process_intervals(
            collar_points,
            collar_data,
            {},  # survey_data
            {},  # interval_data
            "id",
            True,
            "x",
            "y",
            self.mock_line_data,
            self.mock_da,
            50.0,
            0.0,
            {},
            {},
        )

        self.assertEqual(len(dh), 1)
        self.assertEqual(dh[0][0], "DH01")
