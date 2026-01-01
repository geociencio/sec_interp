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

        # Mock DEM page
        self.mock_dialog.page_dem.raster_combo.currentLayer.return_value = MagicMock()
        self.mock_dialog.page_dem.band_combo.currentBand.return_value = 1
        self.mock_dialog.page_dem.scale_spin.value.return_value = 1000.0
        self.mock_dialog.page_dem.vertexag_spin.value.return_value = 2.0

        # Mock Section page
        self.mock_dialog.page_section.line_combo.currentLayer.return_value = MagicMock()
        self.mock_dialog.page_section.buffer_spin.value.return_value = 50.0

        # Mock Geology page
        self.mock_dialog.page_geology.layer_combo.currentLayer.return_value = MagicMock()
        self.mock_dialog.page_geology.field_combo.currentData.return_value = "unit_field"

        # Mock Structure page
        self.mock_dialog.page_struct.layer_combo.currentLayer.return_value = MagicMock()
        self.mock_dialog.page_struct.dip_combo.currentData.return_value = "dip_field"
        self.mock_dialog.page_struct.strike_combo.currentData.return_value = "strike_field"
        self.mock_dialog.page_struct.scale_spin.value.return_value = 1.5

        # Mock output widget
        self.mock_dialog.output_widget.filePath.return_value = "/tmp/output.shp"

        self.validator = DialogValidator(self.mock_dialog)

    def test_collect_params(self):
        """Test parameter collection from UI widgets."""
        params = self.validator._collect_params()

        # Verify all parameters were collected
        self.assertIsNotNone(params.raster_layer)
        self.assertEqual(params.band_number, 1)
        self.assertIsNotNone(params.line_layer)
        self.assertEqual(params.output_path, "/tmp/output.shp")
        self.assertEqual(params.scale, 1000.0)
        self.assertEqual(params.vert_exag, 2.0)
        self.assertEqual(params.buffer_dist, 50.0)
        self.assertIsNotNone(params.outcrop_layer)
        self.assertEqual(params.outcrop_field, "unit_field")
        self.assertIsNotNone(params.struct_layer)
        self.assertEqual(params.struct_dip_field, "dip_field")
        self.assertEqual(params.struct_strike_field, "strike_field")
        self.assertEqual(params.dip_scale_factor, 1.5)

    def test_validate_inputs_success(self):
        """Test successful validation."""
        with patch('sec_interp.gui.main_dialog_validation.vu.ProjectValidator.validate_all') as mock_validate:
            mock_validate.return_value = None  # No exception = success

            success, message = self.validator.validate_inputs()

            self.assertTrue(success)
            self.assertEqual(message, "")
            mock_validate.assert_called_once()

    def test_validate_inputs_failure(self):
        """Test validation failure."""
        with patch('sec_interp.gui.main_dialog_validation.vu.ProjectValidator.validate_all') as mock_validate:
            mock_validate.side_effect = ValidationError("Invalid raster layer")

            success, message = self.validator.validate_inputs()

            self.assertFalse(success)
            self.assertEqual(message, "Invalid raster layer")
            mock_validate.assert_called_once()

    def test_validate_preview_requirements_success(self):
        """Test successful preview validation."""
        with patch('sec_interp.gui.main_dialog_validation.vu.ProjectValidator.validate_preview_requirements') as mock_validate:
            mock_validate.return_value = None

            success, message = self.validator.validate_preview_requirements()

            self.assertTrue(success)
            self.assertEqual(message, "")
            mock_validate.assert_called_once()

    def test_validate_preview_requirements_failure(self):
        """Test preview validation failure."""
        with patch('sec_interp.gui.main_dialog_validation.vu.ProjectValidator.validate_preview_requirements') as mock_validate:
            mock_validate.side_effect = ValidationError("Missing DEM layer")

            success, message = self.validator.validate_preview_requirements()

            self.assertFalse(success)
            self.assertEqual(message, "Missing DEM layer")
            mock_validate.assert_called_once()

    def test_collect_params_with_none_values(self):
        """Test parameter collection with None values from widgets."""
        # Set some widgets to return None
        self.mock_dialog.page_geology.layer_combo.currentLayer.return_value = None
        self.mock_dialog.page_struct.layer_combo.currentLayer.return_value = None

        params = self.validator._collect_params()

        # Verify None values are preserved
        self.assertIsNone(params.outcrop_layer)
        self.assertIsNone(params.struct_layer)
        # But other values should still be present
        self.assertIsNotNone(params.raster_layer)
        self.assertIsNotNone(params.line_layer)
