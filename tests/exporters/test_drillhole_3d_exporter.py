"""Tests for 3D Drillhole Exporters."""

import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile
import shutil

from qgis.core import (
    QgsPoint,
    QgsLineString,
    QgsWkbTypes,
    QgsCoordinateReferenceSystem,
    QgsGeometry,
)

from tests.base_test import BaseTestCase
from sec_interp.exporters.drillhole_3d_exporter import (
    DrillholeTrace3DExporter,
    DrillholeInterval3DExporter,
)


class TestDrillhole3DExporters(BaseTestCase):
    """Tests for Drillhole 3D Exporters."""

    def setUp(self):
        super().setUp()
        self.crs = QgsCoordinateReferenceSystem("EPSG:4326")
        self.settings = {}

        # Sample trace data (hole_id, traces_2d, traces_3d, traces_3d_proj, segments)
        self.sample_drillhole = (
            "DH01",
            [],  # traces_2d
            [(0.0, 0.0, 100.0), (0.0, 0.0, 50.0)],  # traces_3d (real)
            [(10.0, 0.0, 100.0), (10.0, 0.0, 50.0)],  # traces_3d_proj
            [],  # segments
        )

        # Sample interval data
        from sec_interp.core.types import GeologySegment

        seg1 = GeologySegment(
            unit_name="Unit A",
            geometry=QgsGeometry(),
            attributes={"from": 0.0, "to": 10.0},
            points=[],
            points_3d=[(0.0, 0.0, 100.0), (0.0, 0.0, 90.0)],
            points_3d_projected=[(10.0, 0.0, 100.0), (10.0, 0.0, 90.0)],
        )
        # Drillhole structure for intervals: (hole_id, traces_2d, traces_3d, traces_3d_proj, segments)
        self.sample_intervals = [("DH01", [], [], [], [seg1])]

    @patch("sec_interp.exporters.drillhole_3d_exporter.scu.create_shapefile_writer")
    def test_trace_exporter_real(self, mock_writer):
        """Test DrillholeTrace3DExporter using real coordinates."""
        exporter = DrillholeTrace3DExporter(self.settings)
        output_path = Path(self.test_dir) / "traces_3d_real.shp"

        data = {
            "drillhole_data": [self.sample_drillhole],
            "crs": self.crs,
            "use_projected": False,
        }
        exporter.export(output_path, data)

        # Verify writer call
        mock_writer.assert_called_once()
        args, _ = mock_writer.call_args
        self.assertEqual(args[3], QgsWkbTypes.LineStringZ)

        # Verify feature addition
        writer = mock_writer.return_value
        writer.addFeature.assert_called_once()
        feat = writer.addFeature.call_args[0][0]
        geom = feat.geometry().constGet()
        self.assertTrue(geom.is3D())
        self.assertEqual(geom.pointN(0).z(), 100.0)

    @patch("sec_interp.exporters.drillhole_3d_exporter.scu.create_shapefile_writer")
    def test_trace_exporter_projected(self, mock_writer):
        """Test DrillholeTrace3DExporter using projected coordinates."""
        exporter = DrillholeTrace3DExporter(self.settings)
        output_path = Path(self.test_dir) / "traces_3d_proj.shp"

        data = {
            "drillhole_data": [self.sample_drillhole],
            "crs": self.crs,
            "use_projected": True,
        }
        exporter.export(output_path, data)

        # Verify feature addition
        writer = mock_writer.return_value
        writer.addFeature.assert_called_once()
        feat = writer.addFeature.call_args[0][0]
        geom = feat.geometry().constGet()
        self.assertEqual(geom.pointN(0).x(), 10.0)
        self.assertEqual(geom.pointN(0).z(), 100.0)

    @patch("sec_interp.exporters.drillhole_3d_exporter.scu.create_shapefile_writer")
    def test_interval_exporter_real(self, mock_writer):
        """Test DrillholeInterval3DExporter using real coordinates."""
        exporter = DrillholeInterval3DExporter(self.settings)
        output_path = Path(self.test_dir) / "intervals_3d_real.shp"

        data = {
            "drillhole_data": self.sample_intervals,
            "crs": self.crs,
            "use_projected": False,
        }
        exporter.export(output_path, data)

        mock_writer.assert_called_once()
        writer = mock_writer.return_value
        writer.addFeature.assert_called_once()
        feat = writer.addFeature.call_args[0][0]
        self.assertEqual(feat["unit"], "Unit A")
        geom = feat.geometry().constGet()
        self.assertEqual(geom.pointN(0).z(), 100.0)

    @patch("sec_interp.exporters.drillhole_3d_exporter.scu.create_shapefile_writer")
    def test_interval_exporter_projected(self, mock_writer):
        """Test DrillholeInterval3DExporter using projected coordinates."""
        exporter = DrillholeInterval3DExporter(self.settings)
        output_path = Path(self.test_dir) / "intervals_3d_proj.shp"

        data = {
            "drillhole_data": self.sample_intervals,
            "crs": self.crs,
            "use_projected": True,
        }
        exporter.export(output_path, data)

        writer = mock_writer.return_value
        writer.addFeature.assert_called_once()
        feat = writer.addFeature.call_args[0][0]
        geom = feat.geometry().constGet()
        self.assertEqual(geom.pointN(0).x(), 10.0)
        self.assertEqual(geom.pointN(0).z(), 100.0)
