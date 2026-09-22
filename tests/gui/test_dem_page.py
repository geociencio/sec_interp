"""Tests for the DemPage configuration page."""

from __future__ import annotations

import sys

from qgis.PyQt.QtWidgets import QApplication

from sec_interp.gui.ui.pages.dem_page import DemPage
from tests.base_test import BaseTestCase

_GET_DATA_KEYS = {
    "raster_layer",
    "selected_band",
    "scale",
    "vertexag",
    "auto_vert_exag",
}

_DUMP_KEYS = {
    "dem_layer",
    "dem_band",
    "scale",
    "vert_exag",
    "auto_vert_exag",
}


class TestDemPage(BaseTestCase):
    """Verify the DEM page contract and the adaptive VE Auto/Manual toggle."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure a QApplication exists for widget construction."""
        super().setUpClass()
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        super().setUp()
        self.page = DemPage()

    def test_get_data_contract(self) -> None:
        """get_data exposes the flattened configuration, including auto toggle."""
        self.assertEqual(set(self.page.get_data()), _GET_DATA_KEYS)

    def test_dump_contract(self) -> None:
        """Dump returns persistable keys and covers the layer keys."""
        data = self.page.dump()
        self.assertEqual(set(data), _DUMP_KEYS)
        self.assertTrue(DemPage.layer_keys.issubset(data))

    def test_auto_toggle_default_disables_spin(self) -> None:
        """Auto mode is enabled by default, so the manual spin starts disabled."""
        self.assertTrue(self.page.auto_ve_check.isChecked())
        self.page.vertexag_spin.setEnabled.assert_called_with(False)

    def test_auto_toggle_enables_spin_when_manual(self) -> None:
        """Turning Auto off re-enables the manual exaggeration spinbox."""
        self.page._on_auto_ve_toggled(False)
        self.page.vertexag_spin.setEnabled.assert_called_with(True)

    def test_set_auto_ve_updates_label(self) -> None:
        """The adaptive VE value is shown next to the Auto toggle."""
        self.page.set_auto_ve(2.6)
        self.assertEqual(self.page.auto_ve_value.text(), "2.6×")

        self.page.set_auto_ve(None)
        self.assertEqual(self.page.auto_ve_value.text(), "—")

    def test_dump_load_auto_roundtrip(self) -> None:
        """The Auto toggle is persisted and restored, syncing the spin state."""
        self.page.auto_ve_check.setChecked(False)
        self.assertFalse(self.page.dump()["auto_vert_exag"])

        self.page.load({"auto_vert_exag": True})
        self.assertTrue(self.page.auto_ve_check.isChecked())
        self.page.vertexag_spin.setEnabled.assert_called_with(False)

    def test_reset_restores_auto_default(self) -> None:
        """Reset returns the Auto toggle to its default (enabled) state."""
        self.page.auto_ve_check.setChecked(False)
        self.page.reset()
        self.assertTrue(self.page.auto_ve_check.isChecked())

    def test_connect_disconnect_signals(self) -> None:
        """Signal wiring is symmetric and does not raise."""
        self.page.connect_signals()
        self.page.disconnect_signals()
