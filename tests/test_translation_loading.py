
"""Test for verifying translation loading logic."""
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Initialize QGIS Application
from qgis.core import QgsApplication
qgs = QgsApplication([], False)
qgs.initQgis()

from qgis.PyQt.QtCore import QCoreApplication, QTranslator
# Import inside patches or setUp to avoid side effects if possible,
# but here we need to patch classes used by SecInterp BEFORE we instantiate it.

from sec_interp.sec_interp_plugin import SecInterp

class TestTranslationLoading(unittest.TestCase):

    def setUp(self):
        self.iface = MagicMock()

    @patch("sec_interp.sec_interp_plugin.SecInterpDialog")
    @patch("sec_interp.sec_interp_plugin.PreviewRenderer")
    @patch("sec_interp.sec_interp_plugin.ProfileController")
    @patch("sec_interp.sec_interp_plugin.ExportService")
    @patch("sec_interp.sec_interp_plugin.QCoreApplication.installTranslator")
    @patch("sec_interp.sec_interp_plugin.QTranslator")
    @patch("sec_interp.sec_interp_plugin.QSettings")
    def test_translation_loads_es(self, MockSettings, MockTranslatorClass, MockInstall,
                                 MockExport, MockController, MockRenderer, MockDialog):
        """Test that spanish translation loads correctly."""
        # Setup mock settings to return Spanish
        MockSettings.return_value.value.return_value = "es"

        # Mock file existence
        with patch("sec_interp.sec_interp_plugin.Path.exists") as MockExists:
            MockExists.return_value = True

            plugin = SecInterp(self.iface)

            # Check if load was called with correct path pattern
            self.assertTrue(hasattr(plugin, "translator"))
            MockTranslatorClass.return_value.load.assert_called_once()
            args, _ = MockTranslatorClass.return_value.load.call_args
            self.assertTrue(args[0].endswith("i18n/SecInterp_es.qm"))

            # Check if installed
            MockInstall.assert_called_once()

    @patch("sec_interp.sec_interp_plugin.SecInterpDialog")
    @patch("sec_interp.sec_interp_plugin.PreviewRenderer")
    @patch("sec_interp.sec_interp_plugin.ProfileController")
    @patch("sec_interp.sec_interp_plugin.ExportService")
    @patch("sec_interp.sec_interp_plugin.QCoreApplication.installTranslator")
    @patch("sec_interp.sec_interp_plugin.QTranslator")
    @patch("sec_interp.sec_interp_plugin.QSettings")
    def test_translation_loads_fr(self, MockSettings, MockTranslatorClass, MockInstall,
                                 MockExport, MockController, MockRenderer, MockDialog):
        """Test that french translation loads correctly."""
        # Setup mock settings to return French
        MockSettings.return_value.value.return_value = "fr"

        # Mock file existence
        with patch("sec_interp.sec_interp_plugin.Path.exists") as MockExists:
            MockExists.return_value = True

            plugin = SecInterp(self.iface)

            # Check if load was called with correct path pattern
            self.assertTrue(hasattr(plugin, "translator"))
            MockTranslatorClass.return_value.load.assert_called_once()
            args, _ = MockTranslatorClass.return_value.load.call_args
            self.assertTrue(args[0].endswith("i18n/SecInterp_fr.qm"))

            # Check if installed
            MockInstall.assert_called_once()

    @patch("sec_interp.sec_interp_plugin.SecInterpDialog")
    @patch("sec_interp.sec_interp_plugin.PreviewRenderer")
    @patch("sec_interp.sec_interp_plugin.ProfileController")
    @patch("sec_interp.sec_interp_plugin.ExportService")
    @patch("sec_interp.sec_interp_plugin.QCoreApplication.installTranslator")
    @patch("sec_interp.sec_interp_plugin.QTranslator")
    @patch("sec_interp.sec_interp_plugin.QSettings")
    def test_translation_loads_pt_br(self, MockSettings, MockTranslatorClass, MockInstall,
                                 MockExport, MockController, MockRenderer, MockDialog):
        """Test that pt_BR translation loads correctly."""
        # Setup mock settings to return pt_BR
        MockSettings.return_value.value.return_value = "pt_BR"

        # Mock file existence
        with patch("sec_interp.sec_interp_plugin.Path.exists") as MockExists:
            MockExists.return_value = True

            plugin = SecInterp(self.iface)

            # Check if load was called with correct path pattern
            self.assertTrue(hasattr(plugin, "translator"))
            MockTranslatorClass.return_value.load.assert_called_once()
            args, _ = MockTranslatorClass.return_value.load.call_args
            self.assertTrue(args[0].endswith("i18n/SecInterp_pt_BR.qm"))

            # Check if installed
            MockInstall.assert_called_once()

    @patch("sec_interp.sec_interp_plugin.SecInterpDialog")
    @patch("sec_interp.sec_interp_plugin.PreviewRenderer")
    @patch("sec_interp.sec_interp_plugin.ProfileController")
    @patch("sec_interp.sec_interp_plugin.ExportService")
    @patch("sec_interp.sec_interp_plugin.QCoreApplication.installTranslator")
    @patch("sec_interp.sec_interp_plugin.QTranslator")
    @patch("sec_interp.sec_interp_plugin.QSettings")
    def test_translation_loads_de(self, MockSettings, MockTranslatorClass, MockInstall,
                                 MockExport, MockController, MockRenderer, MockDialog):
        """Test that German translation loads correctly."""
        # Setup mock settings to return de
        MockSettings.return_value.value.return_value = "de"

        # Mock file existence
        with patch("sec_interp.sec_interp_plugin.Path.exists") as MockExists:
            MockExists.return_value = True

            plugin = SecInterp(self.iface)

            # Check if load was called with correct path pattern
            self.assertTrue(hasattr(plugin, "translator"))
            MockTranslatorClass.return_value.load.assert_called_once()
            args, _ = MockTranslatorClass.return_value.load.call_args
            self.assertTrue(args[0].endswith("i18n/SecInterp_de.qm"))

            # Check if installed
            MockInstall.assert_called_once()

    @patch("sec_interp.sec_interp_plugin.SecInterpDialog")
    @patch("sec_interp.sec_interp_plugin.PreviewRenderer")
    @patch("sec_interp.sec_interp_plugin.ProfileController")
    @patch("sec_interp.sec_interp_plugin.ExportService")
    @patch("sec_interp.sec_interp_plugin.QCoreApplication.installTranslator")
    @patch("sec_interp.sec_interp_plugin.QSettings")
    def test_translation_loads_default_on_fail(self, MockSettings, MockInstall,
                                              MockExport, MockController, MockRenderer, MockDialog):
        """Test that translation doesn't install if file missing."""
        MockSettings.return_value.value.return_value = "fr"

        # Mock file existence to False
        with patch("sec_interp.sec_interp_plugin.Path.exists") as MockExists:
            MockExists.return_value = False

            plugin = SecInterp(self.iface)

            MockInstall.assert_not_called()

    @patch("sec_interp.sec_interp_plugin.SecInterpDialog")
    @patch("sec_interp.sec_interp_plugin.PreviewRenderer")
    @patch("sec_interp.sec_interp_plugin.ProfileController")
    @patch("sec_interp.sec_interp_plugin.ExportService")
    @patch("sec_interp.sec_interp_plugin.QCoreApplication.installTranslator")
    @patch("sec_interp.sec_interp_plugin.QTranslator")
    @patch("sec_interp.sec_interp_plugin.QSettings")
    def test_translation_loads_ru(self, MockSettings, MockTranslatorClass, MockInstall,
                                 MockExport, MockController, MockRenderer, MockDialog):
        """Test that Russian translation loads correctly."""
        # Setup mock settings to return ru
        MockSettings.return_value.value.return_value = "ru"

        # Mock file existence
        with patch("sec_interp.sec_interp_plugin.Path.exists") as MockExists:
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
