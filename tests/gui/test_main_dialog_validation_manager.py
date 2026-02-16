"""Tests for main_dialog_validation_manager.py - InputManager class."""

import unittest
from unittest.mock import MagicMock, patch

# BaseTestCase MUST be imported before qgis.core to setup mocks correctly
from tests.base_test import BaseTestCase

from sec_interp.gui.dialog_input_manager import InputManager
from sec_interp.core.exceptions import ValidationError


class TestInputManager(BaseTestCase):

    def setUp(self):
        """Set up test fixtures."""
        # Create mock dialog with all required page attributes
        self.mock_dialog = MagicMock()
        # Mock translate function
        self.mock_dialog.tr = lambda x: x

        # Mock pages and their data
        self.mock_dialog.page_dem = MagicMock()
        self.mock_dialog.page_section = MagicMock()
        self.mock_dialog.page_geology = MagicMock()
        self.mock_dialog.page_struct = MagicMock()
        self.mock_dialog.page_drillhole = MagicMock()
        self.mock_dialog.output_widget = MagicMock()

        # Default empty data
        self.default_data = {
            "raster_layer": None,
            "selected_band": 1,
            "scale": 1.0,
            "vertexag": 1.0,
            "crossline_layer": None,
            "buffer_distance": 0.0,
            "outcrop_layer": None,
            "outcrop_name_field": None,
            "structural_layer": None,
            "dip_field": None,
            "strike_field": None,
            "dip_scale_factor": 1.0,
            "collar_layer": None,
            "collar_id": None,
            "use_geometry": True,
            "collar_x": None,
            "collar_y": None,
            "collar_z": None,
            "collar_depth": None,
            "survey_layer": None,
            "survey_id": None,
            "survey_depth": None,
            "survey_azim": None,
            "survey_incl": None,
            "interval_layer": None,
            "interval_id": None,
            "interval_from": None,
            "interval_to": None,
            "interval_lith": None,
        }

        self.mock_dialog.page_dem.get_data.return_value = self.default_data.copy()
        self.mock_dialog.page_section.get_data.return_value = self.default_data.copy()
        self.mock_dialog.page_geology.get_data.return_value = self.default_data.copy()
        self.mock_dialog.page_struct.get_data.return_value = self.default_data.copy()
        self.mock_dialog.page_drillhole.get_data.return_value = self.default_data.copy()
        self.mock_dialog.output_widget.filePath.return_value = ""

        self.manager = InputManager(self.mock_dialog)

    def test_validate_inputs_success(self):
        """Test successful validation."""
        with patch(
            "sec_interp.gui.dialog_input_manager.ProjectValidator.validate_all"
        ) as mock_validate:
            mock_validate.return_value = True

            success, message = self.manager.validate_inputs()

            self.assertTrue(success)
            self.assertEqual(message, "")
            # Verify call with some ANY to avoid strict object identity check
            from sec_interp.core.validation.project_validator import ValidationParams

            mock_validate.assert_called_once()
            args, _ = mock_validate.call_args
            self.assertIsInstance(args[0], ValidationParams)

    def test_validate_inputs_failure(self):
        """Test validation failure."""
        with patch(
            "sec_interp.gui.dialog_input_manager.ProjectValidator.validate_all"
        ) as mock_validate:
            mock_validate.side_effect = ValidationError("Invalid raster layer")

            success, message = self.manager.validate_inputs()

            self.assertFalse(success)
            self.assertEqual(message, "Invalid raster layer")

    def test_is_section_valid(self):
        """Test declarative section validation."""
        # Setup mock page data
        dem_data = self.default_data.copy()
        dem_data.update({"raster_layer": "SomeLayer"})
        self.mock_dialog.page_dem.get_data.return_value = dem_data

        sect_data = self.default_data.copy()
        sect_data.update({"crossline_layer": None})
        self.mock_dialog.page_section.get_data.return_value = sect_data

        self.assertTrue(self.manager.is_section_valid("dem"))
        self.assertFalse(self.manager.is_section_valid("section"))

    def test_can_preview(self):
        """Test can_preview logic."""
        # Case 1: Valid
        dem_data = self.default_data.copy()
        dem_data.update({"raster_layer": "SomeLayer"})
        self.mock_dialog.page_dem.get_data.return_value = dem_data

        sect_data = self.default_data.copy()
        sect_data.update({"crossline_layer": "LineLayer"})
        self.mock_dialog.page_section.get_data.return_value = sect_data

        self.assertTrue(self.manager.can_preview())

        # Case 2: Invalid
        dem_data_invalid = self.default_data.copy()
        dem_data_invalid.update({"raster_layer": None})
        self.mock_dialog.page_dem.get_data.return_value = dem_data_invalid

        sect_data_invalid = self.default_data.copy()
        sect_data_invalid.update({"crossline_layer": None})
        self.mock_dialog.page_section.get_data.return_value = sect_data_invalid

        self.assertFalse(self.manager.can_preview())

    def test_get_section_error(self):
        """Test error message retrieval."""
        # Case 1: Error
        dem_data = self.default_data.copy()
        dem_data.update({"raster_layer": None})
        self.mock_dialog.page_dem.get_data.return_value = dem_data

        error = self.manager.get_section_error("dem")
        self.assertEqual(error, "Raster DEM layer is required")

        # Case 2: No Error
        dem_data_valid = self.default_data.copy()
        dem_data_valid.update({"raster_layer": "Layer"})
        self.mock_dialog.page_dem.get_data.return_value = dem_data_valid

        error = self.manager.get_section_error("dem")
        self.assertEqual(error, "")

    def test_validate_preview_requirements_success(self):
        """Test successful preview validation."""
        with patch(
            "sec_interp.gui.dialog_input_manager.ProjectValidator.validate_preview_requirements"
        ) as mock_validate:
            mock_validate.return_value = True

            success, message = self.manager.validate_preview_requirements()

            self.assertTrue(success)
            self.assertEqual(message, "")

    def test_validate_preview_requirements_failure(self):
        """Test preview validation failure."""
        with patch(
            "sec_interp.gui.dialog_input_manager.ProjectValidator.validate_preview_requirements"
        ) as mock_validate:
            mock_validate.side_effect = ValidationError("Missing DEM layer")

            success, message = self.manager.validate_preview_requirements()

            self.assertFalse(success)
            self.assertEqual(message, "Missing DEM layer")
