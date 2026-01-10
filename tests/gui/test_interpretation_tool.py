"""Tests for the profile interpretation tool."""

from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from qgis.core import QgsPointXY, QgsVectorLayer, QgsProject, QgsWkbTypes
from qgis.gui import QgsMapCanvas, QgsRubberBand, QgsVertexMarker
from qgis.PyQt.QtCore import QPoint, Qt

from sec_interp.gui.tools.interpretation_tool import (
    ProfileInterpretationTool,
    ProfileSnapper,
)


class TestInterpretationTool(BaseTestCase):
    """Tests for ProfileInterpretationTool."""

    def setUp(self):
        super().setUp()
        self.canvas = MagicMock()
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

        self.tool = ProfileInterpretationTool(self.canvas)

    def test_snapper_skips_and_continues(self):
        """Test snapper skips invalid layers and missing locators."""
        l1 = MagicMock()
        l1.type.return_value = 1  # Raster

        l2 = MagicMock()
        l2.type.return_value = 0  # Vector
        l2.id.return_value = "l2"
        l2.name.return_value = "l2"

        self.canvas.layers.return_value = [l1, l2]

        with patch(
            "sec_interp.gui.tools.interpretation_tool.QgsPointLocator"
        ) as mock_locator_cls:
            mock_locator = MagicMock()
            match = MagicMock()
            match.isValid.return_value = False
            match.distance.return_value = 100.0
            mock_locator.nearestVertex.return_value = match
            mock_locator.nearestEdge.return_value = match
            mock_locator_cls.return_value = mock_locator

            snapper = ProfileSnapper(self.canvas)
            snapper.snap(QPoint(0, 0))
            # Hits _is_snappable check

    def test_tool_activate_deactivate(self):
        """Test tool activation and deactivation."""
        # Using patch for log_critical_operation to avoid actual logging if needed
        with patch("sec_interp.gui.tools.interpretation_tool.log_critical_operation"):
            self.tool.activate()
            self.canvas.setCursor.assert_called()

            self.tool.deactivate()
            self.assertEqual(len(self.tool.points), 0)

    def test_add_point(self):
        """Test adding points to the polygon."""
        p1 = QgsPointXY(0, 0)
        self.tool._add_point(p1)
        self.assertEqual(len(self.tool.points), 1)
        self.assertIsNotNone(self.tool.rubber_band)
        self.assertEqual(len(self.tool.vertex_markers), 1)

    def test_remove_last_point(self):
        """Test removing the last added point."""
        p1 = QgsPointXY(0, 0)
        p2 = QgsPointXY(100, 100)
        self.tool._add_point(p1)
        self.tool._add_point(p2)

        self.tool._remove_last_point()
        self.assertEqual(len(self.tool.points), 1)
        self.assertEqual(len(self.tool.vertex_markers), 1)

        self.tool._remove_last_point()
        self.assertEqual(len(self.tool.points), 0)
        self.assertIsNone(self.tool.rubber_band)
        self.assertEqual(len(self.tool.vertex_markers), 0)

    def test_canvas_release_right_click(self):
        """Test right click removing last point."""
        self.tool.points = [QgsPointXY(0, 0)]
        self.tool._remove_last_point = MagicMock()

        event = MagicMock()
        event.button.return_value = Qt.RightButton
        self.tool.canvasReleaseEvent(event)
        self.tool._remove_last_point.assert_called_once()

    def test_canvas_move_preview(self):
        """Test mouse move updating rubber band."""
        self.tool.points = [QgsPointXY(0, 0)]
        self.tool._ensure_rubber_band()
        self.tool.rubber_band = MagicMock()

        event = MagicMock()
        event.pos.return_value = QPoint(100, 0)
        self.tool.canvasMoveEvent(event)
        self.tool.rubber_band.reset.assert_called()

    def test_finalize_polygon(self):
        """Test finalizing a valid polygon."""
        self.tool.points = [QgsPointXY(0, 0), QgsPointXY(100, 0), QgsPointXY(50, 50)]
        self.tool.polygonFinished = MagicMock()

        self.tool.finalize_polygon()

        self.tool.polygonFinished.emit.assert_called_once()
        interp = self.tool.polygonFinished.emit.call_args[0][0]
        self.assertEqual(len(interp.vertices_2d), 3)
        self.assertEqual(interp.name, "New Interpretation")

    def test_finalize_invalid(self):
        """Test finalize with less than 3 points."""
        self.tool.points = [QgsPointXY(0, 0), QgsPointXY(100, 0)]
        self.tool.polygonFinished = MagicMock()
        self.tool.finalize_measurement = MagicMock()  # Oops, tool.finalize_polygon

        self.tool.finalize_polygon()
        self.tool.polygonFinished.emit.assert_not_called()

    def test_double_click_finalize(self):
        """Test double click finalizing the polygon."""
        self.tool.points = [QgsPointXY(0, 0), QgsPointXY(100, 0), QgsPointXY(50, 50)]
        self.tool.finalize_polygon = MagicMock()

        event = MagicMock()
        self.tool.canvasDoubleClickEvent(event)
        self.tool.finalize_polygon.assert_called_once()

    def test_key_events(self):
        """Test Enter and Escape keys."""
        self.tool.points = [QgsPointXY(0, 0), QgsPointXY(100, 0), QgsPointXY(50, 50)]
        self.tool.finalize_polygon = MagicMock()

        # Enter to finalize
        event = MagicMock()
        event.key.return_value = Qt.Key_Return
        self.tool.keyPressEvent(event)
        self.tool.finalize_polygon.assert_called_once()

        # Escape to reset
        self.tool.reset = MagicMock()
        event.key.return_value = Qt.Key_Escape
        self.tool.keyPressEvent(event)
        self.tool.reset.assert_called_once()

    def test_snapper_get_locator_error(self):
        """Test error handling in locator creation."""
        snapper = ProfileSnapper(self.canvas)
        layer = MagicMock()
        layer.id.return_value = "id1"
        layer.name.return_value = "layer1"

        with patch(
            "sec_interp.gui.tools.interpretation_tool.QgsPointLocator",
            side_effect=Exception("mock error"),
        ):
            locator = snapper._get_locator(layer, MagicMock(), MagicMock())
            self.assertIsNone(locator)

    def test_reset_with_exception(self):
        """Test reset handles exceptions during cleanup."""
        self.tool.rubber_band = MagicMock()
        self.tool.rubber_band.reset.side_effect = Exception("reset fail")
        self.tool.vertex_markers = [MagicMock()]
        self.tool.vertex_markers[0].side_effect = Exception("marker fail")

        # Should not raise exception
        self.tool.reset()
        self.assertIsNone(self.tool.rubber_band)
        self.assertEqual(len(self.tool.vertex_markers), 0)

    def test_snapper_full_path(self):
        """Test snapper reaching the end and hitting all branches."""
        layer = QgsVectorLayer()
        layer.id = MagicMock(return_value="layer1")
        layer.type = MagicMock(return_value=0)
        self.canvas.layers.return_value = [layer]

        with patch(
            "sec_interp.gui.tools.interpretation_tool.QgsPointLocator"
        ) as mock_locator_cls:
            mock_locator = mock_locator_cls.return_value
            # Vertex snap invalid
            v_match = MagicMock()
            v_match.isValid.return_value = False
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

    def test_snapper_exception_in_loop(self):
        """Test snapper catches exceptions inside the loop."""
        layer = QgsVectorLayer()
        layer.id = MagicMock(return_value="layer1")
        layer.type = MagicMock(return_value=0)
        self.canvas.layers.return_value = [layer]

        with patch.object(
            ProfileSnapper, "_get_locator", side_effect=Exception("loop fail")
        ):
            snapper = ProfileSnapper(self.canvas)
            snapper.snap(QPoint(0, 0))  # Should hit line 88

    def test_snapper_none_locator(self):
        """Test snapper continues if locator is None."""
        layer = QgsVectorLayer()
        layer.id = MagicMock(return_value="layer1")
        layer.type = MagicMock(return_value=0)
        self.canvas.layers.return_value = [layer]

        with patch.object(ProfileSnapper, "_get_locator", return_value=None):
            snapper = ProfileSnapper(self.canvas)
            snapper.snap(QPoint(0, 0))  # Should hit line 73

    def test_snapper_vertex_match(self):
        """Test snapper reaching vertex match lines."""
        layer = QgsVectorLayer()
        layer.id = MagicMock(return_value="layer1")
        layer.type = MagicMock(return_value=0)
        self.canvas.layers.return_value = [layer]

        with patch(
            "sec_interp.gui.tools.interpretation_tool.QgsPointLocator"
        ) as mock_locator_cls:
            mock_locator = mock_locator_cls.return_value
            # Vertex snap valid
            v_match = MagicMock()
            v_match.isValid.return_value = True
            v_match.distance.return_value = 1.0  # Very close
            v_match.point.return_value = QgsPointXY(10, 10)
            mock_locator.nearestVertex.return_value = v_match
            mock_locator.nearestEdge.return_value = MagicMock(isValid=lambda: False)

            snapper = ProfileSnapper(self.canvas)
            snapper.snap(QPoint(10, 10))

    def test_reset_with_exception_in_remove(self):
        """Test reset handles exceptions during removeItem."""
        self.tool.rubber_band = MagicMock()
        self.canvas.scene().removeItem.side_effect = Exception("scene fail")
        # Should not raise
        self.tool.reset()
        self.assertIsNone(self.tool.rubber_band)

    def test_snapper_cleanup(self):
        """Test locator cleanup."""
        snapper = ProfileSnapper(self.canvas)
        snapper._locators = {"old": MagicMock()}
        self.canvas.layers.return_value = []
        snapper.snap(QPoint(0, 0))
        self.assertEqual(len(snapper._locators), 0)

    def test_canvas_release_left_click(self):
        """Test left click adding a point."""
        event = MagicMock()
        event.button.return_value = Qt.LeftButton
        event.pos.return_value = QPoint(50, 50)

        self.tool.canvasReleaseEvent(event)
        self.assertEqual(len(self.tool.points), 1)
        self.assertEqual(self.tool.points[0].x(), 50)

    def test_canvas_move_no_points(self):
        """Test move event ignored if no points."""
        self.tool.points = []
        self.tool._update_rubber_band = MagicMock()
        self.tool.canvasMoveEvent(MagicMock())
        self.tool._update_rubber_band.assert_not_called()

    def test_remove_last_no_points(self):
        """Test _remove_last_point with no points."""
        self.tool.points = []
        self.tool._remove_last_point()  # Should not fail

    def test_update_rubber_band_missing(self):
        """Test _update_rubber_band handles missing band/points."""
        self.tool.rubber_band = None
        self.tool._update_rubber_band(QgsPointXY(0, 0))  # Should not fail

        self.tool._ensure_rubber_band()
        self.tool.points = []
        self.tool._update_rubber_band(QgsPointXY(0, 0))  # Should not fail
