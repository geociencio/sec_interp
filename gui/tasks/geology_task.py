from __future__ import annotations

"""Task for async geology generation."""

from collections.abc import Callable
from typing import TYPE_CHECKING

from qgis.core import Qgis, QgsMessageLog, QgsTask

from sec_interp.core.types import GeologyData, GeologyTaskInput
from sec_interp.logger_config import get_logger

if TYPE_CHECKING:
    from sec_interp.core.services.geology_service import GeologyService

logger = get_logger(__name__)


class GeologyGenerationTask(QgsTask):
    """Background task for generating geological profiles.

    This task executes the geometric intersection logic in a separate thread,
    using only detached data (DTOs) to ensure thread safety.
    """

    def __init__(
        self,
        service: GeologyService,
        task_input: GeologyTaskInput,
        on_finished: Callable[[GeologyData], None],
        on_error: Callable[[str], None] | None = None,
    ):
        """Initialize the task.

        Args:
            service: The GeologyService instance (stateless logic).
            task_input: The detached data input DTO.
            on_finished: Callback function to receive results (list of segments).
            on_error: Optional callback for error handling.

        """
        super().__init__("SecInterp: Generating Geology", QgsTask.CanCancel)
        self.service = service
        self.task_input = task_input
        self.on_finished_callback = on_finished
        self.on_error_callback = on_error

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
                # Should not happen if run returns True
                self.result = []
            self.on_finished_callback(self.result)
        elif self.exception:
            error_msg = str(self.exception)
            QgsMessageLog.logMessage(
                f"Geology Task Failed: {error_msg}", "SecInterp", Qgis.Critical
            )
            if self.on_error_callback:
                self.on_error_callback(error_msg)
