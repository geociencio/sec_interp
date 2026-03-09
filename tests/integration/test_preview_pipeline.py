"""Integration tests for the Preview Rendering Pipeline.

These tests exercise PreviewRenderer and PreviewLayerFactory end-to-end,
using real QGIS memory layers and verifying geometry and feature counts.
PreviewService.calculate_max_points is also tested as a pure-logic method.
"""

from __future__ import annotations

import os

# Force real QGIS for integration tests
os.environ["FORCE_MOCKS"] = "0"

from sec_interp.core.domain import GeologySegment, InterpretationPolygon
from sec_interp.core.domain.entities import StructureMeasurement
from sec_interp.core.services.preview_service import PreviewService
from sec_interp.gui.preview_layer_factory import PreviewLayerFactory
from sec_interp.gui.preview_renderer import PreviewRenderer
from tests.integration.base_integration import BaseIntegrationTest

# ---------------------------------------------------------------------------
# Shared test data builders
# ---------------------------------------------------------------------------


def _simple_topo() -> list[tuple[float, float]]:
    """Return a minimal 5-point topographic profile."""
    return [(0.0, 500.0), (25.0, 510.0), (50.0, 505.0), (75.0, 512.0), (100.0, 508.0)]


def _simple_geology() -> list[GeologySegment]:
    """Return two geology segments covering the full profile."""
    return [
        GeologySegment(
            unit_name="Andesite",
            geometry_wkt=None,
            attributes={"unit": "Andesite"},
            points=[(0.0, 500.0), (50.0, 505.0)],
        ),
        GeologySegment(
            unit_name="Granite",
            geometry_wkt=None,
            attributes={"unit": "Granite"},
            points=[(50.0, 505.0), (100.0, 508.0)],
        ),
    ]


def _simple_structures() -> list[StructureMeasurement]:
    """Return one structural measurement near the centre of the profile."""
    return [
        StructureMeasurement(
            distance=50.0,
            elevation=505.0,
            apparent_dip=30.0,
            original_dip=35.0,
            original_strike=90.0,
            attributes={"type": "S0"},
        )
    ]


def _simple_interpretations() -> list[InterpretationPolygon]:
    """Return one small interpretation polygon."""
    return [
        InterpretationPolygon(
            id="i1",
            name="Alteration",
            type="Alteration",
            vertices_2d=[(10.0, 490.0), (40.0, 490.0), (40.0, 510.0), (10.0, 510.0)],
        )
    ]


# ---------------------------------------------------------------------------
# PreviewLayerFactory tests
# ---------------------------------------------------------------------------


