"""Logger Configuration Module.

Provides centralized logging configuration for the Sec Interp plugin.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from qgis.core import Qgis, QgsMessageLog


class ImmediateFlushFileHandler(RotatingFileHandler):
    """File handler that flushes immediately after each write.

    This ensures logs are written to disk before a crash occurs.
    Uses os.fsync() to force OS-level write to disk.
    """

    def emit(self, record):
        super().emit(record)
        self.flush()
        # Force OS-level write to disk (slower but safer for crash analysis)
        try:
            if hasattr(self.stream, "fileno"):
                os.fsync(self.stream.fileno())
        except (OSError, AttributeError):
            # If fsync fails, continue anyway
            pass


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
                # Fallback to standard error for background threads to avoid potential UI hangs
                # sys.stderr is safer and doesn't trigger "print" deviations
                sys.stderr.write(f"[{self.tag}] (BG) {msg}\n")
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
            QgsMessageLog.logMessage(
                f"Warning: Could not initialize file logging: {e}", "SecInterp", Qgis.Warning
            )

        logger.propagate = False

    return logger


def log_critical_operation(logger, operation_name, **context):
    """Log a critical operation with maximum persistence.

    Use this before operations that might crash QGIS (e.g., canvas operations,
    rubber band manipulation, tool activation).

    Args:
        logger: Logger instance
        operation_name: Name of the operation
        **context: Additional context to log

    """
    import datetime

    msg = f"CRITICAL_OP: {operation_name}"
    if context:
        ctx_str = ", ".join(f"{k}={v}" for k, v in context.items())
        msg += f" | {ctx_str}"

    # Log through normal channels
    logger.debug(msg)

    # Also write directly to stderr with timestamp (bypasses all buffering)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    sys.stderr.write(f"[{timestamp}] {msg}\n")
    sys.stderr.flush()

    # Try to force OS sync on stderr too
    try:
        if hasattr(sys.stderr, "fileno"):
            os.fsync(sys.stderr.fileno())
    except (OSError, AttributeError):
        pass
