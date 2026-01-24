"""Tests for the profile measurement tool."""

from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from qgis.core import QgsPointXY, QgsVectorLayer, QgsProject, QgsWkbTypes
from qgis.gui import QgsMapCanvas, QgsRubberBand, QgsVertexMarker
from qgis.PyQt.QtCore import QPoint, Qt

from sec_interp.gui.tools.measure_tool import ProfileMeasureTool, ProfileSnapper


class TestMeasureTool(BaseTestCase):
    """Tests for ProfileMeasureTool."""

    def setUp(self):
        super().setUp()
        self.canvas = MagicMock()  # Removed spec=QgsMapCanvas
        self.canvas.scene.return_value = MagicMock()
        self.canvas.layers.return_value = []
        self.canvas.mapUnitsPerPixel.return_value = 1.0

        # Mock transform
        transform = MagicMock()
        transform.toMapCoordinates.side_effect = lambda p: QgsPointXY(p.x(), p.y())
        self.canvas.getCoordinateTransform.return_value = transform

        # Mock map settings
        map_settings = MagicMock()
        map_settings.destinationCrs.return_value = MagicMock()
        self.canvas.mapSettings.return_value = map_settings

        self.tool = ProfileMeasureTool(self.canvas)

    def test_snapper_no_layers(self):
        """Test snapping with no layers."""
        snapper = ProfileSnapper(self.canvas)
        pos = QPoint(10, 20)
        snapped = snapper.snap(pos)

        self.assertEqual(snapped.x(), 10)
        self.assertEqual(snapped.y(), 20)

    @patch("sec_interp.gui.tools.measure_tool.QgsPointLocator")
    def test_snapper_with_layer(self, mock_locator_cls):
        """Test snapping with a vector layer."""
        layer = QgsVectorLayer()
        layer.id = MagicMock(return_value="layer1")
        layer.type = MagicMock(return_value=0)  # VectorLayer
        self.canvas.layers.return_value = [layer]

        # Mock locator match
        mock_locator = mock_locator_cls.return_value
        v_match = MagicMock()
        v_match.isValid.return_value = True
        v_match.distance.return_value = 5.0
        v_match.point.return_value = QgsPointXY(15, 25)
        mock_locator.nearestVertex.return_value = v_match

        # Also mock nearestEdge to avoid float < MagicMock errors
        e_match = MagicMock()
        e_match.isValid.return_value = False
        mock_locator.nearestEdge.return_value = e_match

        snapper = ProfileSnapper(self.canvas)
        pos = QPoint(10, 20)
        snapped = snapper.snap(pos)

        self.assertEqual(snapped.x(), 15)
        self.assertEqual(snapped.y(), 25)

    def test_tool_activate_deactivate(self):
        """Test tool activation and deactivation."""
        self.tool.activate()
        self.canvas.setCursor.assert_called()

        self.tool.points = [QgsPointXY(0, 0)]
        self.tool.deactivate()
        # deactivated tool should NOT reset points anymore
        self.assertEqual(len(self.tool.points), 1)

    def test_add_points(self):
        """Test adding points to the measurement."""
        # signals use .emit()
        self.tool.measurementChanged = MagicMock()

        p1 = QgsPointXY(0, 0)
        self.tool._add_point(p1)
        self.assertEqual(len(self.tool.points), 1)
        self.tool.measurementChanged.emit.assert_not_called()

        p2 = QgsPointXY(100, 100)
        self.tool._add_point(p2)
        self.assertEqual(len(self.tool.points), 2)
        self.tool.measurementChanged.emit.assert_called_once()

        # Verify metrics in signal
        args = self.tool.measurementChanged.emit.call_args[0][0]
        self.assertGreater(args["total_distance"], 0)

    def test_canvas_release_left_click(self):
        """Test left click adding a point."""
        event = MagicMock()
        event.button.return_value = Qt.LeftButton
        event.pos.return_value = QPoint(50, 50)

        self.tool.canvasReleaseEvent(event)
        self.assertEqual(len(self.tool.points), 1)
        self.assertEqual(self.tool.points[0].x(), 50)

    def test_canvas_release_right_click(self):
        """Test right click resetting the tool."""
        self.tool.points = [QgsPointXY(0, 0)]

        event = MagicMock()
        event.button.return_value = Qt.RightButton

        self.tool.canvasReleaseEvent(event)
        self.assertEqual(len(self.tool.points), 0)

    def test_canvas_move_preview(self):
        """Test mouse move providing a measurement preview."""
        self.tool.measurementChanged = MagicMock()
        self.tool.points = [QgsPointXY(0, 0)]

        event = MagicMock()
        event.pos.return_value = QPoint(100, 0)

        self.tool.canvasMoveEvent(event)
        self.tool.measurementChanged.emit.assert_called_once()
        args = self.tool.measurementChanged.emit.call_args[0][0]
        self.assertEqual(args["total_distance"], 100.0)

    def test_finalize_measurement(self):
        """Test finalizing the measurement."""
        self.tool.points = [QgsPointXY(0, 0), QgsPointXY(100, 0)]
        self.tool.measurementFinished = MagicMock()

        # Mock pan tool to avoid constructor issues
        with patch("sec_interp.gui.tools.measure_tool.QgsMapToolPan"):
            self.tool.finalize_measurement()

        self.assertTrue(self.tool.finalized)
        self.assertEqual(len(self.tool.finalized_points), 2)
        # Verify it switched to pan tool
        self.canvas.setMapTool.assert_called()
        # Verify signal emitted
        self.tool.measurementFinished.emit.assert_called_once()

        # Test that clicks are ignored after finalizing
        p_extra = QgsPointXY(200, 200)
        event = MagicMock()
        event.button.return_value = Qt.LeftButton
        event.pos.return_value = QPoint(200, 200)

        self.tool.canvasReleaseEvent(event)
        # points should still have the original 2 points, not 0 nor 3
        self.assertEqual(len(self.tool.points), 2)

    def test_reset_behavior(self):
        """Test difference between normal reset and reset after finalize."""
        self.tool.points = [QgsPointXY(0, 0), QgsPointXY(100, 0)]
        self.tool.rubber_band = MagicMock()

        # Normal reset
        self.tool.reset()
        self.assertEqual(len(self.tool.points), 0)
        self.assertIsNone(self.tool.rubber_band)

        # Reset after finalize
        self.tool.points = [QgsPointXY(0, 0), QgsPointXY(100, 0)]
        self.tool.finalized = True
        self.tool.rubber_band = MagicMock()
        self.tool.reset()
        self.assertEqual(len(self.tool.points), 0)
        self.assertIsNotNone(self.tool.rubber_band)  # Kept visuals

    def test_key_events(self):
        """Test Enter and Escape keys."""
        self.tool.points = [QgsPointXY(0, 0), QgsPointXY(100, 0)]

        # Enter to finalize
        event = MagicMock()
        event.key.return_value = Qt.Key_Return
        self.tool.keyPressEvent(event)
        self.assertTrue(self.tool.finalized)

        # Escape to reset
        self.tool.finalized = False
        event.key.return_value = Qt.Key_Escape
        self.tool.keyPressEvent(event)
        self.assertEqual(len(self.tool.points), 0)

    def test_snapper_edge_snap(self):
        """Test snapping to an edge."""
        layer = QgsVectorLayer()
        layer.id = MagicMock(return_value="layer1")
        layer.type = MagicMock(return_value=0)
        self.canvas.layers.return_value = [layer]

        with patch(
            "sec_interp.gui.tools.measure_tool.QgsPointLocator"
        ) as mock_locator_cls:
            mock_locator = mock_locator_cls.return_value
            # Vertex snap invalid
            v_match = MagicMock()
            v_match.isValid.return_value = False
            v_match.distance.return_value = 100.0
            mock_locator.nearestVertex.return_value = v_match

            # Edge snap valid
            e_match = MagicMock()
            e_match.isValid.return_value = True
            e_match.distance.return_value = 2.0
            e_match.point.return_value = QgsPointXY(20, 30)
            mock_locator.nearestEdge.return_value = e_match

            snapper = ProfileSnapper(self.canvas)
            snapped = snapper.snap(QPoint(18, 28))
            self.assertEqual(snapped.x(), 20)

    def test_snapper_cleanup(self):
        """Test locator cleanup."""
        snapper = ProfileSnapper(self.canvas)
        snapper._locators = {"old_layer": MagicMock()}
        self.canvas.layers.return_value = []  # No layers active

        snapper.snap(QPoint(0, 0))
        self.assertEqual(len(snapper._locators), 0)

    def test_snapper_is_snappable_false(self):
        """Test _is_snappable for non-vector layers."""
        snapper = ProfileSnapper(self.canvas)
        layer = MagicMock()
        layer.type.return_value = 1  # Raster
        self.assertFalse(snapper._is_snappable(layer))
        self.assertFalse(snapper._is_snappable(None))

    def test_snapper_get_locator_error(self):
        """Test error handling in locator creation."""
        snapper = ProfileSnapper(self.canvas)
        layer = MagicMock()
        layer.id.return_value = "id1"
        layer.name.return_value = "layer1"

        with patch(
            "sec_interp.gui.tools.measure_tool.QgsPointLocator",
            side_effect=Exception("mock error"),
        ):
            locator = snapper._get_locator(layer, MagicMock(), MagicMock())
            self.assertIsNone(locator)

    def test_reset_clears_markers(self):
        """Test reset removes markers from scene."""
        marker = MagicMock()
        self.tool.vertex_markers = [marker]
        self.tool.reset()
        self.canvas.scene().removeItem.assert_called_with(marker)
        self.assertEqual(len(self.tool.vertex_markers), 0)

    def test_canvas_move_finalized(self):
        """Test move event ignored if finalized."""
        self.tool.finalized = True
        self.tool.measurementChanged = MagicMock()
        self.tool.canvasMoveEvent(MagicMock())
        self.tool.measurementChanged.emit.assert_not_called()

    def test_finalize_invalid(self):
        """Test finalize with too few points."""
        self.tool.points = [QgsPointXY(0, 0)]
        self.tool.finalize_measurement()
        self.assertFalse(self.tool.finalized)

    def test_calculate_no_points(self):
        """Test _calculate_and_emit_preview with no points."""
        self.tool.points = []
        self.tool.measurementChanged = MagicMock()
        self.tool._calculate_and_emit_preview(QgsPointXY(0, 0))
        self.tool.measurementChanged.emit.assert_not_called()

    def test_snapper_skips_and_continues(self):
        """Test snapper skips invalid layers and missing locators."""
        l1 = MagicMock()
        l1.type.return_value = 1  # Raster (not snappable)

        l2 = MagicMock()
        l2.type.return_value = 0  # Vector
        l2.id.return_value = "l2"
        l2.name.return_value = "l2"

        l3 = MagicMock()
        l3.type.return_value = 0  # Vector
        l3.id.return_value = "l3"
        l3.name.return_value = "l3"

        self.canvas.layers.return_value = [l1, l2, l3]

        with patch(
            "sec_interp.gui.tools.measure_tool.QgsPointLocator"
        ) as mock_locator_cls:
            # l2 fails to get locator
            def get_locator_side_effect(layer, crs, context):
                if layer.id() == "l2":
                    raise Exception("fail")
                m = MagicMock()
                match = MagicMock()
                match.isValid.return_value = False
                match.distance.return_value = 100.0
                m.nearestVertex.return_value = match
                m.nearestEdge.return_value = match
                return m

            mock_locator_cls.side_effect = get_locator_side_effect

            snapper = ProfileSnapper(self.canvas)
            snapper.snap(QPoint(0, 0))
            # Should hit lines 67 and 71

    def test_rubber_band_updates(self):
        """Test rubber band is updated during move and finalize."""
        self.tool.points = [QgsPointXY(0, 0)]
        self.tool._ensure_rubber_band()
        self.tool.rubber_band = MagicMock()

        # Test _update_rubber_band (via move)
        self.tool.canvasMoveEvent(MagicMock(pos=lambda: QPoint(100, 0)))
        self.tool.rubber_band.reset.assert_called()
        self.tool.rubber_band.addPoint.assert_called()

        # Test finalize redrawing rubber band
        self.tool.points = [QgsPointXY(0, 0), QgsPointXY(100, 0)]
        self.tool.rubber_band.reset.reset_mock()
        with patch("sec_interp.gui.tools.measure_tool.QgsMapToolPan"):
            self.tool.finalize_measurement()
        self.tool.rubber_band.reset.assert_called_with(QgsWkbTypes.LineGeometry)
        self.tool.rubber_band.show.assert_called()
