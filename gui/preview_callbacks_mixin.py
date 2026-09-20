"""Async task callback mixin for the dialog preview manager."""

from __future__ import annotations

from typing import Any

from sec_interp.core.domain import PreviewResult
from sec_interp.core.exceptions import ProcessingError, SecInterpError
from sec_interp.logger_config import get_logger

from .preview_reporter import PreviewReporter

logger = get_logger(__name__)


class PreviewCallbacksMixin:
    """Handle completion, progress and error signals from background tasks."""

    def _get_buffer_distance(self) -> float:
        """Get buffer distance from dialog, with fallback to default.

        Returns:
            Buffer distance in meters

        """
        return self.dialog.page_section.buffer_spin.value()

    def _on_geology_finished(self, results: Any) -> None:
        """Handle completion of geology generation task."""
        logger.debug(f"_on_geology_finished called with results type: {type(results)}")

        try:
            if results and isinstance(results, list):
                self.cached_data["geol"] = results
                logger.info(f"Async geology finished: {len(results)} segments")
            else:
                self.cached_data["geol"] = None
                logger.debug("Geology task returned no results or invalid format.")

            self.update_from_checkboxes()
            self._update_results_display()
            self.orchestrator.remove_task(self.orchestrator.geology_task)
        except (AttributeError, TypeError, ValueError, SecInterpError) as e:
            logger.exception(f"Error updating UI after async geology: {e}")
        except Exception as e:
            logger.exception(f"Unexpected critical error after async geology: {e}")

    def _update_results_display(self) -> None:
        """Update results text and status display based on current cache."""
        topo = self.cached_data.get("topo")
        if not topo:
            return

        result = PreviewResult(
            topo=topo,
            geol=self.cached_data.get("geol"),
            struct=self.cached_data.get("struct"),
            drillhole=self.cached_data.get("drillhole"),
            buffer_dist=self._get_buffer_distance(),
        )
        msg = PreviewReporter.format_results_message(result, self.metrics)
        self.dialog.preview_widget.results_text.setPlainText(msg)

        self.last_result = result

    def _on_geology_progress(self, progress: float) -> None:
        """Handle progress updates from parallel service.

        Args:
            progress: Progress percentage (0-100).

        """
        self.dialog.preview_widget.results_text.setPlainText(
            self.tr("Generating Geology: {}%...").format(progress)
        )

    def _on_geology_error(self, error_msg: str) -> None:
        """Handle error during parallel geology generation."""
        logger.error(f"Geology Task Error: {error_msg}")
        error = ProcessingError(self.tr("Geology processing failed: {}").format(error_msg))
        self.dialog.handle_error(error, self.dialog.tr("Geology Error"))

    def _on_drillhole_progress(self, progress: float) -> None:
        """Handle progress updates from parallel drillhole service."""
        self.dialog.preview_widget.results_text.setPlainText(
            self.tr("Generating Drillholes: {:.1f}%...").format(progress)
        )

    def _on_drillhole_error(self, error_msg: str) -> None:
        """Handle error during parallel drillhole generation."""
        logger.error(f"Drillhole Task Error: {error_msg}")
        error = ProcessingError(self.tr("Drillhole processing failed: {}").format(error_msg))
        self.dialog.handle_error(error, self.dialog.tr("Drillhole Error"))

    def _on_drillhole_finished(self, result: Any) -> None:
        """Handle completion of drillhole task."""
        logger.debug(f"_on_drillhole_finished called with result type: {type(result)}")

        if not result:
            logger.debug("Drillhole task returned no results.")
            return

        MIN_RESULT_PARTS = 2
        try:
            if isinstance(result, tuple) and len(result) >= MIN_RESULT_PARTS:
                _, drill_part = result[:MIN_RESULT_PARTS]
                self.cached_data["drillhole"] = drill_part
                logger.info(f"Async Drillholes finished: {len(drill_part)} holes")
            else:
                logger.warning(f"Unexpected result format from drillhole task: {type(result)}")
                return

            self.update_from_checkboxes()
            self._update_results_display()
            self.orchestrator.remove_task(self.orchestrator.drillhole_task)
        except (AttributeError, TypeError, ValueError, SecInterpError) as e:
            logger.exception(f"Error syncing UI after async drillhole: {e}")
        except Exception as e:
            logger.exception(f"Unexpected critical error after async drillhole: {e}")