class TestPreviewLayerFactory(BaseIntegrationTest):
    """Integration tests for PreviewLayerFactory layer creation."""

    def setUp(self) -> None:
        """Initialise factory for each test."""
        super().setUp()
        self.factory = PreviewLayerFactory()

    # --- Topography layer ---

    def test_create_topo_layer_returns_valid_layer(self) -> None:
        """create_topo_layer should produce a valid, non-empty QGIS layer."""
        layer = self.factory.create_topo_layer(_simple_topo(), vert_exag=1.0)

        self.assertIsNotNone(layer, "Expected a layer, got None")
        self.assertTrue(layer.isValid(), "Topography layer is not valid")
        # 5 points → 4 segments / features
        self.assertEqual(layer.featureCount(), 4)

    def test_create_topo_layer_applies_vertical_exaggeration(self) -> None:
        """Vertical exaggeration should scale Y coordinates of features."""
        exag = 2.0
        layer_1x = self.factory.create_topo_layer(_simple_topo(), vert_exag=1.0)
        layer_2x = self.factory.create_topo_layer(_simple_topo(), vert_exag=exag)

        feat_1x = next(layer_1x.getFeatures())
        feat_2x = next(layer_2x.getFeatures())

        y_1x = feat_1x.geometry().vertexAt(0).y()
        y_2x = feat_2x.geometry().vertexAt(0).y()

        self.assertAlmostEqual(y_2x, y_1x * exag, places=3)

    def test_create_topo_layer_returns_none_when_empty(self) -> None:
        """create_topo_layer should return None when given empty data."""
        result = self.factory.create_topo_layer([])
        self.assertIsNone(result)

    def test_create_topo_layer_returns_none_when_single_point(self) -> None:
        """create_topo_layer needs at least 2 points; 1 point → None."""
        result = self.factory.create_topo_layer([(0.0, 500.0)])
        self.assertIsNone(result)

    # --- Geology layer ---

    def test_create_geol_layer_returns_valid_layer(self) -> None:
        """create_geol_layer should produce a valid layer with one feature per segment."""
        layer = self.factory.create_geol_layer(_simple_geology(), vert_exag=1.0)

        self.assertIsNotNone(layer)
        self.assertTrue(layer.isValid())
        self.assertEqual(layer.featureCount(), 2)

    def test_create_geol_layer_stores_unit_name(self) -> None:
        """Each geology feature should carry the correct unit name attribute."""
        layer = self.factory.create_geol_layer(_simple_geology())
        units = {f["unit"] for f in layer.getFeatures()}
        self.assertIn("Andesite", units)
        self.assertIn("Granite", units)

    def test_create_geol_layer_returns_none_when_no_data(self) -> None:
        """create_geol_layer should return None when given None or empty list."""
        self.assertIsNone(self.factory.create_geol_layer(None))
        self.assertIsNone(self.factory.create_geol_layer([]))

    # --- Interpretation layer ---

    def test_create_interp_layer_returns_valid_polygon_layer(self) -> None:
        """create_interp_layer should produce a valid polygon layer with correct attributes."""
        layer = self.factory.create_interp_layer(_simple_interpretations())

        self.assertIsNotNone(layer)
        self.assertTrue(layer.isValid())
        self.assertEqual(layer.featureCount(), 1)

        feat = next(layer.getFeatures())
        self.assertEqual(feat["name"], "Alteration")

    def test_create_interp_layer_returns_none_when_empty(self) -> None:
        """create_interp_layer should return None for empty list."""
        self.assertIsNone(self.factory.create_interp_layer([]))

    # --- Structure layer ---

    def test_create_struct_layer_returns_valid_layer(self) -> None:
        """create_struct_layer should produce one line feature per measurement."""
        layer = self.factory.create_struct_layer(
            _simple_structures(),
            reference_data=_simple_topo(),
            vert_exag=1.0,
        )

        self.assertIsNotNone(layer)
        self.assertTrue(layer.isValid())
        self.assertEqual(layer.featureCount(), 1)

    def test_create_struct_layer_returns_none_when_no_data(self) -> None:
        """create_struct_layer should return None when structural data is absent."""
        self.assertIsNone(
            self.factory.create_struct_layer(None, reference_data=_simple_topo())
        )

    # --- Memory layer helper ---

    def test_create_memory_layer_returns_valid_layer(self) -> None:
        """create_memory_layer should produce a valid in-memory QGIS layer."""
        layer, provider = self.factory.create_memory_layer("Point", "TestLayer")
        self.assertIsNotNone(layer)
        self.assertTrue(layer.isValid())
        self.assertIsNotNone(provider)


# ---------------------------------------------------------------------------
# PreviewRenderer tests
# ---------------------------------------------------------------------------


