"""Tests for StateManager - Consolidation of Status and Settings Managers."""

import unittest
from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from qgis.core import QgsProject
from sec_interp.gui.dialog_state_manager import StateManager


class TestStateManager(BaseTestCase):
    """Tests for the StateManager class."""

    def setUp(self):
        super().setUp()
        self.dialog = MagicMock()
        self.dialog.project = QgsProject.instance()

        # Mock internal project dicts
        self.dialog.project._settings = {}

        self.plugin_instance = MagicMock()
        self.dialog.plugin_instance = self.plugin_instance

        # Mock pages and widgets
        self.dialog.page_section = MagicMock()
        self.dialog.page_dem = MagicMock()
        self.dialog.page_geology = MagicMock()
        self.dialog.page_struct = MagicMock()
        self.dialog.page_drillhole = MagicMock()
        self.dialog.page_interpretation = MagicMock()
        self.dialog.preview_widget = MagicMock()
        self.dialog.button_box = MagicMock()
        self.dialog.output_widget = MagicMock()

        self.manager = StateManager(self.dialog)

    def test_reset_to_defaults_interacts_with_widgets(self):
        """Verify that reset_to_defaults interacts with major UI components."""
        self.manager.reset_to_defaults()

        # Checking some key direct widget interactions in _reset_pages
        self.dialog.page_section.line_combo.setLayer.assert_called()
        self.dialog.page_dem.raster_combo.setLayer.assert_called()
        self.dialog.output_widget.setFilePath.assert_called_with("")

    def test_update_button_state_enabled(self):
        """Test that buttons are enabled when inputs are valid."""
        with patch.object(self.dialog.input_manager, "can_preview", return_value=True):
            with patch.object(
                self.dialog.input_manager, "can_export", return_value=True
            ):
                self.manager.update_button_state()
                self.dialog.preview_widget.btn_preview.setEnabled.assert_called_with(
                    True
                )

    def test_update_button_state_disabled(self):
        """Test that buttons are disabled when inputs are invalid."""
        with patch.object(self.dialog.input_manager, "can_preview", return_value=False):
            with patch.object(
                self.dialog.input_manager, "can_export", return_value=False
            ):
                self.manager.update_button_state()
                self.dialog.preview_widget.btn_preview.setEnabled.assert_called_with(
                    False
                )

    def test_parse_setting_value_types(self):
        """Test the internal parser for different string types."""
        self.assertEqual(self.manager._parse_setting_value("True"), True)
        self.assertEqual(self.manager._parse_setting_value("123"), 123)
        self.assertEqual(self.manager._parse_setting_value("12.5"), 12.5)
        self.assertEqual(self.manager._parse_setting_value("NULL"), None)


if __name__ == "__main__":
    unittest.main()
