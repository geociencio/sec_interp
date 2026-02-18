"""Reproduction test for export functionality."""

import unittest
from unittest.mock import MagicMock, patch

from qgis.core import QgsApplication, QgsSettings
from sec_interp.gui.ui.pages.settings_page import SettingsPage


class TestSettingsReproduction(unittest.TestCase):
    """Test case to reproduce settings retrieval issues."""

    @classmethod
    def setUpClass(cls):
        """Initialize QGIS application."""
        cls.qgs = QgsApplication([], False)
        cls.qgs.initQgis()

    @classmethod
    def tearDownClass(cls):
        """Clean up QGIS application."""
        cls.qgs.exitQgis()

    def setUp(self):
        """Set up test fixtures."""
        self.settings = QgsSettings()
        # Clear settings to ensure clean state
        if hasattr(self.settings, "_shared_values"):
            self.settings._shared_values.clear()

        # Create page
        self.page = SettingsPage()

    def test_default_values(self):
        """Test default values are True."""
        data = self.page.get_data()
        print(f"\nDefault Data: {data}")

        self.assertTrue(data["exp_topo"], "exp_topo must be True by default")
        self.assertTrue(data["exp_geol"], "exp_geol must be True by default")
        self.assertTrue(data["exp_struct"], "exp_struct must be True by default")
        self.assertTrue(data["exp_drill"], "exp_drill must be True by default")
        self.assertTrue(data["exp_interp"], "exp_interp must be True by default")

    def test_settings_persistence(self):
        """Test persistence of changed values."""
        # Simulate user unchecking topo export
        self.page.chk_exp_topo.setChecked(False)
        self.page._on_settings_changed()

        # Verify get_data reflects change
        data = self.page.get_data()
        self.assertFalse(data["exp_topo"], "exp_topo must conform to checkbox state")

        # Verify persistence in QgsSettings
        val = self.settings.value("sec_interp/exp_topo", True, type=bool)
        self.assertFalse(val, "QgsSettings must reflect unchecked state")

    def test_reload_settings(self):
        """Test loading from settings."""
        # Set settings manually
        self.settings.setValue("sec_interp/exp_geol", False)

        # Create new page instance (simulating reopen)
        new_page = SettingsPage()

        data = new_page.get_data()
        self.assertFalse(data["exp_geol"], "exp_geol must load False from settings")
        self.assertTrue(data["exp_topo"], "exp_topo must stay True default")


if __name__ == "__main__":
    unittest.main()
