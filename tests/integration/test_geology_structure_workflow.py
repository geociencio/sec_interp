"""Integration tests for GeologyService and StructureService.

Tests exercise the core processing logic of both services using
in-memory QGIS layers and synthetic domain objects, without requiring
real file-based datasets.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock

os.environ["FORCE_MOCKS"] = "0"

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsPointXY,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QMetaType

from sec_interp.core import utils as scu
from sec_interp.core.domain.task_inputs import GeologyContext, OutcropSegments
from sec_interp.core.exceptions import DataMissingError, ValidationError
from sec_interp.core.services.geology_service import GeologyService
from sec_interp.core.services.structure_service import StructureService
from sec_interp.gui.adapters.geology_extractor import GeologyExtractor
from sec_interp.gui.adapters.structure_extractor import StructureExtractor
from tests.integration.base_integration import BaseIntegrationTest

# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------


def _make_line_layer(x0=0.0, y0=0.0, x1=1000.0, y1=0.0) -> QgsVectorLayer:
    """Create a minimal in-memory line layer with one horizontal feature."""
    layer = QgsVectorLayer("LineString?crs=EPSG:32719", "section_line", "memory")
    feat = QgsFeature()
    feat.setGeometry(
        QgsGeometry.fromPolylineXY([QgsPointXY(x0, y0), QgsPointXY(x1, y1)])
    )
    layer.dataProvider().addFeatures([feat])
    layer.updateExtents()
    return layer


def _make_polygon_layer(
    polygons: list[tuple[str, list[QgsPointXY]]], unit_field: str = "unit"
) -> QgsVectorLayer:
    """Create a polygon layer with given unit names and ring geometries."""
    layer = QgsVectorLayer(
        f"Polygon?crs=EPSG:32719&field={unit_field}:string(50)",
        "outcrops",
        "memory",
    )
    for unit_name, ring in polygons:
        feat = QgsFeature(layer.fields())
        if ring[0] != ring[-1]:
            ring = ring + [ring[0]]
        feat.setGeometry(QgsGeometry.fromPolygonXY([ring]))
        feat.setAttribute(unit_field, unit_name)
        layer.dataProvider().addFeatures([feat])
    layer.updateExtents()
    return layer


def _make_point_layer(
    points: list[tuple[float, float, dict]],
    extra_fields: list[tuple[str, str]] | None = None,
) -> QgsVectorLayer:
    """Create an in-memory point layer with optional extra fields.

    Args:
        points: List of (x, y, attributes_dict) tuples.
        extra_fields: Optional list of (name, type_str) tuples.

    """
    uri = "Point?crs=EPSG:32719"
    if extra_fields:
        for name, type_str in extra_fields:
            uri += f"&field={name}:{type_str}"
    layer = QgsVectorLayer(uri, "structures", "memory")
    for x, y, attrs in points:
        feat = QgsFeature(layer.fields())
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
        for k, v in attrs.items():
            feat.setAttribute(k, v)
        layer.dataProvider().addFeatures([feat])
    layer.updateExtents()
    return layer


# ---------------------------------------------------------------------------
# GeologyService tests
# ---------------------------------------------------------------------------


class TestGeologyExtractorContext(BaseIntegrationTest):
    """Integration tests for GeologyExtractor (Extract + intersection)."""

    def setUp(self) -> None:
        super().setUp()
        self.extractor = GeologyExtractor()

        # 1 km E-W section line at Northing 6_000_000
        self.line_layer = _make_line_layer(0.0, 6_000_000.0, 1000.0, 6_000_000.0)

        # Mock DEM raster (valid, single band, 100 m pixel)
        self.raster = MagicMock()
        self.raster.isValid.return_value = True
        self.raster.bandCount.return_value = 1
        self.raster.rasterUnitsPerPixelX.return_value = 100.0
        self.raster.dataProvider.return_value.sample.return_value = (500.0, True)

    def _make_outcrop_layer(self) -> QgsVectorLayer:
        return _make_polygon_layer(
            [
                (
                    "Andesite",
                    [
                        QgsPointXY(100, 5_999_800),
                        QgsPointXY(400, 5_999_800),
                        QgsPointXY(400, 6_000_200),
                        QgsPointXY(100, 6_000_200),
                    ],
                )
            ]
        )

    def test_extract_context_produces_segments(self) -> None:
        """An outcrop crossing the section line should produce intersection segments."""
        context = self.extractor.extract_context(
            self.line_layer, self.raster, self._make_outcrop_layer(), "unit", 1
        )

        self.assertGreater(len(context.outcrops), 0)
        self.assertEqual(context.outcrops[0].unit_name, "Andesite")
        self.assertGreater(len(context.outcrops[0].segments), 0)
        self.assertGreater(len(context.master_profile_data), 0)

    def test_extract_context_no_outcrop_features_returns_empty(self) -> None:
        """A polygon layer with no features should yield no outcrops."""
        empty = QgsVectorLayer(
            "Polygon?crs=EPSG:32719&field=unit:string(50)", "empty", "memory"
        )
        context = self.extractor.extract_context(
            self.line_layer, self.raster, empty, "unit", 1
        )
        self.assertEqual(context.outcrops, [])

    def test_invalid_line_layer_raises_data_missing_error(self) -> None:
        """_validate_inputs should raise DataMissingError for an invalid line layer."""
        invalid_layer = QgsVectorLayer("invalid_uri", "bad", "ogr")
        with self.assertRaises(DataMissingError):
            self.extractor._validate_inputs(invalid_layer, None, None, "unit", 1)

    def test_extract_line_info_raises_when_layer_empty(self) -> None:
        """_extract_line_info should raise DataMissingError for empty layer."""
        empty_layer = QgsVectorLayer("LineString?crs=EPSG:32719", "empty", "memory")
        with self.assertRaises(DataMissingError):
            self.extractor._extract_line_info(empty_layer)

    def test_extract_line_info_returns_geometry_and_start(self) -> None:
        """_extract_line_info should return valid geometry and start point."""
        geom, start = self.extractor._extract_line_info(self.line_layer)
        self.assertFalse(geom.isNull())
        self.assertAlmostEqual(start.x(), 0.0, places=3)
        self.assertAlmostEqual(start.y(), 6_000_000.0, places=3)


class TestGeologyServiceBuildSegments(BaseIntegrationTest):
    """Tests for GeologyService.build_segments (pure computation)."""

    def setUp(self) -> None:
        super().setUp()
        self.service = GeologyService()

    def _build_context(self, outcrops: list[OutcropSegments]) -> GeologyContext:
        master_profile = [(float(d), 500.0) for d in range(0, 1001, 100)]
        master_grid = [
            (float(d), (float(d), 6_000_000.0), 500.0) for d in range(0, 1001, 100)
        ]
        return GeologyContext(
            master_profile_data=master_profile,
            master_grid_dists=master_grid,
            outcrops=outcrops,
        )

    def test_empty_outcrop_data_returns_empty_list(self) -> None:
        """build_segments with no outcrops should return an empty list."""
        result = self.service.build_segments(self._build_context([]))
        self.assertEqual(result, [])

    def test_single_outcrop_produces_segment(self) -> None:
        """A single outcrop segment should produce a GeologySegment."""
        outcrops = [
            OutcropSegments(
                "Andesite",
                {"unit": "Andesite"},
                [(200.0, 400.0, "LINESTRING(200 6000000, 400 6000000)")],
            )
        ]
        result = self.service.build_segments(self._build_context(outcrops))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].unit_name, "Andesite")

    def test_outcrop_attributes_preserved_in_segment(self) -> None:
        """Attribute dict should be preserved in the segment."""
        outcrops = [
            OutcropSegments("Rhyolite", {"age": "Miocene"}, [(200.0, 400.0, "wkt")])
        ]
        result = self.service.build_segments(self._build_context(outcrops))

        self.assertEqual(result[0].unit_name, "Rhyolite")
        self.assertEqual(result[0].attributes["age"], "Miocene")

    def test_result_segments_are_sorted_by_distance(self) -> None:
        """Segments should be sorted by their first point's distance."""
        outcrops = [
            OutcropSegments("Andesite", {}, [(600.0, 900.0, "wkt")]),
            OutcropSegments("Granite", {}, [(50.0, 350.0, "wkt")]),
        ]
        result = self.service.build_segments(self._build_context(outcrops))

        dists = [seg.points[0][0] for seg in result]
        self.assertEqual(dists, sorted(dists))


