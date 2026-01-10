from tests.base_test import BaseTestCase
from unittest.mock import MagicMock
from sec_interp.gui.main_dialog import SecInterpDialog


class TestCacheRegression(BaseTestCase):
    def test_clear_cache_handler_attribute_error(self):
        # Mock plugin instance with controller and data_cache
        mock_plugin = MagicMock()
        mock_plugin.controller = MagicMock()
        mock_plugin.controller.data_cache = MagicMock()

        # Initialize dialog with mocked plugin
        dialog = SecInterpDialog(iface=None, plugin_instance=mock_plugin)

        # Verify dialog state - just access it, if it raises AssertionError ok, but let's see why
        # hasattr check was failing. Let's try direct access assertion which gives better error message
        self.assertEqual(dialog.plugin_instance, mock_plugin)

        # This should NOT raise AttributeError anymore
        try:
            dialog.clear_cache_handler()
        except AttributeError as e:
            self.fail(f"clear_cache_handler raised AttributeError: {e}")

        # Verify that clear() was called on the correct object
        mock_plugin.controller.data_cache.clear.assert_called_once()
