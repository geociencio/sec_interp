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
        default_data = {
            "raster_layer": None, "selected_band": 1, "scale": 1.0, "vertexag": 1.0,
            "crossline_layer": None, "buffer_distance": 0.0,
            "outcrop_layer": None, "outcrop_name_field": None,
            "structural_layer": None, "dip_field": None, "strike_field": None, "dip_scale_factor": 1.0,
            "collar_layer": None, "collar_id": None, "use_geometry": True,
            "collar_x": None, "collar_y": None, "collar_z": None, "collar_depth": None,
            "survey_layer": None, "survey_id": None, "survey_depth": None, "survey_azim": None, "survey_incl": None,
            "interval_layer": None, "interval_id": None, "interval_from": None, "interval_to": None, "interval_lith": None
        }

        self.mock_dialog.page_dem.get_data.return_value = default_data
        self.mock_dialog.page_section.get_data.return_value = default_data
        self.mock_dialog.page_geology.get_data.return_value = default_data
        self.mock_dialog.page_struct.get_data.return_value = default_data
        self.mock_dialog.page_drillhole.get_data.return_value = default_data
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
        self.mock_dialog.page_dem.get_data.return_value = {
            "raster_layer": "SomeLayer",
            "selected_band": 1,
        }
        self.mock_dialog.page_section.get_data.return_value = {"crossline_layer": None}

        self.assertTrue(self.manager.is_section_valid("dem"))
        self.assertFalse(self.manager.is_section_valid("section"))

    def test_can_preview(self):
        """Test can_preview logic."""
        self.mock_dialog.page_dem.get_data.return_value = {
            "raster_layer": "SomeLayer",
            "selected_band": 1,
        }
        self.mock_dialog.page_section.get_data.return_value = {
            "crossline_layer": "LineLayer"
        }
        self.assertTrue(self.manager.can_preview())

        self.mock_dialog.page_dem.get_data.return_value = {
            "raster_layer": None,
            "selected_band": 1,
        }
        self.mock_dialog.page_section.get_data.return_value = {
            "crossline_layer": None
        }
        self.assertFalse(self.manager.can_preview())

    def test_get_section_error(self):
        """Test error message retrieval."""
        self.mock_dialog.page_dem.get_data.return_value = {
            "raster_layer": None,
            "selected_band": 1,
        }
        error = self.manager.get_section_error("dem")
        self.assertEqual(error, "Raster DEM layer is required")

        self.mock_dialog.page_dem.get_data.return_value = {
            "raster_layer": "Layer",
            "selected_band": 1,
        }
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
