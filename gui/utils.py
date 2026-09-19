"""UI Utilities Module.

General purpose UI helpers and user messaging.
"""

from __future__ import annotations

from typing import Any

from qgis.core import QgsProject, QgsVectorLayer
from qgis.PyQt.QtWidgets import QMessageBox

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


def create_memory_layer(uri: str, name: str) -> QgsVectorLayer | None:
    """Create a memory layer and assign the current project CRS.

    Args:
        uri: Memory provider URI (e.g. "LineString" or "Point?field=...").
        name: Display name for the layer.

    Returns:
        The created layer, or None if creation failed.

    """
    layer = QgsVectorLayer(uri, name, "memory")
    if not layer.isValid():
        logger.error(f"Failed to create memory layer: {name}")
        return None

    project_crs = QgsProject.instance().crs()
    if project_crs.isValid():
        layer.setCrs(project_crs)

    return layer


def show_user_message(parent: Any, title: str, message: str, level: str = "warning") -> Any:
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
            parent,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
    return None
