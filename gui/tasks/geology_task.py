"""Task for async geology generation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qgis.core import Qgis, QgsMessageLog, QgsTask
from qgis.PyQt.QtCore import pyqtSignal

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
    ):
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

    def finished(self, result: bool):
        """Handle task completion on Main Thread."""
        if result:
            if self.result is None:
                self.result = []
            self.finished_with_results.emit(self.result)
        elif self.exception:
            error_msg = str(self.exception)
            QgsMessageLog.logMessage(
                f"Geology Task Failed: {error_msg}", "SecInterp", Qgis.Critical
            )
            self.error_occurred.emit(error_msg)

    def setProgress(self, progress: float):
        """Override to emit signal."""
        super().setProgress(progress)
        self.progress_changed.emit(progress)
