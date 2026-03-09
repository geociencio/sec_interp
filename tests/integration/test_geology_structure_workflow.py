"""Integration tests for GeologyService and StructureService.

Tests exercise the core processing logic of both services using
in-memory QGIS layers and synthetic domain objects, without requiring
real file-based datasets.
"""

from __future__ import annotations

import os

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
from sec_interp.core.domain.task_inputs import GeologyTaskInput
from sec_interp.core.exceptions import DataMissingError, ValidationError
from sec_interp.core.services.geology_service import GeologyService
from sec_interp.core.services.structure_service import StructureService
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


class TestGeologyServiceProcessTaskData(BaseIntegrationTest):
    """Tests for GeologyService.process_task_data (pure domain logic)."""

    def setUp(self) -> None:
        """Initialise service and reusable base geometry."""
        super().setUp()
        self.service = GeologyService()

        # 1 km horizontal line along E–W at Northing 6_000_000
        self.line_wkt = "LINESTRING(0 6000000, 1000 6000000)"
        self.line_start = QgsPointXY(0.0, 6_000_000.0)

        # Flat master profile: every 100 m at constant elevation 500 m
        self.master_profile: list[tuple[float, float]] = [
            (float(d), 500.0) for d in range(0, 1001, 100)
        ]
        # Grid dists: (dist_along, (x, y), elevation)
        self.master_grid_dists: list[tuple[float, tuple[float, float], float]] = [
            (float(d), (float(d), 6_000_000.0), 500.0) for d in range(0, 1001, 100)
        ]
        self.crs = "EPSG:32719"

    def _build_input(self, outcrop_data: list) -> GeologyTaskInput:
        return GeologyTaskInput(
            line_geometry_wkt=self.line_wkt,
            line_start_x=self.line_start.x(),
            line_start_y=self.line_start.y(),
            crs_authid=self.crs,
            master_profile_data=self.master_profile,
            master_grid_dists=self.master_grid_dists,
            outcrop_data=outcrop_data,
            outcrop_name_field="unit",
        )

    def test_empty_outcrop_data_returns_empty_list(self) -> None:
        """process_task_data with no outcrops should return an empty list."""
        task_input = self._build_input([])
        result = self.service.process_task_data(task_input)
        self.assertEqual(result, [])

    def test_single_outcrop_crossing_line_produces_segment(self) -> None:
        """An outcrop polygon crossing the section line should produce ≥1 segment."""
        # Wide polygon straddling the whole line
        poly_wkt = (
            "POLYGON((100 5999800, 400 5999800, 400 6000200, 100 6000200, 100 5999800))"
        )
        outcrop_data = [
            {
                "wkt": poly_wkt,
                "attrs": {"unit": "Andesite"},
                "unit_name": "Andesite",
            }
        ]
        task_input = self._build_input(outcrop_data)
        result = self.service.process_task_data(task_input)

        self.assertGreater(len(result), 0, "Expected at least one geology segment")
        self.assertEqual(result[0].unit_name, "Andesite")

    def test_two_outcrops_produce_two_segments(self) -> None:
        """Two non-overlapping outcrops should yield (at least) two segments, one per unit."""
        poly_a = (
            "POLYGON((50 5999800, 350 5999800, 350 6000200, 50 6000200, 50 5999800))"
        )
        poly_b = (
            "POLYGON((600 5999800, 900 5999800, 900 6000200, 600 6000200, 600 5999800))"
        )
        outcrop_data = [
            {"wkt": poly_a, "attrs": {"unit": "Andesite"}, "unit_name": "Andesite"},
            {"wkt": poly_b, "attrs": {"unit": "Granite"}, "unit_name": "Granite"},
        ]
        task_input = self._build_input(outcrop_data)
        result = self.service.process_task_data(task_input)

        unit_names = {seg.unit_name for seg in result}
        self.assertIn("Andesite", unit_names)
        self.assertIn("Granite", unit_names)

    def test_outcrop_attributes_preserved_in_segment(self) -> None:
        """Attribute dict from the outcrop data should be preserved in the segment."""
        poly_wkt = (
            "POLYGON((100 5999800, 400 5999800, 400 6000200, 100 6000200, 100 5999800))"
        )
        outcrop_data = [
            {
                "wkt": poly_wkt,
                "attrs": {"unit": "Rhyolite", "age": "Miocene"},
                "unit_name": "Rhyolite",
            }
        ]
        task_input = self._build_input(outcrop_data)
        result = self.service.process_task_data(task_input)

        self.assertGreater(len(result), 0)
        self.assertEqual(result[0].unit_name, "Rhyolite")
        self.assertIn("age", result[0].attributes)
        self.assertEqual(result[0].attributes["age"], "Miocene")

    def test_result_segments_are_sorted_by_distance(self) -> None:
        """Segments should be sorted by their first point's distance along the section."""
        # Granite comes first (x=50–350), Andesite second (x=600–900)
        poly_a = (
            "POLYGON((50 5999800, 350 5999800, 350 6000200, 50 6000200, 50 5999800))"
        )
        poly_b = (
            "POLYGON((600 5999800, 900 5999800, 900 6000200, 600 6000200, 600 5999800))"
        )
        outcrop_data = [
            # Deliberately reversed order
            {"wkt": poly_b, "attrs": {"unit": "Andesite"}, "unit_name": "Andesite"},
            {"wkt": poly_a, "attrs": {"unit": "Granite"}, "unit_name": "Granite"},
        ]
        task_input = self._build_input(outcrop_data)
        result = self.service.process_task_data(task_input)

        if len(result) >= 2:
            dists = [seg.points[0][0] for seg in result]
            self.assertEqual(dists, sorted(dists))


