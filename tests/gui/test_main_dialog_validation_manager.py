"""Tests for main_dialog_validation_manager.py - DialogValidationManager class."""

import unittest
from unittest.mock import MagicMock, patch

# BaseTestCase MUST be imported before qgis.core to setup mocks correctly
from tests.base_test import BaseTestCase

from sec_interp.gui.main_dialog_validation_manager import DialogValidationManager
from sec_interp.core.exceptions import ValidationError


class TestDialogValidationManager(BaseTestCase):

    def setUp(self):
        """Set up test fixtures."""
        # Create mock dialog with all required page attributes
        self.mock_dialog = MagicMock()
        # Mock translate function
        self.mock_dialog.tr = lambda x: x

        # Mock Data Aggregator as it's used in ValidationManager
        self.mock_params = MagicMock()
        self.mock_dialog.data_aggregator.get_validation_params.return_value = (
            self.mock_params
        )

        self.manager = DialogValidationManager(self.mock_dialog)

    def test_validate_inputs_success(self):
        """Test successful validation."""
        with patch(
            "sec_interp.gui.main_dialog_validation_manager.ProjectValidator.validate_all"
        ) as mock_validate:
            mock_validate.return_value = True

            success, message = self.manager.validate_inputs()

            self.assertTrue(success)
            self.assertEqual(message, "")
            mock_validate.assert_called_once_with(self.mock_params)

    def test_validate_inputs_failure(self):
        """Test validation failure."""
        with patch(
            "sec_interp.gui.main_dialog_validation_manager.ProjectValidator.validate_all"
        ) as mock_validate:
            mock_validate.side_effect = ValidationError("Invalid raster layer")

            success, message = self.manager.validate_inputs()

            self.assertFalse(success)
            self.assertEqual(message, "Invalid raster layer")

    def test_is_section_valid(self):
        """Test declarative section validation."""
        # Setup mock params
        self.mock_params.raster_layer = "SomeLayer"
        self.mock_params.line_layer = None

        self.assertTrue(self.manager.is_section_valid("dem"))
        self.assertFalse(self.manager.is_section_valid("section"))

    def test_can_preview(self):
        """Test can_preview logic."""
        self.mock_params.raster_layer = "SomeLayer"
        self.mock_params.line_layer = "LineLayer"
        self.assertTrue(self.manager.can_preview())

        self.mock_params.raster_layer = None
        self.assertFalse(self.manager.can_preview())

    def test_get_section_error(self):
        """Test error message retrieval."""
        self.mock_params.raster_layer = None
        error = self.manager.get_section_error("dem")
        self.assertEqual(error, "Raster DEM layer is required")

        self.mock_params.raster_layer = "Layer"
        error = self.manager.get_section_error("dem")
        self.assertEqual(error, "")

    def test_validate_preview_requirements_success(self):
        """Test successful preview validation."""
        with patch(
            "sec_interp.gui.main_dialog_validation_manager.ProjectValidator.validate_preview_requirements"
        ) as mock_validate:
            mock_validate.return_value = True

            success, message = self.manager.validate_preview_requirements()

            self.assertTrue(success)
            self.assertEqual(message, "")

    def test_validate_preview_requirements_failure(self):
        """Test preview validation failure."""
        with patch(
            "sec_interp.gui.main_dialog_validation_manager.ProjectValidator.validate_preview_requirements"
        ) as mock_validate:
            mock_validate.side_effect = ValidationError("Missing DEM layer")

            success, message = self.manager.validate_preview_requirements()

            self.assertFalse(success)
            self.assertEqual(message, "Missing DEM layer")
