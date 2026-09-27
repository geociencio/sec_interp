"""Tests for the central section-feature resolver."""

from __future__ import annotations

from unittest.mock import MagicMock

from tests.base_test import BaseTestCase
from tests.mocks.qgis_features import MockQgsFeature
from tests.mocks.qgis_geometry import MockQgsGeometry, MockQgsPointXY
from tests.mocks.qgis_layers import MockQgsVectorLayer

from sec_interp.gui.adapters import geometry
from sec_interp.gui.adapters.validation_extractor import extract_section_line_metrics


def _line_feature(fid: int, wkt: str) -> MockQgsFeature:
    feature = MockQgsFeature(fid)
    feature.setGeometry(MockQgsGeometry.fromWkt(wkt))
    return feature


def _line_layer(*features: MockQgsFeature) -> MockQgsVectorLayer:
    layer = MockQgsVectorLayer("memory", "line")
    layer.dataProvider().addFeatures(list(features))
    return layer


class TestResolveSectionFeature(BaseTestCase):
    """The resolver picks the first feature or the requested fid."""

    def test_default_returns_first_feature(self) -> None:
        layer = _line_layer(_line_feature(7, "LINESTRING(0 0, 10 0)"))

        feature = geometry.resolve_section_feature(layer)

        self.assertIsNotNone(feature)
        self.assertEqual(feature.id(), 7)

    def test_feature_id_selects_matching(self) -> None:
        layer = _line_layer(
            _line_feature(7, "LINESTRING(0 0, 10 0)"),
            _line_feature(9, "LINESTRING(0 0, 20 0)"),
        )

        self.assertEqual(geometry.resolve_section_feature(layer, 9).id(), 9)

    def test_unknown_feature_id_returns_none(self) -> None:
        layer = _line_layer(_line_feature(7, "LINESTRING(0 0, 10 0)"))

        self.assertIsNone(geometry.resolve_section_feature(layer, 99))

    def test_invalid_layer_returns_none(self) -> None:
        self.assertIsNone(geometry.resolve_section_feature(None))
        invalid = MagicMock()
        invalid.isValid.return_value = False
        self.assertIsNone(geometry.resolve_section_feature(invalid))

    def test_resolve_section_geometry(self) -> None:
        layer = _line_layer(_line_feature(1, "LINESTRING(0 0, 10 0)"))

        self.assertIsNotNone(geometry.resolve_section_geometry(layer))

    def test_null_geometry_returns_none(self) -> None:
        feature = MockQgsFeature(1)
        null_geom = MagicMock()
        null_geom.isNull.return_value = True
        feature.setGeometry(null_geom)
        layer = _line_layer(feature)

        self.assertIsNone(geometry.resolve_section_geometry(layer))


class TestSectionLineStartPoint(BaseTestCase):
    """The start point is the first vertex, simple or multipart."""

    def test_simple_line_start(self) -> None:
        geom = MockQgsGeometry.fromWkt("LINESTRING(3 4, 5 6)")

        point = geometry.section_line_start_point(geom)

        self.assertEqual((point.x(), point.y()), (3.0, 4.0))

    def test_multipart_line_start(self) -> None:
        geom = MagicMock()
        geom.isNull.return_value = False
        geom.isMultipart.return_value = True
        geom.asMultiPolyline.return_value = [
            [MockQgsPointXY(1.0, 2.0), MockQgsPointXY(3.0, 4.0)]
        ]

        point = geometry.section_line_start_point(geom)

        self.assertEqual((point.x(), point.y()), (1.0, 2.0))

    def test_null_geometry_returns_origin(self) -> None:
        geom = MagicMock()
        geom.isNull.return_value = True

        point = geometry.section_line_start_point(geom)

        self.assertEqual((point.x(), point.y()), (0.0, 0.0))


class TestExtractSectionLineMetricsWithFid(BaseTestCase):
    """Validation metrics honor the requested feature id."""

    def test_uses_selected_feature(self) -> None:
        layer = _line_layer(
            _line_feature(7, "LINESTRING(0 0, 10 0)"),
            _line_feature(9, "LINESTRING(0 0, 10 0, 20 0)"),
        )

        self.assertEqual(extract_section_line_metrics(layer, 7)[0], 2)
        self.assertEqual(extract_section_line_metrics(layer, 9)[0], 3)
