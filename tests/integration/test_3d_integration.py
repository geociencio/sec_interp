from __future__ import annotations

"""Integration tests for 3D projection and export."""

import os
import tempfile
import shutil
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsGeometry,
    QgsPointXY,
    QgsVectorLayer,
    QgsWkbTypes,
    QgsPoint
)
from tests.integration.base_integration import BaseIntegrationTest
from sec_interp.core.types import InterpretationPolygon, GeologySegment
from sec_interp.exporters.drillhole_3d_exporter import (
    DrillholeTrace3DExporter,
    DrillholeInterval3DExporter
)
from sec_interp.exporters.interpretation_3d_exporter import Interpretation3DExporter

class Test3DIntegration(BaseIntegrationTest):
    """Integration tests for 3D projection and export functionality."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_dir = tempfile.mkdtemp()
        cls.crs = QgsCoordinateReferenceSystem("EPSG:32719") # Example projected CRS

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def setUp(self):
        super().setUp()
        # Mock drillhole data
        # Structure: (hole_id, [2D points], [3D points], [3D proj points], [GeologySegments])
        self.segments = [
            GeologySegment(
                unit_name="UnitA",
                geometry=None,
                attributes={"from": 0.0, "to": 10.0},
                points=[(0, 50), (5, 45)],
                points_3d=[(1000, 2000, 50), (1005, 2000, 45)],
                points_3d_projected=[(1001, 2001, 50), (1006, 2001, 45)]
            )
        ]
        self.drillhole_data = [
            (
                "DH1",
                [(0, 50), (10, 40)],
                [(1000, 2000, 50), (1010, 2000, 40)],
                [(1001, 2001, 50), (1011, 2001, 40)],
                self.segments
            )
        ]

    def test_drillhole_trace_3d_export_original(self):
        """Test exporting 3D drillhole traces with original coordinates."""
        output_path = os.path.join(self.test_dir, "trace_original.shp")
        print(f"DEBUG: Exporting to {output_path}")
        exporter = DrillholeTrace3DExporter({})

        data = {
            "drillhole_data": self.drillhole_data,
            "crs": self.crs,
            "use_projected": False
        }

        success = exporter.export(output_path, data)
        self.assertTrue(success, "Exporter returned False")
        self.assertTrue(os.path.exists(output_path), f"File {output_path} does not exist after success")

        # Verify layer
        layer = QgsVectorLayer(output_path, "trace", "ogr")
        self.assertTrue(layer.isValid())
        # Shapefiles often report MultiLineStringZ even for single part geometries
        self.assertIn(layer.wkbType(), [QgsWkbTypes.LineStringZ, QgsWkbTypes.MultiLineStringZ])

        # Check coordinates
        features = list(layer.getFeatures())
        self.assertEqual(len(features), 1)
        geom = features[0].geometry()
        # vertexAt handles both single and multi
        p0 = geom.vertexAt(0)
        self.assertAlmostEqual(p0.x(), 1000.0)
        self.assertAlmostEqual(p0.y(), 2000.0)
        self.assertAlmostEqual(p0.z(), 50.0)

    def test_drillhole_trace_3d_export_projected(self):
        """Test exporting 3D drillhole traces with projected coordinates."""
        output_path = os.path.join(self.test_dir, "trace_projected.shp")
        exporter = DrillholeTrace3DExporter({})

        data = {
            "drillhole_data": self.drillhole_data,
            "crs": self.crs,
            "use_projected": True
        }

        success = exporter.export(output_path, data)
        self.assertTrue(success)

        layer = QgsVectorLayer(output_path, "trace_proj", "ogr")
        self.assertTrue(layer.isValid())
        self.assertIn(layer.wkbType(), [QgsWkbTypes.LineStringZ, QgsWkbTypes.MultiLineStringZ])

        geom = next(layer.getFeatures()).geometry()
        p0 = geom.vertexAt(0)
        self.assertAlmostEqual(p0.x(), 1001.0) # From points_3d_projected
        self.assertAlmostEqual(p0.y(), 2001.0)
        self.assertAlmostEqual(p0.z(), 50.0)

    def test_drillhole_interval_3d_export(self):
        """Test exporting 3D drillhole intervals."""
        output_path = os.path.join(self.test_dir, "intervals.shp")
        exporter = DrillholeInterval3DExporter({})

        data = {
            "drillhole_data": self.drillhole_data,
            "crs": self.crs,
            "use_projected": False
        }

        success = exporter.export(output_path, data)
        self.assertTrue(success)

        layer = QgsVectorLayer(output_path, "intervals", "ogr")
        self.assertTrue(layer.isValid())
        self.assertIn(layer.wkbType(), [QgsWkbTypes.LineStringZ, QgsWkbTypes.MultiLineStringZ])

        features = list(layer.getFeatures())
        self.assertEqual(len(features), 1)
        feat = features[0]
        self.assertEqual(feat["unit"], "UnitA")
        self.assertEqual(feat["from_depth"], 0.0)
        self.assertEqual(feat["to_depth"], 10.0)

        p1 = feat.geometry().vertexAt(1)
        self.assertAlmostEqual(p1.x(), 1005.0)
        self.assertAlmostEqual(p1.y(), 2000.0)
        self.assertAlmostEqual(p1.z(), 45.0)

    def test_interpretation_3d_export_polygonz(self):
        """Test exporting interpretations to PolygonZ."""
        output_path = os.path.join(self.test_dir, "interp_3d.shp")
        exporter = Interpretation3DExporter({})

        # Azimuth 0 (East), origin at 1000, 2000
        line_geom = QgsGeometry.fromPolylineXY(
            [QgsPointXY(1000, 2000), QgsPointXY(1100, 2000)]
        )

        interp = InterpretationPolygon(
            "p1", "UnitB", "L",
            [(10, 100), (20, 100), (20, 110), (10, 110), (10, 100)]
        )

        data = {
            "section_line": line_geom,
            "interpretations": [interp],
            "crs": self.crs
        }

        success = exporter.export(output_path, data)
        self.assertTrue(success, "Interpretation exporter returned False")
        self.assertTrue(os.path.exists(output_path))

        # Verify QML existence
        qml_path = output_path.replace(".shp", ".qml")
        self.assertTrue(os.path.exists(qml_path), f"QML style {qml_path} was not generated")

        layer = QgsVectorLayer(output_path, "interp", "ogr")
        self.assertTrue(layer.isValid(), "Layer is not valid")
        # PolygonZ = 1003, MultiPolygonZ = 1006
        self.assertIn(layer.wkbType(), [QgsWkbTypes.PolygonZ, QgsWkbTypes.MultiPolygonZ])

        feat = next(layer.getFeatures())
        self.assertEqual(feat["name"], "UnitB")

        # Check first vertex: dist=10, el=100 -> (1010, 2000, 100)
        p0 = feat.geometry().vertexAt(0)
        self.assertAlmostEqual(p0.x(), 1010.0)
        self.assertAlmostEqual(p0.y(), 2000.0)
        self.assertAlmostEqual(p0.z(), 100.0)
