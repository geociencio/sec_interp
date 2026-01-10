"""Integration tests for export workflow."""

import math
from qgis.core import QgsGeometry, QgsPointXY
from tests.integration.base_integration import BaseIntegrationTest
from sec_interp.core.types import InterpretationPolygon
from sec_interp.exporters.interpretation_3d_exporter import Interpretation3DExporter


class TestExportWorkflow(BaseIntegrationTest):
    """Integration test for 3D export workflow."""

    def test_3d_projection_logic(self):
        """Test internal projection logic from 2D section to 3D space."""
        exporter = Interpretation3DExporter({})

        # 1. Horizontal line pointing East (Azimuth 0)
        line_geom = QgsGeometry.fromPolylineXY(
            [QgsPointXY(1000, 2000), QgsPointXY(1100, 2000)]
        )
        origin_x, origin_y, azimuth = exporter._calculate_section_geometry(line_geom)

        self.assertAlmostEqual(math.degrees(azimuth), 0.0)

        # Point at dist=10, elev=50 -> (1010, 2000, 50)
        interp = InterpretationPolygon(
            "p1", "Unit", "L", [(10, 50), (20, 50), (20, 60), (10, 60), (10, 50)]
        )

        fields, keys = exporter._prepare_fields([interp])
        features = exporter._collect_projected_features(
            [interp], fields, keys, origin_x, origin_y, azimuth
        )

        self.assertEqual(len(features), 1)
        geom = features[0].geometry()
        p = geom.vertexAt(0)
        self.assertAlmostEqual(p.x(), 1010.0)
        self.assertAlmostEqual(p.y(), 2000.0)
        self.assertAlmostEqual(p.z(), 50.0)

    def test_3d_projection_north(self):
        """Test projection for a line pointing North (Azimuth 90)."""
        exporter = Interpretation3DExporter({})

        # Line pointing North
        line_geom = QgsGeometry.fromPolylineXY(
            [QgsPointXY(1000, 2000), QgsPointXY(1000, 2100)]
        )
        origin_x, origin_y, azimuth = exporter._calculate_section_geometry(line_geom)

        self.assertAlmostEqual(math.degrees(azimuth), 90.0)

        # Point at dist=10, elev=50 -> (1000, 2010, 50)
        interp = InterpretationPolygon(
            "p2", "Unit", "L", [(10, 50), (20, 50), (20, 60), (10, 60), (10, 50)]
        )

        fields, keys = exporter._prepare_fields([interp])
        features = exporter._collect_projected_features(
            [interp], fields, keys, origin_x, origin_y, azimuth
        )

        p = features[0].geometry().vertexAt(0)
        self.assertAlmostEqual(p.x(), 1000.0)
        self.assertAlmostEqual(p.y(), 2010.0)
        self.assertAlmostEqual(p.z(), 50.0)
