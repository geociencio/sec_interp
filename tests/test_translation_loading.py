import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# BaseTestCase setup proxies
from tests.base_test import BaseTestCase
from qgis.core import QgsSettings
from qgis.PyQt.QtCore import QCoreApplication, QTranslator

from sec_interp_plugin import SecInterp


class TestTranslationLoading(BaseTestCase):

    def setUp(self):
        self.iface = MagicMock()

    @patch("sec_interp.gui.main_dialog.SecInterpDialog")
    @patch("sec_interp.gui.preview_renderer.PreviewRenderer")
    @patch("sec_interp.core.controller.ProfileController")
    @patch("sec_interp.core.services.export_service.ExportService")
    @patch("sec_interp_plugin.QCoreApplication.installTranslator")
    @patch("sec_interp_plugin.QTranslator")
    @patch("sec_interp_plugin.QSettings")
    def test_translation_loads_es(
        self,
        MockSettings,
        MockTranslatorClass,
        MockInstall,
        MockExport,
        MockController,
        MockRenderer,
        MockDialog,
    ):
        """Test that spanish translation loads correctly."""
        # Setup mock settings to return Spanish
        MockSettings.return_value.value.return_value = "es"

        # Mock file existence
        with patch("sec_interp_plugin.Path.exists") as MockExists:
            MockExists.return_value = True

            plugin = SecInterp(self.iface)

            # Check if load was called with correct path pattern
            self.assertTrue(hasattr(plugin, "translator"))
            MockTranslatorClass.return_value.load.assert_called_once()
            args, _ = MockTranslatorClass.return_value.load.call_args
            self.assertTrue(args[0].endswith("i18n/SecInterp_es.qm"))

            # Check if installed
            MockInstall.assert_called_once()

    @patch("sec_interp.gui.main_dialog.SecInterpDialog")
    @patch("sec_interp.gui.preview_renderer.PreviewRenderer")
    @patch("sec_interp.core.controller.ProfileController")
    @patch("sec_interp.core.services.export_service.ExportService")
    @patch("sec_interp_plugin.QCoreApplication.installTranslator")
    @patch("sec_interp_plugin.QTranslator")
    @patch("sec_interp_plugin.QSettings")
    def test_translation_loads_fr(
        self,
        MockSettings,
        MockTranslatorClass,
        MockInstall,
        MockExport,
        MockController,
        MockRenderer,
        MockDialog,
    ):
        """Test that french translation loads correctly."""
        # Setup mock settings to return French
        MockSettings.return_value.value.return_value = "fr"

        # Mock file existence
        with patch("sec_interp_plugin.Path.exists") as MockExists:
            MockExists.return_value = True

            plugin = SecInterp(self.iface)

            # Check if load was called with correct path pattern
            self.assertTrue(hasattr(plugin, "translator"))
            MockTranslatorClass.return_value.load.assert_called_once()
            args, _ = MockTranslatorClass.return_value.load.call_args
            self.assertTrue(args[0].endswith("i18n/SecInterp_fr.qm"))

            # Check if installed
            MockInstall.assert_called_once()

    @patch("sec_interp.gui.main_dialog.SecInterpDialog")
    @patch("sec_interp.gui.preview_renderer.PreviewRenderer")
    @patch("sec_interp.core.controller.ProfileController")
    @patch("sec_interp.core.services.export_service.ExportService")
    @patch("sec_interp_plugin.QCoreApplication.installTranslator")
    @patch("sec_interp_plugin.QTranslator")
    @patch("sec_interp_plugin.QSettings")
    def test_translation_loads_pt_br(
        self,
        MockSettings,
        MockTranslatorClass,
        MockInstall,
        MockExport,
        MockController,
        MockRenderer,
        MockDialog,
    ):
        """Test that pt_BR translation loads correctly."""
        # Setup mock settings to return pt_BR
        MockSettings.return_value.value.return_value = "pt_BR"

        # Mock file existence
        with patch("sec_interp_plugin.Path.exists") as MockExists:
            MockExists.return_value = True

            plugin = SecInterp(self.iface)

            # Check if load was called with correct path pattern
            self.assertTrue(hasattr(plugin, "translator"))
            MockTranslatorClass.return_value.load.assert_called_once()
            args, _ = MockTranslatorClass.return_value.load.call_args
            self.assertTrue(args[0].endswith("i18n/SecInterp_pt_BR.qm"))

            # Check if installed
            MockInstall.assert_called_once()

    @patch("sec_interp.gui.main_dialog.SecInterpDialog")
    @patch("sec_interp.gui.preview_renderer.PreviewRenderer")
    @patch("sec_interp.core.controller.ProfileController")
    @patch("sec_interp.core.services.export_service.ExportService")
    @patch("sec_interp_plugin.QCoreApplication.installTranslator")
    @patch("sec_interp_plugin.QTranslator")
    @patch("sec_interp_plugin.QSettings")
    def test_translation_loads_de(
        self,
        MockSettings,
        MockTranslatorClass,
        MockInstall,
        MockExport,
        MockController,
        MockRenderer,
        MockDialog,
    ):
        """Test that German translation loads correctly."""
        # Setup mock settings to return de
        MockSettings.return_value.value.return_value = "de"

        # Mock file existence
        with patch("sec_interp_plugin.Path.exists") as MockExists:
            MockExists.return_value = True

            plugin = SecInterp(self.iface)

            # Check if load was called with correct path pattern
            self.assertTrue(hasattr(plugin, "translator"))
            MockTranslatorClass.return_value.load.assert_called_once()
            args, _ = MockTranslatorClass.return_value.load.call_args
            self.assertTrue(args[0].endswith("i18n/SecInterp_de.qm"))

            # Check if installed
            MockInstall.assert_called_once()

    @patch("sec_interp.gui.main_dialog.SecInterpDialog")
    @patch("sec_interp.gui.preview_renderer.PreviewRenderer")
    @patch("sec_interp.core.controller.ProfileController")
    @patch("sec_interp.core.services.export_service.ExportService")
    @patch("sec_interp_plugin.QCoreApplication.installTranslator")
    @patch("sec_interp_plugin.QSettings")
    def test_translation_loads_default_on_fail(
        self,
        MockSettings,
        MockInstall,
        MockExport,
        MockController,
        MockRenderer,
        MockDialog,
    ):
        """Test that translation doesn't install if file missing."""
        MockSettings.return_value.value.return_value = "fr"

        # Mock file existence to False
        with patch("sec_interp_plugin.Path.exists") as MockExists:
            MockExists.return_value = False

            plugin = SecInterp(self.iface)

            MockInstall.assert_not_called()

    @patch("sec_interp.gui.main_dialog.SecInterpDialog")
    @patch("sec_interp.gui.preview_renderer.PreviewRenderer")
    @patch("sec_interp.core.controller.ProfileController")
    @patch("sec_interp.core.services.export_service.ExportService")
    @patch("sec_interp_plugin.QCoreApplication.installTranslator")
    @patch("sec_interp_plugin.QTranslator")
    @patch("sec_interp_plugin.QSettings")
    def test_translation_loads_hi(
        self,
        MockSettings,
        MockTranslatorClass,
        MockInstall,
        MockExport,
        MockController,
        MockRenderer,
        MockDialog,
    ):
        """Test that Hindi translation loads correctly."""
        # Setup mock settings to return hi
        MockSettings.return_value.value.return_value = "hi"

        # Mock file existence
        with patch("sec_interp_plugin.Path.exists") as MockExists:
            MockExists.return_value = True

            plugin = SecInterp(self.iface)

            # Check if load was called with correct path pattern
            self.assertTrue(hasattr(plugin, "translator"))
            MockTranslatorClass.return_value.load.assert_called_once()
            args, _ = MockTranslatorClass.return_value.load.call_args
            self.assertTrue(args[0].endswith("i18n/SecInterp_hi.qm"))

            # Check if installed
            MockInstall.assert_called_once()

            # Check if installed
            MockInstall.assert_called_once()

    @patch("sec_interp.gui.main_dialog.SecInterpDialog")
    @patch("sec_interp.gui.preview_renderer.PreviewRenderer")
    @patch("sec_interp.core.controller.ProfileController")
    @patch("sec_interp.core.services.export_service.ExportService")
    @patch("sec_interp_plugin.QCoreApplication.installTranslator")
    @patch("sec_interp_plugin.QTranslator")
    @patch("sec_interp_plugin.QSettings")
    def test_translation_loads_id(
        self,
        MockSettings,
        MockTranslatorClass,
        MockInstall,
        MockExport,
        MockController,
        MockRenderer,
        MockDialog,
    ):
        """Test that Indonesian translation loads correctly."""
        # Setup mock settings to return id
        MockSettings.return_value.value.return_value = "id"

        # Mock file existence
        with patch("sec_interp_plugin.Path.exists") as MockExists:
            MockExists.return_value = True

            plugin = SecInterp(self.iface)

            # Check if load was called with correct path pattern
            self.assertTrue(hasattr(plugin, "translator"))
            MockTranslatorClass.return_value.load.assert_called_once()
            args, _ = MockTranslatorClass.return_value.load.call_args
            self.assertTrue(args[0].endswith("i18n/SecInterp_id.qm"))

            # Check if installed
            MockInstall.assert_called_once()

    @patch("sec_interp.gui.main_dialog.SecInterpDialog")
    @patch("sec_interp.gui.preview_renderer.PreviewRenderer")
    @patch("sec_interp.core.controller.ProfileController")
    @patch("sec_interp.core.services.export_service.ExportService")
    @patch("sec_interp_plugin.QCoreApplication.installTranslator")
    @patch("sec_interp_plugin.QTranslator")
    @patch("sec_interp_plugin.QSettings")
    def test_translation_loads_ru(
        self,
        MockSettings,
        MockTranslatorClass,
        MockInstall,
        MockExport,
        MockController,
        MockRenderer,
        MockDialog,
    ):
        """Test that Russian translation loads correctly."""
        # Setup mock settings to return ru
        MockSettings.return_value.value.return_value = "ru"

        # Mock file existence
        with patch("sec_interp_plugin.Path.exists") as MockExists:
            MockExists.return_value = True

            plugin = SecInterp(self.iface)

            # Check if load was called with correct path pattern
            self.assertTrue(hasattr(plugin, "translator"))
            MockTranslatorClass.return_value.load.assert_called_once()
            args, _ = MockTranslatorClass.return_value.load.call_args
            self.assertTrue(args[0].endswith("i18n/SecInterp_ru.qm"))

            # Check if installed
            MockInstall.assert_called_once()


if __name__ == "__main__":
    unittest.main()
