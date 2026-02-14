import unittest
from unittest.mock import MagicMock, patch
from sec_interp.core.services.drillhole_service import DrillholeService
from sec_interp.core.exceptions import ValidationError


class TestDrillholeServiceOptionalLayer(unittest.TestCase):
    def setUp(self):
        self.service = DrillholeService()

    def test_prepare_task_input_without_collar_layer(self):
        """Test that prepare_task_input handles missing collar_layer gracefully or raises correct error."""

        # Create mocks
        mock_line = MagicMock()
        mock_line.isValid.return_value = True
        mock_feat = MagicMock()
        mock_geom = MagicMock()
        mock_geom.isMultipart.return_value = False  # Force polyline branch
        mock_geom.asPolyline.return_value = [MagicMock(), MagicMock()]
        mock_geom.vertexAt.return_value = MagicMock()

        # Mock point behavior for azimuth
        mock_start_pt = MagicMock()
        mock_start_pt.azimuth.return_value = 45.0  # Safe float for comparison
        mock_geom.asPolyline.return_value = [mock_start_pt, MagicMock()]

        mock_feat.geometry.return_value = mock_geom
        mock_line.getFeatures.return_value = iter([mock_feat])

        # If collar_layer is None, we expect validation to theoretically handle it
        # OR fail gracefully if it's mandatory but not provided.
        # However, purely optional layers should not crash with AttributeError.

        # This SHOULD fail with AttributeError: 'NoneType' object has no attribute 'fields'
        # if the bug is present.
        self.service.prepare_task_input(
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


if __name__ == "__main__":
    unittest.main()
