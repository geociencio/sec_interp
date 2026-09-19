"""Reproduction test for DrillholeEngine IndexError when trajectory is empty."""

# Import tests to activate QGIS mocks
import unittest

from tests.base_test import BaseTestCase
from sec_interp.core.services.drillhole.trajectory_engine import TrajectoryEngine


class TestDrillholeEngineCrash(BaseTestCase):
    def setUp(self):
        self.engine = TrajectoryEngine()
        self.line_points = [(0.0, 0.0), (100.0, 0.0)]

    def test_create_result_with_empty_traj(self):
        """Test that create_drillhole_result handles empty trajectories without crashing."""
        hole_id = "TEST-01"
        projected_traj = []
        hole_geol_data = []

        # This should NOT raise IndexError
        try:
            result = self.engine.create_drillhole_result(
                hole_id, projected_traj, hole_geol_data
            )
            self.assertEqual(result.hole_id, hole_id)
            self.assertEqual(len(result.points_3d), 0)
        except IndexError:
            self.fail("create_drillhole_result raised IndexError with empty trajectory")

    def test_process_empty_traj(self):
        """Test processing a hole that results in no projected points (e.g. out of buffer)."""
        hole_id = "BH-01"
        collar_point = (0.0, 500.0)  # Far from line
        collar_z = 100.0
        depth = 50.0
        survey = []
        intervals = []

        # The hole is 500m away from the line with a 10m buffer.
        try:
            geol, proj = self.engine.process_single_hole(
                hole_id,
                collar_point,
                collar_z,
                depth,
                survey,
                intervals,
                self.line_points,
                10.0,
                0.0,
            )
            self.assertEqual(len(proj.points_3d), 0)
        except IndexError:
            self.fail(
                "process_single_hole raised IndexError when hole is outside buffer"
            )


if __name__ == "__main__":
    unittest.main()
