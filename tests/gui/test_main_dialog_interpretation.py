"""Tests for DialogInterpretationManager."""

import unittest
from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from sec_interp.gui.main_dialog_interpretation import DialogInterpretationManager
from sec_interp.core.domain import InterpretationPolygon


class TestDialogInterpretationManager(BaseTestCase):
    """Tests for the DialogInterpretationManager class."""

    def setUp(self):
        super().setUp()
        self.dialog = MagicMock()
        self.dialog.project = MagicMock()
        self.manager = DialogInterpretationManager(self.dialog)

    def test_load_interpretations_empty(self):
        """Test loading interpretations when none exist."""
        self.dialog.project.readEntry.return_value = ("[]", True)
        self.manager.load_interpretations()
        self.assertEqual(len(self.manager.interpretations), 0)

    def test_load_interpretations_valid(self):
        """Test loading valid interpretations from project."""
        json_data = '[{"id": "1", "name": "Unit A", "type": "lithology", "vertices_2d": [[0,0], [10,10]]}]'
        self.dialog.project.readEntry.return_value = (json_data, True)

        self.manager.load_interpretations()

        self.assertEqual(len(self.manager.interpretations), 1)
        self.assertEqual(self.manager.interpretations[0].name, "Unit A")
        self.assertEqual(
            self.manager.interpretations[0].vertices_2d, [(0, 0), (10, 10)]
        )

    def test_save_interpretations(self):
        """Test saving interpretations to project."""
        interp = InterpretationPolygon(
            id="1", name="Unit A", type="lithology", vertices_2d=[(0, 0), (1, 1)]
        )
        self.manager.interpretations = [interp]

        self.manager.save_interpretations()

        self.dialog.project.writeEntry.assert_called_once()
        args = self.dialog.project.writeEntry.call_args[0]
        self.assertEqual(args[0], "SecInterp")
        self.assertEqual(args[1], "interpretations")
        self.assertIn('"name": "Unit A"', args[2])

    @patch("sec_interp.gui.main_dialog_interpretation.QgsGeometry")
    def test_apply_attribute_inheritance_geology(self, MockGeom):
        """Test attribute inheritance from geology data."""
        # Setup interpretation to inherit
        interp = InterpretationPolygon(
            id="1", name="", type="", vertices_2d=[(0, 0), (10, 0), (5, 5)]
        )

        # Setup mock geometry and centroid
        mock_poly = MockGeom.fromPolygonXY.return_value
        ref_point = MagicMock()
        mock_poly.centroid.return_value.asPoint.return_value = ref_point
        ref_point.distance.side_effect = lambda p: 1.0  # Constant distance

        # Setup cached sediment
        mock_segment = MagicMock()
        mock_segment.unit_name = "Limestone"
        mock_segment.points = [(0, 0)]
        mock_segment.attributes = {"lithology": "LST"}

        self.dialog.preview_manager.cached_data = {"geol": [mock_segment]}
        self.dialog.layer_factory.get_color_for_unit.return_value.name.return_value = (
            "#FF0000"
        )

        config = {"inherit_geology": True, "inherit_drillholes": False}

        self.manager.apply_attribute_inheritance(interp, config)

        self.assertEqual(interp.name, "Limestone")
        self.assertEqual(interp.attributes["lithology"], "LST")
        self.assertEqual(interp.color, "#FF0000")


if __name__ == "__main__":
    unittest.main()
