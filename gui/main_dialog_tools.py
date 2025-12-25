"""Map tool management module for SecInterp main dialog.

This module handles the initialization and orchestration of map tools
(pan, measure) used in the preview canvas.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qgis.gui import QgsMapToolPan

from .tools.measure_tool import ProfileMeasureTool


if TYPE_CHECKING:
    from .main_dialog import SecInterpDialog


class DialogToolManager:
    """Manages map tools and related event handling for the preview canvas."""

    def __init__(self, dialog: SecInterpDialog):
        """Initialize tool manager with reference to parent dialog.

        Args:
            dialog: The :class:`sec_interp.gui.main_dialog.SecInterpDialog` instance
        """
        self.dialog = dialog
        self.pan_tool = None
        self.measure_tool = None

    def initialize_tools(self) -> None:
        """Create and configure map tools."""
        self.pan_tool = QgsMapToolPan(self.dialog.preview_widget.canvas)
        self.measure_tool = ProfileMeasureTool(self.dialog.preview_widget.canvas)
        self.dialog.preview_widget.canvas.setMapTool(self.pan_tool)

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
        else:
            self.dialog.preview_widget.canvas.setMapTool(self.pan_tool)
            self.pan_tool.activate()
            # Hide finalize button when measurement tool is inactive
            self.dialog.preview_widget.btn_finalize.setVisible(False)

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

    def update_measurement_display(self, metrics: dict[str, Any]) -> None:
        """Display measurement results from multi-point tool.

        Args:
            metrics: Dictionary containing measurement data.
        """
        if not metrics or metrics.get("point_count", 0) < 2:
            return

        total_dist = metrics.get("total_distance", 0)
        horiz_dist = metrics.get("horizontal_distance", 0)
        elev_change = metrics.get("elevation_change", 0)
        avg_slope = metrics.get("avg_slope", 0)
        seg_count = metrics.get("segment_count", 0)
        point_count = metrics.get("point_count", 0)

        # Format result text with HTML for better presentation
        msg = (
            f"<b>Medición Multi-Punto</b><br>"
            f"<b>Puntos:</b> {point_count} | <b>Segmentos:</b> {seg_count}<br>"
            f"<b>Distancia Total:</b> {total_dist:.2f} m<br>"
            f"<b>Distancia Horizontal:</b> {horiz_dist:.2f} m<br>"
            f"<b>Cambio Elevación:</b> {elev_change:+.2f} m<br>"
            f"<b>Pendiente Promedio:</b> {avg_slope:.1f}°"
        )
        self.dialog.preview_widget.results_text.setHtml(msg)
        # Ensure results group is expanded
        self.dialog.preview_widget.results_group.setCollapsed(False)
