import unittest
from unittest.mock import MagicMock, patch
from qgis.core import QgsCoordinateReferenceSystem, QgsFields, QgsVectorFileWriter
from sec_interp.exporters.drillhole_exporters import (
    DrillholeTraceShpExporter,
    DrillholeIntervalShpExporter,
)
from sec_interp.exporters.drillhole_3d_exporter import (
    DrillholeTrace3DExporter,
    DrillholeInterval3DExporter,
)
from sec_interp.core.domain import DrillholeProjection, GeologySegment, SpatialMeta


class TestDrillholeExportObjects(unittest.TestCase):
    def setUp(self):
        self.crs = QgsCoordinateReferenceSystem("EPSG:4326")
        self.trace_exporter = DrillholeTraceShpExporter({})
        self.interval_exporter = DrillholeIntervalShpExporter({})
        self.trace_3d_exporter = DrillholeTrace3DExporter({})
        self.interval_3d_exporter = DrillholeInterval3DExporter({})

    @patch("sec_interp.exporters.drillhole_exporters.scu_io.create_vector_writer")
    def test_export_traces_success(self, mock_writer_factory):
        # 1. Setup
        mock_writer = MagicMock()
        mock_writer.hasError.return_value = QgsVectorFileWriter.NoError
        mock_writer_factory.return_value = mock_writer

        # Create test data with DrillholeProjection object
        dh1 = DrillholeProjection(
            hole_id="DH01",
            distance=100.0,
            elevation=500.0,
            offset=0.0,
            total_depth=200.0,
            points_3d=[
                SpatialMeta(dist_along=0, z=500),
                SpatialMeta(dist_along=100, z=300),
            ],
            segments=[],
        )

        data = {"drillhole_data": [dh1], "crs": self.crs}

        success = self.trace_exporter.export("/tmp/test_traces.shp", data)
        self.assertTrue(success)
        mock_writer.addFeature.assert_called()

    @patch("sec_interp.exporters.drillhole_exporters.scu_io.create_vector_writer")
    def test_export_intervals_success(self, mock_writer_factory):
        # 1. Setup
        mock_writer = MagicMock()
        mock_writer.hasError.return_value = QgsVectorFileWriter.NoError
        mock_writer_factory.return_value = mock_writer

        # Create test data with segments
        seg1 = GeologySegment(
            unit_name="Unit A",
            geometry_wkt=None,
            attributes={"from": 0.0, "to": 50.0},
            points=[(0, 500), (25, 450)],
        )

        dh1 = DrillholeProjection(
            hole_id="DH01",
            distance=100.0,
            elevation=500.0,
            offset=0.0,
            total_depth=200.0,
            points_3d=[],
            segments=[seg1],
        )

        data = {"drillhole_data": [dh1], "crs": self.crs}

        success = self.interval_exporter.export("/tmp/test_intervals.shp", data)
        self.assertTrue(success)
        mock_writer.addFeature.assert_called()

    @patch("sec_interp.exporters.drillhole_3d_exporter.scu_io.create_vector_writer")
    def test_export_3d_traces_with_objects(self, mock_writer_factory):
        # 1. Setup
        mock_writer = MagicMock()
        mock_writer.hasError.return_value = QgsVectorFileWriter.NoError
        mock_writer_factory.return_value = mock_writer

        dh1 = DrillholeProjection(
            hole_id="DH01",
            distance=100.0,
            elevation=500.0,
            offset=0.0,
            total_depth=200.0,
            points_3d=[
                SpatialMeta(dist_along=0, z=500, x_3d=1000, y_3d=2000),
                SpatialMeta(dist_along=100, z=300, x_3d=1100, y_3d=2100),
            ],
            segments=[],
        )

        data = {"drillhole_data": [dh1], "crs": self.crs}
        success = self.trace_3d_exporter.export("/tmp/test_traces_3d.shp", data)
        self.assertTrue(success)
        mock_writer.addFeature.assert_called()

    @patch("sec_interp.exporters.drillhole_3d_exporter.scu_io.create_vector_writer")
    def test_export_3d_intervals_with_objects(self, mock_writer_factory):
        # 1. Setup
        mock_writer = MagicMock()
        mock_writer.hasError.return_value = QgsVectorFileWriter.NoError
        mock_writer_factory.return_value = mock_writer

        seg1 = GeologySegment(
            unit_name="Unit A",
            geometry_wkt=None,
            attributes={"from": 0.0, "to": 50.0},
            points=[],
            points_3d=[(1000, 2000, 500), (1020, 2020, 450)],
        )

        dh1 = DrillholeProjection(
            hole_id="DH01",
            distance=100.0,
            elevation=500.0,
            offset=0.0,
            total_depth=200.0,
            points_3d=[],
            segments=[seg1],
        )

        data = {"drillhole_data": [dh1], "crs": self.crs}
        success = self.interval_3d_exporter.export("/tmp/test_intervals_3d.shp", data)
        self.assertTrue(success)
        mock_writer.addFeature.assert_called()


if __name__ == "__main__":
    unittest.main()
