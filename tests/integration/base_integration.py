import os
import unittest

# Disable mocks for integration tests
os.environ["FORCE_MOCKS"] = "0"

# Note: FORCE_MOCKS=0 is checked in base_test.py to skip mock setup
# No need to manually remove patches

from qgis.core import QgsApplication


class BaseIntegrationTest(unittest.TestCase):
    """Base class for integration tests needing a real QgsApplication.

    This class ensures that QgsApplication is initialized once for the test class,
    allowing access to real QGIS API components.
    """

    @classmethod
    def setUpClass(cls):
        """Initialize QgsApplication in headless mode (Singleton)."""
        from qgis.core import QgsApplication

        cls.qgs = QgsApplication.instance()
        if cls.qgs is None:
            cls.qgs = QgsApplication([], False)
            cls.qgs.initQgis()

    def setUp(self):
        """Setup for each test."""
        # With FORCE_MOCKS=0, mocks are not applied, so no need to restore
        pass

    @classmethod
    def tearDownClass(cls):
        """Do not exit QGIS here to allow reuse by other test classes.
        QGIS will clean up on process exit.
        """
        pass


class DummyPlugin:
    """Mock plugin instance for testing dialogs."""

    def __init__(self):
        from sec_interp.core.controller import ProfileController

        self.controller = ProfileController()
