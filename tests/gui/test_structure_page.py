"""Tests for the StructurePage configuration page."""

from __future__ import annotations

import sys

from qgis.PyQt.QtWidgets import QApplication

from sec_interp.gui.ui.pages.structure_page import StructurePage
from tests.base_test import BaseTestCase


class TestStructurePage(BaseTestCase):
    """Verify field-combo repopulation and the signal contract."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure a QApplication exists for widget construction."""
        super().setUpClass()
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        super().setUp()
        self.page = StructurePage()

    def test_layer_change_repopulates_field_combos(self) -> None:
        """Selecting a structural layer feeds both field combos.

        Mirrors ``SignalManager.connect_all`` (disconnect then reconnect) to
        guard against regressions where the wiring is only done in ``_setup_ui``
        and lost on the first reconnection.
        """
        self.page.connect_signals()
        self.page.disconnect_signals()
        self.page.connect_signals()
        layer = object()

        self.page.layer_combo.layerChanged.emit(layer)

        self.page.dip_combo.setLayer.assert_called_with(layer)
        self.page.strike_combo.setLayer.assert_called_with(layer)

    def test_field_combos_stay_empty_before_connect(self) -> None:
        """Wiring lives in connect_signals, not in _setup_ui."""
        self.page.layer_combo.layerChanged.emit(object())

        self.page.dip_combo.setLayer.assert_not_called()
        self.page.strike_combo.setLayer.assert_not_called()

    def test_connect_disconnect_signals(self) -> None:
        """Signal wiring is symmetric and does not raise."""
        self.page.connect_signals()
        self.page.disconnect_signals()