# ---------------------------------------------------------------------------
# StructureService tests
# ---------------------------------------------------------------------------


class TestStructureServiceParseData(BaseIntegrationTest):
    """Tests for StructureService._parse_structural_data (pure logic)."""

    def setUp(self) -> None:
        super().setUp()
        self.service = StructureService()

    def test_valid_strike_dip_returns_tuple(self) -> None:
        """Valid strike and dip should return (strike, dip, apparent_dip) tuple."""
        attrs = {"strike": 90.0, "dip": 45.0}
        result = self.service._parse_structural_data(attrs, "strike", "dip", 0.0)

        self.assertIsNotNone(result)
        strike, dip, app_dip = result
        self.assertAlmostEqual(strike, 90.0, places=1)
        self.assertAlmostEqual(dip, 45.0, places=1)

    def test_section_parallel_strike_gives_zero_apparent_dip(self) -> None:
        """Strike parallel to the section line should yield near-zero apparent dip."""
        # Section azimuth = 90° (E–W), strike = 90° → apparent dip ≈ 0
        attrs = {"strike": 90.0, "dip": 60.0}
        result = self.service._parse_structural_data(attrs, "strike", "dip", 90.0)
        self.assertIsNotNone(result)
        _, _, app_dip = result
        self.assertAlmostEqual(abs(app_dip), 0.0, places=1)

    def test_section_perpendicular_strike_gives_full_dip(self) -> None:
        """Strike perpendicular to section (section az=0) should give maximum apparent dip."""
        # Section azimuth = 0° (N–S), strike = 90° (E–W), dip = 45°
        attrs = {"strike": 90.0, "dip": 45.0}
        result = self.service._parse_structural_data(attrs, "strike", "dip", 0.0)
        self.assertIsNotNone(result)
        _, dip, app_dip = result
        self.assertAlmostEqual(abs(app_dip), dip, places=0)

    def test_none_strike_returns_none(self) -> None:
        """Missing strike value should return None."""
        attrs = {"strike": None, "dip": 30.0}
        result = self.service._parse_structural_data(attrs, "strike", "dip", 0.0)
        self.assertIsNone(result)

    def test_none_dip_returns_none(self) -> None:
        """Missing dip value should return None."""
        attrs = {"strike": 45.0, "dip": None}
        result = self.service._parse_structural_data(attrs, "strike", "dip", 0.0)
        self.assertIsNone(result)

    def test_out_of_range_dip_returns_none(self) -> None:
        """Dip > 90° is geometrically invalid and should return None."""
        attrs = {"strike": 45.0, "dip": 95.0}
        result = self.service._parse_structural_data(attrs, "strike", "dip", 0.0)
        self.assertIsNone(result)

    def test_missing_field_returns_none(self) -> None:
        """Missing attribute key should return None gracefully."""
        attrs = {}
        result = self.service._parse_structural_data(attrs, "strike", "dip", 0.0)
        self.assertIsNone(result)


