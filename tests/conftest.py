"""
Pytest configuration for SecInterp plugin.
"""

import os
import sys
import pytest
from qgis.core import QgsApplication

# Add the plugin directory to sys.path so we can import the plugin modules
PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PLUGIN_DIR)


@pytest.fixture(scope="session", autouse=True)
def qgis_app():
    """
    Fixture to initialize QGIS application for testing.
    """
    # Initialize QGIS Application
    qgs = QgsApplication([], False)
    qgs.initQgis()

    yield qgs

    # Exit QGIS Application
    qgs.exitQgis()
