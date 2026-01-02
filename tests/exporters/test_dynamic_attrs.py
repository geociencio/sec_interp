"""Tests for dynamic attributes in interpretation exporters."""

import unittest
from unittest.mock import MagicMock
from pathlib import Path
from qgis.core import QgsApplication, QgsFields
from qgis.PyQt.QtCore import QVariant
from sec_interp.exporters.interpretation_exporters import Interpretation2DExporter
from sec_interp.core.types import InterpretationPolygon

class TestDynamicAttributes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qgs = QgsApplication([], False)
        cls.qgs.initQgis()

    @classmethod
    def tearDownClass(cls):
        cls.qgs.exitQgis()

    def test_2d_exporter_dynamic_fields(self):
        """Verify that 2D exporter creates fields for custom attributes."""
        exporter = Interpretation2DExporter({})

        # Create interpretation with custom attributes
        interp = InterpretationPolygon(
            id="1",
            name="Test",
            type="Lithology",
            vertices_2d=[(0, 0), (10, 0), (10, 10), (0, 0)],
            attributes={"Confianza": "Alta", "Comentario": "Validado"},
            color="#FF0000",
            created_at="2024-01-01"
        )

        # Mock writeAsVectorFormatV3 to avoid file I/O errors in headless env
        import qgis.core
        original_write = qgis.core.QgsVectorFileWriter.writeAsVectorFormatV3
        qgis.core.QgsVectorFileWriter.writeAsVectorFormatV3 = MagicMock(return_value=(0, "", "", ""))

        try:
            output_path = Path("/tmp/test_dynamic.shp")
            exporter.export(output_path, {"interpretations": [interp]})

            # Check if fields were correctly generated in the internal layer
            # We need to capture the layer passed to writeAsVectorFormatV3
            call_args = qgis.core.QgsVectorFileWriter.writeAsVectorFormatV3.call_args
            layer = call_args[0][0]

            fields = layer.fields()
            field_names = [f.name() for f in fields]

            self.assertIn("Confianza", field_names)
            self.assertIn("Comentario", field_names)
            self.assertIn("id", field_names)

            # Check values in first feature
            feat = next(layer.getFeatures())
            self.assertEqual(feat["Confianza"], "Alta")
            self.assertEqual(feat["Comentario"], "Validado")

        finally:
            qgis.core.QgsVectorFileWriter.writeAsVectorFormatV3 = original_write

if __name__ == "__main__":
    unittest.main()
