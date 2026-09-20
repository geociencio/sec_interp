"""Interval configuration tab for the drillhole page."""

from __future__ import annotations

import contextlib
from typing import Any

from qgis.core import Qgis, QgsMapLayerProxyModel
from qgis.gui import QgsFieldComboBox, QgsMapLayerComboBox
from qgis.PyQt.QtCore import QCoreApplication, pyqtSignal
from qgis.PyQt.QtWidgets import QGridLayout, QLabel, QWidget

from sec_interp.gui.ui.pages.base_page import set_combo_layer
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class IntervalTab(QWidget):
    """Interval layer and depth/lithology field configuration."""

    dataChanged = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the interval tab."""
        super().__init__(parent)
        self._setup_ui()

    def tr(self, message: str) -> str:
        """Translate a message for this tab."""
        return QCoreApplication.translate("IntervalTab", message)  # type: ignore[no-any-return]

    def _setup_ui(self) -> None:
        """Build the interval grid layout."""
        layout = QGridLayout(self)
        row = 0

        layout.addWidget(QLabel(self.tr("Interval Layer:")), row, 0)
        self.i_layer = QgsMapLayerComboBox()
        try:
            self.i_layer.setFilters(
                Qgis.LayerFilters(Qgis.LayerFilter.PointLayer | Qgis.LayerFilter.NoGeometry)
            )
        except (AttributeError, TypeError):
            self.i_layer.setFilters(
                QgsMapLayerProxyModel.Filter.PointLayer | QgsMapLayerProxyModel.Filter.NoGeometry
            )
        self.i_layer.setAllowEmptyLayer(True)
        self.i_layer.setCurrentIndex(0)
        layout.addWidget(self.i_layer, row, 1)
        row += 1

        layout.addWidget(QLabel(self.tr("Hole ID:")), row, 0)
        self.i_id = QgsFieldComboBox()
        layout.addWidget(self.i_id, row, 1)
        row += 1

        layout.addWidget(QLabel(self.tr("From Depth:")), row, 0)
        self.i_from = QgsFieldComboBox()
        layout.addWidget(self.i_from, row, 1)
        row += 1

        layout.addWidget(QLabel(self.tr("To Depth:")), row, 0)
        self.i_to = QgsFieldComboBox()
        layout.addWidget(self.i_to, row, 1)
        row += 1

        layout.addWidget(QLabel(self.tr("Lithology/Attribute:")), row, 0)
        self.i_lith = QgsFieldComboBox()
        layout.addWidget(self.i_lith, row, 1)
        layout.setRowStretch(row, 1)

    def get_data(self) -> dict[str, Any]:
        """Return interval configuration values."""
        return {
            "interval_layer": self.i_layer.currentLayer(),
            "interval_id": self.i_id.currentField(),
            "interval_from": self.i_from.currentField(),
            "interval_to": self.i_to.currentField(),
            "interval_lith": self.i_lith.currentField(),
        }

    def dump(self) -> dict[str, Any]:
        """Return persistable interval state."""
        return {
            "dh_interval_layer": self.i_layer.currentLayer(),
            "dh_interval_id": self.i_id.currentField(),
            "dh_interval_from": self.i_from.currentField(),
            "dh_interval_to": self.i_to.currentField(),
            "dh_interval_lith": self.i_lith.currentField(),
        }

    def load(self, data: dict[str, Any]) -> None:
        """Apply persisted interval state."""
        i_layer = data.get("dh_interval_layer")
        if i_layer is not None:
            set_combo_layer(self.i_layer, i_layer)
            for w in (self.i_id, self.i_from, self.i_to, self.i_lith):
                w.setLayer(i_layer)

        for key, combo in [
            ("dh_interval_id", self.i_id),
            ("dh_interval_from", self.i_from),
            ("dh_interval_to", self.i_to),
            ("dh_interval_lith", self.i_lith),
        ]:
            field = data.get(key)
            if field:
                combo.setField(field)

    def reset(self) -> None:
        """Reset interval inputs to defaults."""
        self.i_layer.setLayer(None)

    def connect_signals(self) -> None:
        """Connect interval tab signals."""
        self.i_layer.layerChanged.connect(self.i_id.setLayer)
        self.i_layer.layerChanged.connect(self.i_from.setLayer)
        self.i_layer.layerChanged.connect(self.i_to.setLayer)
        self.i_layer.layerChanged.connect(self.i_lith.setLayer)
        self.i_layer.layerChanged.connect(self.dataChanged.emit)

        self.i_id.fieldChanged.connect(self.dataChanged.emit)
        self.i_from.fieldChanged.connect(self.dataChanged.emit)
        self.i_to.fieldChanged.connect(self.dataChanged.emit)
        self.i_lith.fieldChanged.connect(self.dataChanged.emit)

    def disconnect_signals(self) -> None:
        """Disconnect all interval signals to prevent memory leaks."""
        with contextlib.suppress(TypeError, RuntimeError):
            self.i_layer.layerChanged.disconnect(self.i_id.setLayer)
            self.i_layer.layerChanged.disconnect(self.i_from.setLayer)
            self.i_layer.layerChanged.disconnect(self.i_to.setLayer)
            self.i_layer.layerChanged.disconnect(self.i_lith.setLayer)
            self.i_layer.layerChanged.disconnect(self.dataChanged.emit)

        with contextlib.suppress(TypeError, RuntimeError):
            self.i_id.fieldChanged.disconnect(self.dataChanged.emit)
        with contextlib.suppress(TypeError, RuntimeError):
            self.i_from.fieldChanged.disconnect(self.dataChanged.emit)
        with contextlib.suppress(TypeError, RuntimeError):
            self.i_to.fieldChanged.disconnect(self.dataChanged.emit)
        with contextlib.suppress(TypeError, RuntimeError):
            self.i_lith.fieldChanged.disconnect(self.dataChanged.emit)
