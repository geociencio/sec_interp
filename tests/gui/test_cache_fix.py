import unittest
from unittest.mock import MagicMock
from sec_interp.gui.main_dialog import SecInterpDialog

class TestCacheRegression(unittest.TestCase):
    def test_clear_cache_handler_attribute_error(self):
        # Mock plugin instance with controller and data_cache
        mock_plugin = MagicMock()
        mock_plugin.controller = MagicMock()
        mock_plugin.controller.data_cache = MagicMock()

        # Initialize dialog with mocked plugin
        # We don't need iface for this specific test as we're testing clear_cache_handler logic
        dialog = SecInterpDialog(iface=None, plugin_instance=mock_plugin)

        # Verify initial state
        self.assertTrue(hasattr(dialog, "plugin_instance"))

        # This should NOT raise AttributeError anymore
        try:
            dialog.clear_cache_handler()
        except AttributeError as e:
            self.fail(f"clear_cache_handler raised AttributeError: {e}")

        # Verify that clear() was called on the correct object
        mock_plugin.controller.data_cache.clear.assert_called_once()

if __name__ == "__main__":
    unittest.main()
