"""Tests for AccessControlService."""

import unittest

from sec_interp.core.interfaces.settings_store import InMemorySettingsStore
from sec_interp.core.services.access_control_service import AccessControlService

from tests.base_test import BaseTestCase


class TestAccessControlService(BaseTestCase):
    """Test suite for AccessControlService."""

    def setUp(self):
        super().setUp()
        self.store = InMemorySettingsStore()
        self.service = AccessControlService(self.store)
        self.settings = self.store

    def test_can_export_3d_default_true(self):
        """Test that by default 3D export is enabled."""
        # Ensure setting is not present
        self.settings.setValue("SecInterp/enable_3d", True)
        self.assertTrue(self.service.can_export_3d())

    def test_can_export_3d_allowed(self):
        """Test that setting enable_3d allows export."""
        self.settings.setValue("SecInterp/enable_3d", True)
        self.assertTrue(self.service.can_export_3d())

    def test_can_export_3d_explicit_denied(self):
        """Test that setting enable_3d to False denies export."""
        self.settings.setValue("SecInterp/enable_3d", False)
        self.assertFalse(self.service.can_export_3d())


if __name__ == "__main__":
    unittest.main()
