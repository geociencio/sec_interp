"""Task for async drillhole generation."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from qgis.core import Qgis, QgsMessageLog, QgsTask

from sec_interp.core.types import DrillholeTaskInput
from sec_interp.logger_config import get_logger

if TYPE_CHECKING:
    from sec_interp.core.services.drillhole_service import DrillholeService

logger = get_logger(__name__)


class DrillholeGenerationTask(QgsTask):
    """Background task for generating drillhole traces/intervals.

    This task executes the projection and intersection logic in a separate thread,
    using only detached data (DTOs) ensuring thread safety.
    """

    def __init__(
        self,
        service: DrillholeService,
        task_input: DrillholeTaskInput,
        on_finished: Callable[[Any], None],
        on_error: Callable[[str], None] | None = None,
    ):
        """Initialize the task.

        Args:
            service: The DrillholeService instance (stateless logic).
            task_input: The detached data input DTO.
            on_finished: Callback function to receive results (drillhole tuple).
            on_error: Optional callback for error handling.

        """
        super().__init__("SecInterp: Generating Drillholes", QgsTask.CanCancel)
        self.service = service
        self.task_input = task_input
        self.on_finished_callback = on_finished
        self.on_error_callback = on_error

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
            self.on_finished_callback(self.result)
        elif self.exception:
            error_msg = str(self.exception)
            QgsMessageLog.logMessage(
                f"Drillhole Task Failed: {error_msg}", "SecInterp", Qgis.Critical
            )
            if self.on_error_callback:
                self.on_error_callback(error_msg)
