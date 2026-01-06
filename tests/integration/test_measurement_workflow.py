"""Integration tests for measurement tool workflow."""

from qgis.core import QgsPointXY, QgsMapSettings
from qgis.gui import QgsMapCanvas
from tests.integration.base_integration import BaseIntegrationTest
from sec_interp.gui.tools.measure_tool import ProfileMeasureTool

class TestMeasurementWorkflow(BaseIntegrationTest):
    """Integration test for multi-point measurement workflow."""

    def setUp(self):
        super().setUp()
        self.canvas = QgsMapCanvas()

        self.tool = ProfileMeasureTool(self.canvas)
        self.received_metrics = []
        self.tool.measurementChanged.connect(self.received_metrics.append)

    def test_multi_point_measurement(self):
        """Test sequence of points and final metrics calculation."""
        # Simulate adding points (programmatically to avoid UI event issues)
        p1 = QgsPointXY(0, 0)
        p2 = QgsPointXY(100, 100)
        p3 = QgsPointXY(200, 150)

        self.tool._add_point(p1)
        self.tool._add_point(p2)

        # Should have received 1 metric update (after second point)
        self.assertEqual(len(self.received_metrics), 1)
        latest = self.received_metrics[-1]

        # Vector (100, 100). Total dist = sqrt(100^2 + 100^2) approx 141.42
        self.assertAlmostEqual(latest["total_distance"], 141.42, places=1)
        self.assertAlmostEqual(latest["horizontal_distance"], 100.0)
        self.assertAlmostEqual(latest["elevation_change"], 100.0)

        self.tool._add_point(p3)
        self.assertEqual(len(self.received_metrics), 2)
        latest = self.received_metrics[-1]

        # Second segment: (100, 50). Dist = sqrt(100^2 + 50^2) approx 111.8
        # Total dist approx 141.42 + 111.8 = 253.22
        self.assertAlmostEqual(latest["total_distance"], 253.2, places=1)
        self.assertEqual(latest["point_count"], 3)
        self.assertEqual(latest["segment_count"], 2)

    def test_finalize_and_reset(self):
        """Test finalization and cleanup of measurement tool."""
        self.tool._add_point(QgsPointXY(0, 0))
        self.tool._add_point(QgsPointXY(10, 10))

        self.tool.finalize_measurement()
        self.assertTrue(self.tool.finalized)

        # Reset should clear data
        self.tool.reset()
        self.assertEqual(len(self.tool.points), 0)
        self.assertFalse(self.tool.finalized)
