"""Unit tests for MessageManager."""

import unittest
from unittest.mock import MagicMock, patch
from qgis.core import Qgis
from sec_interp.core.exceptions import SecInterpError
from sec_interp.gui.main_dialog import SecInterpDialog
from tests.base_test import BaseTestCase


class TestMessageMethods(BaseTestCase):
    """Test suite for message methods in SecInterpDialog."""

    def setUp(self):
        super().setUp()
        self.dialog = MagicMock(spec=SecInterpDialog)
        self.dialog.messagebar = MagicMock()
        self.dialog.tr = lambda x: x
        # We'll use the real methods from the class
        self.dialog.push_message = SecInterpDialog.push_message.__get__(
            self.dialog, SecInterpDialog
        )
        self.dialog.show_dialog = SecInterpDialog.show_dialog.__get__(
            self.dialog, SecInterpDialog
        )
        self.dialog.handle_error = SecInterpDialog.handle_error.__get__(
            self.dialog, SecInterpDialog
        )

    def test_push_message(self):
        """Test pushing a message to the message bar."""
        self.dialog.push_message("Title", "Message", level=Qgis.Info)
        self.dialog.messagebar.pushMessage.assert_called_once_with(
            "Title", "Message", level=Qgis.Info, duration=5
        )

    def test_push_message_no_bar(self):
        """Test pushing a message when no message bar is available."""
        self.dialog.messagebar = None
        # Should not raise exception
        self.dialog.push_message("Title", "Message")

    @patch("sec_interp.gui.main_dialog.show_user_message")
    def test_show_dialog(self, mock_show):
        """Test showing a message dialog."""
        self.dialog.show_dialog("Title", "Message", level="warning")
        mock_show.assert_called_once_with(
            self.dialog, "Title", "Message", level="warning"
        )

    @patch("sec_interp.gui.main_dialog.show_user_message")
    def test_handle_error_sec_interp_error(self, mock_show):
        """Test handling a SecInterpError."""
        error = SecInterpError("Validation failed", details="Check inputs")
        self.dialog.handle_error(error, "App Error")

        mock_show.assert_called_once_with(
            self.dialog, "App Error", "Validation failed", level="warning"
        )

    @patch("sec_interp.gui.main_dialog.show_user_message")
    @patch("traceback.format_exc")
    def test_handle_error_unexpected(self, mock_trace, mock_show):
        """Test handling an unexpected exception."""
        mock_trace.return_value = "Stack trace details"
        error = ValueError("Something went wrong")

        self.dialog.handle_error(error, "System Error")

        mock_show.assert_called_once()
        args = mock_show.call_args[0]
        self.assertEqual(args[1], "System Error")
        self.assertIn("An unexpected error occurred: Something went wrong", args[2])
        self.assertEqual(mock_show.call_args[1]["level"], "critical")