class TestPreviewRenderer(BaseIntegrationTest):
    """Integration tests for PreviewRenderer orchestration layer."""

    def setUp(self) -> None:
        """Initialise renderer (no canvas required for headless tests)."""
        super().setUp()
        self.renderer = PreviewRenderer(canvas=None)

    # --- Topo-only render ---

    def test_render_topo_only_returns_non_empty_layers(self) -> None:
        """render() with topo data should return a non-empty layer list."""
        _canvas, layers = self.renderer.render(topo_data=_simple_topo())

        self.assertIsInstance(layers, list)
        self.assertGreater(len(layers), 0, "Expected at least one layer")
        for layer in layers:
            self.assertTrue(layer.isValid(), f"Layer '{layer.name()}' is not valid")

    def test_render_topo_with_geology_returns_more_layers(self) -> None:
        """render() with geology should return more layers than topo alone."""
        _canvas, topo_only = self.renderer.render(topo_data=_simple_topo())
        self.renderer._cleanup_layers()

        _canvas, topo_geol = self.renderer.render(
            topo_data=_simple_topo(),
            geol_data=_simple_geology(),
        )

        self.assertGreater(
            len(topo_geol),
            len(topo_only),
            "Geology mode should produce more layers than topo-only",
        )

    def test_render_with_interpretations_includes_polygon_layer(self) -> None:
        """render() with interpretation data should include a polygon layer."""
        _canvas, layers = self.renderer.render(
            topo_data=_simple_topo(),
            interp_data=_simple_interpretations(),
        )

        geom_types = {layer.geometryType() for layer in layers}
        # GeometryType 2 = QgsWkbTypes.PolygonGeometry
        from qgis.core import QgsWkbTypes

        self.assertIn(
            QgsWkbTypes.PolygonGeometry,
            geom_types,
            "Expected a polygon layer for interpretations",
        )

    def test_render_returns_empty_list_with_no_data(self) -> None:
        """render() with empty topo data should return (None, [])."""
        canvas, layers = self.renderer.render(topo_data=[])

        self.assertIsNone(canvas)
        self.assertEqual(layers, [])

    def test_render_sets_has_topography_flag(self) -> None:
        """render() with topo data should set has_topography=True."""
        self.renderer.render(topo_data=_simple_topo())
        self.assertTrue(self.renderer.has_topography)

    def test_render_sets_has_structures_flag(self) -> None:
        """render() with structures should set has_structures=True."""
        self.renderer.render(
            topo_data=_simple_topo(),
            struct_data=_simple_structures(),
        )
        self.assertTrue(self.renderer.has_structures)

    def test_render_cleanup_resets_layers_list(self) -> None:
        """_cleanup_layers() should clear self.layers and active_units.

        Note: has_topography / has_structures are reset at the START of the
        next render() call, not inside _cleanup_layers(). This is intentional
        design: the flags reflect the last *rendered* state until a new render
        cycle begins.
        """
        self.renderer.render(topo_data=_simple_topo())
        self.assertGreater(len(self.renderer.layers), 0)

        self.renderer._cleanup_layers()

        # Internal layers list must be cleared
        self.assertEqual(len(self.renderer.layers), 0)
        # active_units (geology color map) must also be reset
        self.assertEqual(self.renderer.active_units, {})


# ---------------------------------------------------------------------------
# PreviewService pure-logic tests
# ---------------------------------------------------------------------------


class TestPreviewServiceCalculateMaxPoints(BaseIntegrationTest):
    """Unit-integration tests for PreviewService.calculate_max_points (pure logic)."""

    def test_auto_lod_returns_canvas_width_based_value(self) -> None:
        """With auto_lod=True the result should be proportional to canvas_width."""
        result = PreviewService.calculate_max_points(
            canvas_width=800, manual_max=500, auto_lod=True
        )
        # Should be roughly 2x the pixel width
        self.assertGreaterEqual(result, 800)

    def test_auto_lod_false_returns_manual_max(self) -> None:
        """With auto_lod=False the manual_max value should be returned exactly."""
        result = PreviewService.calculate_max_points(
            canvas_width=800, manual_max=250, auto_lod=False
        )
        self.assertEqual(result, 250)

    def test_auto_lod_with_zoom_ratio_boosts_detail(self) -> None:
        """A ratio > 1.1 should boost the point count above the base value."""
        base = PreviewService.calculate_max_points(
            canvas_width=800, manual_max=500, auto_lod=True, ratio=1.0
        )
        boosted = PreviewService.calculate_max_points(
            canvas_width=800, manual_max=500, auto_lod=True, ratio=3.0
        )
        self.assertGreater(boosted, base)

    def test_very_small_canvas_uses_minimum(self) -> None:
        """Very small canvas_width should still return at least 200 points."""
        result = PreviewService.calculate_max_points(
            canvas_width=10, manual_max=500, auto_lod=True
        )
        self.assertGreaterEqual(result, 200)
