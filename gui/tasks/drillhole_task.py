"""Task for async drillhole generation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qgis.core import Qgis, QgsMessageLog, QgsTask
from qgis.PyQt.QtCore import pyqtSignal

from sec_interp.core.domain import DrillholeTaskInput
from sec_interp.logger_config import get_logger

if TYPE_CHECKING:
    from sec_interp.core.services.drillhole_service import DrillholeService

logger = get_logger(__name__)


class DrillholeGenerationTask(QgsTask):
    """Background task for generating drillhole traces/intervals.

    This task executes the projection and intersection logic in a separate thread,
    using only detached data (DTOs) ensuring thread safety.
    """

    # Signals
    finished_with_results = pyqtSignal(object)
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        description: str,
        task_input: DrillholeTaskInput,
        service: DrillholeService,
        params: Any,
    ):
        """Initialize the task.

        Args:
            description: Description of the task.
            task_input: The detached data input DTO.
            service: The DrillholeService instance (stateless logic).
            params: Original params for context (backward compatibility).

        """
        super().__init__(description, QgsTask.CanCancel)
        self.service = service
        self.task_input = task_input
        self.params = params

        # Result is tuple (geol_data_all, drillhole_data_all)
        self.result: Any | None = None
        self.exception: Exception | None = None

    def run(self) -> bool:
        """Execute the task in background thread."""
        try:
            logger.info("DrillholeGenerationTask started (Background Thread)")
            self.result = self.service.process_task_data(self.task_input, feedback=self)

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

    def finished(self, result: bool):
        """Handle task completion on Main Thread."""
        if result:
            if self.result is None:
                self.result = ([], [])
            self.finished_with_results.emit(self.result)
        elif self.exception:
            error_msg = str(self.exception)
            QgsMessageLog.logMessage(
                f"Drillhole Task Failed: {error_msg}", "SecInterp", Qgis.Critical
            )
            self.error_occurred.emit(error_msg)
