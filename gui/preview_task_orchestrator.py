"""Orchestrator for background preview generation tasks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qgis.core import QgsApplication

from .tasks.drillhole_task import DrillholeGenerationTask
from .tasks.geology_task import GeologyGenerationTask

if TYPE_CHECKING:
    from .main_dialog_preview import PreviewManager


class PreviewTaskOrchestrator:
    """Manages asynchronous geology and drillhole generation tasks."""

    def __init__(self, manager: PreviewManager):
        """Initialize the orchestrator with its parent manager.

        Args:
            manager: The preview manager owning this orchestrator.

        """
        self.manager = manager
        self.geology_task: GeologyGenerationTask | None = None
        self.drillhole_task: DrillholeGenerationTask | None = None

    def cancel_active_tasks(self) -> None:
        """Cancel any existing async work."""
        import contextlib

        if self.geology_task:
            with contextlib.suppress(RuntimeError):
                self.geology_task.cancel()
            self.geology_task = None

        if self.drillhole_task:
            with contextlib.suppress(RuntimeError):
                self.drillhole_task.cancel()
            self.drillhole_task = None

    def start_geology_task(self, params: Any, service: Any) -> None:
        """Launch background geology generation."""
        if self.geology_task:
            self.geology_task.cancel()

        task_input = service.prepare_task_input(
            params.line_layer,
            params.raster_layer,
            params.outcrop_layer,
            params.outcrop_name_field,
            params.band_num,
        )

        self.geology_task = GeologyGenerationTask(
            "Geology Preview (Async)",
            task_input,
            service,
            params,
        )

        # Connect signals
        self.geology_task.finished_with_results.connect(self.manager._on_geology_finished)
        self.geology_task.progress_changed.connect(self.manager._on_geology_progress)
        self.geology_task.error_occurred.connect(self.manager._on_geology_error)

        QgsApplication.taskManager().addTask(self.geology_task)

    def start_drillhole_task(self, params: Any, service: Any) -> None:
        """Launch background drillhole generation."""
        if self.drillhole_task:
            self.drillhole_task.cancel()

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
            params.line_layer,
            params.buffer_dist,
            params.collar_layer,
            params.collar_id_field,
            params.collar_use_geometry,
            params.collar_x_field,
            params.collar_y_field,
            params.collar_z_field,
            params.collar_depth_field,
            params.survey_layer,
            survey_fields_dict,
            params.interval_layer,
            interval_fields_dict,
            params.raster_layer,
            params.band_num,
        )

        self.drillhole_task = DrillholeGenerationTask(
            "Drillhole Preview (Async)",
            task_input,
            service,
            params,
        )

        self.drillhole_task.finished_with_results.connect(self.manager._on_drillhole_finished)
        self.drillhole_task.error_occurred.connect(self.manager._on_drillhole_error)

        QgsApplication.taskManager().addTask(self.drillhole_task)
