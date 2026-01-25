import os

# Force real QGIS for integration tests
os.environ["FORCE_MOCKS"] = "0"

"""Integration tests for interpretation management workflow."""

import json
from qgis.core import QgsProject
from tests.integration.base_integration import BaseIntegrationTest, DummyPlugin
from sec_interp.core.types import InterpretationPolygon
from sec_interp.gui.main_dialog import SecInterpDialog


class TestInterpretationWorkflow(BaseIntegrationTest):
    """Integration test for interpretation management workflow."""

    def setUp(self):
        super().setUp()
        # Ensure project is clean
        self.project = QgsProject.instance()
        self.project.clear()

        # Instantiate dialog
        self.dialog = SecInterpDialog(iface=None, plugin_instance=DummyPlugin())

    def test_add_and_save_interpretation(self):
        """Test adding an interpretation and saving it to the project."""
        interp = InterpretationPolygon(
            id="test-id-1",
            name="Test Unit",
            type="Lithology",
            vertices_2d=[(0, 0), (100, 0), (100, 50), (0, 50)],
        )

        # Manually add to dialog
        self.dialog.interpretations.append(interp)

        # Trigger save
        self.dialog.interpretation_manager.save_interpretations()

        # Verify in project
        json_data, ok = self.project.readEntry("SecInterp", "interpretations")
        self.assertTrue(ok)
        data = json.loads(json_data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Test Unit")
        self.assertEqual(data[0]["vertices_2d"], [[0, 0], [100, 0], [100, 50], [0, 50]])

    def test_load_interpretation_from_project(self):
        """Test loading interpretations from project entries."""
        # Pre-populate project
        data = [
            {
                "id": "load-id",
                "name": "Stored Unit",
                "type": "Fault",
                "vertices_2d": [[10.0, 10.0], [20.0, 20.0]],
                "attributes": {"source": "manual"},
                "color": "#00FF00",
                "created_at": "2026-01-01",
            }
        ]
        self.project.writeEntry("SecInterp", "interpretations", json.dumps(data))

        # Trigger load
        self.dialog.interpretation_manager.load_interpretations()

        self.assertEqual(len(self.dialog.interpretations), 1)
        loaded = self.dialog.interpretations[0]
        self.assertEqual(loaded.name, "Stored Unit")
        self.assertEqual(loaded.type, "Fault")
        self.assertEqual(loaded.attributes["source"], "manual")
        # Check vertices (converted from lists to tuples)
        self.assertEqual(loaded.vertices_2d, [(10.0, 10.0), (20.0, 20.0)])

    def test_clear_all_interpretations(self):
        """Test clearing all interpretations from project."""
        # Add one
        self.dialog.interpretations.append(InterpretationPolygon("id1", "n1", "t1", []))
        self.dialog.interpretation_manager.save_interpretations()

        # Clear dialog list and save
        # Using proxy property interpretations to clear the list in the manager
        self.dialog.interpretations = []
        self.dialog.interpretation_manager.save_interpretations()

        # Verify empty in project
        json_data, ok = self.project.readEntry("SecInterp", "interpretations")
        self.assertTrue(ok)
        self.assertEqual(json_data, "[]")
