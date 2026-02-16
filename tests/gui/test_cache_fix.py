from tests.base_test import BaseTestCase
from unittest.mock import MagicMock


class TestCacheRegression(BaseTestCase):
    def test_clear_cache_handler_no_facade(self):
        """Test that clear_cache_handler correctly processes clearing."""
        # Create a mock dialog
        mock_dialog = MagicMock()
        mock_dialog.plugin_instance = MagicMock()
        mock_dialog.plugin_instance.controller = MagicMock()
        mock_dialog.tool_manager = MagicMock()
        mock_dialog.preview_widget = MagicMock()
        mock_dialog.tr = lambda x: x

        # Import and bind the clear_cache_handler method
        from sec_interp.gui.main_dialog import SecInterpDialog

        # Call the method directly with our mock dialog as self
        SecInterpDialog.clear_cache_handler(mock_dialog)

        # Verify that data_cache.clear() was called
        mock_dialog.plugin_instance.controller.data_cache.clear.assert_called_once()
        mock_dialog.tool_manager.measure_tool.reset.assert_called_once()
