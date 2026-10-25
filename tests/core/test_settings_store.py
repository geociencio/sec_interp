"""Tests for the pure settings store and its core consumers."""

from __future__ import annotations

from sec_interp.core.config import ConfigService
from sec_interp.core.interfaces.settings_store import InMemorySettingsStore
from sec_interp.core.services.access_control_service import AccessControlService
from tests.base_test import BaseTestCase


class TestInMemorySettingsStore(BaseTestCase):
    """The in-memory store mimics the QgsSettings subset used by core."""

    def test_defaults_and_roundtrip(self) -> None:
        store = InMemorySettingsStore()
        self.assertEqual(store.value("missing", 42), 42)
        store.setValue("SecInterp/scale", 1000)
        self.assertEqual(store.value("SecInterp/scale"), 1000)
        store.sync()

    def test_bool_conversion(self) -> None:
        store = InMemorySettingsStore({"SecInterp/enable_3d": "false"})
        self.assertFalse(store.value("SecInterp/enable_3d", True, type=bool))

    def test_config_service_uses_store(self) -> None:
        store = InMemorySettingsStore()
        service = ConfigService(store)
        service.set("scale", 25000.0)
        self.assertEqual(service.get("scale"), 25000.0)

    def test_access_control_uses_store(self) -> None:
        store = InMemorySettingsStore()
        self.assertTrue(AccessControlService(store).can_export_3d())
        store.setValue("SecInterp/enable_3d", False)
        self.assertFalse(AccessControlService(store).can_export_3d())