class TestGeologyServiceValidation(BaseIntegrationTest):
    """Tests for GeologyService input validation (integration with real layers)."""

    def setUp(self) -> None:
        super().setUp()
        self.service = GeologyService()

    def test_invalid_line_layer_raises_data_missing_error(self) -> None:
        """_validate_inputs should raise DataMissingError for an invalid line layer."""
        invalid_layer = QgsVectorLayer("invalid_uri", "bad", "ogr")
        raster_layer = None  # will fail on line_lyr check first

        with self.assertRaises(DataMissingError):
            self.service._validate_inputs(invalid_layer, raster_layer, None, "unit", 1)

    def test_extract_line_info_raises_when_layer_empty(self) -> None:
        """_extract_line_info should raise DataMissingError for empty layer."""
        empty_layer = QgsVectorLayer("LineString?crs=EPSG:32719", "empty", "memory")
        with self.assertRaises(DataMissingError):
            self.service._extract_line_info(empty_layer)

    def test_extract_line_info_returns_geometry_and_start(self) -> None:
        """_extract_line_info should return valid geometry and start point for real layer."""
        line_lyr = _make_line_layer()
        geom, start = self.service._extract_line_info(line_lyr)

        self.assertFalse(geom.isNull())
        self.assertAlmostEqual(start.x(), 0.0, places=3)
        self.assertAlmostEqual(start.y(), 0.0, places=3)


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


class TestStructureServiceDetach(BaseIntegrationTest):
    """Integration tests for StructureService.detach_structures with real QGIS layers."""

    def setUp(self) -> None:
        super().setUp()
        self.service = StructureService()

        # 1 km E–W section line at Northing 6_000_000
        self.line_geom = QgsGeometry.fromPolylineXY(
            [QgsPointXY(0, 6_000_000), QgsPointXY(1000, 6_000_000)]
        )

    def test_points_inside_buffer_are_detached(self) -> None:
        """Points within the buffer zone should appear in the detached list."""
        struct_layer = _make_point_layer(
            [
                (500.0, 6_000_000.0, {"strike": 90.0, "dip": 45.0}),
            ],
            extra_fields=[("strike", "double"), ("dip", "double")],
        )

        result = self.service.detach_structures(struct_layer, self.line_geom, 500.0)

        self.assertEqual(len(result), 1)
        self.assertIn("wkt", result[0])
        self.assertIn("attributes", result[0])

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

        result = self.service.detach_structures(struct_layer, self.line_geom, 500.0)

        self.assertEqual(len(result), 3)
        # Each item should carry wkt and attributes
        for item in result:
            self.assertIn("wkt", item)
            self.assertIn("attributes", item)

    def test_empty_layer_returns_empty_list(self) -> None:
        """An empty point layer should return an empty detached list."""
        empty_layer = QgsVectorLayer(
            "Point?crs=EPSG:32719&field=strike:double&field=dip:double",
            "empty_structs",
            "memory",
        )
        result = self.service.detach_structures(empty_layer, self.line_geom, 500.0)
        self.assertEqual(result, [])
