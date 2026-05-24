"""Task for async drillhole generation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qgis.core import Qgis, QgsMessageLog, QgsTask
from qgis.PyQt.QtCore import QTimer, pyqtSignal

from sec_interp.core.domain import DrillholeTaskInput
from sec_interp.logger_config import get_logger

if TYPE_CHECKING:
    from sec_interp.core.services.drillhole.drillhole_orchestrator import (
        DrillholeTaskOrchestrator,
    )

logger = get_logger(__name__)


class DrillholeGenerationTask(QgsTask):
    """Background task for generating drillhole traces/intervals.

    This task executes the projection and intersection logic in a separate thread,
    using only detached data (DTOs) ensuring thread safety.
    """

    # Signals
    finished_with_results = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    progress_changed = pyqtSignal(float)

    def __init__(
        self,
        description: str,
        task_input: DrillholeTaskInput,
        orchestrator: DrillholeTaskOrchestrator,
        params: Any,
    ) -> None:
        """Initialize the task.

        Args:
            description: Description of the task.
            task_input: The detached data input DTO.
            orchestrator: The DrillholeTaskOrchestrator instance.
            params: Original params for context (backward compatibility).

        """
        super().__init__(description, QgsTask.CanCancel)
        self.orchestrator = orchestrator
        self.task_input = task_input
        self.params = params

        # Result is tuple (geol_data_all, drillhole_data_all)
        self.result: Any | None = None
        self.exception: Exception | None = None

    def run(self) -> bool:
        """Execute the task in background thread."""
        try:
            logger.info("DrillholeGenerationTask started (Background Thread)")
            self.result = self.orchestrator.process_task_data(self.task_input, feedback=self)

            count = 0
            if self.result and len(self.result) > 1:
                # result[1] is drillhole_data_list
                count = len(self.result[1])

            logger.info(f"DrillholeGenerationTask finished with {count} holes")
            return True

        except Exception as e:
            logger.error(f"Error in DrillholeGenerationTask: {e}", exc_info=True)
            self.exception = e
            return False

    def finished(self, is_successful: bool) -> None:
        """Handle task completion on Main Thread."""
        logger.debug(f"DrillholeGenerationTask.finished() called. Success: {is_successful}")
        try:
            if is_successful:
                if self.result is None:
                    self.result = ([], [])

                res_type = type(self.result)
                res_len = len(self.result) if isinstance(self.result, tuple | list) else "N/A"
                logger.debug(
                    f"Emitting finished_with_results deferred. Type: {res_type}, Len: {res_len}"
                )

                # Defer emission to next event loop cycle to avoid race conditions with geology render
                QTimer.singleShot(0, lambda: self.finished_with_results.emit(self.result))
                logger.debug("Deferred emission scheduled")
            elif self.exception:
                error_msg = str(self.exception)
                logger.error(f"Drillhole Task Exception: {error_msg}")
                QgsMessageLog.logMessage(
                    f"Drillhole Task Failed: {error_msg}",  # no-i18n: developer log tag
                    "SecInterp",
                    Qgis.Critical,
                )
                self.error_occurred.emit(error_msg)
        except Exception as e:
            logger.exception(f"Critical error in DrillholeGenerationTask.finished: {e}")

    def setProgress(self, progress: float) -> None:
        """Override to emit signal for UI progress bar."""
        super().setProgress(progress)
        self.progress_changed.emit(progress)
