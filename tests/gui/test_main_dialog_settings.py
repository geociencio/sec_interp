"""Tests for DialogSettingsManager with enhanced persistence logic."""

import unittest
from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from qgis.core import QgsProject, QgsSettings
from sec_interp.gui.main_dialog_settings import DialogSettingsManager


class TestMainDialogSettings(BaseTestCase):
    """Tests for the DialogSettingsManager class."""

    def setUp(self):
        super().setUp()
        self.dialog = MagicMock()
        self.dialog.project = QgsProject.instance()

        # Reset project entries
        self.dialog.project._entries = {}
        self.dialog.project._layers = {}

        # Mock plugin_instance and controller
        self.plugin_instance = MagicMock()
        self.dialog.plugin_instance = self.plugin_instance
        self.config_service = MagicMock()
        self.plugin_instance.controller.config_service = self.config_service

        # Mock pages
        self.dialog.page_section = MagicMock()
        self.dialog.page_dem = MagicMock()
        self.dialog.page_interpretation = MagicMock()
        self.dialog.preview_widget = MagicMock()
        self.dialog.status_manager = MagicMock()

        self.manager = DialogSettingsManager(self.dialog)

    def test_parse_setting_value(self):
        """Test parsing of different value types and edge cases."""
        self.assertEqual(self.manager._parse_setting_value("True"), True)
        self.assertEqual(self.manager._parse_setting_value("false"), False)
        self.assertEqual(self.manager._parse_setting_value("123"), 123)
        self.assertEqual(self.manager._parse_setting_value("123.4"), 123.4)
        self.assertEqual(self.manager._parse_setting_value("None"), None)
        self.assertEqual(self.manager._parse_setting_value("NULL"), None)
        self.assertEqual(self.manager._parse_setting_value(""), None)
        self.assertEqual(self.manager._parse_setting_value("MyLayer"), "MyLayer")

    def test_save_and_load_layer_with_name(self):
        """Test that layer ID and Name are saved and restored."""
        mock_layer = MagicMock()
        mock_layer.id.return_value = "id_123"
        mock_layer.name.return_value = "RealName"

        combo = MagicMock()
        combo.currentLayer.return_value = mock_layer

        self.manager._save_layer(combo, "test_layer")

        # Check that both ID and Name were stored (in project mock)
        self.assertEqual(self.dialog.project._entries["SecInterp/test_layer"], "id_123")
        self.assertEqual(
            self.dialog.project._entries["SecInterp/test_layer_name"], "RealName"
        )

        # Now clear the ID (simulate new project) but keep the name
        del self.dialog.project._entries["SecInterp/test_layer"]

        # Add layer to project by name
        self.dialog.project._layers["some_other_id"] = mock_layer

        restore_combo = MagicMock()
        self.manager._restore_layer(restore_combo, "test_layer")

        # Should have found it by name fallback
        restore_combo.setLayer.assert_called_with(mock_layer)

    def test_load_settings_fallback_to_global_with_parsing(self):
        """Test that global values are correctly parsed when falling back."""
        # 1. Project empty
        # 2. Global has a numeric string
        self.config_service.get.return_value = "100.5"

        val = self.manager._get_setting("buffer_dist")
        self.assertEqual(val, 100.5)

    def test_reset_to_defaults_clears_interpretations(self):
        """Test that reset_to_defaults clears persistent interpretations."""
        # Setup initial state
        self.dialog.interpretations = ["interp1", "interp2"]
        self.dialog._save_interpretations = MagicMock()

        # Run reset
        self.manager.reset_to_defaults()

        # Assertions
        self.assertEqual(
            self.dialog.interpretations, [], "Interpretations list should be cleared"
        )
        self.dialog._save_interpretations.assert_called_once()


if __name__ == "__main__":
    unittest.main()
