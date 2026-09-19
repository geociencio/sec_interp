import unittest
from unittest.mock import MagicMock

from qgis.core import QgsCoordinateReferenceSystem, QgsFeature, QgsGeometry, QgsPointXY

from sec_interp.gui.adapters.drillhole_extractor import DrillholeExtractor


class TestDrillholeExtractorOptionalLayer(unittest.TestCase):
    """Test that the DrillholeExtractor tolerates an optional collar layer."""

    def setUp(self):
        self.extractor = DrillholeExtractor()

    def test_extract_context_without_collar_layer(self):
        """extract_context should handle a missing collar layer gracefully."""
        mock_line = MagicMock()
        mock_line.crs.return_value = QgsCoordinateReferenceSystem("EPSG:32719")
        line_feat = QgsFeature()
        line_feat.setGeometry(
            QgsGeometry.fromPolylineXY([QgsPointXY(0, 0), QgsPointXY(100, 0)])
        )
        mock_line.getFeatures.return_value = iter([line_feat])

        context = self.extractor.extract_context(
            line_layer=mock_line,
            buffer_width=100.0,
            collar_layer=None,
            collar_id_field="HoleID",
            use_geometry=True,
            collar_x_field=None,
            collar_y_field=None,
            collar_z_field=None,
            collar_depth_field=None,
            survey_layer=None,
            survey_fields={},
            interval_layer=None,
            interval_fields={},
        )

        self.assertIsNotNone(context)
        self.assertEqual(context.collar_data, [])


if __name__ == "__main__":
    unittest.main()
