"""Tests for main_dialog_tools.py - ToolManager and NavigationManager classes."""

import unittest
from unittest.mock import MagicMock, patch, call

# BaseTestCase MUST be imported before qgis.core to setup mocks correctly
from tests.base_test import BaseTestCase

from sec_interp.gui.dialog_tool_manager import ToolManager, NavigationManager


class TestToolManager(BaseTestCase):

    def setUp(self):
        """Set up test fixtures."""
        # Create mock dialog with preview_widget
        self.mock_dialog = MagicMock()
        self.mock_canvas = MagicMock()
        self.mock_dialog.preview_widget.canvas = self.mock_canvas
        self.mock_dialog.preview_widget.btn_finalize = MagicMock()
        self.mock_dialog.preview_widget.btn_measure = MagicMock()
        self.mock_dialog.preview_widget.results_text = MagicMock()
        self.mock_dialog.preview_widget.results_group = MagicMock()

        self.manager = ToolManager(self.mock_dialog)

    def test_initialize_tools_creates_default_tools(self):
        """Test that initialize_tools creates tools if not provided."""
        with (
            patch("sec_interp.gui.dialog_tool_manager.QgsMapToolPan") as MockPan,
            patch(
                "sec_interp.gui.dialog_tool_manager.ProfileMeasureTool"
            ) as MockMeasure,
            patch(
                "sec_interp.gui.dialog_tool_manager.ProfileInterpretationTool"
            ) as MockInterp,
        ):

            self.manager.initialize_tools()

            # Verify tools were created
            MockPan.assert_called_once_with(self.mock_canvas)
            MockMeasure.assert_called_once_with(self.mock_canvas)
            MockInterp.assert_called_once_with(self.mock_canvas)

            # Verify interpretation tool signal connection
            MockInterp.return_value.polygonFinished.connect.assert_called_once()

            # Verify default tool set
            self.mock_canvas.setMapTool.assert_called()

    def test_initialize_tools_uses_provided_tools(self):
        """Test that provided tools are used instead of creating new ones."""
        mock_pan = MagicMock()
        mock_measure = MagicMock()
        mock_interp = MagicMock()

        manager = ToolManager(
            self.mock_dialog,
            pan_tool=mock_pan,
            measure_tool=mock_measure,
            interpretation_tool=mock_interp,
        )

        with patch("sec_interp.gui.dialog_tool_manager.QgsMapToolPan") as MockPan:
            manager.initialize_tools()

            # Verify no new tools were created
            MockPan.assert_not_called()

            # Verify provided tools are used
            self.assertEqual(manager.pan_tool, mock_pan)
            self.assertEqual(manager.measure_tool, mock_measure)
            self.assertEqual(manager.interpretation_tool, mock_interp)

    def test_toggle_measure_tool_activate(self):
        """Test activating measure tool."""
        self.manager.measure_tool = MagicMock()
        self.manager.pan_tool = MagicMock()

        self.manager.toggle_measure_tool(True)

        # Verify measure tool activated
        self.manager.measure_tool.reset.assert_called_once()
        self.mock_canvas.setMapTool.assert_called_with(self.manager.measure_tool)
        self.manager.measure_tool.activate.assert_called_once()

        # Verify finalize button shown
        self.mock_dialog.preview_widget.btn_finalize.setVisible.assert_called_with(True)

    def test_toggle_measure_tool_deactivate(self):
        """Test deactivating measure tool."""
        self.manager.measure_tool = MagicMock()
        self.manager.pan_tool = MagicMock()

        self.manager.toggle_measure_tool(False)

        # Verify pan tool activated
        self.mock_canvas.setMapTool.assert_called_with(self.manager.pan_tool)
        self.manager.pan_tool.activate.assert_called_once()

        # Verify finalize button hidden
        self.mock_dialog.preview_widget.btn_finalize.setVisible.assert_called_with(
            False
        )

    def test_activate_default_tool(self):
        """Test activating default (pan) tool."""
        self.manager.pan_tool = MagicMock()

        self.manager.activate_default_tool()

        self.mock_canvas.setMapTool.assert_called_with(self.manager.pan_tool)
        self.manager.pan_tool.activate.assert_called_once()

    def test_toggle_interpretation_tool_activate(self):
        """Test activating interpretation tool."""
        self.manager.interpretation_tool = MagicMock()
        self.manager.pan_tool = MagicMock()

        self.manager.toggle_interpretation_tool(True)

        # Verify measure button deactivated
        self.mock_dialog.preview_widget.btn_measure.setChecked.assert_called_with(False)

        # Verify interpretation tool activated
        self.manager.interpretation_tool.reset.assert_called_once()
        self.mock_canvas.setMapTool.assert_called_with(self.manager.interpretation_tool)
        self.manager.interpretation_tool.activate.assert_called_once()

    def test_toggle_interpretation_tool_deactivate(self):
        """Test deactivating interpretation tool."""
        self.manager.interpretation_tool = MagicMock()
        self.manager.pan_tool = MagicMock()

        self.manager.toggle_interpretation_tool(False)

        # Verify pan tool activated
        self.mock_canvas.setMapTool.assert_called_with(self.manager.pan_tool)
        self.manager.pan_tool.activate.assert_called_once()

    def test_update_measurement_display_valid_metrics(self):
        """Test displaying measurement results with valid metrics."""
        metrics = {
            "point_count": 3,
            "segment_count": 2,
            "total_distance": 150.5,
            "horizontal_distance": 140.2,
            "elevation_change": 25.3,
            "avg_slope": 10.5,
        }

        self.manager.update_measurement_display(metrics)

        # Verify HTML was set
        self.mock_dialog.preview_widget.results_text.setHtml.assert_called_once()
        html_content = self.mock_dialog.preview_widget.results_text.setHtml.call_args[
            0
        ][0]

        # Verify content includes key metrics
        self.assertIn("150.50", html_content)
        self.assertIn("140.20", html_content)
        self.assertIn("25.3", html_content)
        self.assertIn("10.5", html_content)

        # Verify results group expanded
        self.mock_dialog.preview_widget.results_group.setCollapsed.assert_called_with(
            False
        )

    def test_update_measurement_display_insufficient_points(self):
        """Test that display is not updated with insufficient points."""
        metrics = {"point_count": 1}

        self.manager.update_measurement_display(metrics)

        # Verify no updates made
        self.mock_dialog.preview_widget.results_text.setHtml.assert_not_called()

    def test_update_measurement_display_empty_metrics(self):
        """Test that display is not updated with empty metrics."""
        self.manager.update_measurement_display({})

        # Verify no updates made
        self.mock_dialog.preview_widget.results_text.setHtml.assert_not_called()

    def test_update_measurement_display_none_metrics(self):
        """Test that display is not updated with None metrics."""
        self.manager.update_measurement_display(None)

        # Verify no updates made
        self.mock_dialog.preview_widget.results_text.setHtml.assert_not_called()


