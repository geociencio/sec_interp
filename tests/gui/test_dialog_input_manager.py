"""Tests for InputManager - Consolidation of Data Aggregator and Validation Manager."""

import unittest
from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from sec_interp.gui.dialog_input_manager import InputManager
from sec_interp.core.exceptions import ValidationError


class TestInputManager(BaseTestCase):
    """Tests for the InputManager class."""

    def setUp(self):
        super().setUp()
        self.mock_dialog = MagicMock()
        self.mock_dialog.tr = lambda x: x

        # Mock pages
        self.mock_dialog.page_section = MagicMock()
        self.mock_dialog.page_dem = MagicMock()
        self.mock_dialog.page_geology = MagicMock()
        self.mock_dialog.page_drillhole = MagicMock()
        self.mock_dialog.page_struct = MagicMock()
        self.mock_dialog.page_interpretation = MagicMock()
        self.mock_dialog.output_widget = MagicMock()

        self.manager = InputManager(self.mock_dialog)

    def test_get_all_values_collects_from_all_pages(self):
        """Verify that get_all_values calls gathering methods on all pages."""
        # Setup returns for the mocked pages to avoid KeyErrors
        empty_data = MagicMock(return_value={})
        for page in [
            "page_section",
            "page_dem",
            "page_geology",
            "page_drillhole",
            "page_struct",
        ]:
            getattr(self.mock_dialog, page).get_data.return_value = {}

        # Specific keys needed for Dict packing
        self.mock_dialog.page_dem.get_data.return_value = {
            "raster_layer": None,
            "selected_band": 1,
            "scale": 1,
            "vertexag": 1,
        }
        self.mock_dialog.page_section.get_data.return_value = {
            "crossline_layer": None,
            "buffer_distance": 50,
        }
        self.mock_dialog.page_geology.get_data.return_value = {
            "outcrop_layer": None,
            "outcrop_name_field": "",
        }
        self.mock_dialog.page_struct.get_data.return_value = {
            "structural_layer": None,
            "dip_field": "",
            "strike_field": "",
            "dip_scale_factor": 1,
        }
        self.mock_dialog.page_drillhole.get_data.return_value = {
            "collar_layer": None,
            "collar_id": "",
            "use_geometry": True,
            "collar_x": "",
            "collar_y": "",
            "collar_z": "",
            "collar_depth": "",
            "survey_layer": None,
            "survey_id": "",
            "survey_depth": "",
            "survey_azim": "",
            "survey_incl": "",
            "interval_layer": None,
            "interval_id": "",
            "interval_from": "",
            "interval_to": "",
            "interval_lith": "",
        }

        self.manager.get_all_values()

        self.mock_dialog.page_section.get_data.assert_called_once()
        self.mock_dialog.page_dem.get_data.assert_called_once()
        self.mock_dialog.page_geology.get_data.assert_called_once()
        self.mock_dialog.page_drillhole.get_data.assert_called_once()
        self.mock_dialog.page_struct.get_data.assert_called_once()

    @patch("sec_interp.gui.dialog_input_manager.ProjectValidator.validate_all")
    def test_validate_inputs_success(self, mock_validate):
        """Test successful validation orquestration."""
        mock_validate.return_value = True

        success, message = self.manager.validate_inputs()

        self.assertTrue(success)
        self.assertEqual(message, "")
        mock_validate.assert_called_once()

    @patch("sec_interp.gui.dialog_input_manager.ProjectValidator.validate_all")
    def test_validate_inputs_failure(self, mock_validate):
        """Test validation failure handling."""
        mock_validate.side_effect = ValidationError("Test Error")

        success, message = self.manager.validate_inputs()

        self.assertFalse(success)
        self.assertEqual(message, "Test Error")

    def test_is_section_valid_logic(self):
        """Test the logic for individual section validity."""
        # Mock what get_validation_params returns
        mock_params = MagicMock()
        mock_params.raster_layer = "SomeLayer"
        mock_params.line_layer = None

        with patch.object(
            self.manager, "get_validation_params", return_value=mock_params
        ):
            self.assertTrue(self.manager.is_section_valid("dem"))
            self.assertFalse(self.manager.is_section_valid("section"))

    def test_get_section_error_messages(self):
        """Test that correct error messages are returned for missing inputs."""
        mock_params = MagicMock()
        mock_params.raster_layer = None

        with patch.object(
            self.manager, "get_validation_params", return_value=mock_params
        ):
            error = self.manager.get_section_error("dem")
            self.assertEqual(error, "Raster DEM layer is required")


if __name__ == "__main__":
    unittest.main()
