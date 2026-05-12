"""Orchestrator for background preview generation tasks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qgis.core import QgsApplication

from sec_interp.core.utils.qgis import resolve_layer
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

from .tasks.drillhole_task import DrillholeGenerationTask  # noqa: E402
from .tasks.geology_task import GeologyGenerationTask  # noqa: E402

if TYPE_CHECKING:
    from .main_dialog_preview import PreviewManager


class PreviewTaskOrchestrator:
    """Manages asynchronous geology and drillhole generation tasks."""

    def __init__(self, manager: PreviewManager) -> None:
        """Initialize the orchestrator with its parent manager.

        Args:
            manager: The preview manager owning this orchestrator.

        """
        self.manager = manager
        self.geology_task: GeologyGenerationTask | None = None
        self.drillhole_task: DrillholeGenerationTask | None = None

        # Anchor tasks to prevent GC issues in QGIS 4/Qt6
        self._active_tasks: set[Any] = set()

    def cancel_active_tasks(self) -> None:
        """Cancel any existing async work and clear anchors."""
        import contextlib

        for task in list(self._active_tasks):
            if task:
                with contextlib.suppress(RuntimeError):
                    task.cancel()
                try:
                    task.finished_with_results.disconnect()
                    task.progress_changed.disconnect()
                    task.error_occurred.disconnect()
                except (TypeError, RuntimeError):
                    pass

        self._active_tasks.clear()
        self.geology_task = None
        self.drillhole_task = None

    def remove_task(self, task: Any) -> None:
        """Safely remove a task from active anchors."""
        if task in self._active_tasks:
            self._active_tasks.remove(task)
            logger.debug(f"Task removed from anchors: {task}")

    def start_geology_task(self, params: Any, service: Any) -> None:
        """Launch background geology generation."""
        if self.geology_task:
            self.geology_task.cancel()

        # Resolve layer IDs to actual layer objects
        line_lyr = resolve_layer(params.line_layer)
        raster_lyr = resolve_layer(params.raster_layer)
        outcrop_lyr = resolve_layer(params.outcrop_layer)

        task_input = service.prepare_task_input(
            line_lyr,
            raster_lyr,
            outcrop_lyr,
            params.outcrop_name_field,
            params.band_num,
        )

        self.geology_task = GeologyGenerationTask(
            "Geology Preview (Async)",
            task_input,
            service,
            params,
        )

        # Anchor task
        self._active_tasks.add(self.geology_task)

        # Connect signals
        self.geology_task.finished_with_results.connect(self.manager._on_geology_finished)
        self.geology_task.progress_changed.connect(self.manager._on_geology_progress)
        self.geology_task.error_occurred.connect(self.manager._on_geology_error)

        logger.debug(f"Adding Geology task to manager: {self.geology_task}")
        QgsApplication.taskManager().addTask(self.geology_task)

    def start_drillhole_task(self, params: Any, service: Any) -> None:
        """Launch background drillhole generation."""
        if self.drillhole_task:
            self.drillhole_task.cancel()

        # Resolve layer IDs to actual layer objects
        line_lyr = resolve_layer(params.line_layer)
        collar_lyr = resolve_layer(params.collar_layer)
        survey_lyr = resolve_layer(params.survey_layer)
        interval_lyr = resolve_layer(params.interval_layer)
        raster_lyr = resolve_layer(params.raster_layer)

        survey_fields_dict = {
            "id": params.survey_id_field,
            "depth": params.survey_depth_field,
            "azim": params.survey_azim_field,
            "incl": params.survey_incl_field,
        }
        interval_fields_dict = {
            "id": params.interval_id_field,
            "from": params.interval_from_field,
            "to": params.interval_to_field,
            "lith": params.interval_lith_field,
        }

        task_input = service.prepare_task_input(
            line_lyr,
            params.buffer_dist,
            collar_lyr,
            params.collar_id_field,
            params.collar_use_geometry,
            params.collar_x_field,
            params.collar_y_field,
            params.collar_z_field,
            params.collar_depth_field,
            survey_lyr,
            survey_fields_dict,
            interval_lyr,
            interval_fields_dict,
            raster_lyr,
            params.band_num,
        )

        self.drillhole_task = DrillholeGenerationTask(
            "Drillhole Preview (Async)",
            task_input,
            service,
            params,
        )

        # Anchor task
        self._active_tasks.add(self.drillhole_task)

        self.drillhole_task.finished_with_results.connect(self.manager._on_drillhole_finished)
        self.drillhole_task.progress_changed.connect(self.manager._on_drillhole_progress)
        self.drillhole_task.error_occurred.connect(self.manager._on_drillhole_error)

        logger.debug(f"Adding Drillhole task to manager: {self.drillhole_task}")
        QgsApplication.taskManager().addTask(self.drillhole_task)
