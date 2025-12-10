"""Geology configuration page."""
from qgis.core import QgsMapLayerProxyModel
from qgis.gui import QgsMapLayerComboBox, QgsFieldComboBox
from qgis.PyQt.QtWidgets import QGridLayout, QLabel

from .base_page import BasePage


from qgis.PyQt.QtCore import pyqtSignal

class GeologyPage(BasePage):
    """Configuration page for Geology/Outcrop settings."""

    dataChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("Geological Outcrops", parent)

    def _setup_ui(self):
        super()._setup_ui()
        
        self.group_layout = QGridLayout(self.group_box)
        self.group_layout.setSpacing(6)

        # Row 0: Outcrop Layer
        self.group_layout.addWidget(QLabel("Outcrops Layer"), 0, 0)
        
        self.layer_combo = QgsMapLayerComboBox()
        self.layer_combo.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.layer_combo.setAllowEmptyLayer(True)
        self.layer_combo.setToolTip("Select the polygon layer with geological outcrops")
        self.layer_combo.setCurrentIndex(0)
        self.group_layout.addWidget(self.layer_combo, 0, 1)

        # Row 1: Name Field
        self.group_layout.addWidget(QLabel("Name Field"), 1, 0)
        
        self.field_combo = QgsFieldComboBox()
        self.field_combo.setToolTip("Select the field containing unit names")
        self.group_layout.addWidget(self.field_combo, 1, 1)

        # Connection: update fields when layer changes
        self.layer_combo.layerChanged.connect(self.field_combo.setLayer)

        # Emit dataChanged when selections change
        self.layer_combo.layerChanged.connect(self.dataChanged.emit)
        self.field_combo.fieldChanged.connect(self.dataChanged.emit)

    def get_data(self) -> dict:
        """Get geology configuration."""
        return {
            "outcrop_layer": self.layer_combo.currentLayer(),
            "outcrop_name_field": self.field_combo.currentField(),
        }

    def is_complete(self) -> bool:
        """Check if required fields are filled."""
        return bool(self.layer_combo.currentLayer() and self.field_combo.currentField())
