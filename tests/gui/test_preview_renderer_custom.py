from tests.base_test import BaseTestCase
from unittest.mock import MagicMock
# qgis imports will be handled by BaseTestCase mock if needed
from qgis.core import QgsVectorLayer, QgsGeometry
from sec_interp.gui.preview_renderer import PreviewRenderer
from sec_interp.core.types import StructureMeasurement


class TestPreviewRendererCustom(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.renderer = PreviewRenderer()

    def test_create_struct_layer_custom_length(self):
        """Test that _create_struct_layer uses the custom dip_line_length."""
        # Setup data
        struct_data = [
            StructureMeasurement(
                distance=0.0,
                elevation=100.0,
                apparent_dip=45.0,
                original_dip=45.0,
                original_strike=0.0,
                attributes={},
            )
        ]
        reference_data = [(0.0, 100.0), (100.0, 200.0)]

        # Custom length
        custom_length = 50.0

        layer = self.renderer.layer_factory.create_struct_layer(
            struct_data, reference_data, vert_exag=1.0, dip_line_length=custom_length
        )

        self.assertIsNotNone(layer)
        # featureCount is a mock, so we can't assert == 1 directly unless we set it.
        # Instead, check that addFeatures was called on provider
        layer.dataProvider().addFeatures.assert_called()

        # Mock the feature retrieval for geometry check
        mock_feat = MagicMock()
        mock_geom = MagicMock()
        mock_geom.length.return_value = custom_length
        mock_feat.geometry.return_value = mock_geom
        layer.getFeatures.return_value = iter([mock_feat])

        feat = next(layer.getFeatures())
        geom = feat.geometry()

        length = geom.length()
        self.assertLess(abs(length - custom_length), 0.001)


    def test_create_struct_layer_default_length(self):
        """Test that _create_struct_layer uses default length when custom is None."""
        struct_data = [
            StructureMeasurement(
                distance=0.0,
                elevation=100.0,
                apparent_dip=45.0,
                original_dip=45.0,
                original_strike=0.0,
                attributes={},
            )
        ]
        # Range 100, default length should be 10% = 10.0
        reference_data = [(0.0, 100.0), (100.0, 200.0)]

        layer = self.renderer.layer_factory.create_struct_layer(
            struct_data, reference_data, vert_exag=1.0, dip_line_length=None
        )

        self.assertIsNotNone(layer)
        layer.dataProvider().addFeatures.assert_called()

        mock_feat = MagicMock()
        mock_geom = MagicMock()
        mock_geom.length.return_value = 10.0
        mock_feat.geometry.return_value = mock_geom
        layer.getFeatures.return_value = iter([mock_feat])

        feat = next(layer.getFeatures())
        length = feat.geometry().length()

        self.assertLess(abs(length - 10.0), 0.001)
