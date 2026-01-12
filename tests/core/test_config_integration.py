import sys
from unittest.mock import MagicMock

# Mock qgis.core before any imports of sec_interp modules that depend on it
mock_qgis = MagicMock()
sys.modules['qgis'] = mock_qgis
sys.modules['qgis.core'] = mock_qgis

import unittest
from unittest.mock import patch
from sec_interp.core.config import ConfigService
from sec_interp.core.models.settings_model import PluginSettings

class TestConfigServiceIntegration(unittest.TestCase):
    """Integration test between ConfigService and PluginSettings."""

    def setUp(self):
        # We need a clean ConfigService and mock QgsSettings if possible.
        # Since QgsSettings is a core object, we might need to mock its response.
        self.patcher = patch('sec_interp.core.config.QgsSettings')
        self.mock_qgs_settings_class = self.patcher.start()
        self.mock_qgs_settings = MagicMock()
        self.mock_qgs_settings_class.return_value = self.mock_qgs_settings

        self.config = ConfigService()

    def tearDown(self):
        self.patcher.stop()

    def test_get_all_settings_mapping(self):
        """Test that get_all_settings correctly maps and validates QgsSettings."""

        # Setup mock return values for specific keys
        def mock_value(key, default):
            if "scale" in key: return "10000" # String that should be float
            if "buffer_dist" in key: return -50.0 # Invalid value
            if "show_topo" in key: return "false" # String bool
            return default

        self.mock_qgs_settings.value.side_effect = mock_value

        settings = self.config.get_all_settings()

        self.assertIsInstance(settings, PluginSettings)
        # Check validation outcomes
        self.assertEqual(settings.dem.scale, 10000.0) # Type conversion
        self.assertEqual(settings.section.buffer_dist, 0.0) # Range validation
        self.assertEqual(settings.preview.show_topo, False) # Bool conversion

    def test_cache_invalidation(self):
        """Test that set() invalidates the internal cache."""
        self.config.get_all_settings() # Populate cache
        self.assertIsNotNone(self.config._current_settings)

        self.config.set("scale", 20000.0)
        self.assertIsNone(self.config._current_settings)

if __name__ == '__main__':
    unittest.main()
