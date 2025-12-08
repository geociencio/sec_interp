"""Logger Configuration Module.

Provides centralized logging configuration for the Sec Interp plugin.
"""

import logging

from qgis.core import Qgis, QgsMessageLog


class QgsLogHandler(logging.Handler):
    """Custom logging handler that writes to QGIS message log."""

    def __init__(self, tag="SecInterp"):
        super().__init__()
        self.tag = tag

    def emit(self, record):
        """Emit a log record to QGIS message log."""
        try:
            msg = self.format(record)

            # Map Python logging levels to QGIS levels
            if record.levelno >= logging.ERROR:
                level = Qgis.Critical
            elif record.levelno >= logging.WARNING:
                level = Qgis.Warning
            elif record.levelno >= logging.INFO:
                level = Qgis.Info
            else:
                level = Qgis.Info  # DEBUG messages as Info

            QgsMessageLog.logMessage(msg, self.tag, level)
        except Exception:
            self.handleError(record)


def get_logger(name):
    """Get a configured logger for the plugin.

    Args:
        name: Name of the logger (typically __name__ from calling module)

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(f"SecInterp.{name}")

    # Only configure if not already configured
    if not logger.handlers:
        # Set level - change to INFO for production, DEBUG for development
        logger.setLevel(logging.INFO)

        # Create QGIS message log handler
        handler = QgsLogHandler(tag="SecInterp")
        handler.setLevel(logging.INFO)

        # Create formatter (simpler for QGIS message panel)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

        # Prevent propagation to avoid duplicate messages
        logger.propagate = False

    return logger
