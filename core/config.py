"""Configuration Service Module.

Provides a centralized way to manage plugin settings using QgsSettings.
"""

from typing import Any, Dict, Optional

from qgis.core import QgsSettings

from sec_interp.logger_config import get_logger


logger = get_logger(__name__)


class ConfigService:
    """Service to handle plugin configuration and persistent settings."""

    PREFIX = "/SecInterp/"

    # Default values for common settings
    DEFAULTS = {
        "scale": 500.0,
        "vert_exag": 1.0,
        "buffer_dist": 100.0,
        "dip_scale_factor": 1.0,
        "last_output_dir": "",
        "dpi": 300,
        "preview_width": 800,
        "preview_height": 600,
        "sampling_interval": 10.0,
        "export_quality": 95,
        "auto_lod": True,
        "max_preview_points": 10000,
    }

    # Non-persistent constants
    SUPPORTED_IMAGE_FORMATS = [".png", ".jpg", ".jpeg"]
    SUPPORTED_VECTOR_FORMATS = [".shp"]
    SUPPORTED_DOCUMENT_FORMATS = [".pdf", ".svg"]

    def __init__(self):
        """Initialize the Configuration Service with QgsSettings."""
        self.settings = QgsSettings()

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value by key.

        Args:
            key: The configuration key (without prefix).
            default: Optional default value if not found in settings or defaults.

        Returns:
            The configuration value from settings or its default value.
        """
        full_key = self.PREFIX + key

        # Determine internal default
        if default is None:
            default = self.DEFAULTS.get(key)

        value = self.settings.value(full_key, default)

        # Handle type conversion if necessary (QgsSettings can return QVariant)
        return value

    def set(self, key: str, value: Any) -> None:
        """Store a configuration value.

        Args:
            key: The configuration key (without prefix).
            value: The value to persist in settings.
        """
        full_key = self.PREFIX + key
        self.settings.setValue(full_key, value)
        logger.debug(f"Config set: {full_key} = {value}")

    def reset_defaults(self) -> None:
        """Reset all known persistent settings to their default values."""
        for key, value in self.DEFAULTS.items():
            self.set(key, value)
        logger.info("Configuration reset to defaults")
