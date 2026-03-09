"""Tests for InterpretationManager."""

import unittest
import json
from unittest.mock import MagicMock, patch
from tests.base_test import BaseTestCase
from qgis.core import QgsGeometry, QgsPointXY
from sec_interp.gui.dialog_interpretation_manager import InterpretationManager
from sec_interp.core.domain import InterpretationPolygon


class TestDialogInterpretationManager(BaseTestCase):
    """Tests for the InterpretationManager class."""

    def setUp(self):
        super().setUp()
        self.dialog = MagicMock()
        self.manager = InterpretationManager(self.dialog)

    def test_load_interpretations_success(self):
        """Test loading interpretations from QGIS project."""
        data = [
            {
                "id": "1",
                "name": "Unit A",
                "type": "lithology",
                "vertices_2d": [[0, 0], [1, 1]],
                "color": "#FF0000",
            }
        ]
        self.dialog.project.readEntry.return_value = (json.dumps(data), True)

        self.manager.load_interpretations()

        self.assertEqual(len(self.manager.interpretations), 1)
        self.assertEqual(self.manager.interpretations[0].name, "Unit A")

    def test_load_interpretations_fail(self):
        """Test loading interpretations when project returns error."""
        self.dialog.project.readEntry.return_value = ("", False)
        self.manager.load_interpretations()
        self.assertEqual(len(self.manager.interpretations), 0)

    def test_save_interpretations(self):
        """Test saving interpretations to QGIS project."""
        interp = InterpretationPolygon(
            id="1",
            name="Unit A",
            type="lithology",
            vertices_2d=[(0, 0), (1, 1)],
            color="#FF0000",
        )
        self.manager.interpretations = [interp]

        self.manager.save_interpretations()

        self.dialog.project.writeEntry.assert_called_once()
        args = self.dialog.project.writeEntry.call_args[0]
        self.assertEqual(args[1], "interpretations")
        saved_data = json.loads(args[2])
        self.assertEqual(len(saved_data), 1)
        self.assertEqual(saved_data[0]["name"], "Unit A")

    def test_handle_interpretation_finished_accepted(self):
        """Test processing a finished interpretation flow (Accepted)."""
        interp = InterpretationPolygon(
            id="1", name="New", type="lithology", vertices_2d=[(0, 0), (1, 0), (1, 1)]
        )
        self.dialog.page_interpretation.get_data.return_value = {
            "inherit_geology": False
        }

        target = "sec_interp.gui.dialogs.interpretation_properties_dialog.InterpretationPropertiesDialog"
        with patch(target, create=True) as mock_dlg_class:
            mock_dlg = mock_dlg_class.return_value
            from qgis.PyQt.QtWidgets import QDialog

            mock_dlg.exec_.return_value = QDialog.Accepted

            self.manager.handle_interpretation_finished(interp)

            self.assertIn(interp, self.manager.interpretations)
            self.dialog.update_preview_from_checkboxes.assert_called_once()

    def test_handle_interpretation_finished_rejected(self):
        """Test processing a finished interpretation flow (Rejected/Canceled)."""
        interp = InterpretationPolygon(
            id="1", name="New", type="lithology", vertices_2d=[(0, 0), (1, 0), (1, 1)]
        )
        self.dialog.page_interpretation.get_data.return_value = {}

        target = "sec_interp.gui.dialogs.interpretation_properties_dialog.InterpretationPropertiesDialog"
        with patch(target, create=True) as mock_dlg_class:
            mock_dlg = mock_dlg_class.return_value
            from qgis.PyQt.QtWidgets import QDialog

            mock_dlg.exec_.return_value = QDialog.Rejected

            self.manager.handle_interpretation_finished(interp)

            self.assertNotIn(interp, self.manager.interpretations)

    def test_apply_attribute_inheritance_geology(self):
        """Test attribute inheritance from geology."""
        interp = InterpretationPolygon(
            id="1", name="Temp", type="lithology", vertices_2d=[(0, 0), (1, 0), (1, 1)]
        )
        config = {"inherit_geology": True, "inherit_drillholes": False}

        # Mock cached geology data
        mock_segment = MagicMock()
        mock_segment.unit_name = "Inherited Unit"
        mock_segment.points = [(0, 0)]  # Centroid is near 0,0
        mock_segment.attributes = {"key": "val"}
        self.dialog.preview_manager.cached_data = {"geol": [mock_segment]}
        self.dialog.layer_factory.get_color_for_unit.return_value.name.return_value = (
            "#0000FF"
        )

        self.manager.apply_attribute_inheritance(interp, config)

        self.assertEqual(interp.name, "Inherited Unit")
        self.assertEqual(interp.attributes["key"], "val")
        self.assertEqual(interp.color, "#0000FF")

    def test_apply_attribute_inheritance_drillholes(self):
        """Test attribute inheritance from drillholes."""
        interp = InterpretationPolygon(
            id="1", name="Temp", type="lithology", vertices_2d=[(0, 0), (1, 0), (1, 1)]
        )
        config = {"inherit_geology": False, "inherit_drillholes": True}

        # Mock cached drillhole data (legacy tuple format)
        mock_interval = MagicMock()
        mock_interval.rock_unit = "DH Unit"
        mock_interval.points = [(0.1, 0.1)]
        mock_interval.attributes = {"dh": "val"}

        # dh = (id, collar, survey, intervals_legacy, intervals) or something like that
        # _extract_intervals_from_dh_data returns dh[4] for legacy or dh[2] or dh.intervals
        dh_data = (None, None, [mock_interval])  # dh[2] flow
        self.dialog.preview_manager.cached_data = {"drillhole": [dh_data]}
        self.dialog.layer_factory.get_color_for_unit.return_value.name.return_value = (
            "#00FF00"
        )

        self.manager.apply_attribute_inheritance(interp, config)

        self.assertEqual(interp.name, "DH Unit")
        self.assertEqual(interp.attributes["dh"], "val")

    def test_json_serial_special(self):
        """Test the custom JSON serializer for QVariant-like objects."""
        interp = InterpretationPolygon(
            id="1",
            name="Unit A",
            type="lithology",
            vertices_2d=[(0, 0)],
            color="#FF0000",
        )

        # Mock an object with isNull (like QVariant)
        mock_qv = MagicMock()
        mock_qv.isNull.return_value = False
        mock_qv.value.return_value = "Val"

        interp.attributes = {"qv": mock_qv, "null_qv": MagicMock(isNull=lambda: True)}
        self.manager.interpretations = [interp]

        self.manager.save_interpretations()
        args = self.dialog.project.writeEntry.call_args[0]
        saved_data = json.loads(args[2])
        self.assertEqual(saved_data[0]["attributes"]["qv"], "Val")
        self.assertIsNone(saved_data[0]["attributes"]["null_qv"])

    def test_no_project_guards(self):
        """Test guards when dialog has no project."""
        self.dialog.project = None
        # Should return early and not raise
        self.manager.load_interpretations()
        self.manager.save_interpretations()

    def test_inheritance_no_cached_data(self):
        """Test inheritance when no cached data is available."""
        interp = InterpretationPolygon(id="1", name="T", type="L", vertices_2d=[(0, 0)])
        config = {"inherit_geology": True, "inherit_drillholes": True}
        self.dialog.preview_manager.cached_data = {}

        self.manager.apply_attribute_inheritance(interp, config)
        self.assertEqual(interp.name, "T")  # Unchanged


if __name__ == "__main__":
    unittest.main()
