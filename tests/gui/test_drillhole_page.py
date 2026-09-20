"""Tests for the decomposed DrillholePage coordinator and its tabs."""

from __future__ import annotations

import sys

from qgis.PyQt.QtWidgets import QApplication

from sec_interp.gui.ui.pages.drillhole import CollarTab, IntervalTab, SurveyTab
from sec_interp.gui.ui.pages.drillhole_page import DrillholePage
from tests.base_test import BaseTestCase

_GET_DATA_KEYS = {
    "collar_layer",
    "use_geometry",
    "collar_id",
    "collar_x",
    "collar_y",
    "collar_z",
    "collar_depth",
    "survey_layer",
    "survey_id",
    "survey_depth",
    "survey_azim",
    "survey_incl",
    "interval_layer",
    "interval_id",
    "interval_from",
    "interval_to",
    "interval_lith",
}

_DUMP_KEYS = {
    "dh_collar_layer",
    "dh_collar_id",
    "dh_use_geom",
    "dh_collar_x",
    "dh_collar_y",
    "dh_collar_z",
    "dh_collar_depth",
    "dh_survey_layer",
    "dh_survey_id",
    "dh_survey_depth",
    "dh_survey_azim",
    "dh_survey_incl",
    "dh_interval_layer",
    "dh_interval_id",
    "dh_interval_from",
    "dh_interval_to",
    "dh_interval_lith",
}


class TestDrillholePage(BaseTestCase):
    """Verify the coordinator preserves the page contract after decomposition."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure a QApplication exists for widget construction."""
        super().setUpClass()
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        super().setUp()
        self.page = DrillholePage()

    def test_tabs_are_composed(self) -> None:
        """The page exposes the three decomposed tab widgets."""
        self.assertIsInstance(self.page.collar_tab, CollarTab)
        self.assertIsInstance(self.page.survey_tab, SurveyTab)
        self.assertIsInstance(self.page.interval_tab, IntervalTab)
        self.assertIsNotNone(self.page.tab_widget)

    def test_get_data_contract(self) -> None:
        """get_data returns the full flattened configuration mapping."""
        self.assertEqual(set(self.page.get_data()), _GET_DATA_KEYS)

    def test_dump_contract(self) -> None:
        """Dump returns the persistable keys and covers the layer keys."""
        data = self.page.dump()
        self.assertEqual(set(data), _DUMP_KEYS)
        self.assertTrue(DrillholePage.layer_keys.issubset(data))

    def test_load_reset_roundtrip(self) -> None:
        """Load and reset complete without raising."""
        self.page.load(self.page.dump())
        self.page.reset()

    def test_connect_disconnect_signals(self) -> None:
        """Signal wiring is symmetric and does not raise."""
        self.page.connect_signals()
        self.page.disconnect_signals()

    def test_is_complete_returns_bool(self) -> None:
        """is_complete returns a boolean for an empty configuration."""
        self.assertIsInstance(self.page.is_complete(), bool)
