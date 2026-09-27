"""DEM configuration page."""

from __future__ import annotations

import contextlib
import math
from typing import Any

from qgis.core import (
    Qgis,
    QgsRasterBandStats,
    QgsRectangle,
    QgsUnitTypes,
)
from qgis.gui import QgsDoubleSpinBox, QgsMapLayerComboBox, QgsRasterBandComboBox
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
)

from sec_interp.core.validation.project_validator import (
    ProjectValidator,
    ValidationParams,
)
from sec_interp.gui.adapters.validation_extractor import resolve_layer_metadata
from sec_interp.gui.main_dialog_config import DialogDefaults
from sec_interp.logger_config import get_logger

from .base_page import BasePage, set_combo_layer

logger = get_logger(__name__)

STATS_SAMPLE_SIZE = 250_000
"""Bounded sample size for band statistics (avoids blocking on huge/remote DEMs)."""


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
        title = QCoreApplication.translate("DemPage", "Digital Elevation Model")
        mandatory = QCoreApplication.translate("DemPage", "Mandatory")
        super().__init__(f"{title} — {mandatory}", parent)
        self.iface = iface

    def _setup_ui(self) -> None:
        super()._setup_ui()

        self.group_layout = QGridLayout(self.group_box)
        self.group_layout.setSpacing(6)

        self._setup_raster_selection()
        self._setup_band_and_resolution()
        self._setup_raster_stats()
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
        self.raster_combo.setMinimumWidth(220)
        # Span the value columns so layer names are readable.
        self.group_layout.addWidget(self.raster_combo, 0, 1, 1, 3)

        self.lbl_raster_status = QLabel()
        self.lbl_raster_status.setFixedSize(16, 16)
        self.group_layout.addWidget(self.lbl_raster_status, 0, 4)

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

    def _setup_raster_stats(self) -> None:
        """Set up read-only band statistics rows (min/max/mean/nodata)."""
        self.min_edit = self._stats_edit("Minimum elevation of the selected band")
        self.max_edit = self._stats_edit("Maximum elevation of the selected band")
        self.mean_edit = self._stats_edit("Mean elevation of the selected band")
        self.nodata_edit = self._stats_edit("NoData value of the selected band")

        self.group_layout.addWidget(QLabel(self.tr("Min")), 2, 0)
        self.group_layout.addWidget(self.min_edit, 2, 1)
        self.group_layout.addWidget(QLabel(self.tr("Max")), 2, 2)
        self.group_layout.addWidget(self.max_edit, 2, 3)

        self.group_layout.addWidget(QLabel(self.tr("Mean")), 3, 0)
        self.group_layout.addWidget(self.mean_edit, 3, 1)
        self.group_layout.addWidget(QLabel(self.tr("No data")), 3, 2)
        self.group_layout.addWidget(self.nodata_edit, 3, 3)

    def _stats_edit(self, tooltip: str) -> QLineEdit:
        """Create a read-only line edit for a statistic value."""
        edit = QLineEdit()
        edit.setReadOnly(True)
        edit.setToolTip(self.tr(tooltip))
        return edit

    def _update_raster_stats(self) -> None:
        """Refresh the read-only band statistics for the current DEM and band.

        ``bandStatistics`` is synchronous; a bounded ``sampleSize`` keeps it
        cheap and the call is defensive (remote/odd providers may fail).
        """
        layer = self.raster_combo.currentLayer()
        if not layer or not layer.isValid():
            self._clear_raster_stats()
            return

        band = self.band_combo.currentBand()
        if not isinstance(band, int) or band < 1:
            band = 1

        provider = layer.dataProvider()
        try:
            stats = provider.bandStatistics(
                band, QgsRasterBandStats.Stats.All, QgsRectangle(), STATS_SAMPLE_SIZE
            )
        except (AttributeError, TypeError, ValueError, RuntimeError):
            logger.warning("Could not compute DEM band statistics (band %s)", band, exc_info=True)
            self._clear_raster_stats()
            return

        self.min_edit.setText(self._format_stat(stats.minimumValue))
        self.max_edit.setText(self._format_stat(stats.maximumValue))
        self.mean_edit.setText(self._format_stat(stats.mean))
        self.nodata_edit.setText(self._format_nodata(provider, band))

    @staticmethod
    def _format_stat(value: Any) -> str:
        """Format a statistic, rendering non-finite values as an em dash."""
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return "—"
        if not math.isfinite(numeric):
            return "—"
        return f"{numeric:.2f}"

    @staticmethod
    def _format_nodata(provider: Any, band: int) -> str:
        """Return a display string for the band's NoData value."""
        try:
            value = provider.sourceNoDataValue(band)
        except (AttributeError, TypeError, ValueError, RuntimeError):
            return "—"
        if value is None:
            return "—"
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return "—"
        if math.isnan(numeric):
            return "—"
        return f"{numeric:g}"

    def _clear_raster_stats(self) -> None:
        """Blank the statistics fields (no raster or unavailable stats)."""
        for edit in (self.min_edit, self.max_edit, self.mean_edit, self.nodata_edit):
            edit.setText("")

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

        self.auto_ve_check = QCheckBox(self.tr("Auto"))
        self.auto_ve_check.setToolTip(self.tr("Calculated automatically"))
        self.auto_ve_check.setChecked(bool(DialogDefaults.AUTO_VERTICAL_EXAGGERATION))
        settings_layout.addWidget(self.auto_ve_check, 1, 2)

        self.auto_ve_value = QLabel("—")
        self.auto_ve_value.setToolTip(
            self.tr("Adaptive vertical exaggeration (updated on preview)")
        )
        settings_layout.addWidget(self.auto_ve_value, 1, 3)

        self._on_auto_ve_toggled(self.auto_ve_check.isChecked())

        # Insert before the stretch (which is the last item)
        count = self.main_layout.count()
        self.main_layout.insertWidget(count - 1, self.settings_group)

    def _on_auto_ve_toggled(self, checked: bool) -> None:
        """Enable/disable the manual spinbox based on the Auto toggle.

        Args:
            checked: True if Auto mode is selected (manual spin disabled).

        """
        self.vertexag_spin.setEnabled(not checked)
        self.auto_ve_value.setVisible(checked)

    def set_auto_ve(self, value: float | None) -> None:
        """Display the adaptive VE value next to the Auto toggle.

        Args:
            value: The computed VE factor, or None when not yet available.

        """
        self.auto_ve_value.setText("—" if value is None else f"{value:.1f}×")

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
        self.units_edit.setText(QgsUnitTypes.toAbbreviatedString(units))

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
            "auto_vert_exag": self.auto_ve_check.isChecked(),
        }

    def dump(self) -> dict[str, Any]:
        """Return the persistable DEM state."""
        return {
            "dem_layer": self.raster_combo.currentLayer(),
            "dem_band": self.band_combo.currentBand(),
            "scale": self.scale_spin.value(),
            "vert_exag": self.vertexag_spin.value(),
            "auto_vert_exag": self.auto_ve_check.isChecked(),
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
        auto_vert_exag = data.get("auto_vert_exag")
        if auto_vert_exag is not None:
            self.auto_ve_check.setChecked(bool(auto_vert_exag))
        self._on_auto_ve_toggled(self.auto_ve_check.isChecked())

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
        self.auto_ve_check.setChecked(bool(DialogDefaults.AUTO_VERTICAL_EXAGGERATION))
        self._on_auto_ve_toggled(self.auto_ve_check.isChecked())
        self._clear_raster_stats()

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
        self.raster_combo.layerChanged.connect(self._update_raster_stats)
        self.band_combo.bandChanged.connect(self._update_raster_stats)
        self.auto_ve_check.toggled.connect(self._on_auto_ve_toggled)

    def disconnect_signals(self) -> None:
        """Disconnect all signals to prevent memory leaks."""
        for signal, slot in (
            (self.raster_combo.layerChanged, self.band_combo.setLayer),
            (self.raster_combo.layerChanged, self._update_resolution),
            (self.raster_combo.layerChanged, self._update_raster_stats),
            (self.band_combo.bandChanged, self._update_raster_stats),
            (self.auto_ve_check.toggled, self._on_auto_ve_toggled),
        ):
            with contextlib.suppress(TypeError, RuntimeError):
                signal.disconnect(slot)
