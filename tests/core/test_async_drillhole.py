"""Tests for Async Drillhole Processing."""

from unittest.mock import MagicMock
from tests.base_test import BaseTestCase
from qgis.core import (
    QgsPointXY,
    QgsGeometry,
    QgsFields,
    QgsField,
    QgsFeature,
    QgsCoordinateReferenceSystem,
)
from qgis.PyQt.QtCore import QWaitCondition, QMutex

from sec_interp.core.services.drillhole_service import DrillholeService
from sec_interp.core.types import DrillholeTaskInput


class TestAsyncDrillhole(BaseTestCase):
    """Tests for asynchronous drillhole processing logic."""

    def setUp(self):
        super().setUp()
        self.service = DrillholeService()
        self.line_geom = QgsGeometry.fromPolylineXY(
            [QgsPointXY(0, 0), QgsPointXY(100, 0)]
        )
        self.line_start = QgsPointXY(0, 0)
        self.crs = QgsCoordinateReferenceSystem("EPSG:32719")

    def test_prepare_task_input(self):
        """Test gathering detached data."""
        # Setup layers
        collar_layer = MagicMock()
        collar_layer.getFeatures.return_value = []

        survey_layer = MagicMock()
        interval_layer = MagicMock()

        # Test basic preparation
        mock_line_layer = MagicMock()
        line_feat = QgsFeature()
        line_feat.setGeometry(
            QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(100, 0)])
        )
        mock_line_layer.getFeatures.return_value = iter([line_feat])
        mock_line_layer.crs.return_value = self.crs

        task_input = self.service.prepare_task_input(
            line_layer=mock_line_layer,
            buffer_width=50.0,
            collar_layer=collar_layer,
            collar_id_field="id",
            use_geometry=True,
            collar_x_field="",
            collar_y_field="",
            collar_z_field="z",
            collar_depth_field="depth",
            survey_layer=survey_layer,
            survey_fields={},
            interval_layer=interval_layer,
            interval_fields={},
        )

        self.assertIsInstance(task_input, DrillholeTaskInput)
        self.assertEqual(task_input.section_azimuth, 90.0)
        self.assertEqual(task_input.buffer_width, 50.0)

    def test_process_task_data(self):
        """Test processing detached data."""
        # Create detached input manually
        task_input = DrillholeTaskInput(
            line_geometry_wkt=self.line_geom.asWkt(),
            line_start_x=self.line_start.x(),
            line_start_y=self.line_start.y(),
            line_crs_authid=self.crs.authid(),
            section_azimuth=90.0,
            buffer_width=50.0,
            collar_id_field="id",
            use_geometry=True,
            collar_x_field="",
            collar_y_field="",
            collar_z_field="",
            collar_depth_field="",
            collar_data=[
                {
                    "id": "DH01",
                    "attributes": {"id": "DH01", "z": 100.0, "depth": 200.0},
                    "wkt": QgsGeometry.fromPointXY(QgsPointXY(50, 10)).asWkt(),
                }
            ],
            survey_data={"DH01": [(0.0, 0.0, -90.0), (200.0, 0.0, -90.0)]},
            interval_data={"DH01": [(0.0, 50.0, "RockA"), (50.0, 100.0, "RockB")]},
            pre_sampled_z={},
        )

        results = self.service.process_task_data(task_input)

        self.assertIsNotNone(results)
        geol_data, drill_data = results

        self.assertEqual(len(drill_data), 1)
        hid, trace2d, trace3d, proj3d, segments = drill_data[0]
        self.assertEqual(hid, "DH01")
        self.assertTrue(len(segments) > 0)
