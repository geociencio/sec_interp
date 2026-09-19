"""Map tool management module for SecInterp main dialog.

This module handles the initialization and orchestration of map tools
(pan, measure) used in the preview canvas.
"""

from __future__ import annotations

import contextlib
from collections.abc import Callable
from typing import Any

from qgis.gui import QgsMapTool, QgsMapToolPan

from .tools.interpretation_tool import ProfileInterpretationTool
from .tools.measure_tool import ProfileMeasureTool


class ToolManager:
    """Manages map tools and related event handling for the preview canvas."""

    def __init__(
        self,
        canvas: Any,
        preview_widget: Any,
        translate: Callable[[str], str],
        on_interpretation_finished: Callable[[Any], None],
        update_measurement_display: Callable[[dict], None],
        pan_tool: QgsMapTool | None = None,
        measure_tool: ProfileMeasureTool | None = None,
        interpretation_tool: ProfileInterpretationTool | None = None,
    ) -> None:
        """Initialize tool manager with its collaborators.

        Args:
            canvas: The preview map canvas the tools operate on.
            preview_widget: The preview widget (buttons, results area).
            translate: Translation function (dialog ``tr``).
            on_interpretation_finished: Callback for finished polygons.
            update_measurement_display: Callback to display measurements.
            pan_tool: Optional pan tool for injection.
            measure_tool: Optional measure tool for injection.
            interpretation_tool: Optional interpretation tool for injection.

        """
        self.canvas = canvas
        self.preview_widget = preview_widget
        self.tr = translate
        self.on_interpretation_finished = on_interpretation_finished
        self._update_measurement_display_cb = update_measurement_display
        self.pan_tool = pan_tool
        self.measure_tool = measure_tool
        self.interpretation_tool = interpretation_tool

    def initialize_tools(self) -> None:
        """Create and configure map tools if not already provided."""
        if not self.pan_tool:
            self.pan_tool = QgsMapToolPan(self.canvas)
        if not self.measure_tool:
            self.measure_tool = ProfileMeasureTool(self.canvas)
        if not self.interpretation_tool:
            self.interpretation_tool = ProfileInterpretationTool(self.canvas)

        self.connect_signals()
        self.canvas.setMapTool(self.pan_tool)

    def connect_signals(self) -> None:
        """Connect map tool signals idempotently."""
        # Always disconnect first to ensure we don't have multiple connections
        self.disconnect_signals()

        if self.interpretation_tool:
            self.interpretation_tool.polygonFinished.connect(self.on_interpretation_finished)

        if self.measure_tool:
            self.measure_tool.measurementChanged.connect(self._update_measurement_display_cb)
            self.measure_tool.measurementFinished.connect(
                lambda: self.preview_widget.btn_measure.setChecked(False)
            )
            self.measure_tool.measurementCleared.connect(self.preview_widget.results_text.clear)

    def toggle_measure_tool(self, checked: bool) -> None:
        """Toggle between measurement and pan tools.

        Args:
            checked: True to activate measure tool, False for pan tool.

        """
        if checked:
            # Reset any previous measurement when starting new one
            self.measure_tool.reset()
            self.canvas.setMapTool(self.measure_tool)
            self.measure_tool.activate()
            # Show finalize button when measurement tool is active
            self.preview_widget.btn_finalize.setVisible(True)
            # Ensure canvas has focus for keyboard events
            self.canvas.setFocus()
        else:
            self.canvas.setMapTool(self.pan_tool)
            self.pan_tool.activate()
            # Hide finalize button when measurement tool is inactive
            self.preview_widget.btn_finalize.setVisible(False)

    def activate_default_tool(self) -> None:
        """Set the default (pan) tool."""
        self.canvas.setMapTool(self.pan_tool)
        self.pan_tool.activate()

    def toggle_interpretation_tool(self, checked: bool) -> None:
        """Toggle between interpretation and pan tools.

        Args:
            checked: True to activate interpretation tool, False for pan tool.

        """
        if checked:
            # Deactivate measure tool if active
            self.preview_widget.btn_measure.setChecked(False)
            # Reset and activate interpretation tool
            self.interpretation_tool.reset()
            self.canvas.setMapTool(self.interpretation_tool)
            self.interpretation_tool.activate()
            # Ensure canvas has focus for keyboard events
            self.canvas.setFocus()
        else:
            self.canvas.setMapTool(self.pan_tool)
            self.pan_tool.activate()

    def update_measurement_display(self, metrics: dict[str, Any]) -> None:
        """Display measurement results from multi-point tool.

        Args:
            metrics: Dictionary containing measurement data.

        """
        MIN_POINT_COUNT = 2
        if not metrics or metrics.get("point_count", 0) < MIN_POINT_COUNT:
            return

        total_dist = metrics.get("total_distance", 0)
        horiz_dist = metrics.get("horizontal_distance", 0)
        elev_change = metrics.get("elevation_change", 0)
        avg_slope = metrics.get("avg_slope", 0)
        seg_count = metrics.get("segment_count", 0)
        point_count = metrics.get("point_count", 0)

        # Format result text with HTML for better presentation
        msg = (
            f"<b>{self.tr('Multi-Point Measurement')}</b><br>"
            f"<b>{self.tr('Points')}:</b> {point_count} | <b>{self.tr('Segments')}:</b> {seg_count}<br>"
            f"<b>{self.tr('Total Distance')}:</b> {total_dist:.2f} m<br>"
            f"<b>{self.tr('Horizontal Distance')}:</b> {horiz_dist:.2f} m<br>"
            f"<b>{self.tr('Elevation Change')}:</b> {elev_change:+.2f} m<br>"
            f"<b>{self.tr('Average Slope')}:</b> {avg_slope:.1f}°"
        )
        self.preview_widget.results_text.setHtml(msg)
        # Ensure results group is expanded
        self.preview_widget.results_group.setCollapsed(False)

    def disconnect_signals(self) -> None:
        """Disconnect all signals to prevent memory leaks."""
        if self.interpretation_tool:
            with contextlib.suppress(TypeError, RuntimeError):
                self.interpretation_tool.polygonFinished.disconnect()
        if self.measure_tool:
            with contextlib.suppress(TypeError, RuntimeError):
                self.measure_tool.measurementChanged.disconnect()
            with contextlib.suppress(TypeError, RuntimeError):
                self.measure_tool.measurementFinished.disconnect()
            with contextlib.suppress(TypeError, RuntimeError):
                self.measure_tool.measurementCleared.disconnect()


class NavigationManager:
    """Handles navigation events (zooming) for the preview canvas."""

    def __init__(self, canvas: Any) -> None:
        """Initialize navigation manager.

        Args:
            canvas: The preview map canvas to navigate.

        """
        self.canvas = canvas

    def handle_wheel_event(self, event: Any) -> bool:
        """Handle mouse wheel for zooming in preview canvas.

        Args:
            event: The mouse wheel event.

        Returns:
            bool: True if event was handled, False otherwise.

        """
        if self.canvas.underMouse():
            if event.angleDelta().y() > 0:
                self.canvas.zoomIn()
            else:
                self.canvas.zoomOut()
            event.accept()
            return True
        return False
