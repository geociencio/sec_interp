"""Tests for interpretation export functionality."""

import unittest
from unittest.mock import MagicMock, patch
from qgis.core import QgsVectorLayer, QgsPointXY
from sec_interp.gui.preview_renderer import PreviewRenderer
from sec_interp.core.domain import InterpretationPolygon


class TestInterpretationExport(unittest.TestCase):
    def setUp(self):
        self.mock_canvas = MagicMock()
        self.renderer = PreviewRenderer(self.mock_canvas)

        # Mock ProfileData (topo) which is required for render
        self.mock_topo = [(0, 100), (500, 120)]

    def test_interpretation_layer_included_in_render(self):
        """Verify that an interpretation layer is created and included in final layers list."""
        interp = InterpretationPolygon(
            id="test-1",
            name="Test Unit",
            type="lithology",
            vertices_2d=[(10, 110), (50, 115), (100, 110)],
            attributes={},
            color="#FF0000",
        )

        # Render with interpretations
        _, layers = self.renderer.render(topo_data=self.mock_topo, interp_data=[interp])

        # Check if any layer is the Interpretations layer
        interp_layer = next((l for l in layers if l.name() == "Interpretations"), None)

        self.assertIsNotNone(
            interp_layer, "Interpretations layer missing from render output"
        )
        self.assertIsInstance(interp_layer, QgsVectorLayer)
        self.assertEqual(interp_layer.featureCount(), 1)

        # Verify geometry
        feat = next(interp_layer.getFeatures())
        self.assertTrue(
            feat.geometry().isMultipart() or feat.geometry().type() == 2
        )  # Polygon


if __name__ == "__main__":
    unittest.main()
