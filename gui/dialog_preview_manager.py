"""Preview management module for SecInterp main dialog.

This module handles preview generation, rendering, and updates,
separating preview logic from the main dialog class. Async callbacks and the
render pipeline live in dedicated mixins.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from qgis.core import QgsVectorLayer
from qgis.PyQt.QtCore import QTimer

from sec_interp.core.domain import (
    PreviewParams,
    PreviewResult,
)
from sec_interp.core.exceptions import SecInterpError
from sec_interp.core.interfaces.preview_interface import IPreviewService
from sec_interp.core.performance_metrics import (
    MetricsCollector,
    PerformanceTimer,
)
from sec_interp.core.services.preview_service import PreviewService
from sec_interp.core.services.vertical_exaggeration_service import (
    VerticalExaggerationService,
)
from sec_interp.core.utils.i18n import TranslatableMixin
from sec_interp.gui.adapters.geometry import resolve_section_geometry
from sec_interp.gui.adapters.layer_resolver import resolve_layer
from sec_interp.gui.preview_callbacks_mixin import PreviewCallbacksMixin
from sec_interp.gui.preview_render_mixin import PreviewRenderMixin
from sec_interp.logger_config import get_logger

from .main_dialog_config import DialogConfig
from .preview_param_hasher import PreviewParamHasher, assemble_preview_params
from .preview_reporter import PreviewReporter
from .preview_state import PreviewCache
from .preview_task_orchestrator import PreviewTaskOrchestrator

logger = get_logger(__name__)

VE_EPSILON = 1e-6


class PreviewManager(TranslatableMixin, PreviewCallbacksMixin, PreviewRenderMixin):
    """Manages preview generation and rendering for the dialog.

    This class encapsulates all preview-related logic, including data
    generation, rendering, and updates based on user interactions.
    """

    def __init__(
        self,
        dialog: Any,
        preview_service: IPreviewService | None = None,
        cache: PreviewCache | None = None,
        ve_service: VerticalExaggerationService | None = None,
    ) -> None:
        """Initialize preview manager with specialized components."""
        self.dialog = dialog
        self.preview_service = preview_service or PreviewService(
            self.dialog.plugin_instance.controller
        )
        self.metrics = MetricsCollector()
        self.ve_service = ve_service or VerticalExaggerationService()

        self.orchestrator = PreviewTaskOrchestrator(self)
        self.hasher = PreviewParamHasher()

        self.cached_data = cache if cache is not None else PreviewCache()
        self.last_params_hash: str | None = None
        self.last_result: PreviewResult | None = None
        self.last_success_hash: str | None = None
        self.last_success_ve: float | None = None

        self._on_interpretations_cleared: Callable[[], None] | None = None

        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)

        self.connect_signals()

    def set_interpretations_cleared_handler(self, handler: Callable[[], None]) -> None:
        """Register the callback invoked when section geometry changes.

        Args:
            handler: Callable that clears persisted interpretations.

        """
        self._on_interpretations_cleared = handler

    def cleanup(self) -> None:
        """Clean up resources and stop background tasks."""
        self.orchestrator.cancel_active_tasks()
        self.debounce_timer.stop()
        self.last_success_hash = None
        self.last_success_ve = None
        self.last_result = None
        self.disconnect_signals()

    def is_preview_current(self) -> bool:
        """Check whether the last successful preview matches the current inputs.

        Fail-closed: without a successful generation (or on any assembly
        failure) the dependent buttons stay disabled. Assembly is
        side-effect free (no validation dialogs, no notification wiring,
        no geometry reads).
        """
        if self.last_success_hash is None or self.last_result is None:
            return False
        try:
            values = self.dialog.get_selected_values()
            options = self.dialog.get_preview_options()
            width = self.dialog.preview_widget.canvas.width()
            params = assemble_preview_params(values, options, width)
            current_ve, _mode = self._compute_vertical_exaggeration()
        except Exception:
            return False
        if self.last_success_ve is None or abs(current_ve - self.last_success_ve) > VE_EPSILON:
            return False
        return self._calculate_params_hash(params) == self.last_success_hash

    def generate_preview(self) -> tuple[bool, str]:
        """Generate complete preview with all available data layers."""
        self.metrics.clear()

        try:
            with PerformanceTimer("Total Preview Generation", self.metrics):
                params = self.dialog.plugin_instance._get_and_validate_inputs()
                if not params:
                    return False, self.tr("Invalid configuration")

                result = self._process_preview_data(params)
                self._update_ui_state(params, result)

        except SecInterpError as e:
            self.dialog.handle_error(e, self.dialog.tr("Preview Error"))
            return False, str(e)
        except (AttributeError, TypeError, ValueError) as e:
            logger.exception("Unexpected UI error during preview generation")
            self.dialog.handle_error(e, self.dialog.tr("Unexpected Preview Error"))
            return False, str(e)
        except Exception as e:
            logger.exception("Critical unexpected error in preview generation")
            self.dialog.handle_error(e, self.dialog.tr("Critical Error"))
            return False, str(e)
        else:
            return True, self.tr("Preview generated successfully")

    def _update_ui_state(self, params: PreviewParams, result: PreviewResult) -> None:
        """Update UI and trigger render pipeline."""
        line_lyr = resolve_layer(params.line_layer)
        self._update_crs_label(line_lyr)
        self._run_render_pipeline(result)

        auto_vert_exag = self.dialog.page_dem.auto_ve_check.isChecked()
        vert_exag = self._resolve_vertical_exaggeration()
        self.dialog.page_dem.set_auto_ve(vert_exag if auto_vert_exag else None)
        result_msg = PreviewReporter.format_results_message(
            result,
            self.metrics,
            vert_exag=vert_exag,
            auto_vert_exag=auto_vert_exag,
        )
        self.dialog.preview_widget.results_text.setPlainText(result_msg)

        if DialogConfig.LOG_DETAILED_METRICS:
            logger.info(f"Preview Performance: {self.metrics.get_summary()}")

        self.last_success_hash = self._calculate_params_hash(params)
        self.last_success_ve = vert_exag
        self.dialog.state_manager.update_button_state()

    def _process_preview_data(self, params: PreviewParams) -> PreviewResult:
        """Process or retrieve cached preview data."""
        if self._is_data_unchanged(params):
            logger.info("Using cached data (params unchanged)")
            return self.last_result

        self._handle_geometric_changes(params)
        transform_context = self._get_transform_context()

        result = self.preview_service.generate_all(params, transform_context)

        self._update_cache_and_metrics(result)
        self._cancel_active_tasks()
        self._trigger_async_updates(params)

        self.last_result = result
        return result

    def _get_transform_context(self) -> Any:
        """Safely retrieve transform context from canvas."""
        if not self.dialog.plugin_instance:
            return None
        return self.dialog.plugin_instance.iface.mapCanvas().mapSettings().transformContext()

    def _update_cache_and_metrics(self, result: PreviewResult) -> None:
        """Update local cache and cumulative metrics."""
        self.cached_data.update(
            {
                "topo": result.topo,
                "geol": result.geol,
                "struct": result.struct,
                "drillhole": result.drillhole,
            }
        )
        self.metrics.timings.update(result.metrics.timings)
        self.metrics.counts.update(result.metrics.counts)

    def _trigger_async_updates(self, params: PreviewParams) -> None:
        """Launch background tasks via orchestrator."""
        self.orchestrator.start_geology_task(params, self.preview_service.geology_service)
        self.orchestrator.start_drillhole_task(
            params,
            self.preview_service.drillhole_service,
            self.preview_service.controller.drillhole_extractor,
        )

    def _is_data_unchanged(self, params: PreviewParams) -> bool:
        """Check if parameters haven't changed since last generation."""
        current_hash = self._calculate_params_hash(params)
        unchanged = current_hash == self.last_params_hash
        self.last_params_hash = current_hash
        return unchanged and self.last_result is not None

    def _handle_geometric_changes(self, params: PreviewParams) -> None:
        """Clear interpretations if the section geometry has changed."""
        old_geo_params = getattr(self, "_last_geo_params", None)
        line_lyr = resolve_layer(params.line_layer)
        section_geom = resolve_section_geometry(
            line_lyr, getattr(params, "section_feature_id", None)
        )
        line_geom = section_geom.asWkt() if section_geom else None

        new_geo_params = (
            params.line_layer,
            params.raster_layer,
            line_geom,
        )
        self._last_geo_params = new_geo_params

        if old_geo_params and old_geo_params != new_geo_params:
            logger.info("Geometric change detected: Clearing interpretations.")
            if self._on_interpretations_cleared:
                self._on_interpretations_cleared()

    def _cancel_active_tasks(self) -> None:
        """Cancel any existing async work via orchestrator."""
        self.orchestrator.cancel_active_tasks()

    def _calculate_params_hash(self, params: PreviewParams) -> str:
        """Analyze params via hasher."""
        return self.hasher.calculate_hash(params)

    def _handle_invalid_plugin_instance(self) -> None:
        """Handle case where plugin instance is not available for rendering."""
        logger.error("Plugin instance not available in PreviewManager")
        raise AttributeError("Plugin instance or draw_preview method not available")

    def _update_crs_label(self, layer: QgsVectorLayer | None) -> None:
        """Update the CRS label in the dialog status bar.

        Args:
            layer: The reference layer to get CRS from.

        """
        try:
            if layer and layer.isValid():
                auth_id = layer.crs().authid()
                self.dialog.preview_widget.lbl_crs.setText(self.tr("CRS: {}").format(auth_id))
            else:
                self.dialog.preview_widget.lbl_crs.setText(self.tr("CRS: None"))
        except (AttributeError, TypeError, ValueError):
            self.dialog.preview_widget.lbl_crs.setText(self.tr("CRS: Unknown"))
        except Exception:
            logger.exception("Unexpected error updating CRS label")
