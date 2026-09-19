"""Tests for DialogSettingsPersistence."""

import unittest
from unittest.mock import MagicMock
from tests.base_test import BaseTestCase
from sec_interp.gui.dialog_settings_persistence import DialogSettingsPersistence


class TestDialogSettingsPersistence(BaseTestCase):
    """Tests for the DialogSettingsPersistence class."""

    def setUp(self):
        super().setUp()
        self.dialog = MagicMock()

        self.pages = []
        for name in [
            "page_section",
            "page_dem",
            "page_geology",
            "page_struct",
            "page_drillhole",
            "page_interpretation",
        ]:
            page = MagicMock()
            page.dump.return_value = {}
            page.layer_keys = frozenset()
            setattr(self.dialog, name, page)
            self.pages.append(page)

        self.dialog.output_widget = MagicMock()
        self.dialog.preview_widget = MagicMock()
        self.dialog.preview_widget.dump.return_value = {}

        # Default behavior for readEntry to avoid StopIteration
        self.dialog.project.readEntry.return_value = ("", False)

        self.persistence = DialogSettingsPersistence(self.dialog)

    def test_load_settings(self):
        """Test that load_settings loads each page and the preview widget."""
        self.dialog.project.readEntry.return_value = ("1.0", True)

        self.persistence.load_settings()

        for page in self.pages:
            page.load.assert_called_once()
        self.dialog.preview_widget.load.assert_called_once()

    def test_save_settings(self):
        """Test that save_settings writes settings for each page."""
        self.persistence.config = MagicMock()

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

    def test_resolve_layer_value(self):
        """Test resolving a stored layer ID back into a layer."""
        self.dialog.project.readEntry.side_effect = None
        self.dialog.project.readEntry.return_value = ("layer_id", True)
        mock_layer = MagicMock()
        self.dialog.project.mapLayer.return_value = mock_layer

        self.assertEqual(self.persistence._resolve_layer_value("key"), mock_layer)

    def test_reset_pages(self):
        """Test resetting all page inputs."""
        self.persistence.reset_pages()

        for page in self.pages:
            page.reset.assert_called_once()
        self.dialog.output_widget.setFilePath.assert_called_with("")

    def test_parse_setting_value(self):
        """Test parsing of various types from strings."""
        self.assertEqual(self.persistence._parse_setting_value("True"), True)
        self.assertEqual(self.persistence._parse_setting_value("123"), 123)
        self.assertEqual(self.persistence._parse_setting_value("1.23"), 1.23)
        self.assertEqual(self.persistence._parse_setting_value("abc"), "abc")


if __name__ == "__main__":
    unittest.main()
