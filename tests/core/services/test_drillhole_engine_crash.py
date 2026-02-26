"""Reproduction test for DrillholeEngine IndexError when trajectory is empty."""

# Import tests to activate QGIS mocks
from sec_interp import tests  # noqa: F401

import unittest
from unittest.mock import MagicMock
from qgis.core import QgsGeometry, QgsPointXY, QgsDistanceArea
from sec_interp.core.services.drillhole.trajectory_engine import TrajectoryEngine

class TestDrillholeEngineCrash(unittest.TestCase):
    def setUp(self):
        self.engine = TrajectoryEngine()
        self.line_geom = QgsGeometry.fromWkt("LINESTRING(0 0, 100 0)")
        self.line_start = QgsPointXY(0, 0)
        self.da = QgsDistanceArea()

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
        # We mock calculate_drillhole_trajectory or project_trajectory_to_section 
        # but here we can just test the engine logic if we can force an empty traj.
        
        # If we use a hole ID that has no survey or intervals, it might still have a collar point
        # but let's test the specific case where it produces no projected points.
        
        # Forcing empty projected_traj by using a buffer of 0 or far distance
        hole_id = "BH-01"
        collar_point = QgsPointXY(0, 500) # Far from line
        collar_z = 100.0
        depth = 50.0
        survey = []
        intervals = []
        
        # This will likely call create_drillhole_result with empty projected_traj
        # since the hole is 500m away from the line and we'll use a 10m buffer.
        try:
            geol, proj = self.engine.process_single_hole(
                hole_id, collar_point, collar_z, depth, survey, intervals,
                self.line_geom, self.line_start, self.da, 10.0, 0.0
            )
            self.assertEqual(len(proj.points_3d), 0)
        except IndexError:
            self.fail("process_single_hole raised IndexError when hole is outside buffer")

if __name__ == "__main__":
    unittest.main()
