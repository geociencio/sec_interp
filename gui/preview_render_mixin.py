"""Preview rendering mixin for the dialog preview manager."""

from __future__ import annotations

import contextlib

from sec_interp.core.performance_metrics import PerformanceTimer
from sec_interp.core.services.preview_service import PreviewService
from sec_interp.logger_config import get_logger

from .main_dialog_config import DialogConfig

logger = get_logger(__name__)


class PreviewRenderMixin:
    """Render cached preview data and handle zoom-driven LOD updates."""

    def connect_signals(self) -> None:
        """Connect all signals for the preview manager."""
        self.disconnect_signals()

        self.debounce_timer.timeout.connect(self._update_lod_for_zoom)
        self.dialog.preview_widget.canvas.extentsChanged.connect(self._on_extents_changed)

    def disconnect_signals(self) -> None:
        """Disconnect all signals for the preview manager."""
        with contextlib.suppress(TypeError, RuntimeError):
            self.debounce_timer.timeout.disconnect()

        with contextlib.suppress(AttributeError, TypeError, RuntimeError):
            self.dialog.preview_widget.canvas.extentsChanged.disconnect(self._on_extents_changed)

    def _run_render_pipeline(self, result) -> None:
        """Orchestrate the rendering of generated data.

        Args:
            result: The preview data to render.

        """
        if not self.dialog.plugin_instance:
            self._handle_invalid_plugin_instance()
            return

        try:
            with PerformanceTimer("Rendering", self.metrics):
                self._render_cached_data()
        except (AttributeError, TypeError, ValueError) as e:
            logger.exception(f"Rendering error: {e}")
            raise ValueError(f"Failed to render preview: {e!s}") from e
        except Exception as e:
            logger.exception("Unexpected rendering pipeline error")
            raise ValueError(f"Critical rendering error: {e!s}") from e

    def _render_cached_data(self, preserve_extent: bool = False) -> None:
        """Re-render the cached preview data using the current options.

        Args:
            preserve_extent: Keep the current canvas extent instead of zooming.

        """
        if not self.dialog.plugin_instance:
            return

        opts = self.dialog.get_preview_options()
        max_points = PreviewService.calculate_max_points(
            canvas_width=self.dialog.preview_widget.canvas.width(),
            manual_max=opts["max_points"],
            auto_lod=opts["auto_lod"],
        )

        self.dialog.plugin_instance.draw_preview(
            self.cached_data["topo"],
            self.cached_data.get("geol"),
            self.cached_data["struct"],
            drillhole_data=self.cached_data["drillhole"],
            max_points=max_points,
            preserve_extent=preserve_extent,
            use_adaptive_sampling=opts["use_adaptive_sampling"],
        )

    def update_from_checkboxes(self) -> None:
        """Update preview when checkboxes change.

        This method re-renders the preview using cached data. Visibility
        filtering is handled by the plugin's draw_preview.
        """
        if not self.last_result:
            return

        try:
            self._render_cached_data()
        except (AttributeError, TypeError, ValueError) as e:
            logger.exception(f"UI Sync error in preview: {e}")
        except Exception:
            logger.exception("Unexpected error updating preview from checkboxes")

    def _on_extents_changed(self) -> None:
        """Handle map canvas extent changes (zoom/pan)."""
        if not self.dialog.preview_widget.chk_auto_lod.isChecked():
            return

        self.debounce_timer.start(DialogConfig.ZOOM_DEBOUNCE_MS)

    def _update_lod_for_zoom(self) -> None:
        """Update preview detail based on current zoom level."""
        if not self.dialog.preview_widget.canvas:
            return
        self._render_cached_data(preserve_extent=True)
