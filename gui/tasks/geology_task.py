"""Task for async geology generation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qgis.core import Qgis, QgsMessageLog, QgsTask
from qgis.PyQt.QtCore import QTimer, pyqtSignal

from sec_interp.core.domain import GeologyData, GeologyTaskInput
from sec_interp.logger_config import get_logger

if TYPE_CHECKING:
    from sec_interp.core.services.geology_service import GeologyService

logger = get_logger(__name__)


class GeologyGenerationTask(QgsTask):
    """Background task for generating geological profiles.

    This task executes the geometric intersection logic in a separate thread,
    using only detached data (DTOs) to ensure thread safety.
    """

    # Signals
    finished_with_results = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    progress_changed = pyqtSignal(float)

    def __init__(
        self,
        description: str,
        task_input: GeologyTaskInput,
        service: GeologyService,
        params: Any,
    ) -> None:
        """Initialize the task.

        Args:
            description: Description of the task.
            task_input: The detached data input DTO.
            service: The GeologyService instance (stateless logic).
            params: Original params for context (backward compatibility).

        """
        super().__init__(description, QgsTask.CanCancel)
        self.service = service
        self.task_input = task_input
        self.params = params

        self.result: GeologyData | None = None
        self.exception: Exception | None = None

    def run(self) -> bool:
        """Execute the task in background thread."""
        try:
            logger.info("GeologyGenerationTask started (Background Thread)")
            # Passing self as feedback object (has isCanceled and setProgress)
            self.result = self.service.process_task_data(self.task_input, feedback=self)
            logger.info(f"GeologyGenerationTask finished with {len(self.result)} segments")
            return True

        except Exception as e:
            logger.error(f"Error in GeologyGenerationTask: {e}", exc_info=True)
            self.exception = e
            return False

    def finished(self, is_successful: bool) -> None:
        """Handle task completion on Main Thread."""
        logger.debug(f"GeologyGenerationTask.finished() called. Success: {is_successful}")
        try:
            if is_successful:
                if self.result is None:
                    self.result = []

                res_type = type(self.result)
                res_len = len(self.result) if isinstance(self.result, list) else "N/A"
                logger.debug(
                    f"Emitting finished_with_results deferred. Type: {res_type}, Len: {res_len}"
                )

                # Defer emission to avoid race conditions during task management overhead
                QTimer.singleShot(0, lambda: self.finished_with_results.emit(self.result))
                logger.debug("Deferred emission scheduled")
            elif self.exception:
                error_msg = str(self.exception)
                logger.error(f"Geology Task Exception: {error_msg}")
                QgsMessageLog.logMessage(
                    f"Geology Task Failed: {error_msg}",  # no-i18n: developer log tag
                    "SecInterp",
                    Qgis.Critical,
                )
                self.error_occurred.emit(error_msg)
        except Exception as e:
            logger.exception(f"Critical error in GeologyGenerationTask.finished: {e}")

    def setProgress(self, progress: float) -> None:
        """Override to emit signal."""
        super().setProgress(progress)
        self.progress_changed.emit(progress)
