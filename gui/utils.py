"""UI Utilities Module.

General purpose UI helpers and user messaging.
"""

from qgis.PyQt.QtWidgets import QMessageBox

from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


def show_user_message(parent, title: str, message: str, level: str = "warning"):
    """Show message box with consistent styling and automatic logging.

    Args:
        parent: Parent widget (usually dialog or main window)
        title: Message box title
        message: Message content
        level: Message level - "warning", "info", "error", "critical", "question"

    Returns:
        QMessageBox.StandardButton for "question" level, None otherwise
    """
    # Log the message
    if level in {"error", "critical"}:
        logger.error(f"{title}: {message}")
    elif level == "warning":
        logger.warning(f"{title}: {message}")
    else:
        logger.info(f"{title}: {message}")

    # Show message box
    if level == "warning":
        return QMessageBox.warning(parent, title, message)
    elif level == "info":
        return QMessageBox.information(parent, title, message)
    elif level in {"error", "critical"}:
        return QMessageBox.critical(parent, title, message)
    elif level == "question":
        return QMessageBox.question(
            parent, title, message, QMessageBox.Yes | QMessageBox.No
        )
    return None
