from tests.base_test import BaseTestCase
from unittest.mock import MagicMock, patch


class TestCacheRegression(BaseTestCase):
    def test_clear_cache_handler_attribute_error(self):
        """Test that clear_cache_handler correctly calls cache_handler.clear_cache()"""
        # Create a minimal mock dialog with just the necessary attributes
        mock_dialog = MagicMock()
        mock_dialog.cache_handler = MagicMock()

        # Import and bind the clear_cache_handler method
        from sec_interp.gui.main_dialog import SecInterpDialog

        # Call the method directly with our mock dialog as self
        SecInterpDialog.clear_cache_handler(mock_dialog)

        # Verify that cache_handler.clear_cache() was called
        mock_dialog.cache_handler.clear_cache.assert_called_once()