class TestStructureExtractorDetach(BaseIntegrationTest):
    """Integration tests for StructureExtractor with real QGIS layers."""

    def setUp(self) -> None:
        super().setUp()
        self.extractor = StructureExtractor()

        # 1 km E–W section line at Northing 6_000_000
        self.line_layer = _make_line_layer(0.0, 6_000_000.0, 1000.0, 6_000_000.0)

    def test_points_inside_buffer_are_detached(self) -> None:
        """Points within the buffer zone should appear in the detached list."""
        struct_layer = _make_point_layer(
            [
                (500.0, 6_000_000.0, {"strike": 90.0, "dip": 45.0}),
            ],
            extra_fields=[("strike", "double"), ("dip", "double")],
        )

        ctx = self.extractor.extract_section_and_structures(
            self.line_layer, struct_layer, 500.0
        )

        self.assertIsNotNone(ctx)
        self.assertEqual(len(ctx.structures), 1)
        self.assertIn("point", ctx.structures[0])
        self.assertIn("attributes", ctx.structures[0])

    def test_multiple_points_on_line_all_detached(self) -> None:
        """Multiple points within the buffer should all appear in the detached list."""
        struct_layer = _make_point_layer(
            [
                (200.0, 6_000_000.0, {"strike": 90.0, "dip": 30.0}),
                (500.0, 6_000_000.0, {"strike": 45.0, "dip": 60.0}),
                (800.0, 6_000_000.0, {"strike": 135.0, "dip": 20.0}),
            ],
            extra_fields=[("strike", "double"), ("dip", "double")],
        )

        ctx = self.extractor.extract_section_and_structures(
            self.line_layer, struct_layer, 500.0
        )

        self.assertIsNotNone(ctx)
        self.assertEqual(len(ctx.structures), 3)
        # Each item should carry point and attributes
        for item in ctx.structures:
            self.assertIn("point", item)
            self.assertIn("attributes", item)

    def test_empty_layer_returns_empty_list(self) -> None:
        """An empty point layer should return an empty detached list."""
        empty_layer = QgsVectorLayer(
            "Point?crs=EPSG:32719&field=strike:double&field=dip:double",
            "empty_structs",
            "memory",
        )
        ctx = self.extractor.extract_section_and_structures(
            self.line_layer, empty_layer, 500.0
        )
        self.assertIsNotNone(ctx)
        self.assertEqual(ctx.structures, [])
