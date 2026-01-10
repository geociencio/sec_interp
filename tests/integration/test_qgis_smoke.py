"""Smoke test to verify QGIS integration infrastructure."""

from qgis.core import QgsVectorLayer, QgsProject
from tests.integration.base_integration import BaseIntegrationTest


class TestQGisSmoke(BaseIntegrationTest):
    """Verifies that the integration test base correctly initializes QGIS."""

    def test_qgis_layer_instantiation(self):
        """Verify that real QGS objects can be created."""
        layer = QgsVectorLayer(
            "Point?crs=EPSG:4326&field=id:integer", "test_layer", "memory"
        )
        self.assertTrue(layer.isValid())
        self.assertEqual(layer.name(), "test_layer")
        self.assertEqual(layer.fields().count(), 1)

    def test_qgis_project(self):
        """Verify project instance accessibility."""
        project = QgsProject.instance()
        self.assertIsNotNone(project)
        # Default project might not have a CRS set until a layer is added
        # or it might have a default from QGIS settings
        print(f"DEBUG: Project CRS: {project.crs().authid()}")
        # Just check it's accessible, exact value depend on env
        self.assertTrue(hasattr(project, "crs"))

    def test_dialog_instantiation(self):
        """Verify that the main dialog can be instantiated in headless mode."""
        from sec_interp.gui.main_dialog import SecInterpDialog
        from sec_interp.core.controller import ProfileController

        class DummyPlugin:
            def __init__(self):
                self.controller = ProfileController()

        dialog = SecInterpDialog(iface=None, plugin_instance=DummyPlugin())
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.windowTitle(), "Sec Interp")
        # Check some children were created
        self.assertIsNotNone(dialog.sidebar)
        self.assertIsNotNone(dialog.preview_widget)
