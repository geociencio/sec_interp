"""DEM configuration page."""

from __future__ import annotations

from typing import Any

from qgis.core import (
    Qgis,
    QgsUnitTypes,
)
from qgis.gui import QgsDoubleSpinBox, QgsMapLayerComboBox, QgsRasterBandComboBox
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit

from sec_interp.core.validation.project_validator import (
    ProjectValidator,
    ValidationParams,
)
from sec_interp.gui.adapters.validation_extractor import resolve_layer_metadata
from sec_interp.gui.main_dialog_config import DialogDefaults

from .base_page import BasePage, set_combo_layer


class DemPage(BasePage):
    """Configuration page for DEM/Raster settings."""

    layer_keys = frozenset({"dem_layer"})

    def __init__(self, iface: Any = None, parent: Any = None) -> None:
        """Initialize DEM page.

        Args:
            iface: QGIS interface (optional, for resolution calculation).
            parent: Parent widget.

        """
        self.iface = iface
        super().__init__(QCoreApplication.translate("DemPage", "Digital Elevation Model"), parent)
        self.iface = iface

    def _setup_ui(self) -> None:
        super()._setup_ui()

        self.group_layout = QGridLayout(self.group_box)
        self.group_layout.setSpacing(6)

        self._setup_raster_selection()
        self._setup_band_and_resolution()
        self._setup_profile_settings()

    def _setup_raster_selection(self) -> None:
        """Set up raster layer selection widgets."""
        # Row 0: Raster Layer
        self.group_layout.addWidget(QLabel(self.tr("Raster Layer *")), 0, 0)

        self.raster_combo = QgsMapLayerComboBox()
        self.raster_combo.setFilters(Qgis.LayerFilters(Qgis.LayerFilter.RasterLayer))
        self.raster_combo.setAllowEmptyLayer(True)
        self.raster_combo.setToolTip(self.tr("Select the raster DEM layer"))
        self.raster_combo.setCurrentIndex(0)
        self.group_layout.addWidget(self.raster_combo, 0, 1)

        self.lbl_raster_status = QLabel()
        self.lbl_raster_status.setFixedSize(16, 16)
        self.group_layout.addWidget(self.lbl_raster_status, 0, 2)

    def _setup_band_and_resolution(self) -> None:
        """Set up band and resolution display widgets."""
        # Row 1: Band, Resolution
        self.group_layout.addWidget(QLabel(self.tr("Band")), 1, 0)

        self.band_combo = QgsRasterBandComboBox()
        self.band_combo.setMinimumWidth(150)
        self.band_combo.setToolTip(self.tr("Select the raster band"))
        self.group_layout.addWidget(self.band_combo, 1, 1)

        self.group_layout.addWidget(QLabel(self.tr("Resolution")), 1, 2)

        res_layout = QHBoxLayout()
        self.res_edit = QLineEdit()
        self.res_edit.setReadOnly(True)
        self.res_edit.setToolTip(self.tr("Raster resolution (auto-calculated)"))

        self.units_edit = QLineEdit()
        self.units_edit.setReadOnly(True)
        self.units_edit.setMaximumWidth(50)

        res_layout.addWidget(self.res_edit)
        res_layout.addWidget(self.units_edit)
        self.group_layout.addLayout(res_layout, 1, 3)

    def _setup_profile_settings(self) -> None:
        """Set up scale and exaggeration settings."""
        self.settings_group = QGroupBox(self.tr("Profile Settings"))
        settings_layout = QGridLayout(self.settings_group)

        # Scale
        settings_layout.addWidget(QLabel(self.tr("Scale 1:")), 0, 0)
        self.scale_spin = QgsDoubleSpinBox()
        self.scale_spin.setRange(1, 1000000)
        self.scale_spin.setValue(float(DialogDefaults.SCALE))
        self.scale_spin.setDecimals(0)
        settings_layout.addWidget(self.scale_spin, 0, 1)

        # Vertical Exaggeration
        settings_layout.addWidget(QLabel(self.tr("Vert. Exag.")), 1, 0)
        self.vertexag_spin = QgsDoubleSpinBox()
        self.vertexag_spin.setRange(0.1, 100.0)
        self.vertexag_spin.setValue(float(DialogDefaults.VERTICAL_EXAGGERATION))
        self.vertexag_spin.setSingleStep(0.5)
        self.vertexag_spin.setDecimals(1)
        settings_layout.addWidget(self.vertexag_spin, 1, 1)

        # Insert before the stretch (which is the last item)
        count = self.main_layout.count()
        self.main_layout.insertWidget(count - 1, self.settings_group)

    def _update_resolution(self) -> None:
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

        try:
            res_val = float(res)
            self.res_edit.setText(f"{res_val:.2f}")
        except (ValueError, TypeError):
            self.res_edit.setText(str(res))
        self.units_edit.setText(QgsUnitTypes.toString(units))

        # Auto-calculate scale estimate (simplified)
        if units == QgsUnitTypes.DistanceUnit.Meters:
            scale = round((res * 2000) / 1000) * 1000
            if scale > 0:
                self.scale_spin.setValue(scale)

    def get_data(self) -> dict[str, Any]:
        """Get DEM configuration."""
        return {
            "raster_layer": self.raster_combo.currentLayer(),
            "selected_band": self.band_combo.currentBand(),
            "scale": self.scale_spin.value(),
            "vertexag": self.vertexag_spin.value(),
        }

    def dump(self) -> dict[str, Any]:
        """Return the persistable DEM state."""
        return {
            "dem_layer": self.raster_combo.currentLayer(),
            "dem_band": self.band_combo.currentBand(),
            "scale": self.scale_spin.value(),
            "vert_exag": self.vertexag_spin.value(),
        }

    def load(self, data: dict[str, Any]) -> None:
        """Apply persisted DEM state."""
        raster_layer = data.get("dem_layer")
        if raster_layer is not None:
            set_combo_layer(self.raster_combo, raster_layer)
            self.band_combo.setLayer(raster_layer)

        band_idx = data.get("dem_band")
        if band_idx is not None:
            self.band_combo.setBand(int(band_idx))
        scale = data.get("scale")
        if scale is not None:
            self.scale_spin.setValue(float(scale))
        vert_exag = data.get("vert_exag")
        if vert_exag is not None:
            self.vertexag_spin.setValue(float(vert_exag))

        if raster_layer is not None:
            self.scale_spin.blockSignals(True)
            self._update_resolution()
            self.scale_spin.blockSignals(False)
            if scale is not None:
                self.scale_spin.setValue(float(scale))

    def reset(self) -> None:
        """Reset DEM inputs to defaults."""
        self.raster_combo.setLayer(None)
        self.band_combo.setBand(DialogDefaults.DEFAULT_BAND)
        self.scale_spin.setValue(float(DialogDefaults.SCALE))
        self.vertexag_spin.setValue(float(DialogDefaults.VERTICAL_EXAGGERATION))

    def validate(self) -> tuple[bool, str]:
        """Validate page settings.

        Returns:
            Tuple of (success, error message).

        """
        if not self.raster_combo.currentLayer():
            return False, self.tr("Raster layer is required")
        return True, ""

    def is_complete(self) -> bool:
        """Check if required fields are filled if a layer is selected."""
        data = self.get_data()
        params = ValidationParams(raster_layer=resolve_layer_metadata(data["raster_layer"]))
        return ProjectValidator.is_dem_complete(params)

    def connect_signals(self) -> None:
        """Connect internal signals for the DEM page."""
        self.raster_combo.layerChanged.connect(self.band_combo.setLayer)
        self.raster_combo.layerChanged.connect(self._update_resolution)

    def disconnect_signals(self) -> None:
        """Disconnect all signals to prevent memory leaks."""
        try:
            self.raster_combo.layerChanged.disconnect(self.band_combo.setLayer)
            self.raster_combo.layerChanged.disconnect(self._update_resolution)
        except (TypeError, RuntimeError):
            pass
