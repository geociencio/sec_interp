"""Access Control Service.

This module provides a service to manage access to restricted features.
"""

from qgis.core import QgsSettings

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class AccessControlService:
    """Service to manage access to restricted features."""

    def __init__(self):
        """Initialize the access control service."""
        self.settings = QgsSettings()

    def can_export_3d(self) -> bool:
        """Check if the user has permission to export 3D data.

        Returns:
            bool: True if authorized, False otherwise.

        """
        # For now, we link it to the UI toggle in Settings persisted via QgsSettings.
        # Default to False to demonstrate the "locked" feel or restricted nature.
        allowed = self.settings.value("sec_interp/enable_3d", False, type=bool)

        if not allowed:
            logger.info("Access denied for restricted feature: 3D Export")

        return allowed
