# -*- coding: utf-8 -*-
"""
Integration tests for real vector drivers (GeoPackage, DXF).
Verifies that files are actually created and can be read back.
"""

import os
from pathlib import Path
from qgis.core import (
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
    QgsWkbTypes,
    QgsFields,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsPointXY
)
from qgis.PyQt.QtCore import QVariant
from tests.base_test import BaseTestCase
from sec_interp.exporters.vector_exporter import VectorExporter


class TestVectorDriversIntegration(BaseTestCase):
    """Integration tests for GPKG and DXF drivers."""

    def setUp(self):
        super().setUp()
        self.crs = QgsCoordinateReferenceSystem("EPSG:4326")
        self.exporter = VectorExporter({
            "crs": self.crs,
            "geometry_type": QgsWkbTypes.Point
        })

        # Create some real test data with geometries
        self.test_features = []
        for i in range(3):
            feat = {
                "geometry": QgsGeometry.fromPointXY(QgsPointXY(i, i)),
                "attributes": {"id": i, "label": f"Point {i}"}
            }
            self.test_features.append(feat)

    def test_geopackage_creation(self):
        """Verify that a real .gpkg file is created and readable."""
        output_path = self.output_dir / "test_integration.gpkg"
        layer_name = "test_layer"

        # Export
        result = self.exporter.export(
            output_path,
            self.test_features,
            layer_name=layer_name
        )

        self.assertTrue(result)
        self.assertTrue(output_path.exists())
        self.assertGreater(output_path.stat().st_size, 0)

        # Verify with QgsVectorLayer
        uri = f"{output_path}|layername={layer_name}"
        layer = QgsVectorLayer(uri, "verify", "ogr")

        self.assertTrue(layer.isValid(), f"Layer {uri} is not valid")
        self.assertEqual(layer.featureCount(), 3)
        self.assertEqual(layer.crs().authid(), "EPSG:4326")

    def test_dxF_creation(self):
        """Verify that a real .dxf file is created and has content."""
        output_path = self.output_dir / "test_integration.dxf"

        # Export
        result = self.exporter.export(
            output_path,
            self.test_features
        )

        self.assertTrue(result)
        self.assertTrue(output_path.exists())
        self.assertGreater(output_path.stat().st_size, 0)

        # DXF is harder to verify with QgsVectorLayer (unreliable)
        # But we can at least check it contains some DXF headers
        with open(output_path, 'r', encoding='ascii', errors='ignore') as f:
            content = f.read(1024)
            self.assertIn("SECTION", content)
            self.assertIn("HEADER", content)

    def test_shapefile_creation(self):
        """Verify that a real .shp (and friends) are created."""
        output_path = self.output_dir / "test_integration.shp"

        # Export
        result = self.exporter.export(
            output_path,
            self.test_features
        )

        self.assertTrue(result)
        self.assertTrue(output_path.exists())
        self.assertTrue(output_path.with_suffix(".shx").exists())
        self.assertTrue(output_path.with_suffix(".dbf").exists())

        # Verify with QgsVectorLayer
        layer = QgsVectorLayer(str(output_path), "verify", "ogr")
        self.assertTrue(layer.isValid())
        self.assertEqual(layer.featureCount(), 3)
