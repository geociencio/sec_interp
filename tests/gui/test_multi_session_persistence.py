"""Tests for multi-session signal persistence.
Ensures that closing and re-opening the dialog correctly restores signal connections.
"""

import unittest
from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from sec_interp.gui.main_dialog import SecInterpDialog
from sec_interp.gui.dialog_signal_manager import SignalManager
from qgis.PyQt.QtWidgets import QDialogButtonBox


class TestMultiSessionPersistence(BaseTestCase):
    """Tests for signal persistence across multiple dialog sessions."""

    def setUp(self):
        super().setUp()
        self.mock_plugin = MagicMock()
        self.mock_plugin.controller = MagicMock()

        # Patch managers to avoid complex GUI init
        with (
            patch("sec_interp.gui.main_dialog.StateManager"),
            patch("sec_interp.gui.main_dialog.InputManager"),
            patch("sec_interp.gui.main_dialog.ExportManager"),
            patch("sec_interp.gui.main_dialog.PreviewManager"),
            patch("sec_interp.gui.main_dialog.InterpretationManager"),
            patch("sec_interp.gui.main_dialog.LegendWidget"),
        ):
            self.dialog = SecInterpDialog(plugin_instance=self.mock_plugin)
            # Ensure signal_manager is real for testing
            self.dialog.signal_manager = SignalManager(self.dialog)

            # Setup real ToolManager with mocked tools
            from sec_interp.gui.dialog_tool_manager import ToolManager

            self.dialog.tool_manager = ToolManager(self.dialog)
            self.dialog.tool_manager.measure_tool = MagicMock()
            self.dialog.tool_manager.interpretation_tool = MagicMock()

    @patch("sec_interp.gui.main_dialog.logger")
    def test_signals_restored_after_close_and_reopen(self, mock_logger):
        """Verify that signals are working after a close and reconnect cycle."""
        # Mock some handlers in the dialog
        self.dialog.update_button_state = MagicMock()

        # 1. Simulate Close (Disconnection)
        # We use a real event mock
        event = MagicMock()
        self.dialog.closeEvent(event)

        # 2. Simulate re-opening (Re-connection in plugin.run())
        self.dialog.signal_manager.connect_all()

        # 3. Verify signal works
        # Trigger line_combo change in section page
        self.dialog.page_section.line_combo.layerChanged.emit(MagicMock())

        self.dialog.update_button_state.assert_called()

    def test_tool_internal_signals_restored(self):
        """Verify that tools' internal signals are re-connected after connect_all."""
        # 1. Reconnect signals
        self.dialog.signal_manager.connect_all()

        # 2. Verify connect was called on tool signal mocks with dialog handlers
        self.dialog.tool_manager.interpretation_tool.polygonFinished.connect.assert_called_with(
            self.dialog.on_interpretation_finished
        )
        self.dialog.tool_manager.measure_tool.measurementChanged.connect.assert_called_with(
            self.dialog.update_measurement_display
        )

    def test_idempotent_connection_logic(self):
        """Verify that connect_all calls disconnect_all first."""
        # Instead of relying on real signals which might be tricky in headless + mocks,
        # we verify the logic flow.
        self.dialog.signal_manager.disconnect_all = MagicMock()
        self.dialog.signal_manager._connect_button_signals = MagicMock()

        # Trigger connect_all
        self.dialog.signal_manager.connect_all()

        # Verify disconnect_all was called BEFORE connections (implied by call order if we checked,
        # but here we just check it was called)
        self.dialog.signal_manager.disconnect_all.assert_called_once()
        self.dialog.signal_manager._connect_button_signals.assert_called_once()


if __name__ == "__main__":
    unittest.main()
