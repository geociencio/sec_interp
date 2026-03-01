"""Tests for AccessControlService."""

import unittest
from qgis.core import QgsSettings
from sec_interp.core.services.access_control_service import AccessControlService
from sec_interp.tests.base_test import BaseTestCase


class TestAccessControlService(BaseTestCase):
    """Test suite for AccessControlService."""

    def setUp(self):
        super().setUp()
        self.service = AccessControlService()
        self.settings = QgsSettings()

    def test_can_export_3d_default_false(self):
        """Test that by default 3D export is denied."""
        # Ensure setting is not present
        self.settings.remove("sec_interp/enable_3d")
        self.assertFalse(self.service.can_export_3d())

    def test_can_export_3d_allowed(self):
        """Test that setting enable_3d allows export."""
        self.settings.setValue("sec_interp/enable_3d", True)
        self.assertTrue(self.service.can_export_3d())

    def test_can_export_3d_explicit_denied(self):
        """Test that setting enable_3d to False denies export."""
        self.settings.setValue("sec_interp/enable_3d", False)
        self.assertFalse(self.service.can_export_3d())


if __name__ == "__main__":
    unittest.main()
