# -*- coding: utf-8 -*-
"""
I/O Utilities Module

File I/O operations and user messaging.
"""

from pathlib import Path
from qgis.core import (
    QgsVectorFileWriter,
    QgsProject,
    QgsWkbTypes,
    QgsFields,
    QgsCoordinateReferenceSystem,
)


def create_shapefile_writer(
    output_path,
    crs: QgsCoordinateReferenceSystem,
    fields: QgsFields,
    geometry_type=QgsWkbTypes.LineString,
):
    """Helper to create a QgsVectorFileWriter.

    Args:
        output_path: Path where shapefile will be created.
        crs: CRS for the shapefile.
        fields: Fields definition for the shapefile.
        geometry_type: Geometry type (default: LineString).

    Returns:
        QgsVectorFileWriter: Initialized writer object.

    Raises:
        IOError: If writer creation fails.
    """
    # Use new static create method for QGIS 3.38+
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "ESRI Shapefile"
    options.fileEncoding = "UTF-8"

    writer = QgsVectorFileWriter.create(
        str(output_path),
        fields,
        geometry_type,
        crs,
        QgsProject.instance().transformContext(),
        options,
    )

    if writer.hasError() != QgsVectorFileWriter.NoError:
        raise IOError(
            f"Error creating shapefile {output_path}: {writer.errorMessage()}"
        )

    return writer


def show_user_message(parent, title: str, message: str, level: str = "warning"):
    """Show message box with consistent styling and automatic logging.

    Args:
        parent: Parent widget (usually dialog or main window)
        title: Message box title
        message: Message content
        level: Message level - "warning", "info", "error", "critical", "question"

    Returns:
        QMessageBox.StandardButton for "question" level, None otherwise

    Example:
        show_user_message(self.dlg, "Error", "Invalid input", "warning")
    """
    from qgis.PyQt.QtWidgets import QMessageBox
    from sec_interp.logger_config import get_logger

    logger = get_logger(__name__)

    # Log the message
    if level == "error" or level == "critical":
        logger.error(f"{title}: {message}")
    elif level == "warning":
        logger.warning(f"{title}: {message}")
    else:
        logger.info(f"{title}: {message}")

    # Show message box
    if level == "warning":
        QMessageBox.warning(parent, title, message)
    elif level == "info":
        QMessageBox.information(parent, title, message)
    elif level == "error" or level == "critical":
        QMessageBox.critical(parent, title, message)
    elif level == "question":
        return QMessageBox.question(
            parent, title, message, QMessageBox.Yes | QMessageBox.No
        )
