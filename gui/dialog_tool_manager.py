"""Map tool management module for SecInterp main dialog.

This module handles the initialization and orchestration of map tools
(pan, measure) used in the preview canvas.
"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

from qgis.gui import QgsMapTool, QgsMapToolPan

from .tools.interpretation_tool import ProfileInterpretationTool
from .tools.measure_tool import ProfileMeasureTool

if TYPE_CHECKING:
    from .main_dialog import SecInterpDialog


class ToolManager:
    """Manages map tools and related event handling for the preview canvas."""

    def __init__(
        self,
        dialog: SecInterpDialog,
        pan_tool: QgsMapTool | None = None,
        measure_tool: ProfileMeasureTool | None = None,
        interpretation_tool: ProfileInterpretationTool | None = None,
    ) -> None:
        """Initialize tool manager with reference to parent dialog.

        Args:
            dialog: The :class:`sec_interp.gui.main_dialog.SecInterpDialog` instance
            pan_tool: Optional pan tool for injection
            measure_tool: Optional measure tool for injection
            interpretation_tool: Optional interpretation tool for injection

        """
        self.dialog = dialog
        self.pan_tool = pan_tool
        self.measure_tool = measure_tool
        self.interpretation_tool = interpretation_tool

    def initialize_tools(self) -> None:
        """Create and configure map tools if not already provided."""
        if not self.pan_tool:
            self.pan_tool = QgsMapToolPan(self.dialog.preview_widget.canvas)
        if not self.measure_tool:
            self.measure_tool = ProfileMeasureTool(self.dialog.preview_widget.canvas)
        if not self.interpretation_tool:
            self.interpretation_tool = ProfileInterpretationTool(self.dialog.preview_widget.canvas)

        self.connect_signals()
        self.dialog.preview_widget.canvas.setMapTool(self.pan_tool)

    def connect_signals(self) -> None:
        """Connect map tool signals idempotently."""
        # Always disconnect first to ensure we don't have multiple connections
        self.disconnect_signals()

        if self.interpretation_tool:
            self.interpretation_tool.polygonFinished.connect(self.dialog.on_interpretation_finished)

        if self.measure_tool:
            self.measure_tool.measurementChanged.connect(self.dialog.update_measurement_display)
            self.measure_tool.measurementFinished.connect(
                lambda: self.dialog.preview_widget.btn_measure.setChecked(False)
            )
            self.measure_tool.measurementCleared.connect(
                self.dialog.preview_widget.results_text.clear
            )

    def toggle_measure_tool(self, checked: bool) -> None:
        """Toggle between measurement and pan tools.

        Args:
            checked: True to activate measure tool, False for pan tool.

        """
        if checked:
            # Reset any previous measurement when starting new one
            self.measure_tool.reset()
            self.dialog.preview_widget.canvas.setMapTool(self.measure_tool)
            self.measure_tool.activate()
            # Show finalize button when measurement tool is active
            self.dialog.preview_widget.btn_finalize.setVisible(True)
            # Ensure canvas has focus for keyboard events
            self.dialog.preview_widget.canvas.setFocus()
        else:
            self.dialog.preview_widget.canvas.setMapTool(self.pan_tool)
            self.pan_tool.activate()
            # Hide finalize button when measurement tool is inactive
            self.dialog.preview_widget.btn_finalize.setVisible(False)

    def activate_default_tool(self) -> None:
        """Set the default (pan) tool."""
        self.dialog.preview_widget.canvas.setMapTool(self.pan_tool)
        self.pan_tool.activate()

    def toggle_interpretation_tool(self, checked: bool) -> None:
        """Toggle between interpretation and pan tools.

        Args:
            checked: True to activate interpretation tool, False for pan tool.

        """
        if checked:
            # Deactivate measure tool if active
            self.dialog.preview_widget.btn_measure.setChecked(False)
            # Reset and activate interpretation tool
            self.interpretation_tool.reset()
            self.dialog.preview_widget.canvas.setMapTool(self.interpretation_tool)
            self.interpretation_tool.activate()
            # Ensure canvas has focus for keyboard events
            self.dialog.preview_widget.canvas.setFocus()
        else:
            self.dialog.preview_widget.canvas.setMapTool(self.pan_tool)
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
            f"<b>{self.dialog.tr('Multi-Point Measurement')}</b><br>"
            f"<b>{self.dialog.tr('Points')}:</b> {point_count} | <b>{self.dialog.tr('Segments')}:</b> {seg_count}<br>"
            f"<b>{self.dialog.tr('Total Distance')}:</b> {total_dist:.2f} m<br>"
            f"<b>{self.dialog.tr('Horizontal Distance')}:</b> {horiz_dist:.2f} m<br>"
            f"<b>{self.dialog.tr('Elevation Change')}:</b> {elev_change:+.2f} m<br>"
            f"<b>{self.dialog.tr('Average Slope')}:</b> {avg_slope:.1f}°"
        )
        self.dialog.preview_widget.results_text.setHtml(msg)
        # Ensure results group is expanded
        self.dialog.preview_widget.results_group.setCollapsed(False)

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

    def __init__(self, dialog: SecInterpDialog) -> None:
        """Initialize navigation manager.

        Args:
            dialog: The SecInterpDialog instance

        """
        self.dialog = dialog

    def handle_wheel_event(self, event: Any) -> bool:
        """Handle mouse wheel for zooming in preview canvas.

        Args:
            event: The mouse wheel event.

        Returns:
            bool: True if event was handled, False otherwise.

        """
        if self.dialog.preview_widget.canvas.underMouse():
            if event.angleDelta().y() > 0:
                self.dialog.preview_widget.canvas.zoomIn()
            else:
                self.dialog.preview_widget.canvas.zoomOut()
            event.accept()
            return True
        return False
