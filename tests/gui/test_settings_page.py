"""Tests for the SettingsPage using the noble unittest library."""

from tests.base_test import BaseTestCase
from unittest.mock import MagicMock

# Mock QGIS and PyQt before importing the page
from qgis.PyQt.QtWidgets import QApplication
from qgis.core import QgsSettings
import sys

from sec_interp.gui.ui.pages.settings_page import SettingsPage


class TestSettingsPage(BaseTestCase):
    """Tests for the SettingsPage class."""

    @classmethod
    def setUpClass(cls):
        """Initialize QApplication for the entire test class."""
        super().setUpClass()
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        super().setUp()
        # Reset settings before each test
        for key in list(QgsSettings()._shared_values.keys()):
            QgsSettings().remove(key)

    def test_initialization(self):
        """Test that the page initializes correctly without errors."""

        page = SettingsPage()

        # Verify initialization order
        self.assertIsNotNone(page.settings)

        # Verify UI setup was called (attributes exist)
        self.assertTrue(hasattr(page, "chk_enable_3d"))
        self.assertTrue(hasattr(page, "group_box"))

    def test_load_settings(self):
        """Test that settings are loaded into the UI."""
        # Pre-populate settings
        QgsSettings().setValue("sec_interp/enable_3d", True)

        page = SettingsPage()

        # Verify checkbox was set based on settings
        # The checkbox is a Mock (because QtWidgets is mocked globally)
        # So we check if setChecked(True) was called on it.
        page.chk_enable_3d.setChecked.assert_called_with(True)

    def test_save_settings(self):
        """Test that changing settings saves to QgsSettings."""

        page = SettingsPage()

        # Simulate checkbox change
        # chk_enable_3d is a Mock. We set its state.
        page.chk_enable_3d.isChecked.return_value = True

        # Manually trigger the slot
        page._on_settings_changed()

        # Verify settings were saved to global QgsSettings
        self.assertEqual(QgsSettings().value("sec_interp/enable_3d"), True)

    def test_get_data(self):
        """Test get_data returns correct dictionary."""
        page = SettingsPage()

        # Set mock state
        page.chk_enable_3d.isChecked.return_value = True

        data = page.get_data()
        self.assertEqual(
            data,
            {
                "enable_3d": True,
                "exp_topo": True,
                "exp_geol": True,
                "exp_struct": True,
                "exp_drill": True,
                "exp_interp": True,
            },
        )
