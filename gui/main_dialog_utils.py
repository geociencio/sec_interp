"""UI utility module for SecInterp main dialog.

This module provides helper methods for layer filtering and field population.
"""

from typing import List, Optional
from qgis.core import QgsMapLayer, QgsWkbTypes, QgsProject, QgsApplication
from qgis.PyQt.QtGui import QIcon

class DialogEntityManager:
    """Provides utility methods for interacting with QGIS entities."""

    @staticmethod
    def populate_field_combobox(source_combobox, target_combobox) -> None:
        """Populate a combobox with field names from a selected vector layer."""
        layer = source_combobox.currentLayer()
        target_combobox.clear()
        if layer:
            fields = [field.name() for field in layer.fields()]
            target_combobox.addItems(fields)

    @staticmethod
    def get_layer_names_by_type(layer_type: QgsMapLayer.LayerType) -> List[str]:
        """Get a list of layer names filtered by the specified layer type."""
        return [
            layer.name()
            for layer in QgsProject.instance().mapLayers().values()
            if layer.type() == layer_type
        ]

    @staticmethod
    def get_layer_names_by_geometry(geometry_type: QgsWkbTypes.GeometryType) -> List[str]:
        """Get a list of layer names filtered by the specified geometry type."""
        return [
            layer.name()
            for layer in QgsProject.instance().mapLayers().values()
            if (
                layer.type() == QgsMapLayer.VectorLayer
                and layer.geometryType() == geometry_type
            )
        ]

    @staticmethod
    def get_theme_icon(name: str) -> QIcon:
        """Get a theme icon from QGIS."""
        return QgsApplication.getThemeIcon(name)
