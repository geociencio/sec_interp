"""Survey configuration tab for the drillhole page."""

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


class SurveyTab(QWidget):
    """Survey layer and downhole measurement field configuration."""

    dataChanged = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the survey tab."""
        super().__init__(parent)
        self._setup_ui()

    def tr(self, message: str) -> str:
        """Translate a message for this tab."""
        return QCoreApplication.translate("SurveyTab", message)  # type: ignore[no-any-return]

    def _setup_ui(self) -> None:
        """Build the survey grid layout."""
        layout = QGridLayout(self)
        row = 0

        layout.addWidget(QLabel(self.tr("Survey Layer:")), row, 0)
        self.s_layer = QgsMapLayerComboBox()
        try:
            self.s_layer.setFilters(
                Qgis.LayerFilters(Qgis.LayerFilter.PointLayer | Qgis.LayerFilter.NoGeometry)
            )
        except (AttributeError, TypeError):
            self.s_layer.setFilters(
                QgsMapLayerProxyModel.Filter.PointLayer | QgsMapLayerProxyModel.Filter.NoGeometry
            )
        self.s_layer.setAllowEmptyLayer(True)
        self.s_layer.setCurrentIndex(0)
        layout.addWidget(self.s_layer, row, 1)
        row += 1

        layout.addWidget(QLabel(self.tr("Hole ID:")), row, 0)
        self.s_id = QgsFieldComboBox()
        layout.addWidget(self.s_id, row, 1)
        row += 1

        layout.addWidget(QLabel(self.tr("Depth:")), row, 0)
        self.s_depth = QgsFieldComboBox()
        layout.addWidget(self.s_depth, row, 1)
        row += 1

        layout.addWidget(QLabel(self.tr("Azimuth:")), row, 0)
        self.s_azim = QgsFieldComboBox()
        layout.addWidget(self.s_azim, row, 1)
        row += 1

        layout.addWidget(QLabel(self.tr("Inclination:")), row, 0)
        self.s_incl = QgsFieldComboBox()
        layout.addWidget(self.s_incl, row, 1)
        layout.setRowStretch(row, 1)

    def get_data(self) -> dict[str, Any]:
        """Return survey configuration values."""
        return {
            "survey_layer": self.s_layer.currentLayer(),
            "survey_id": self.s_id.currentField(),
            "survey_depth": self.s_depth.currentField(),
            "survey_azim": self.s_azim.currentField(),
            "survey_incl": self.s_incl.currentField(),
        }

    def dump(self) -> dict[str, Any]:
        """Return persistable survey state."""
        return {
            "dh_survey_layer": self.s_layer.currentLayer(),
            "dh_survey_id": self.s_id.currentField(),
            "dh_survey_depth": self.s_depth.currentField(),
            "dh_survey_azim": self.s_azim.currentField(),
            "dh_survey_incl": self.s_incl.currentField(),
        }

    def load(self, data: dict[str, Any]) -> None:
        """Apply persisted survey state."""
        s_layer = data.get("dh_survey_layer")
        if s_layer is not None:
            set_combo_layer(self.s_layer, s_layer)
            for w in (self.s_id, self.s_depth, self.s_azim, self.s_incl):
                w.setLayer(s_layer)

        for key, combo in [
            ("dh_survey_id", self.s_id),
            ("dh_survey_depth", self.s_depth),
            ("dh_survey_azim", self.s_azim),
            ("dh_survey_incl", self.s_incl),
        ]:
            field = data.get(key)
            if field:
                combo.setField(field)

    def reset(self) -> None:
        """Reset survey inputs to defaults."""
        self.s_layer.setLayer(None)

    def connect_signals(self) -> None:
        """Connect survey tab signals."""
        self.s_layer.layerChanged.connect(self.s_id.setLayer)
        self.s_layer.layerChanged.connect(self.s_depth.setLayer)
        self.s_layer.layerChanged.connect(self.s_azim.setLayer)
        self.s_layer.layerChanged.connect(self.s_incl.setLayer)
        self.s_layer.layerChanged.connect(self.dataChanged.emit)

        self.s_id.fieldChanged.connect(self.dataChanged.emit)
        self.s_depth.fieldChanged.connect(self.dataChanged.emit)
        self.s_azim.fieldChanged.connect(self.dataChanged.emit)
        self.s_incl.fieldChanged.connect(self.dataChanged.emit)

    def disconnect_signals(self) -> None:
        """Disconnect all survey signals to prevent memory leaks."""
        with contextlib.suppress(TypeError, RuntimeError):
            self.s_layer.layerChanged.disconnect(self.s_id.setLayer)
            self.s_layer.layerChanged.disconnect(self.s_depth.setLayer)
            self.s_layer.layerChanged.disconnect(self.s_azim.setLayer)
            self.s_layer.layerChanged.disconnect(self.s_incl.setLayer)
            self.s_layer.layerChanged.disconnect(self.dataChanged.emit)

        with contextlib.suppress(TypeError, RuntimeError):
            self.s_id.fieldChanged.disconnect(self.dataChanged.emit)
        with contextlib.suppress(TypeError, RuntimeError):
            self.s_depth.fieldChanged.disconnect(self.dataChanged.emit)
        with contextlib.suppress(TypeError, RuntimeError):
            self.s_azim.fieldChanged.disconnect(self.dataChanged.emit)
        with contextlib.suppress(TypeError, RuntimeError):
            self.s_incl.fieldChanged.disconnect(self.dataChanged.emit)
