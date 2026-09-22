"""Tests for ConfigService."""

from unittest.mock import patch

from sec_interp.core.config import ConfigService
from tests.base_test import BaseTestCase


class TestConfigService(BaseTestCase):
    """Tests for ConfigService."""

    def setUp(self):
        super().setUp()
        # Start patching QgsSettings
        self.settings_patcher = patch("sec_interp.core.config.QgsSettings")
        self.mock_settings_cls = self.settings_patcher.start()
        self.mock_settings = self.mock_settings_cls.return_value

        self.service = ConfigService()

        # Ensure patch is stopped after test
        self.addCleanup(self.settings_patcher.stop)

    def test_get_default(self):
        """Test getting a value that is not set (should return default)."""
        # Side effect: return the second argument of value() if key not found
        self.mock_settings.value.side_effect = lambda k, d: d

        result = self.service.get("scale")
        self.assertEqual(result, 50000.0)
        # The last call should be the fallback to old prefix
        self.mock_settings.value.assert_called_with("/SecInterp/scale", 50000.0)

    def test_get_explicit_default(self):
        """Test getting a value with an explicit default."""
        self.mock_settings.value.side_effect = lambda k, d: d

        result = self.service.get("nonexistent", default="foo")
        self.assertEqual(result, "foo")
        # The last call should be the fallback to old prefix
        self.mock_settings.value.assert_called_with("/SecInterp/nonexistent", "foo")

    def test_set_value(self):
        """Test setting a configuration value."""
        self.service.set("scale", 200.0)
        self.mock_settings.setValue.assert_called_with("SecInterp/scale", 200.0)

    def test_reset_defaults(self):
        """Test resetting to defaults."""
        self.service.reset_defaults()
        # Verify at least some defaults are set
        self.mock_settings.setValue.assert_any_call("SecInterp/scale", 50000.0)
        self.mock_settings.setValue.assert_any_call("SecInterp/vert_exag", 1.0)

    def test_auto_vert_exag_default(self):
        """Auto VE toggle defaults to True when not persisted."""
        self.mock_settings.value.side_effect = lambda k, d: d
        self.assertEqual(self.service.get("auto_vert_exag"), True)

    def test_reset_auto_vert_exag(self):
        """reset_defaults restores the Auto VE toggle to True."""
        self.service.reset_defaults()
        self.mock_settings.setValue.assert_any_call("SecInterp/auto_vert_exag", True)
