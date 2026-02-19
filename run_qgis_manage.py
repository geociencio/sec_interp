"""Script to run qgis-manage CLI locally."""

import sys

sys.path.insert(0, "/home/jmbernales/qgispluginsdev/qgis-plugin-manager/src")

from qgis_manager.cli.app import CLIApp

if __name__ == "__main__":
    app = CLIApp()
    sys.exit(app.run())
