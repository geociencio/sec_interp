"""Tests for GUI utilities."""

from unittest.mock import Mock, patch
from sec_interp.gui.utils import show_user_message

class TestShowUserMessage:
    """Tests for show_user_message helper."""

    @patch("sec_interp.gui.utils.QMessageBox")
    def test_show_user_message_warning(self, mock_qmessagebox):
        """Test warning message."""
        mock_parent = Mock()
        show_user_message(mock_parent, "Test Title", "Test Message", "warning")

        # Verify QMessageBox.warning was called
        mock_qmessagebox.warning.assert_called_once_with(
            mock_parent, "Test Title", "Test Message"
        )

    @patch("sec_interp.gui.utils.QMessageBox")
    def test_show_user_message_info(self, mock_qmessagebox):
        """Test info message."""
        mock_parent = Mock()
        show_user_message(mock_parent, "Test Title", "Test Message", "info")

        # Verify QMessageBox.information was called
        mock_qmessagebox.information.assert_called_once_with(
            mock_parent, "Test Title", "Test Message"
        )

    @patch("sec_interp.gui.utils.QMessageBox")
    def test_show_user_message_error(self, mock_qmessagebox):
        """Test error message."""
        mock_parent = Mock()
        show_user_message(mock_parent, "Test Title", "Test Message", "error")

        # Verify QMessageBox.critical was called
        mock_qmessagebox.critical.assert_called_once_with(
            mock_parent, "Test Title", "Test Message"
        )
