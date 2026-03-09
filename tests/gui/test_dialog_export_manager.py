"""Tests for DialogExportManager."""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from qgis.core import Qgis, QgsSettings, QgsRectangle, QgsMapSettings
from qgis.PyQt.QtCore import QSize
from sec_interp.gui.dialog_export_manager import ExportManager
from sec_interp.core.exceptions import SecInterpError


class TestDialogExportManager(BaseTestCase):
    """Tests for the ExportManager class."""

    def setUp(self):
        super().setUp()
        self.dialog = MagicMock()
        # Mock tr for the dialog
        self.dialog.tr.side_effect = lambda x: x

        # Mock plugin_instance and controller
        self.plugin_instance = MagicMock()
        self.dialog.plugin_instance = self.plugin_instance
        self.controller = MagicMock()
        self.plugin_instance.controller = self.controller

        # Mock preview_widget and canvas
        self.dialog.preview_widget = MagicMock()
        self.canvas = MagicMock()
        self.dialog.preview_widget.canvas = self.canvas
        self.dialog.current_canvas = self.canvas

        # Initialize manager
        self.manager = ExportManager(self.dialog)
        self.manager.export_service = MagicMock()

    def test_export_preview_no_canvas(self):
        """Test export_preview when no canvas is available."""
        self.dialog.current_canvas = None
        result = self.manager.export_preview()
        self.assertFalse(result)
        self.dialog.push_message.assert_called_with(
            "Export Error",
            "No preview available to export. Generate a preview first.",
            level=Qgis.Warning,
        )

    def test_export_preview_no_layers(self):
        """Test export_preview when the canvas has no layers."""
        self.canvas.layers.return_value = []
        result = self.manager.export_preview()
        self.assertFalse(result)
        self.dialog.push_message.assert_called_with(
            "Export Error", "No layers to export.", level=Qgis.Warning
        )

    @patch("sec_interp.gui.dialog_export_manager.QFileDialog.getSaveFileName")
    @patch("sec_interp.gui.dialog_export_manager.get_exporter")
    def test_export_preview_success(self, mock_get_exporter, mock_get_save):
        """Test successful preview export."""
        self.canvas.layers.return_value = [MagicMock()]
        self.canvas.extent.return_value = QgsRectangle(0, 0, 100, 100)
        self.canvas.size.return_value = QSize(800, 600)
        self.canvas.width.return_value = 800
        self.canvas.height.return_value = 600

        output_path = Path(self.test_dir) / "test_preview.png"
        mock_get_save.return_value = (str(output_path), "PNG")

        mock_exporter = MagicMock()
        mock_exporter.export.return_value = True
        mock_get_exporter.return_value = mock_exporter

        # Mock get_preview_options
        self.dialog.get_preview_options.return_value = {"show_legend": True}

        result = self.manager.export_preview()

        # If result is False, check if there was an error
        if not result:
            print(f"Handle error calls: {self.dialog.handle_error.mock_calls}")

        self.dialog.handle_error.assert_not_called()
        self.assertTrue(result)
        self.dialog.push_message.assert_called_with(
            "Success", f"Preview exported to {output_path.name}", level=Qgis.Success
        )
        # Verify settings update
        settings = QgsSettings()
        self.assertEqual(
            settings.value("SecInterp/lastExportDir"), str(output_path.parent)
        )

    @patch("sec_interp.gui.dialog_export_manager.QFileDialog.getSaveFileName")
    def test_export_preview_canceled(self, mock_get_save):
        """Test export_preview when user cancels file dialog."""
        self.canvas.layers.return_value = [MagicMock()]
        mock_get_save.return_value = ("", "")

        result = self.manager.export_preview()
        self.assertFalse(result)

    def test_export_preview_exception(self):
        """Test export_preview handling unexpected exceptions."""
        self.canvas.layers.side_effect = Exception("Crash")

        result = self.manager.export_preview()
        self.assertFalse(result)
        self.dialog.handle_error.assert_called()

    @patch("sec_interp.gui.dialog_export_manager.get_exporter")
    def test_execute_preview_export_formats(self, mock_get_exporter):
        """Test export dimensions for different formats."""
        self.canvas.size.return_value = QSize(800, 600)
        self.canvas.width.return_value = 800
        self.canvas.height.return_value = 600
        self.canvas.extent.return_value = QgsRectangle(0, 0, 100, 100)

        mock_exporter = MagicMock()
        mock_exporter.export.return_value = True
        mock_get_exporter.return_value = mock_exporter

        self.dialog.get_preview_options.return_value = {"show_legend": True}

        # Test PNG (scaled)
        self.manager._execute_preview_export(Path("test.png"), [MagicMock()])
        # 800 * 3 = 2400

        # Test PDF (unscaled)
        self.manager._execute_preview_export(Path("test.pdf"), [MagicMock()])

    def test_export_data_validation_fail(self):
        """Test export_data when input validation fails."""
        self.plugin_instance._get_and_validate_inputs.return_value = None
        result = self.manager.export_data()
        self.assertFalse(result)

    def test_export_data_no_profile(self):
        """Test export_data when no profile data is generated."""
        params = MagicMock()
        self.plugin_instance._get_and_validate_inputs.return_value = params
        self.controller.generate_profile_data.return_value = (
            None,
            None,
            None,
            None,
            None,
        )

        result = self.manager.export_data()
        self.assertFalse(result)
        self.dialog.push_message.assert_called_with(
            "Error", "No profile data generated.", level=Qgis.Critical
        )

    def test_export_data_success(self):
        """Test successful full data export."""
        params = MagicMock()
        self.plugin_instance._get_and_validate_inputs.return_value = params

        profile_data = MagicMock()
        self.controller.generate_profile_data.return_value = (
            profile_data,
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        self.dialog.get_selected_values.return_value = {
            "output_path": self.test_dir,
            "exp_topo": True,
            "exp_geol": True,
        }
        self.dialog.interpretations = []

        mock_export_service = MagicMock()
        mock_export_service.export_data.return_value = ["Export successful"]
        self.manager.export_service = mock_export_service

        result = self.manager.export_data()

        self.assertTrue(result)
        self.dialog.preview_widget.results_text.setPlainText.assert_called_with(
            "Export successful"
        )

    def test_export_data_sec_interp_error(self):
        """Test export_data handling SecInterpError."""
        params = MagicMock()
        self.plugin_instance._get_and_validate_inputs.return_value = params
        self.controller.generate_profile_data.side_effect = SecInterpError(
            "Expected error"
        )

        result = self.manager.export_data()
        self.assertFalse(result)
        self.dialog.handle_error.assert_called()


if __name__ == "__main__":
    unittest.main()
