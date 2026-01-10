"""Tests for main_dialog_validation.py - DialogValidator class."""

import unittest
from unittest.mock import MagicMock, patch

# BaseTestCase MUST be imported before qgis.core to setup mocks correctly
from tests.base_test import BaseTestCase

from sec_interp.gui.main_dialog_validation import DialogValidator
from sec_interp.core.exceptions import ValidationError


class TestDialogValidator(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        # Create mock dialog with all required page attributes
        self.mock_dialog = MagicMock()

        # Mock Data Aggregator
        self.mock_dialog.data_aggregator.get_validation_params.return_value = (
            MagicMock()
        )

        self.validator = DialogValidator(self.mock_dialog)

    def test_validate_inputs_success(self):
        """Test successful validation."""
        with patch(
            "sec_interp.gui.main_dialog_validation.ProjectValidator.validate_all"
        ) as mock_validate:
            mock_validate.return_value = None  # No exception = success

            success, message = self.validator.validate_inputs()

            self.assertTrue(success)
            self.assertEqual(message, "")
            mock_validate.assert_called_once()

    def test_validate_inputs_failure(self):
        """Test validation failure."""
        with patch(
            "sec_interp.gui.main_dialog_validation.ProjectValidator.validate_all"
        ) as mock_validate:
            mock_validate.side_effect = ValidationError("Invalid raster layer")

            success, message = self.validator.validate_inputs()

            self.assertFalse(success)
            self.assertEqual(message, "Invalid raster layer")
            mock_validate.assert_called_once()

    def test_validate_preview_requirements_success(self):
        """Test successful preview validation."""
        with patch(
            "sec_interp.gui.main_dialog_validation.ProjectValidator.validate_preview_requirements"
        ) as mock_validate:
            mock_validate.return_value = None

            success, message = self.validator.validate_preview_requirements()

            self.assertTrue(success)
            self.assertEqual(message, "")
            mock_validate.assert_called_once()

    def test_validate_preview_requirements_failure(self):
        """Test preview validation failure."""
        with patch(
            "sec_interp.gui.main_dialog_validation.ProjectValidator.validate_preview_requirements"
        ) as mock_validate:
            mock_validate.side_effect = ValidationError("Missing DEM layer")

            success, message = self.validator.validate_preview_requirements()

            self.assertFalse(success)
            self.assertEqual(message, "Missing DEM layer")
            mock_validate.assert_called_once()
