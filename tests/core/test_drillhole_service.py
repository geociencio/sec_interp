"""Tests for Drillhole Service."""

from unittest.mock import MagicMock
from qgis.core import (
    QgsFeature,
    QgsField,
    QgsFields,
    QMetaType,
)
from tests.base_test import BaseTestCase

from sec_interp.core.domain import DrillholeContext
from sec_interp.core.services.drillhole_service import DrillholeService
from sec_interp.core.services.drillhole.collar_processor import CollarProcessor


class TestDrillholeService(BaseTestCase):
    """Tests for DrillholeService."""

    def setUp(self):
        super().setUp()
        self.service = DrillholeService()

    def _build_context(self, collar_data=None, survey_data=None, interval_data=None):
        return DrillholeContext(
            line_points=[(0.0, 0.0), (100.0, 0.0)],
            section_azimuth=90.0,
            buffer_width=50.0,
            collar_id_field="id",
            collar_z_field="z",
            collar_depth_field="depth",
            collar_data=collar_data or [],
            survey_data=survey_data or {},
            interval_data=interval_data or {},
        )

    def test_process_context_projects_collar(self):
        """Test that a detached collar is projected onto the section line."""
        context = self._build_context(
            collar_data=[
                {
                    "id": "DH01",
                    "point": (50.0, 10.0),
                    "attributes": {"z": 50.0, "depth": 100.0},
                }
            ],
            survey_data={"DH01": [(0.0, 0.0, -90.0), (100.0, 0.0, -90.0)]},
            interval_data={"DH01": [(0.0, 50.0, "RockA")]},
        )

        geol, drillhole_data = self.service.process_context(context)

        self.assertEqual(len(drillhole_data), 1)
        self.assertEqual(drillhole_data[0].hole_id, "DH01")
        self.assertGreater(len(drillhole_data[0].points_3d), 0)
        self.assertGreater(len(drillhole_data[0].segments), 0)

    def test_process_context_empty_returns_empty(self):
        """Test that no collars produces empty results."""
        context = self._build_context()
        geol, drillhole_data = self.service.process_context(context)

        self.assertEqual(geol, [])
        self.assertEqual(drillhole_data, [])

    def test_process_context_collar_outside_buffer_skipped(self):
        """Test that a collar far from the line is excluded by buffer width."""
        context = self._build_context(
            collar_data=[
                {
                    "id": "DH99",
                    "point": (50.0, 500.0),  # far outside buffer
                    "attributes": {"z": 50.0, "depth": 100.0},
                }
            ]
        )

        _, drillhole_data = self.service.process_context(context)
        self.assertEqual(drillhole_data, [])

    def test_collar_processor_project(self):
        """Test CollarProcessor projection directly."""
        processor = CollarProcessor()
        result = processor.extract_and_project_detached(
            {"id": "DH01", "point": (50.0, 5.0), "attributes": {"z": 50.0, "depth": 100.0}},
            line_points=[(0.0, 0.0), (100.0, 0.0)],
            buffer_width=50.0,
            collar_id_field="id",
            collar_z_field="z",
            collar_depth_field="depth",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.hole_id, "DH01")
        self.assertAlmostEqual(result.distance, 50.0, places=0)

    def test_fetch_bulk_data_survey(self):
        """Test bulk fetching survey data."""
        from sec_interp.gui.adapters.feature_fetcher import DataFetcher

        fetcher = DataFetcher()
        survey_layer = MagicMock()
        survey_layer.isValid.return_value = True

        fields_cfg = QgsFields()
        fields_cfg.append(QgsField("hole_id", QMetaType.Type.QString))
        fields_cfg.append(QgsField("depth", QMetaType.Type.Double))
        fields_cfg.append(QgsField("azim", QMetaType.Type.Double))
        fields_cfg.append(QgsField("incl", QMetaType.Type.Double))

        feat = QgsFeature(fields_cfg)
        feat["hole_id"] = "DH01"
        feat["depth"] = 10.0
        feat["azim"] = 180.0
        feat["incl"] = -45.0

        survey_layer.getFeatures.return_value = [feat]

        fields = {"id": "hole_id", "depth": "depth", "azim": "azim", "incl": "incl"}
        res = fetcher.fetch_bulk_data(survey_layer, {"DH01"}, fields)

        self.assertIn("DH01", res)
        self.assertEqual(len(res["DH01"]), 1)
        self.assertEqual(res["DH01"][0], (10.0, 180.0, -45.0))
