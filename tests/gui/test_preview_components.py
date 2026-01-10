"""Tests for preview components: PreviewLayerFactory, PreviewAxesManager, and PreviewRenderer."""

import unittest
from unittest.mock import MagicMock, patch, call
from pathlib import Path

# BaseTestCase MUST be imported before qgis.core to setup mocks correctly
from tests.base_test import BaseTestCase

from qgis.core import (
    QgsPointXY,
    QgsGeometry,
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
    QgsRectangle,
    QgsProject,
    QgsLineString,
)
from qgis.PyQt.QtGui import QColor, QPainter
from qgis.PyQt.QtCore import QRectF

from sec_interp.gui.preview_layer_factory import PreviewLayerFactory
from sec_interp.gui.preview_axes_manager import PreviewAxesManager
from sec_interp.gui.preview_renderer import PreviewRenderer
from sec_interp.core.types import GeologySegment, InterpretationPolygon


class TestPreviewComponents(BaseTestCase):
    """Tests for Phase 8: Preview Components."""

    def setUp(self):
        super().setUp()
        self.factory = PreviewLayerFactory()
        self.axes_manager = PreviewAxesManager()
        self.renderer = PreviewRenderer()
        self.crs = QgsCoordinateReferenceSystem("EPSG:4326")

    # --- PreviewLayerFactory Tests ---

    def test_factory_get_color_for_unit(self):
        """Test consistent color generation for units."""
        c1 = self.factory.get_color_for_unit("Unit A")
        c2 = self.factory.get_color_for_unit("Unit A")
        c3 = self.factory.get_color_for_unit("Unit B")

        self.assertEqual(c1, c2)
        # It's a modulo based selection, different names might have different colors
        # but the factory has a cache.
        self.assertIn("Unit A", self.factory.active_units)

    def test_create_memory_layer(self):
        """Test creation of memory layers."""
        layer, provider = self.factory.create_memory_layer(
            "Point", "Test Layer", "field=id:integer"
        )
        self.assertIsNotNone(layer)
        self.assertIsNotNone(provider)
        self.assertEqual(layer.name(), "Test Layer")

    def test_create_topo_layer(self):
        """Test topography layer creation."""
        topo_data = [(0, 100), (100, 200), (200, 150)]
        layer = self.factory.create_topo_layer(topo_data, vert_exag=2.0)
        self.assertIsNotNone(layer)
        # It's either "Topography" or "Topographic Profile" depending on implementation
        self.assertTrue("Topograph" in layer.name())
        layer.dataProvider().addFeatures.assert_called()

    def test_create_geol_layer(self):
        """Test geology layer creation."""
        seg1 = GeologySegment(
            unit_name="A",
            geometry=MagicMock(),
            attributes={"unit": "A"},
            points=[(0, 100), (50, 110)],
        )
        seg2 = GeologySegment(
            unit_name="B",
            geometry=MagicMock(),
            attributes={"unit": "B"},
            points=[(50, 110), (100, 120)],
        )
        geol_data = [seg1, seg2]

        layer = self.factory.create_geol_layer(geol_data)
        self.assertIsNotNone(layer)
        self.assertTrue("Geolog" in layer.name())
        # Should add 2 features
        self.assertEqual(len(layer.dataProvider().addFeatures.call_args[0][0]), 2)

    def test_create_struct_layer(self):
        """Test structural points layer creation."""
        topo_data = [(0, 100), (100, 200)]
        struct_data = [
            MagicMock(
                distance=50,
                elevation=150.0,
                apparent_dip=45,
                attributes={"type": "fold"},
            )
        ]

        layer = self.factory.create_struct_layer(struct_data, topo_data, vert_exag=1.0)
        self.assertIsNotNone(layer)
        self.assertTrue("Struct" in layer.name())

    def test_create_drillhole_layers(self):
        """Test drillhole trace and interval layers."""
        # Factory expects list of tuples: (hole_id, trace_points, segments)
        dh_data = [
            (
                "DH1",
                [(0, 100), (0, 50)],
                [
                    GeologySegment(
                        unit_name="A",
                        geometry=MagicMock(),
                        attributes={},
                        points=[(0, 100), (0, 80)],
                    )
                ],
            )
        ]

        trace_layer = self.factory.create_drillhole_trace_layer(dh_data)
        self.assertIsNotNone(trace_layer)

        interval_layer = self.factory.create_drillhole_interval_layer(dh_data)
        self.assertIsNotNone(interval_layer)

    def test_interpolate_elevation(self):
        """Test elevation interpolation."""
        topo_data = [(0, 100), (100, 200)]
        elev = self.factory.interpolate_elevation(topo_data, 50)
        self.assertEqual(elev, 150.0)

        # Edge cases
        self.assertEqual(self.factory.interpolate_elevation(topo_data, -10), 100.0)
        self.assertEqual(self.factory.interpolate_elevation(topo_data, 110), 200.0)
        self.assertEqual(self.factory.interpolate_elevation([], 50), 0.0)
        # d1 == d2 case
        topo_flat = [(0, 100), (0, 100)]
        self.assertEqual(self.factory.interpolate_elevation(topo_flat, 0), 100.0)

    def test_factory_edge_cases(self):
        """Test factory edge cases."""
        # Empty unit name color
        c = self.factory.get_color_for_unit("")
        self.assertTrue(c.isValid())  # Should get default grey

        # Memory layer creation failure
        with patch("sec_interp.gui.preview_layer_factory.QgsVectorLayer") as mock_vl:
            mock_vl.return_value.isValid.return_value = False
            l, p = self.factory.create_memory_layer("Point", "Fail")
            self.assertIsNone(l)
            self.assertIsNone(p)

        # Adaptive sampling
        topo = [(0, 0), (10, 10)]
        l = self.factory.create_topo_layer(topo, use_adaptive_sampling=True)
        self.assertIsNotNone(l)

        # Create geol layer skip short segments
        seg_short = GeologySegment("A", MagicMock(), {}, [(0, 0)])
        l = self.factory.create_geol_layer([seg_short])
        # Layer is created but has 0 features
        self.assertEqual(len(l.dataProvider().addFeatures.call_args[0][0]), 0)

        # Struct layer edge cases
        # Negative dip
        struct_data = [
            MagicMock(
                distance=50,
                elevation=150.0,
                apparent_dip=-45,
                attributes={"type": "fold"},
            )
        ]
        l = self.factory.create_struct_layer(struct_data, [(0, 0), (100, 0)])
        self.assertIsNotNone(l)

        # Dip line length override
        l = self.factory.create_struct_layer(struct_data, [], dip_line_length=50)
        self.assertIsNotNone(l)

        # No reference data for struct calculation default
        l = self.factory.create_struct_layer(struct_data, [])
        self.assertIsNotNone(l)

        # Drillhole edge cases
        self.assertIsNone(self.factory.create_drillhole_trace_layer([]))
        self.assertIsNone(self.factory.create_drillhole_interval_layer([]))

        # Trace skipped if < 2 points
        dh_data = [("H1", [(0, 0)], [])]
        l = self.factory.create_drillhole_trace_layer(dh_data)
        # Layer created but empty features
        self.assertEqual(len(l.dataProvider().addFeatures.call_args[0][0]), 0)

        # Interval skipped if < 2 points
        dh_data_shorts = [("H1", [], [GeologySegment("A", None, {}, [(0, 0)])])]
        l = self.factory.create_drillhole_interval_layer(dh_data_shorts)
        # Layer created but empty features
        self.assertEqual(len(l.dataProvider().addFeatures.call_args[0][0]), 0)

        # Force create_memory_layer failure for all create methods
        # We need data that passes initial checks
        dh_data_full = [
            (
                "H1",
                [(0, 0), (10, 10)],
                [GeologySegment("A", None, {}, [(0, 0), (10, 10)])],
            )
        ]

        with patch.object(
            self.factory, "create_memory_layer", return_value=(None, None)
        ):
            self.assertIsNone(self.factory.create_topo_layer([(0, 0), (10, 10)]))
            self.assertIsNone(
                self.factory.create_geol_layer(
                    [GeologySegment("A", None, {}, [(0, 0), (10, 10)])]
                )
            )
            self.assertIsNone(
                self.factory.create_struct_layer(struct_data, [(0, 0), (100, 0)])
            )
            self.assertIsNone(self.factory.create_drillhole_trace_layer(dh_data_full))
            self.assertIsNone(
                self.factory.create_drillhole_interval_layer(dh_data_full)
            )

        # Drillhole interval with empty segments
        dh_empty_segs = [("H1", [], [])]
        self.assertIsNone(self.factory.create_drillhole_interval_layer(dh_empty_segs))

    # --- PreviewAxesManager Tests ---

    def test_get_nice_interval(self):
        """Test nice interval calculation."""
        self.assertEqual(self.axes_manager.get_nice_interval(12), 10.0)
        self.assertEqual(self.axes_manager.get_nice_interval(25), 20.0)
        self.assertEqual(self.axes_manager.get_nice_interval(60), 50.0)
        self.assertEqual(self.axes_manager.get_nice_interval(80), 100.0)
        self.assertEqual(self.axes_manager.get_nice_interval(-1), 100.0)

    def test_create_axes_layer(self):
        """Test axes layer creation."""
        extent = QgsRectangle(0, 0, 1000, 500)

        layer = self.axes_manager.create_axes_layer(extent)
        self.assertIsNotNone(layer)
        layer.dataProvider().addFeatures.assert_called()

    def test_create_axes_labels_layer(self):
        """Test axes labels layer creation."""
        extent = QgsRectangle(0, 0, 100, 100)

        layer = self.axes_manager.create_axes_labels_layer(extent)
        self.assertIsNotNone(layer)
        self.assertTrue(layer.labelsEnabled())

    def test_axes_manager_edge_cases(self):
        """Test edge cases for axes manager."""
        self.assertIsNone(self.axes_manager.create_axes_layer(None))
        self.assertIsNone(self.axes_manager.create_axes_labels_layer(None))

    # --- PreviewRenderer Tests ---

    def test_renderer_render(self):
        """Test the main render orchestrator."""
        topo_data = [(0, 100), (100, 200)]

        with patch.object(
            self.renderer.layer_factory, "create_topo_layer"
        ) as mock_topo:
            l = QgsVectorLayer("LineString", "topo", "memory")
            mock_topo.return_value = l
            self.renderer.render(topo_data)
            mock_topo.assert_called()

    def test_renderer_render_full(self):
        """Test render with all data types including failures."""
        topo_data = [(0, 100), (100, 200)]
        geol_data = [GeologySegment("A", None, {}, [(0, 0), (10, 10)])]
        # Simulate factory returning None for some, real for others

        with (
            patch.object(
                self.renderer.layer_factory, "create_topo_layer", return_value=None
            ),
            patch.object(
                self.renderer.layer_factory, "create_geol_layer", return_value=None
            ),
            patch.object(
                self.renderer.layer_factory, "create_struct_layer", return_value=None
            ),
            patch.object(
                self.renderer.layer_factory,
                "create_drillhole_trace_layer",
                return_value=None,
            ),
            patch.object(
                self.renderer.layer_factory,
                "create_drillhole_interval_layer",
                return_value=None,
            ),
            patch.object(
                self.renderer.layer_factory, "create_topo_fill_layer", return_value=None
            ),
        ):
            # Should run without error but return None (no valid layers)
            res, layers = self.renderer.render(
                topo_data, geol_data=geol_data, struct_data=[], drillhole_data=[]
            )
            self.assertIsNone(res)
            self.assertEqual(len(layers), 0)

        # Partial success case: Topo fails, but Geol succeeds
        mock_geol_layer = MagicMock()
        mock_geol_layer.id.return_value = "geol"
        mock_geol_layer.extent.return_value = QgsRectangle(0, 0, 10, 10)

        with (
            patch.object(
                self.renderer.layer_factory, "create_topo_layer", return_value=None
            ),
            patch.object(
                self.renderer.layer_factory,
                "create_geol_layer",
                return_value=mock_geol_layer,
            ),
            patch.object(
                self.renderer.layer_factory, "create_struct_layer", return_value=None
            ),
            patch.object(
                self.renderer.layer_factory,
                "create_drillhole_trace_layer",
                return_value=None,
            ),
            patch.object(
                self.renderer.layer_factory,
                "create_drillhole_interval_layer",
                return_value=None,
            ) as mock_create_interp,
            patch.object(
                self.renderer.layer_factory, "create_topo_fill_layer", return_value=None
            ),
        ):
            res, layers = self.renderer.render(topo_data, geol_data=geol_data)

            self.assertIsNone(res)  # Canvas is None
            self.assertIn(mock_geol_layer, layers)
            # Also should have axes and labels
            self.assertEqual(len(layers), 3)

        # Test with drillhole data active
        dh_data = [("H1", [], [])]
        mock_dh_layer = MagicMock()
        mock_dh_layer.id.return_value = "dh"
        mock_dh_layer.extent.return_value = QgsRectangle(0, 0, 10, 10)
        with (
            patch.object(
                self.renderer.layer_factory,
                "create_drillhole_trace_layer",
                return_value=mock_dh_layer,
            ),
            patch.object(
                self.renderer.layer_factory,
                "create_drillhole_interval_layer",
                return_value=None,
            ),
        ):
            res, layers = self.renderer.render(topo_data, drillhole_data=dh_data)
            # Should include drillhole trace layer
            self.assertTrue(mock_dh_layer in layers)

    def test_renderer_render_everything(self):
        """Test render with all features enabled (canvas, structures, interp)."""
        self.renderer.canvas = MagicMock()
        topo_data = [(0, 100), (100, 200)]
        struct_data = [MagicMock(distance=50, elevation=150.0, apparent_dip=45)]
        dh_data = [
            (
                "H1",
                [(0, 0), (0, 10)],
                [GeologySegment("A", None, {}, [(0, 0), (0, 10)])],
            )
        ]
        interp_data = [
            InterpretationPolygon("1", "A", "lith", [(0, 0), (10, 10), (10, 0)])
        ]

        with (
            patch.object(
                self.renderer.layer_factory,
                "create_topo_layer",
                return_value=MagicMock(),
            ) as m_topo,
            patch.object(
                self.renderer.layer_factory,
                "create_geol_layer",
                return_value=MagicMock(),
            ),
            patch.object(
                self.renderer.layer_factory,
                "create_struct_layer",
                return_value=MagicMock(),
            ) as m_struct,
            patch.object(
                self.renderer.layer_factory,
                "create_drillhole_trace_layer",
                return_value=MagicMock(),
            ),
            patch.object(
                self.renderer.layer_factory,
                "create_drillhole_interval_layer",
                return_value=MagicMock(),
            ) as m_dh_int,
            patch.object(
                self.renderer.axes_manager,
                "create_axes_layer",
                return_value=MagicMock(),
            ),
            patch.object(
                self.renderer.axes_manager,
                "create_axes_labels_layer",
                return_value=MagicMock(),
            ),
        ):
            m_topo.return_value.extent.return_value = QgsRectangle(0, 0, 100, 200)

            res, _ = self.renderer.render(
                topo_data,
                struct_data=struct_data,
                drillhole_data=dh_data,
                interp_data=interp_data,
            )

            self.assertIsNotNone(res)
            self.assertTrue(self.renderer.has_topography)
            self.assertTrue(self.renderer.has_structures)
            # Canvas calls
            self.renderer.canvas.setLayers.assert_called()
            self.renderer.canvas.refresh.assert_called()
            # Interp
            self.assertEqual(len(self.renderer.interpretation_rubbers), 1)

    def test_renderer_cleanup(self):
        """Test layer cleanup."""
        mock_layer = MagicMock()
        mock_layer.id.return_value = "mock_id"
        self.renderer.layers = [mock_layer]

        project = QgsProject.instance()
        project.addMapLayer(mock_layer)  # Ensure it's in the project

        with patch.object(project, "removeMapLayer") as mock_remove:
            self.renderer._cleanup_layers()
            mock_remove.assert_called()
            self.assertEqual(len(self.renderer.layers), 0)

    def test_renderer_render_interpretations(self):
        """Test interpretation rendering."""
        # Fix: canvas is required for rubber bands
        self.renderer.canvas = MagicMock()
        interp_data = [
            InterpretationPolygon(
                id="1",
                name="A",
                type="lithology",
                vertices_2d=[(0, 0), (10, 10), (10, 0)],
                color="#FF0000",
            )
        ]
        self.renderer._render_interpretations(interp_data, vert_exag=1.0)
        self.assertEqual(len(self.renderer.interpretation_rubbers), 1)

        # Cleanup
        self.renderer._cleanup_layers()
        self.assertEqual(len(self.renderer.interpretation_rubbers), 0)

    def test_renderer_calculate_extent(self):
        """Test combined extent calculation."""
        l1 = MagicMock()
        l1.extent.return_value = QgsRectangle(0, 0, 50, 50)
        l2 = MagicMock()
        l2.extent.return_value = QgsRectangle(20, 20, 100, 100)

        extent = self.renderer._calculate_extent([l1, l2])
        self.assertEqual(extent.xMinimum(), 0)
        self.assertEqual(extent.xMaximum(), 100)
        self.assertEqual(extent.yMinimum(), 0)
        self.assertEqual(extent.yMaximum(), 100)

    def test_renderer_export_to_image(self):
        """Test image export."""
        from sec_interp.gui import preview_renderer

        # Reset mocks
        preview_renderer.QgsMapSettings.reset_mock()
        preview_renderer.QgsMapRendererCustomPainterJob.reset_mock()

        # Setup return values
        mock_job_inst = MagicMock()
        preview_renderer.QgsMapRendererCustomPainterJob.return_value = mock_job_inst
        mock_job_inst.start.return_value = None

        success = self.renderer.export_to_image(
            [], QgsRectangle(0, 0, 10, 10), 800, 600, "/tmp/out.png"
        )

        preview_renderer.QgsMapSettings.assert_called()
        preview_renderer.QgsMapRendererCustomPainterJob.assert_called()
        mock_job_inst.start.assert_called()

    def test_renderer_draw_legend(self):
        """Test legend drawing delegation."""
        painter = MagicMock()
        rect = QRectF(0, 0, 100, 100)
        # Match the multi-arg call
        with patch.object(self.renderer.legend_renderer, "draw_legend") as mock_draw:
            self.renderer.draw_legend(painter, rect)
            mock_draw.assert_called()

    def test_renderer_edge_cases(self):
        """Test renderer edge cases."""
        # Invalid vert_exag
        self.assertEqual(self.renderer.render([], vert_exag=0), (None, []))

        # Render interpretations without canvas
        self.renderer.canvas = None
        self.renderer._render_interpretations([MagicMock()], 1.0)
        # Should just return/log, not crash

        # Regression: Render with geol but no topo (unpacking error)
        geol_data = [GeologySegment("A", MagicMock(), {}, [(0, 0), (10, 10)])]
        # Should NOT raise TypeError
        self.renderer.render(topo_data=None, geol_data=geol_data)

        # Render interpretations with short polygon (coverage for continue)
        self.renderer.canvas = MagicMock()
        short_poly = InterpretationPolygon("s", "S", "lite", [(0, 0), (0, 10)])
        self.renderer._render_interpretations([short_poly], 1.0)

        # Render interp invalid color
        from sec_interp.gui import preview_renderer

        self.renderer.canvas = MagicMock()
        poly = InterpretationPolygon(
            "1", "A", "lith", [(0, 0), (10, 10), (10, 0)], color=None
        )

        # Checking color validity logic by mocking QColor(None) -> invalid
        with patch.object(preview_renderer, "QColor") as mock_color:
            mock_inst = mock_color.return_value
            mock_inst.isValid.return_value = False
            # Force invalid color path
            self.renderer._render_interpretations([poly], 1.0)
            # Should use default color (second call to QColor)
            self.assertGreaterEqual(mock_color.call_count, 2)

        # Interp color exception
        # First call raises ValueError, second call returns mock
        with patch.object(
            preview_renderer, "QColor", side_effect=[ValueError, MagicMock()]
        ):
            self.renderer._render_interpretations([poly], 1.0)

        # Export exception
        with patch(
            "sec_interp.gui.preview_renderer.QgsMapSettings",
            side_effect=Exception("Boom"),
        ):
            self.assertFalse(self.renderer.export_to_image([], None, 100, 100, "path"))


if __name__ == "__main__":
    unittest.main()
