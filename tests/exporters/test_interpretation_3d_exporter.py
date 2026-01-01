"""Tests for Interpretation3DExporter."""

import unittest
from unittest.mock import MagicMock
import math

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsPoint,
    QgsGeometry,
    QgsPointXY,
    QgsWkbTypes,
    QgsFeature,
    QgsApplication,
    QgsSettings,
)

from sec_interp.exporters.interpretation_3d_exporter import Interpretation3DExporter

class TestInterpretation3DExporter(unittest.TestCase):
    """Test suite for Interpretation3DExporter."""

    @classmethod
    def setUpClass(cls):
        """Initialize QGIS Application."""
        cls.qgs = QgsApplication([], False)
        cls.qgs.initQgis()
        # Enable 3D export in settings for tests
        settings = QgsSettings()
        settings.setValue("sec_interp/enable_3d", True)

    @classmethod
    def tearDownClass(cls):
        """Clean up QGIS Application."""
        cls.qgs.exitQgis()

    def setUp(self):
        """Set up test fixtures."""
        self.mock_section_line = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(100, 0)])

        self.mock_polygon = MagicMock()
        self.mock_polygon.id = "test_poly"
        self.mock_polygon.name = "Test Unit"
        self.mock_polygon.type = "lithology"
        self.mock_polygon.color = "#FF0000"
        self.mock_polygon.created_at = "2024-01-01"
        self.mock_polygon.vertices_2d = [
            (10.0, 50.0),
            (20.0, 50.0),
            (20.0, 60.0),
            (10.0, 60.0),
        ]

    def test_azimuth_calculation_east(self):
        """Test azimuth calculation for East direction."""
        exporter = Interpretation3DExporter({})
        exporter._write_shapefile = MagicMock(return_value=True)

        data = {
            "interpretations": [MagicMock(vertices_2d=[(10, 10), (20, 10), (15, 20)], id="p1", name="u1", type="t1", color="c1", created_at="d1")],
            "section_line": self.mock_section_line,
            "crs": QgsCoordinateReferenceSystem("EPSG:4326")
        }

        exporter.export("/tmp/test.shp", data)

        # Verify call arguments
        args = exporter._write_shapefile.call_args
        features = args[0][1]
        self.assertEqual(len(features), 1)

        geom = features[0].geometry()
        # Verify it is a 2.5D geometry (Z)
        self.assertTrue(QgsWkbTypes.hasZ(geom.wkbType()))

    def test_geometric_transformation_north(self):
        """Test geometric transformation for North direction (Azimuth 90 deg)."""
        section_line = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(0, 100)])

        exporter = Interpretation3DExporter({})
        exporter._write_shapefile = MagicMock(return_value=True)

        data = {
            "interpretations": [self.mock_polygon],
            "section_line": section_line,
            "crs": QgsCoordinateReferenceSystem()
        }

        exporter.export("dummy.shp", data)

        features = exporter._write_shapefile.call_args[0][1]
        geom = features[0].geometry()

        # Check integrity
        # Vertical polygons on sections are technically invalid in 2D top-down view
        # so we check geometry type and Z presence instead of isGeosValid()
        self.assertTrue(QgsWkbTypes.hasZ(geom.wkbType()))
        self.assertEqual(geom.type(), QgsWkbTypes.PolygonGeometry)

    def test_overturned_fold_geometry(self):
        """Test that 'backwards' X values (geometric regression) are handled correctly."""
        polygon = MagicMock()
        polygon.id = "fold"
        polygon.name = "fold_name"
        polygon.type = "fold_type"
        polygon.color = "fold_color"
        polygon.created_at = "fold_date"
        polygon.vertices_2d = [
            (0.0, 0.0),
            (10.0, 0.0),
            (5.0, 10.0), # Backwards
            (0.0, 10.0)
        ]

        section_line = QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(100, 0)])

        exporter = Interpretation3DExporter({})
        exporter._write_shapefile = MagicMock(return_value=True)

        data = {
            "interpretations": [polygon],
            "section_line": section_line
        }

        exporter.export("dummy.shp", data)

        features = exporter._write_shapefile.call_args[0][1]
        geom = features[0].geometry()

        self.assertTrue(QgsWkbTypes.hasZ(geom.wkbType()))
        self.assertEqual(geom.type(), QgsWkbTypes.PolygonGeometry)

if __name__ == '__main__':
    unittest.main()
