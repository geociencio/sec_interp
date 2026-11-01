"""Integration tests for signal idempotency in the symbology tab."""

import unittest

from qgis.core import QgsApplication

from sec_interp.gui.renderers.color_manager import ColorManager
from sec_interp.gui.ui.pages.settings.symbology_tab import SymbologyTab
from tests.integration.base_integration import BaseIntegrationTest

# The mock-first suite imports this module too; only run against real QGIS/Qt.
_IS_MOCK = getattr(QgsApplication, "__module__", "").startswith("tests.mocks")


@unittest.skipIf(_IS_MOCK, "requires real QGIS/Qt (run with FORCE_MOCKS=0)")
class TestSymbologySignalIdempotency(BaseIntegrationTest):
    """A re-invoked ``connect_signals`` must not duplicate connections."""

    def test_changed_emits_once_after_two_connect_calls(self) -> None:
        """Two ``connect_signals`` calls produce one ``changed`` emission."""
        tab = SymbologyTab()
        emitted = []
        tab.changed.connect(lambda: emitted.append(1))

        tab.connect_signals()
        tab.connect_signals()
        tab.chk_drill_labels.setChecked(not tab.chk_drill_labels.isChecked())

        self.assertEqual(len(emitted), 1)

    def test_reset_runs_once_after_two_connect_calls(self) -> None:
        """Two ``connect_signals`` calls produce one reset execution."""
        tab = SymbologyTab()
        manager = ColorManager()
        manager.register_units({"A"})
        tab.set_unit_manager(manager)

        calls = []
        original_set_order = manager.set_order
        manager.set_order = lambda order: (calls.append(1), original_set_order(order))[1]

        tab.connect_signals()
        tab.connect_signals()
        tab.btn_reset_units.click()

        self.assertEqual(len(calls), 1)