class TestNavigationManager(BaseTestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.mock_dialog = MagicMock()
        self.mock_canvas = MagicMock()
        self.mock_dialog.preview_widget.canvas = self.mock_canvas

        self.manager = NavigationManager(self.mock_dialog)

    def test_handle_wheel_event_zoom_in(self):
        """Test zoom in via mouse wheel."""
        mock_event = MagicMock()
        mock_event.angleDelta().y.return_value = 120  # Positive = zoom in
        self.mock_canvas.underMouse.return_value = True

        result = self.manager.handle_wheel_event(mock_event)

        self.assertTrue(result)
        self.mock_canvas.zoomIn.assert_called_once()
        mock_event.accept.assert_called_once()

    def test_handle_wheel_event_zoom_out(self):
        """Test zoom out via mouse wheel."""
        mock_event = MagicMock()
        mock_event.angleDelta().y.return_value = -120  # Negative = zoom out
        self.mock_canvas.underMouse.return_value = True

        result = self.manager.handle_wheel_event(mock_event)

        self.assertTrue(result)
        self.mock_canvas.zoomOut.assert_called_once()
        mock_event.accept.assert_called_once()

    def test_handle_wheel_event_mouse_not_over_canvas(self):
        """Test that event is not handled when mouse is not over canvas."""
        mock_event = MagicMock()
        self.mock_canvas.underMouse.return_value = False

        result = self.manager.handle_wheel_event(mock_event)

        self.assertFalse(result)
        self.mock_canvas.zoomIn.assert_not_called()
        self.mock_canvas.zoomOut.assert_not_called()
        mock_event.accept.assert_not_called()
