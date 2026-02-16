"""Tests for signal wiring in SecInterpDialog.
Ensures that UI interactions correctly trigger state updates and logic.
"""

import unittest
from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from sec_interp.gui.main_dialog import SecInterpDialog


class TestMainDialogWiring(BaseTestCase):
    """Tests for the wiring of signals in the main dialog."""

    def setUp(self):
        super().setUp()
        # Mocking complex dialog dependencies
        mock_plugin = MagicMock()
        mock_plugin.controller = MagicMock()

        with (
            patch("sec_interp.gui.main_dialog.StateManager"),
            patch("sec_interp.gui.main_dialog.InputManager"),
            patch("sec_interp.gui.main_dialog.ExportManager"),
            patch("sec_interp.gui.main_dialog.PreviewManager"),
            patch("sec_interp.gui.main_dialog.InterpretationManager"),
            patch("sec_interp.gui.main_dialog.ToolManager"),
            patch("sec_interp.gui.main_dialog.LegendWidget"),
        ):
            self.dialog = SecInterpDialog(plugin_instance=mock_plugin)

    def test_reset_button_triggers_state_manager(self):
        """Verify that the reset button call's the state manager's reset method."""
        # Setup mock behavior
        self.dialog.state_manager.reset_to_defaults = MagicMock()

        # Trigger the slot manually
        self.dialog.reset_defaults_handler()

        self.dialog.state_manager.reset_to_defaults.assert_called_once()

    @patch("sec_interp.gui.main_dialog.logger")
    def test_close_saves_settings(self, mock_logger):
        """Verify that closing the dialog triggers settings save."""
        self.dialog.state_manager.save_settings = MagicMock()

        # Simulate accept (which should save settings via accept_handler)
        self.dialog.accept_handler()

        self.dialog.state_manager.save_settings.assert_called_once()

    def test_page_signals_trigger_status_update(self):
        """Verify that page changes trigger dialog update methods."""
        # 1. Test direct delegation (slot logic)
        self.dialog.state_manager.update_button_state.reset_mock()
        self.dialog.update_button_state()
        self.dialog.state_manager.update_button_state.assert_called_once()

        # 2. Test signal wiring (if connection works)
        self.dialog.state_manager.update_button_state.reset_mock()
        self.dialog.page_section.line_combo.layerChanged.emit(MagicMock())

        # If this fails but the direct call passed, then it's a wiring issue
        self.dialog.state_manager.update_button_state.assert_called()


if __name__ == "__main__":
    unittest.main()
