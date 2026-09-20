"""Message-bar and error-reporting mixin for the SecInterp main dialog."""

from __future__ import annotations

import traceback

from qgis.core import Qgis

from sec_interp.core.exceptions import SecInterpError
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class DialogMessageMixin:
    """Push messages to the QGIS message bar and the plugin results area."""

    def push_message(
        self,
        title: str,
        message: str,
        level: int = Qgis.MessageLevel.Info,
        duration: int = 5,
        show_in_plugin: bool = True,
    ) -> None:
        """Push a message to the QGIS message bar and optionally to plugin results.

        Args:
            title: Message title.
            message: Message content.
            level: Qgis message level (Info, Warning, Critical, Success).
            duration: Visibility duration in seconds.
            show_in_plugin: If True, also show message in plugin results area.

        """
        if self.messagebar:
            self.messagebar.pushMessage(title, message, level=level, duration=duration)

        if show_in_plugin and hasattr(self, "preview_widget"):
            if level == Qgis.MessageLevel.Success:
                icon = "✓"
                color = "#28a745"
            elif level == Qgis.MessageLevel.Warning:
                icon = "⚠"
                color = "#ffc107"
            elif level == Qgis.MessageLevel.Critical:
                icon = "✗"
                color = "#dc3545"
            else:
                icon = "ℹ"
                color = "#17a2b8"

            formatted_msg = (
                f'<span style="color: {color}; font-weight: bold;">{icon} {title}:</span> {message}'
            )
            self.preview_widget.results_text.append(formatted_msg)

    def handle_error(self, error: Exception, title: str = "Error") -> None:
        """Centralized error handling for the dialog.

        Args:
            error: The exception to handle.
            title: Title for the error message box.

        """
        if isinstance(error, SecInterpError):
            msg = str(error)
            logger.warning(f"{title}: {msg} - Details: {getattr(error, 'details', 'N/A')}")
            self.show_dialog(title, msg, level="warning")
        else:
            msg = self.tr("An unexpected error occurred: {}").format(error)
            details = traceback.format_exc()
            logger.error(f"{title}: {msg}\n{details}")
            self.show_dialog(
                title,
                self.tr("{}\n\nPlease check the logs for details.").format(msg),
                level="critical",
            )
