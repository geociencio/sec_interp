"""Unit tests for MessageManager."""

import unittest
from unittest.mock import MagicMock, patch
from qgis.core import Qgis
from sec_interp.core.exceptions import SecInterpError
from sec_interp.gui.main_dialog_messages import MessageManager
from tests.base_test import BaseTestCase


class TestMessageManager(BaseTestCase):
    """Test suite for MessageManager component."""

    def setUp(self):
        super().setUp()
        self.mock_dialog = MagicMock()
        self.mock_dialog.messagebar = MagicMock()
        self.mock_dialog.tr = lambda x: x
        self.manager = MessageManager(self.mock_dialog)

    def test_push_message(self):
        """Test pushing a message to the message bar."""
        self.manager.push_message("Title", "Message", level=Qgis.Info)
        self.mock_dialog.messagebar.pushMessage.assert_called_once_with(
            "Title", "Message", level=Qgis.Info, duration=5
        )

    def test_push_message_no_bar(self):
        """Test pushing a message when no message bar is available."""
        self.mock_dialog.messagebar = None
        # Should not raise exception
        self.manager.push_message("Title", "Message")

    @patch("sec_interp.gui.main_dialog_messages.show_user_message")
    def test_show_dialog(self, mock_show):
        """Test showing a message dialog."""
        self.manager.show_dialog("Title", "Message", level="warning")
        mock_show.assert_called_once_with(
            self.mock_dialog, "Title", "Message", level="warning"
        )

    @patch("sec_interp.gui.main_dialog_messages.show_user_message")
    def test_handle_error_sec_interp_error(self, mock_show):
        """Test handling a SecInterpError."""
        error = SecInterpError("Validation failed", details="Check inputs")
        self.manager.handle_error(error, "App Error")

        mock_show.assert_called_once_with(
            self.mock_dialog, "App Error", "Validation failed", level="warning"
        )

    @patch("sec_interp.gui.main_dialog_messages.show_user_message")
    @patch("sec_interp.gui.main_dialog_messages.traceback.format_exc")
    def test_handle_error_unexpected(self, mock_trace, mock_show):
        """Test handling an unexpected exception."""
        mock_trace.return_value = "Stack trace details"
        error = ValueError("Something went wrong")

        self.manager.handle_error(error, "System Error")

        mock_show.assert_called_once()
        args = mock_show.call_args[0]
        self.assertEqual(args[1], "System Error")
        self.assertIn("An unexpected error occurred: Something went wrong", args[2])
        self.assertEqual(mock_show.call_args[1]["level"], "critical")
