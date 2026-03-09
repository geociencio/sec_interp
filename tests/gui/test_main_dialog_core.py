"""Tests for core Main Dialog logic and delegation."""

import unittest
from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from qgis.core import Qgis
from sec_interp.gui.main_dialog import SecInterpDialog
from sec_interp.core.exceptions import SecInterpError


class TestMainDialogCore(BaseTestCase):
    """Tests for core SecInterpDialog functionality."""

    def setUp(self):
        super().setUp()
        self.iface = MagicMock()
        self.plugin_instance = MagicMock()

        # Avoid full initialization side effects if possible, or mock managers
        with patch("sec_interp.gui.main_dialog.SignalManager"):
            with patch("sec_interp.gui.main_dialog.StateManager"):
                with patch("sec_interp.gui.main_dialog.PreviewManager"):
                    with patch("sec_interp.gui.main_dialog.InterpretationManager"):
                        with patch("sec_interp.gui.main_dialog.ToolManager"):
                            with patch("sec_interp.gui.main_dialog.InputManager"):
                                self.dialog = SecInterpDialog(
                                    self.iface, self.plugin_instance
                                )

    def test_push_message_levels(self):
        """Test push_message with different Qgis levels and HTML formatting."""
        levels = [Qgis.Info, Qgis.Success, Qgis.Warning, Qgis.Critical]
        titles = ["Info", "Success", "Warning", "Critical"]

        for level, title in zip(levels, titles):
            self.dialog.push_message(title, "Test message", level=level)
            # Verify it reaches iface message bar
            self.iface.messageBar().pushMessage.assert_called()
            # Verify it reaches plugin results as HTML
            self.assertTrue(self.dialog.preview_widget.results_text.append.called)

    def test_handle_error_sec_interp_error(self):
        """Test handle_error with SecInterpError."""
        err = SecInterpError("Expected", details="Some details")
        with patch.object(self.dialog, "show_dialog") as mock_show:
            self.dialog.handle_error(err, "Operation Failed")
            mock_show.assert_called_with(
                "Operation Failed", "Expected", level="warning"
            )

    def test_handle_error_generic_exception(self):
        """Test handle_error with generic Exception."""
        err = Exception("Unexpected")
        with patch.object(self.dialog, "show_dialog") as mock_show:
            self.dialog.handle_error(err, "Crash")
            mock_show.assert_called_with("Crash", unittest.mock.ANY, level="critical")

    def test_close_event_cleanup(self):
        """Test that closeEvent triggers cleanup in all managers."""
        event = MagicMock()
        self.dialog.closeEvent(event)

        self.dialog.preview_manager.cleanup.assert_called_once()
        self.dialog.state_manager.save_settings.assert_called_once()
        self.dialog.interpretation_manager.save_interpretations.assert_called_once()

    def test_open_help_locale_fallback(self):
        """Test help file opening logic with locale fallbacks."""
        with patch("sec_interp.gui.main_dialog.QSettings") as mock_settings:
            with patch("sec_interp.gui.main_dialog.Path.exists") as mock_exists:
                with patch(
                    "sec_interp.gui.main_dialog.QDesktopServices.openUrl"
                ) as mock_open:
                    mock_settings.return_value.value.return_value = "es"
                    mock_exists.return_value = True

                    self.dialog.open_help()
                    mock_open.assert_called()

    def test_preview_profile_handler_success(self):
        """Test preview_profile_handler success flow."""
        self.dialog.preview_manager.generate_preview.return_value = (True, "Success")
        self.dialog.preview_profile_handler()
        self.dialog.state_manager.save_settings.assert_called_once()

    def test_preview_profile_handler_fail(self):
        """Test preview_profile_handler failure flow."""
        self.dialog.preview_manager.generate_preview.return_value = (False, "Error")
        with patch.object(self.dialog, "push_message") as mock_push:
            self.dialog.preview_profile_handler()
            mock_push.assert_called_with("Preview Error", "Error", level=Qgis.Warning)

    def test_accept_handler_no_iface(self):
        """Test accept_handler in test environment (no iface)."""
        self.dialog.iface = None
        with patch.object(self.dialog, "accept") as mock_accept:
            self.dialog.accept_handler()
            mock_accept.assert_called_once()

    def test_proxy_methods(self):
        """Test simple delegation proxy methods."""
        # Test clear_cache_handler
        self.dialog.clear_cache_handler()
        self.assertTrue(self.plugin_instance.controller.data_cache.clear.called)

        # Test reset_defaults_handler
        self.dialog.reset_defaults_handler()
        self.dialog.state_manager.reset_to_defaults.assert_called_once()

        # Test other proxies
        self.dialog.toggle_measure_tool(True)
        self.dialog.tool_manager.toggle_measure_tool.assert_called_with(True)

        self.dialog.get_selected_values()
        self.dialog.input_manager.get_all_values.assert_called_once()

        self.dialog.update_button_state()
        self.dialog.state_manager.update_button_state.assert_called_once()

    def test_wheel_event_delegation(self):
        """Test wheelEvent delegation to navigation_manager."""
        self.dialog.navigation_manager = MagicMock()
        self.dialog.navigation_manager.handle_wheel_event.return_value = True
        event = MagicMock()
        self.dialog.wheelEvent(event)
        self.dialog.navigation_manager.handle_wheel_event.assert_called_with(event)

    def test_accept_handler_validation_fail(self):
        """Test accept_handler when validation fails."""
        self.dialog.iface = MagicMock()
        self.dialog.input_manager.validate_inputs.return_value = (False, "Error")
        with patch.object(self.dialog, "accept") as mock_accept:
            self.dialog.accept_handler()
            mock_accept.assert_not_called()

    def test_open_help_english_fallback(self):
        """Test open_help falling back to English."""
        with patch("sec_interp.gui.main_dialog.QSettings") as mock_settings:
            with patch("sec_interp.gui.main_dialog.Path.exists") as mock_exists:
                with patch(
                    "sec_interp.gui.main_dialog.QDesktopServices.openUrl"
                ) as mock_open:
                    mock_settings.return_value.value.return_value = "non_existent"
                    # Checks at lines 256, 260, 263
                    mock_exists.side_effect = [False, False, True]

                    self.dialog.open_help()
                    self.assertEqual(mock_exists.call_count, 3)
                    mock_open.assert_called()

    def test_reject_handler(self):
        """Test reject_handler sets flag and closes."""
        with patch.object(self.dialog, "close") as mock_close:
            self.dialog.reject_handler()
            self.assertFalse(self.dialog._save_on_close)
            mock_close.assert_called_once()

    def test_show_dialog(self):
        """Test show_dialog proxy."""
        with patch("sec_interp.gui.main_dialog.show_user_message") as mock_show:
            self.dialog.show_dialog("T", "M", level="info")
            mock_show.assert_called_with(self.dialog, "T", "M", level="info")

    def test_more_proxies(self):
        """Test remaining delegation methods."""
        # interpretations getter/setter
        self.dialog.interpretations = [1, 2, 3]
        self.assertEqual(self.dialog.interpretation_manager.interpretations, [1, 2, 3])
        _ = self.dialog.interpretations

        # update_measurement_display
        self.dialog.update_measurement_display({"dist": 10})
        self.dialog.tool_manager.update_measurement_display.assert_called_with(
            {"dist": 10}
        )

        # update_preview_checkbox_states
        self.dialog.update_preview_checkbox_states()
        self.dialog.state_manager.update_preview_checkbox_states.assert_called_once()

        # get_preview_options
        options = self.dialog.get_preview_options()
        self.assertIn("show_topo", options)

        # update_preview_from_checkboxes
        self.dialog.update_preview_from_checkboxes()
        self.dialog.preview_manager.update_from_checkboxes.assert_called_once()

        # export_preview
        with patch(
            "sec_interp.gui.main_dialog.ExportManager"
        ):  # Re-mocking local instance
            self.dialog.export_manager = MagicMock()
            self.dialog.export_preview()
            self.dialog.export_manager.export_preview.assert_called_once()

        # layer proxies
        self.dialog.get_layer_names_by_type("raster")
        self.dialog.get_layer_names_by_geometry("point")
        self.dialog.getThemeIcon("icon")

        # state proxies
        self.dialog._load_interpretations()
        self.dialog._save_interpretations()
        self.dialog._load_user_settings()
        self.dialog._save_user_settings()


if __name__ == "__main__":
    unittest.main()
