"""Structural configuration page."""
from qgis.core import QgsMapLayerProxyModel
from qgis.gui import QgsMapLayerComboBox, QgsFieldComboBox, QgsDoubleSpinBox
from qgis.PyQt.QtWidgets import QGridLayout, QLabel

from .base_page import BasePage
from ...main_dialog_config import DialogDefaults



from qgis.PyQt.QtCore import pyqtSignal

class StructurePage(BasePage):
    """Configuration page for Structural Measurements."""

    dataChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("Structural Measurements", parent)

    def _setup_ui(self):
        super()._setup_ui()
        
        self.group_layout = QGridLayout(self.group_box)
        self.group_layout.setSpacing(6)

        # Row 0: Structural Layer
        self.group_layout.addWidget(QLabel("Structural Layer"), 0, 0)
        
        self.layer_combo = QgsMapLayerComboBox()
        self.layer_combo.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.layer_combo.setAllowEmptyLayer(True)
        self.layer_combo.setToolTip("Select the point layer with structural measurements")
        self.layer_combo.setCurrentIndex(0)
        self.group_layout.addWidget(self.layer_combo, 0, 1)

        # Row 1: Dip Field
        self.group_layout.addWidget(QLabel("Dip Field"), 1, 0)
        
        self.dip_combo = QgsFieldComboBox()
        self.dip_combo.setToolTip("Select field with dip values (0-90)")
        self.group_layout.addWidget(self.dip_combo, 1, 1)

        # Row 2: Strike Field
        self.group_layout.addWidget(QLabel("Strike Field"), 2, 0)
        
        self.strike_combo = QgsFieldComboBox()
        self.strike_combo.setToolTip("Select field with strike values (0-360)")
        self.group_layout.addWidget(self.strike_combo, 2, 1)
        
        # Row 3: Dip Line Scale
        self.group_layout.addWidget(QLabel("Dip Line Scale"), 3, 0)
        
        self.scale_spin = QgsDoubleSpinBox()
        self.scale_spin.setRange(0.1, 100.0)
        self.scale_spin.setValue(float(DialogDefaults.DIP_SCALE_FACTOR))
        self.scale_spin.setSingleStep(0.5)
        self.scale_spin.setToolTip("Length factor for drawing dip lines")
        self.group_layout.addWidget(self.scale_spin, 3, 1)

        # Connections: update fields when layer changes
        self.layer_combo.layerChanged.connect(self._on_layer_changed)

        # Emit dataChanged when selections change
        self.layer_combo.layerChanged.connect(self.dataChanged.emit)
        self.dip_combo.fieldChanged.connect(self.dataChanged.emit)
        self.strike_combo.fieldChanged.connect(self.dataChanged.emit)

    def _on_layer_changed(self, layer):
        """Update both field combos when layer changes."""
        self.dip_combo.setLayer(layer)
        self.strike_combo.setLayer(layer)

    def get_data(self) -> dict:
        """Get structural configuration."""
        return {
            "structural_layer": self.layer_combo.currentLayer(),
            "dip_field": self.dip_combo.currentField(),
            "strike_field": self.strike_combo.currentField(),
            "dip_scale_factor": self.scale_spin.value(),
        }

    def is_complete(self) -> bool:
        """Check if required fields are filled."""
        return bool(
            self.layer_combo.currentLayer()
            and self.dip_combo.currentField()
            and self.strike_combo.currentField()
        )
