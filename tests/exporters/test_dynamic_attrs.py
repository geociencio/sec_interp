import unittest
from pathlib import Path
from unittest.mock import MagicMock
from tests.base_test import BaseTestCase
from qgis.core import QgsFields
from sec_interp.exporters.interpretation_exporters import Interpretation2DExporter
from sec_interp.core.domain import InterpretationPolygon


class TestDynamicAttributes(BaseTestCase):

    def test_2d_exporter_dynamic_fields(self):
        """Verify that 2D exporter creates fields for custom attributes."""
        super().setUp()
        exporter = Interpretation2DExporter({})

        # Create interpretation with custom attributes
        interp = InterpretationPolygon(
            id="1",
            name="Test",
            type="Lithology",
            vertices_2d=[(0, 0), (10, 0), (10, 10), (0, 0)],
            attributes={"Confianza": "Alta", "Comentario": "Validado"},
            color="#FF0000",
            created_at="2024-01-01",
        )

        output_path = Path("/tmp/test_dynamic.shp")

        from unittest.mock import patch

        with patch.object(exporter, "_write_to_file", return_value=True) as mock_write:
            exporter.export(output_path, {"interpretations": [interp]})

            # Check if fields were correctly generated in the internal layer
            call_args = mock_write.call_args
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


if __name__ == "__main__":
    unittest.main()
