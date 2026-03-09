"""Tests for DialogSettingsPersistence."""

import unittest
import json
from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from sec_interp.gui.dialog_settings_persistence import DialogSettingsPersistence


class TestDialogSettingsPersistence(BaseTestCase):
    """Tests for the DialogSettingsPersistence class."""

    def setUp(self):
        super().setUp()
        self.dialog = MagicMock()
        # Mock pages and widgets
        self.dialog.page_section = MagicMock()
        self.dialog.page_dem = MagicMock()
        self.dialog.page_geology = MagicMock()
        self.dialog.page_struct = MagicMock()
        self.dialog.page_drillhole = MagicMock()
        self.dialog.page_interpretation = MagicMock()
        self.dialog.output_widget = MagicMock()
        self.dialog.preview_widget = MagicMock()

        # Default behavior for readEntry to avoid StopIteration
        self.dialog.project.readEntry.return_value = ("", False)

        # Provide real-ish data for JSON serialization during save
        self.dialog.page_interpretation.get_data.return_value = {"custom_fields": []}

        self.persistence = DialogSettingsPersistence(self.dialog)

    def test_load_settings(self):
        """Test that load_settings calls all sub-loaders."""
        # Use return_value for stability
        self.dialog.project.readEntry.return_value = ("1.0", True)

        self.persistence.load_settings()
        self.dialog.project.readEntry.assert_called()

    def test_save_settings(self):
        """Test that save_settings calls all sub-savers."""
        self.persistence.config = MagicMock()
        # Ensure interpretation data is serializable
        self.dialog.page_interpretation.get_data.return_value = {
            "custom_fields": [{"n": "f"}]
        }

        self.persistence.save_settings()
        self.dialog.project.writeEntry.assert_called()

    def test_get_set_setting_fallbacks(self):
        """Test setting retrieval with fallbacks."""

        def mock_read(scope, key, default):
            if scope == "SecInterp":
                return ("", False)
            if scope == "SecInterpUI":
                return ("ui_val", True)
            return ("", False)

        self.dialog.project.readEntry.side_effect = mock_read
        self.assertEqual(self.persistence._get_setting("k"), "ui_val")

    def test_restore_layer_success(self):
        """Test restoring a layer."""
        combo = MagicMock()
        self.dialog.project.readEntry.side_effect = None
        self.dialog.project.readEntry.return_value = ("layer_id", True)
        mock_layer = MagicMock()
        self.dialog.project.mapLayer.return_value = mock_layer

        self.persistence._restore_layer(combo, "key")
        combo.setLayer.assert_called_with(mock_layer)

    def test_reset_pages(self):
        """Test resetting all page inputs."""
        self.persistence.reset_pages()
        self.dialog.page_section.line_combo.setLayer.assert_called_with(None)
        self.dialog.page_interpretation.fields_table.setRowCount.assert_called_with(0)

    def test_load_interpretation_settings_with_data(self):
        """Test loading custom fields from JSON."""
        fields = [{"name": "F1", "type": "String", "default": "D"}]
        self.dialog.project.readEntry.side_effect = None
        self.dialog.project.readEntry.return_value = (json.dumps(fields), True)

        self.persistence._load_interpretation_settings()
        self.dialog.page_interpretation._add_field_row.assert_called()

    def test_parse_setting_value(self):
        """Test parsing of various types from strings."""
        self.assertEqual(self.persistence._parse_setting_value("True"), True)
        self.assertEqual(self.persistence._parse_setting_value("123"), 123)
        self.assertEqual(self.persistence._parse_setting_value("1.23"), 1.23)
        self.assertEqual(self.persistence._parse_setting_value("abc"), "abc")


if __name__ == "__main__":
    unittest.main()
