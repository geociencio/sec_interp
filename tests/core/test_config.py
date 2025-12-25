"""Tests for ConfigService."""

import pytest
from unittest.mock import MagicMock, patch
from sec_interp.core.config import ConfigService

class TestConfigService:
    """Tests for ConfigService."""

    @pytest.fixture
    def config_service(self):
        """Create a ConfigService with a mocked QgsSettings."""
        with patch("sec_interp.core.config.QgsSettings") as mock_settings_cls:
            mock_settings = mock_settings_cls.return_value
            service = ConfigService()
            yield service, mock_settings

    def test_get_default(self, config_service):
        """Test getting a value that is not set (should return default)."""
        service, mock_settings = config_service
        # Side effect: return the second argument of value() if key not found
        mock_settings.value.side_effect = lambda k, d: d
        
        result = service.get("scale")
        assert result == 500.0
        mock_settings.value.assert_called_with("/SecInterp/scale", 500.0)

    def test_get_explicit_default(self, config_service):
        """Test getting a value with an explicit default."""
        service, mock_settings = config_service
        mock_settings.value.side_effect = lambda k, d: d
        
        result = service.get("nonexistent", default="foo")
        assert result == "foo"
        mock_settings.value.assert_called_with("/SecInterp/nonexistent", "foo")

    def test_set_value(self, config_service):
        """Test setting a configuration value."""
        service, mock_settings = config_service
        
        service.set("scale", 200.0)
        mock_settings.setValue.assert_called_with("/SecInterp/scale", 200.0)

    def test_reset_defaults(self, config_service):
        """Test resetting to defaults."""
        service, mock_settings = config_service
        
        service.reset_defaults()
        # Verify at least some defaults are set
        mock_settings.setValue.assert_any_call("/SecInterp/scale", 500.0)
        mock_settings.setValue.assert_any_call("/SecInterp/vert_exag", 1.0)
