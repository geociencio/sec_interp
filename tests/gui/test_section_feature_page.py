"""Tests for SectionPage feature selection persistence and signal wiring."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

from qgis.PyQt.QtWidgets import QApplication

from sec_interp.gui.ui.pages.section_page import SectionPage
from tests.base_test import BaseTestCase
from tests.gui.test_section_feature_selector import _feature, _layer
from tests.mocks.qt_mocks import mock_signal


class TestSectionPageFeatureSelection(BaseTestCase):
    """SectionPage owns the selector and persists its feature/label state."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        super().setUp()
        self.page = SectionPage()
        self.layer = _layer([_feature(7, 2, "North"), _feature(9, 2, "South")])
        self.page.line_combo.currentLayer = MagicMock(return_value=self.layer)

    def test_layer_change_selects_first_valid_feature(self) -> None:
        self.page._on_line_layer_changed(self.layer)
        self.assertEqual(self.page.section_feature_id, 7)
        self.assertEqual(self.page.feature_selector.feature_combo.count(), 2)

    def test_feature_change_updates_id_and_data_changed(self) -> None:
        self.page.connect_signals()
        self.page._on_line_layer_changed(self.layer)
        changes: list[int] = []
        self.page.dataChanged = mock_signal()
        self.page.dataChanged.connect(lambda: changes.append(1))
        self.page.feature_selector.select_feature(9)
        self.assertEqual(self.page.section_feature_id, 9)
        self.assertEqual(len(changes), 1)

    def test_get_data_and_dump_persist_feature_and_label_field(self) -> None:
        self.page.connect_signals()
        self.page._on_line_layer_changed(self.layer)
        self.page.feature_selector.select_feature(9)
        self.page.feature_selector.set_label_field("name")

        data = self.page.get_data()
        self.assertEqual(data["section_feature_id"], 9)
        self.assertEqual(data["section_feature_label_field"], "name")
        dumped = self.page.dump()
        self.assertEqual(dumped["section_feature_id"], 9)
        self.assertEqual(dumped["section_feature_label_field"], "name")

    def test_load_restores_valid_feature_and_field(self) -> None:
        self.page.load(
            {
                "section_layer": self.layer,
                "section_feature_id": 9,
                "section_feature_label_field": "name",
            }
        )
        self.assertEqual(self.page.section_feature_id, 9)
        self.assertEqual(self.page.feature_selector.label_field(), "name")

    def test_load_missing_feature_falls_back_to_first_valid(self) -> None:
        self.page.load({"section_layer": self.layer, "section_feature_id": 999})
        self.assertEqual(self.page.section_feature_id, 7)

    def test_reset_clears_selector(self) -> None:
        self.page._on_line_layer_changed(self.layer)
        self.page.reset()
        self.assertIsNone(self.page.section_feature_id)
        self.assertEqual(self.page.feature_selector.feature_combo.count(), 0)
