"""Lifecycle and cleanup mixin for the SecInterp main dialog."""

from __future__ import annotations

import contextlib
from typing import Any

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class DialogLifecycleMixin:
    """Wheel handling and deterministic resource cleanup on close."""

    def wheelEvent(self, event: Any) -> None:
        """Handle mouse wheel for zooming in preview via navigation_manager."""
        if self.navigation_manager.handle_wheel_event(event):
            return
        super().wheelEvent(event)

    def closeEvent(self, event: Any) -> None:
        """Handle dialog close event to clean up all resources."""
        if self._save_on_close:
            self.state_manager.save_settings()

        self._cleanup_resources()

        with contextlib.suppress(AttributeError, RuntimeError, TypeError):
            super().closeEvent(event)

    def _cleanup_resources(self) -> None:
        """Clean up map tools, managers, signals, and components."""
        logger.info("Closing dialog, cleaning up resources...")
        self._cleanup_map_tools()
        self._cleanup_managers()
        self._cleanup_signals_and_components()

    def _cleanup_map_tools(self) -> None:
        """Clean up active map tools and reset their states."""
        if hasattr(self, "tool_manager") and self.tool_manager:
            with contextlib.suppress(Exception):
                if self.tool_manager.measure_tool:
                    self.tool_manager.measure_tool.cleanup_finalized()
                if self.tool_manager.interpretation_tool:
                    self.tool_manager.interpretation_tool.reset()
            logger.debug("Map tools cleaned up")

    def _cleanup_managers(self) -> None:
        """Clean up all manager instances and save their data."""
        with contextlib.suppress(Exception):
            self.interpretation_manager.save_interpretations()
            self.preview_manager.cleanup()
        logger.debug("Managers cleaned up")

    def _cleanup_signals_and_components(self) -> None:
        """Disconnect all signals and clean up UI components."""
        if hasattr(self, "signal_manager"):
            self.signal_manager.disconnect_all()
        logger.debug("Signals disconnected")

        if hasattr(self, "legend_widget") and self.legend_widget:
            with contextlib.suppress(Exception):
                self.legend_widget.cleanup()
