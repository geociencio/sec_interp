"""Tests for the section feature selector (2-vertex filter and fid-label)."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

from qgis.PyQt.QtWidgets import QApplication

from sec_interp.gui.ui.pages.section_feature_selector import SectionFeatureSelector
from tests.base_test import BaseTestCase
from tests.mocks.qgis_features import MockQgsField, MockQgsFields
from tests.mocks.qgis_geometry import MockQgsGeometry, MockQgsPointXY


def _feature(fid: int, vertices: int, name: str | None = None) -> MagicMock:
    feature = MagicMock()
    feature.id.return_value = fid
    points = [MockQgsPointXY(i, 0) for i in range(vertices)]
    feature.geometry.return_value = MockQgsGeometry.fromPolylineXY(points)
    values = {"name": name}
    feature.attribute.side_effect = values.get
    return feature


def _layer(features: list[MagicMock]) -> MagicMock:
    layer = MagicMock()
    layer.isValid.return_value = True
    fields = MockQgsFields()
    fields.append(MockQgsField("name"))
    layer.fields.return_value = fields
    layer.getFeatures.return_value = iter(features)
    layer.displayExpression.return_value = ""
    layer.displayField.return_value = ""
    return layer


class TestSectionFeatureSelector(BaseTestCase):
    """The selector only lists 2-vertex features and labels them by field."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_lists_only_two_vertex_features(self) -> None:
        selector = SectionFeatureSelector()
        selector.set_layer(
            _layer(
                [
                    _feature(7, 2, "North"),
                    _feature(9, 2, "South"),
                    _feature(11, 3, "Three points"),
                    _feature(13, 1, "One point"),
                ]
            )
        )

        self.assertEqual(selector.feature_combo.count(), 2)
        self.assertEqual(selector.selected_feature_id(), 7)
        self.assertEqual(selector.feature_combo.findData(11), -1)
        self.assertEqual(selector.feature_combo.findData(13), -1)

    def test_fid_label_uses_selected_field(self) -> None:
        selector = SectionFeatureSelector()
        selector.set_layer(_layer([_feature(7, 2, "North"), _feature(9, 2, "South")]))
        self.assertTrue(selector.set_label_field("name"))

        self.assertEqual(selector.feature_combo.currentText(), "7 — North")
        selector.select_feature(9)
        self.assertEqual(selector.feature_combo.currentText(), "9 — South")

    def test_auto_label_falls_back_to_fid(self) -> None:
        selector = SectionFeatureSelector()
        selector.set_layer(_layer([_feature(7, 2, "North")]))
        self.assertEqual(selector.feature_combo.currentText(), "7")

    def test_missing_or_null_field_falls_back_to_fid(self) -> None:
        selector = SectionFeatureSelector()
        selector.set_layer(_layer([_feature(7, 2, None)]))
        self.assertTrue(selector.set_label_field("name"))
        self.assertEqual(selector.feature_combo.currentText(), "7")

    def test_select_invalid_feature_returns_false(self) -> None:
        selector = SectionFeatureSelector()
        selector.set_layer(_layer([_feature(7, 2, "North")]))
        self.assertFalse(selector.select_feature(11))
        self.assertEqual(selector.selected_feature_id(), 7)

    def test_invalid_label_field_falls_back_to_auto(self) -> None:
        selector = SectionFeatureSelector()
        selector.set_layer(_layer([_feature(7, 2, "North")]))
        self.assertFalse(selector.set_label_field("missing"))
        self.assertIsNone(selector.label_field())

    def test_feature_change_emits_signal(self) -> None:
        selector = SectionFeatureSelector()
        selector.set_layer(_layer([_feature(7, 2), _feature(9, 2)]))
        changes: list[int] = []
        selector.featureChanged.connect(lambda: changes.append(1))
        selector.select_feature(9)
        self.assertEqual(len(changes), 1)
        self.assertEqual(selector.selected_feature_id(), 9)

    def test_empty_layer_disables_selector(self) -> None:
        selector = SectionFeatureSelector()
        selector.set_layer(_layer([]))
        self.assertEqual(selector.feature_combo.count(), 0)
        self.assertIsNone(selector.selected_feature_id())
        self.assertFalse(selector.feature_combo.isEnabled())

    def test_layer_without_valid_sections_disables_selector(self) -> None:
        selector = SectionFeatureSelector()
        selector.set_layer(_layer([_feature(11, 3)]))
        self.assertEqual(selector.feature_combo.count(), 0)
        self.assertIsNone(selector.selected_feature_id())
        self.assertFalse(selector.label_field_combo.isEnabled())
