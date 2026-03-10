import unittest
from unittest.mock import MagicMock, patch

from qgis.core import QgsVectorLayer
from qgis.PyQt.QtWidgets import QCheckBox

# Mock components that are not strictly necessary to test signal logic
with patch("sec_interp.gui.dialog_preview_manager.PreviewManager"):
    from sec_interp.gui.main_dialog import SecInterpDialog


class TestSignalRestoration(unittest.TestCase):
    """Test suite to ensure internal page signals survive the SignalManager's global disconnect."""

    def setUp(self):
        """Initialize the dialog for testing."""
        self.mock_iface = MagicMock()
        self.mock_plugin = MagicMock()

        with patch("sec_interp.gui.dialog_preview_manager.PreviewManager"):
            self.dialog = SecInterpDialog(self.mock_iface, self.mock_plugin)

    def test_page_signals_survive_connect_all(self):
        """Test that page-internal signals are reconnected after SignalManager.connect_all()."""
        # 1. Ensure the signal manager completes a full connect cycle
        # This calls disconnect_all() under the hood, then connects global signals,
        # and should end by calling connect_signals() on each page.
        self.dialog.signal_manager.connect_all()

        # 2. Test GeologyPage (changing layer updates field combo)
        geology_page = self.dialog.page_geology
        test_layer = QgsVectorLayer("Polygon", "test_geol", "memory")
        self.assertTrue(test_layer.isValid(), "Test layer must be valid")

        # Simulate user changing the combination box layer
        # The internal page signal should catch this and update the field_combo's layer
        geology_page.layer_combo.setLayer(test_layer)

        # Assuming it is connected, the field combo should now know about the test_layer
        self.assertIsNotNone(geology_page.field_combo.layer())

    def test_settings_reset_button_restores_defaults(self):
        """Test that the Reset to Defaults button on the Settings page works correctly."""
        self.dialog.signal_manager.connect_all()

        settings_page = self.dialog.page_settings

        # Alter the checkboxes from their defaults
        settings_page.chk_exp_topo.setChecked(False)
        settings_page.chk_exp_drill.setChecked(False)
        settings_page.chk_enable_3d.setChecked(True)
        settings_page.chk_3d_projected.setChecked(True)

        # Click the reset button
        settings_page._reset_export_defaults()

        # Verify they've been reset to defaults
        self.assertTrue(settings_page.chk_exp_topo.isChecked())
        self.assertTrue(settings_page.chk_exp_drill.isChecked())
        self.assertFalse(settings_page.chk_enable_3d.isChecked())
        self.assertTrue(settings_page.chk_3d_traces.isChecked())
        self.assertFalse(settings_page.chk_3d_projected.isChecked())

    def test_preview_signals_wire(self):
        """Test that PreviewWidget signals are reconnected by SignalManager."""
        with (
            patch.object(self.dialog.preview_widget, "connect_signals") as mock_connect,
            patch.object(
                self.dialog.preview_widget, "disconnect_signals"
            ) as mock_disconnect,
        ):

            # This should trigger the calls
            self.dialog.signal_manager.connect_all()

            # Verify SignalManager integration
            mock_disconnect.assert_called()
            mock_connect.assert_called()

    def test_preview_manager_signals_wire(self):
        """Test that PreviewManager signals are reconnected by SignalManager."""
        with (
            patch.object(
                self.dialog.preview_manager, "connect_signals"
            ) as mock_connect,
            patch.object(
                self.dialog.preview_manager, "disconnect_signals"
            ) as mock_disconnect,
        ):

            self.dialog.signal_manager.connect_all()

            # Verify SignalManager integration
            mock_disconnect.assert_called()
            mock_connect.assert_called()

    def test_preview_widget_connect_logic(self):
        """Test the internal connection logic of PreviewWidget."""
        widget = self.dialog.preview_widget
        with patch.object(widget, "_update_coords") as mock_coords:
            # Re-run connection to bind the mock
            widget.connect_signals()

            from qgis.core import QgsPointXY

            widget.canvas.xyCoordinates.emit(QgsPointXY(123, 456))

            mock_coords.assert_called_once()
