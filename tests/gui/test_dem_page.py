"""Tests for the DemPage configuration page."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

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


class TestDemPageStats(BaseTestCase):
    """Read-only band statistics (min/max/mean/NoData)."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure a QApplication exists for widget construction."""
        super().setUpClass()
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        super().setUp()
        self.page = DemPage()

    def _layer(self, nodata: float = -9999.0) -> MagicMock:
        layer = MagicMock()
        layer.isValid.return_value = True
        stats = MagicMock()
        stats.minimumValue = 221.0
        stats.maximumValue = 593.0
        stats.mean = 433.38
        provider = MagicMock()
        provider.bandStatistics.return_value = stats
        provider.sourceNoDataValue.return_value = nodata
        layer.dataProvider.return_value = provider
        return layer

    def _with_layer(self, layer: MagicMock):
        self.page.band_combo.currentBand.return_value = 1
        return patch.object(self.page.raster_combo, "currentLayer", return_value=layer)

    def test_display_min_max_mean_nodata(self) -> None:
        """The four statistics are shown with sensible formatting."""
        with self._with_layer(self._layer()):
            self.page._update_raster_stats()

        self.assertEqual(self.page.min_edit.text(), "221.00")
        self.assertEqual(self.page.max_edit.text(), "593.00")
        self.assertEqual(self.page.mean_edit.text(), "433.38")
        self.assertEqual(self.page.nodata_edit.text(), "-9999")

    def test_no_raster_clears_stats(self) -> None:
        """Without a layer the fields are blanked."""
        self.page.min_edit.setText("stale")
        with patch.object(self.page.raster_combo, "currentLayer", return_value=None):
            self.page._update_raster_stats()

        self.assertEqual(self.page.min_edit.text(), "")

    def test_nan_nodata_shows_dash(self) -> None:
        """A NaN NoData value is rendered as an em dash."""
        with self._with_layer(self._layer(nodata=float("nan"))):
            self.page._update_raster_stats()

        self.assertEqual(self.page.nodata_edit.text(), "—")

    def test_non_finite_stat_shows_dash(self) -> None:
        """A NaN minimum is rendered as an em dash."""
        layer = self._layer()
        layer.dataProvider.return_value.bandStatistics.return_value.minimumValue = float("nan")

        with self._with_layer(layer):
            self.page._update_raster_stats()

        self.assertEqual(self.page.min_edit.text(), "—")

    def test_provider_failure_clears_stats(self) -> None:
        """A failing provider does not raise and blanks the fields."""
        layer = self._layer()
        layer.dataProvider.return_value.bandStatistics.side_effect = RuntimeError("boom")

        with self._with_layer(layer):
            self.page._update_raster_stats()

        self.assertEqual(self.page.mean_edit.text(), "")
