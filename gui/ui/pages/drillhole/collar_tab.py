"""Collar configuration tab for the drillhole page."""

from __future__ import annotations

import contextlib
from typing import Any

from qgis.core import Qgis
from qgis.gui import QgsFieldComboBox, QgsMapLayerComboBox
from qgis.PyQt.QtCore import QCoreApplication, pyqtSignal
from qgis.PyQt.QtWidgets import QCheckBox, QGridLayout, QLabel, QWidget

from sec_interp.gui.ui.pages.base_page import set_combo_layer
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class CollarTab(QWidget):
    """Collar layer, identifier, coordinates and depth configuration."""

    dataChanged = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the collar tab."""
        super().__init__(parent)
        self._setup_ui()

    def tr(self, message: str) -> str:
        """Translate a message for this tab."""
        return QCoreApplication.translate("CollarTab", message)  # type: ignore[no-any-return]

    def _setup_ui(self) -> None:
        """Build the collar grid layout."""
        layout = QGridLayout(self)
        layout.setSpacing(6)

        layout.addWidget(QLabel(self.tr("Collar Layer:")), 0, 0)
        self.c_layer = QgsMapLayerComboBox()
        self.c_layer.setFilters(Qgis.LayerFilter.PointLayer)
        self.c_layer.setAllowEmptyLayer(True)
        self.c_layer.setCurrentIndex(0)
        layout.addWidget(self.c_layer, 0, 1)

        self.chk_use_geom = QCheckBox(self.tr("Use Layer Geometry for Coordinates"))
        self.chk_use_geom.setChecked(True)
        layout.addWidget(self.chk_use_geom, 1, 0, 1, 2)

        layout.addWidget(QLabel(self.tr("Hole ID:")), 2, 0)
        self.c_id = QgsFieldComboBox()
        layout.addWidget(self.c_id, 2, 1)

        self.lbl_x = QLabel(self.tr("East (X):"))
        layout.addWidget(self.lbl_x, 3, 0)
        self.c_x = QgsFieldComboBox()
        self.c_x.setAllowEmptyFieldName(True)
        layout.addWidget(self.c_x, 3, 1)

        self.lbl_y = QLabel(self.tr("North (Y):"))
        layout.addWidget(self.lbl_y, 4, 0)
        self.c_y = QgsFieldComboBox()
        self.c_y.setAllowEmptyFieldName(True)
        layout.addWidget(self.c_y, 4, 1)

        layout.addWidget(QLabel(self.tr("Elevation (Z):")), 5, 0)
        self.c_z = QgsFieldComboBox()
        self.c_z.setAllowEmptyFieldName(True)
        self.c_z.setToolTip(self.tr("Leave empty to use DEM elevation"))
        layout.addWidget(self.c_z, 5, 1)

        layout.addWidget(QLabel(self.tr("Total Depth:")), 6, 0)
        self.c_depth = QgsFieldComboBox()
        self.c_depth.setAllowEmptyFieldName(True)
        layout.addWidget(self.c_depth, 6, 1)

        layout.setRowStretch(7, 1)

    def _toggle_xy_fields(self, checked: bool) -> None:
        """Enable/disable Easting/Northing fields based on geometry checkbox."""
        enabled = not checked
        self.lbl_x.setEnabled(enabled)
        self.c_x.setEnabled(enabled)
        self.lbl_y.setEnabled(enabled)
        self.c_y.setEnabled(enabled)

    def get_data(self) -> dict[str, Any]:
        """Return collar configuration values."""
        return {
            "collar_layer": self.c_layer.currentLayer(),
            "use_geometry": self.chk_use_geom.isChecked(),
            "collar_id": self.c_id.currentField(),
            "collar_x": self.c_x.currentField(),
            "collar_y": self.c_y.currentField(),
            "collar_z": self.c_z.currentField(),
            "collar_depth": self.c_depth.currentField(),
        }

    def dump(self) -> dict[str, Any]:
        """Return persistable collar state."""
        return {
            "dh_collar_layer": self.c_layer.currentLayer(),
            "dh_collar_id": self.c_id.currentField(),
            "dh_use_geom": self.chk_use_geom.isChecked(),
            "dh_collar_x": self.c_x.currentField(),
            "dh_collar_y": self.c_y.currentField(),
            "dh_collar_z": self.c_z.currentField(),
            "dh_collar_depth": self.c_depth.currentField(),
        }

    def load(self, data: dict[str, Any]) -> None:
        """Apply persisted collar state."""
        c_layer = data.get("dh_collar_layer")
        if c_layer is not None:
            set_combo_layer(self.c_layer, c_layer)
            for w in (self.c_id, self.c_x, self.c_y, self.c_z, self.c_depth):
                w.setLayer(c_layer)

        for key, combo in [
            ("dh_collar_id", self.c_id),
            ("dh_collar_x", self.c_x),
            ("dh_collar_y", self.c_y),
            ("dh_collar_z", self.c_z),
            ("dh_collar_depth", self.c_depth),
        ]:
            field = data.get(key)
            if field:
                combo.setField(field)

        use_geom = data.get("dh_use_geom")
        if use_geom is not None:
            self.chk_use_geom.setChecked(bool(use_geom))

    def reset(self) -> None:
        """Reset collar inputs to defaults."""
        self.c_layer.setLayer(None)
        self.chk_use_geom.setChecked(True)

    def connect_signals(self) -> None:
        """Connect collar tab signals."""
        self.c_layer.layerChanged.connect(self.c_id.setLayer)
        self.c_layer.layerChanged.connect(self.c_x.setLayer)
        self.c_layer.layerChanged.connect(self.c_y.setLayer)
        self.c_layer.layerChanged.connect(self.c_z.setLayer)
        self.c_layer.layerChanged.connect(self.c_depth.setLayer)
        self.c_layer.layerChanged.connect(self.dataChanged.emit)

        self.chk_use_geom.toggled.connect(self._toggle_xy_fields)
        self._toggle_xy_fields(True)

        self.c_id.fieldChanged.connect(self.dataChanged.emit)
        self.c_x.fieldChanged.connect(self.dataChanged.emit)
        self.c_y.fieldChanged.connect(self.dataChanged.emit)
        self.c_z.fieldChanged.connect(self.dataChanged.emit)
        self.c_depth.fieldChanged.connect(self.dataChanged.emit)
        self.chk_use_geom.toggled.connect(self.dataChanged.emit)

    def disconnect_signals(self) -> None:
        """Disconnect all collar signals to prevent memory leaks."""
        with contextlib.suppress(TypeError, RuntimeError):
            self.c_layer.layerChanged.disconnect(self.c_id.setLayer)
            self.c_layer.layerChanged.disconnect(self.c_x.setLayer)
            self.c_layer.layerChanged.disconnect(self.c_y.setLayer)
            self.c_layer.layerChanged.disconnect(self.c_z.setLayer)
            self.c_layer.layerChanged.disconnect(self.c_depth.setLayer)
            self.c_layer.layerChanged.disconnect(self.dataChanged.emit)

        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_use_geom.toggled.disconnect(self._toggle_xy_fields)
            self.chk_use_geom.toggled.disconnect(self.dataChanged.emit)

        with contextlib.suppress(TypeError, RuntimeError):
            self.c_id.fieldChanged.disconnect(self.dataChanged.emit)
        with contextlib.suppress(TypeError, RuntimeError):
            self.c_x.fieldChanged.disconnect(self.dataChanged.emit)
        with contextlib.suppress(TypeError, RuntimeError):
            self.c_y.fieldChanged.disconnect(self.dataChanged.emit)
        with contextlib.suppress(TypeError, RuntimeError):
            self.c_z.fieldChanged.disconnect(self.dataChanged.emit)
        with contextlib.suppress(TypeError, RuntimeError):
            self.c_depth.fieldChanged.disconnect(self.dataChanged.emit)
