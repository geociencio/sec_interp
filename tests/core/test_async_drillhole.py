"""Tests for Async Drillhole Processing."""

from tests.base_test import BaseTestCase

from sec_interp.core.domain.task_inputs import DrillholeContext
from sec_interp.core.services.drillhole_service import DrillholeService


class TestAsyncDrillhole(BaseTestCase):
    """Tests for drillhole processing logic over a detached context."""

    def setUp(self):
        super().setUp()
        self.service = DrillholeService()
        self.line_points = [(0.0, 0.0), (100.0, 0.0)]

    def test_process_context(self):
        """Test processing a detached context into geol + drillhole data."""
        context = DrillholeContext(
            line_points=self.line_points,
            section_azimuth=90.0,
            buffer_width=50.0,
            collar_id_field="id",
            collar_z_field="z",
            collar_depth_field="depth",
            collar_data=[
                {
                    "id": "DH01",
                    "point": (50.0, 10.0),
                    "attributes": {"id": "DH01", "z": 100.0, "depth": 200.0},
                }
            ],
            survey_data={"DH01": [(0.0, 0.0, -90.0), (200.0, 0.0, -90.0)]},
            interval_data={"DH01": [(0.0, 50.0, "RockA"), (50.0, 100.0, "RockB")]},
            pre_sampled_z={},
        )

        results = self.service.process_context(context)

        self.assertIsNotNone(results)
        geol_data, drill_data = results
        self.assertEqual(len(drill_data), 1)
        proj = drill_data[0]
        self.assertEqual(proj.hole_id, "DH01")
        self.assertTrue(len(proj.points_3d) > 0)
        self.assertTrue(len(proj.segments) > 0)
