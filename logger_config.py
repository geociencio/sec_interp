"""Logger Configuration Module.

Provides centralized logging configuration for the Sec Interp plugin.
"""

import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys

from qgis.core import Qgis, QgsMessageLog


class ImmediateFlushFileHandler(RotatingFileHandler):
    """File handler that flushes immediately after each write.

    This ensures logs are written to disk before a crash occurs.
    """

    def emit(self, record):
        super().emit(record)
        self.flush()


class QgsLogHandler(logging.Handler):
    """Custom logging handler that writes to QGIS message log."""

    def __init__(self, tag="SecInterp"):
        super().__init__()
        self.tag = tag

    def emit(self, record):
        """Emit a log record to QGIS message log safely."""
        try:
            from qgis.PyQt.QtCore import QCoreApplication, QThread

            msg = self.format(record)

            # Map Python logging levels to QGIS levels
            if record.levelno >= logging.ERROR:
                level = Qgis.Critical
            elif record.levelno >= logging.WARNING:
                level = Qgis.Warning
            elif record.levelno >= logging.INFO:
                level = Qgis.Info
            else:
                level = Qgis.Info

            # Critical: UI updates from background threads cause segfaults in QGIS
            if QThread.currentThread() == QCoreApplication.instance().thread():
                QgsMessageLog.logMessage(msg, self.tag, level)
            else:
                # Fallback to standard output for background threads
                # This prevents the most common cause of QGIS segfaults in plugins
                print(f"[{self.tag}] (BG) {msg}")
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
        # Set level - DEBUG for crash analysis
        logger.setLevel(logging.DEBUG)

        # 1. Create QGIS message log handler (for UI)
        qgis_handler = QgsLogHandler(tag="SecInterp")
        qgis_handler.setLevel(logging.INFO)
        qgis_formatter = logging.Formatter("%(levelname)s - %(message)s")
        qgis_handler.setFormatter(qgis_formatter)
        logger.addHandler(qgis_handler)

        # 2. Create file handler for detailed crash analysis
        try:
            # Determine log directory (in repository root)
            plugin_dir = Path(__file__).parent
            log_dir = plugin_dir / "logs"
            log_dir.mkdir(exist_ok=True)

            log_file = log_dir / "sec_interp_debug.log"

            # Use ImmediateFlushFileHandler for crash analysis
            file_handler = ImmediateFlushFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setLevel(logging.DEBUG)

            # Detailed formatter for file logs
            file_formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | "
                "%(funcName)s:%(lineno)d | Thread-%(thread)d | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

            # 3. Add stderr handler as backup for crash scenarios
            stderr_handler = logging.StreamHandler(sys.stderr)
            stderr_handler.setLevel(logging.WARNING)  # Only warnings and errors to stderr
            stderr_handler.setFormatter(file_formatter)
            logger.addHandler(stderr_handler)

            # Log the initialization
            logger.debug(f"File logging initialized: {log_file}")

        except Exception as e:
            # If file logging fails, continue with QGIS logging only
            print(f"Warning: Could not initialize file logging: {e}")

        # Prevent propagation to avoid duplicate messages
        logger.propagate = False

    return logger
