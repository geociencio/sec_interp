"""DEM configuration page."""
from qgis.core import QgsMapLayerProxyModel, QgsUnitTypes, QgsProject, QgsCoordinateTransform
from qgis.gui import QgsMapLayerComboBox, QgsRasterBandComboBox, QgsDoubleSpinBox
from qgis.PyQt.QtWidgets import QGridLayout, QLabel, QLineEdit, QHBoxLayout, QGroupBox

from .base_page import BasePage
from ...main_dialog_config import DialogDefaults


class DemPage(BasePage):
    """Configuration page for DEM/Raster settings."""

    def __init__(self, iface=None, parent=None):
        """Initialize DEM page.
        
        Args:
            iface: QGIS interface (optional, for resolution calculation)
            parent: Parent widget
        """
        self.iface = iface
        super().__init__("Digital Elevation Model", parent)

    def _setup_ui(self):
        super()._setup_ui()
        
        self.group_layout = QGridLayout(self.group_box)
        self.group_layout.setSpacing(6)

        # Row 0: Raster Layer
        self.group_layout.addWidget(QLabel("Raster Layer *"), 0, 0)
        
        self.raster_combo = QgsMapLayerComboBox()
        
        # Use modern flags if available (QGIS 3.32+)
        try:
            from qgis.core import Qgis
            self.raster_combo.setFilters(Qgis.LayerFilters(Qgis.LayerFilter.RasterLayer))
        except (ImportError, AttributeError, TypeError):
            self.raster_combo.setFilters(QgsMapLayerProxyModel.RasterLayer)
            
        self.raster_combo.setAllowEmptyLayer(True)
        self.raster_combo.setToolTip("Select the raster DEM layer")
        self.raster_combo.setCurrentIndex(0)
        self.group_layout.addWidget(self.raster_combo, 0, 1)

        self.lbl_raster_status = QLabel()
        self.lbl_raster_status.setFixedSize(16, 16)
        self.group_layout.addWidget(self.lbl_raster_status, 0, 2)

        # Row 1: Band, Resolution
        self.group_layout.addWidget(QLabel("Band"), 1, 0)
        
        self.band_combo = QgsRasterBandComboBox()
        self.band_combo.setMinimumWidth(150)
        self.band_combo.setToolTip("Select the raster band")
        self.group_layout.addWidget(self.band_combo, 1, 1)

        self.group_layout.addWidget(QLabel("Resolution"), 1, 2)
        
        res_layout = QHBoxLayout()
        self.res_edit = QLineEdit()
        self.res_edit.setReadOnly(True)
        self.res_edit.setToolTip("Raster resolution (auto-calculated)")
        
        self.units_edit = QLineEdit()
        self.units_edit.setReadOnly(True)
        self.units_edit.setMaximumWidth(50)
        
        res_layout.addWidget(self.res_edit)
        res_layout.addWidget(self.units_edit)
        self.group_layout.addLayout(res_layout, 1, 3)

        # -- Profile Settings Group --
        # We add this directly to the main layout, outside the DEM group box
        # but logically it belongs to the DEM/Raster configuration
        
        # NOTE: In old UI it was a separate group box. Let's keep it clean
        # and add it below the DEM group box.
        
        # However, BasePage structure puts a stretch at the end.
        # We can add another GroupBox to self.main_layout before the stretch.
        
        self.settings_group = QGroupBox("Profile Settings")
        settings_layout = QGridLayout(self.settings_group)
        
        # Scale
        settings_layout.addWidget(QLabel("Scale 1:"), 0, 0)
        self.scale_spin = QgsDoubleSpinBox()
        self.scale_spin.setRange(1, 1000000)
        self.scale_spin.setValue(float(DialogDefaults.SCALE))
        self.scale_spin.setDecimals(0)
        settings_layout.addWidget(self.scale_spin, 0, 1)

        # Vertical Exaggeration
        settings_layout.addWidget(QLabel("Vert. Exag."), 1, 0)
        self.vertexag_spin = QgsDoubleSpinBox()
        self.vertexag_spin.setRange(0.1, 100.0)
        self.vertexag_spin.setValue(float(DialogDefaults.VERTICAL_EXAGGERATION))
        self.vertexag_spin.setSingleStep(0.5)
        self.vertexag_spin.setDecimals(1)
        settings_layout.addWidget(self.vertexag_spin, 1, 1)
        
        # Insert before the stretch (which is the last item)
        count = self.main_layout.count()
        self.main_layout.insertWidget(count - 1, self.settings_group)

        # Connections
        self.raster_combo.layerChanged.connect(self.band_combo.setLayer)
        self.raster_combo.layerChanged.connect(self._update_resolution)

    def _update_resolution(self):
        """Calculate and update resolution and suggested scale."""
        layer = self.raster_combo.currentLayer()
        if not layer:
            self.res_edit.clear()
            self.units_edit.clear()
            return

        # Simplified resolution logic ported from old dialog
        # For now, we use simple native resolution logic
        res = layer.rasterUnitsPerPixelX()
        units = layer.crs().mapUnits()
        
        self.res_edit.setText(f"{res:.2f}")
        self.units_edit.setText(QgsUnitTypes.toString(units))
        
        # Auto-calculate scale estimate (simplified)
        if units == QgsUnitTypes.DistanceUnit.Meters:
            scale = round((res * 2000) / 1000) * 1000
            if scale > 0:
                self.scale_spin.setValue(scale)

    def get_data(self) -> dict:
        """Get DEM configuration."""
        return {
            "raster_layer": self.raster_combo.currentLayer(),
            "selected_band": self.band_combo.currentBand(),
            "scale": self.scale_spin.value(),
            "vertexag": self.vertexag_spin.value(),
        }

    def validate(self) -> tuple[bool, str]:
        if not self.raster_combo.currentLayer():
            return False, "Raster layer is required"
        return True, ""

    def is_complete(self) -> bool:
        """Check if required fields are filled."""
        return bool(self.raster_combo.currentLayer())
