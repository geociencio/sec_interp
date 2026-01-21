from __future__ import annotations

"""Message Management Module.

Centralizes error handling and user notifications for the main dialog.
"""

import traceback

from qgis.core import Qgis

from sec_interp.core.exceptions import SecInterpError
from sec_interp.gui.utils import show_user_message
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class MessageManager:
    """Manages user messages and error handling for the SecInterp dialog."""

    def __init__(self, dialog):
        """Initialize the MessageManager.

        Args:
            dialog: The main SecInterpDialog instance.

        """
        self.dialog = dialog

    def push_message(self, title: str, message: str, level: int = Qgis.Info, duration: int = 5):
        """Push a message to the QGIS message bar.

        Args:
            title: Message title.
            message: Message content.
            level: Qgis message level (Info, Warning, Critical, Success).
            duration: Visibility duration in seconds.

        """
        if self.dialog.messagebar:
            self.dialog.messagebar.pushMessage(title, message, level=level, duration=duration)

    def show_dialog(self, title: str, message: str, level: str = "info"):
        """Show a message box dialog.

        Args:
            title: Dialog title.
            message: Dialog content.
            level: Message level ("info", "warning", "critical", "question").

        """
        return show_user_message(self.dialog, title, message, level=level)

    def handle_error(self, error: Exception, title: str = "Error"):
        """Centralized error handling.

        Args:
            error: The exception to handle.
            title: Title for the error message.

        """
        if isinstance(error, SecInterpError):
            msg = str(error)
            logger.warning(f"{title}: {msg} - Details: {getattr(error, 'details', 'N/A')}")
            self.show_dialog(title, msg, level="warning")
        else:
            msg = self.dialog.tr("An unexpected error occurred: {}").format(error)
            details = traceback.format_exc()
            logger.error(f"{title}: {msg}\n{details}")
            self.show_dialog(
                title,
                self.dialog.tr("{}\n\nPlease check the logs for details.").format(msg),
                level="critical",
            )
