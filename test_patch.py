import sys
from pathlib import Path

sys.path.insert(0, "/home/jmbernales/qgispluginsdev/qgis-plugin-manager/src")

from qgis_manager.discovery import get_plugin_metadata, find_project_root

project_root = Path("/home/jmbernales/qgispluginsdev/sec_interp")
metadata = get_plugin_metadata(project_root)
print("Metadatos leidos:")
for k in metadata.keys():
    print(f"  '{k}'")
print(f"qgisMinimumVersion en metadata: {'qgisMinimumVersion' in metadata}")
