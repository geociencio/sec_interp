"""UI page for drillhole data configuration.

This page is a thin coordinator: it owns the tab container and delegates the
collar, survey and interval forms to :mod:`gui.ui.pages.drillhole`.
"""

from __future__ import annotations

import contextlib
from typing import Any

from qgis.PyQt.QtCore import QCoreApplication, pyqtSignal
from qgis.PyQt.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from sec_interp.core.validation.project_validator import (
    ProjectValidator,
    ValidationParams,
)
from sec_interp.gui.adapters.validation_extractor import resolve_layer_metadata
from sec_interp.logger_config import get_logger

from .base_page import BasePage
from .drillhole import CollarTab, IntervalTab, SurveyTab

logger = get_logger(__name__)


class DrillholePage(BasePage):
    """Configuration page for Drillhole data (Collar, Survey, Intervals)."""

    dataChanged = pyqtSignal()
    layer_keys = frozenset({"dh_collar_layer", "dh_survey_layer", "dh_interval_layer"})

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the drillhole page.

        Args:
            parent: Optional parent widget.

        """
        super().__init__(QCoreApplication.translate("DrillholePage", "Drillhole Data"), parent)

    def _setup_ui(self) -> None:
        """Build the tabbed drillhole interface."""
        super()._setup_ui()

        layout = self.group_box.layout()
        if layout is None:
            layout = QVBoxLayout(self.group_box)
            self.group_box.setLayout(layout)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self.collar_tab = CollarTab()
        self.tab_widget.addTab(self.collar_tab, self.tr("Collars"))

        self.survey_tab = SurveyTab()
        self.tab_widget.addTab(self.survey_tab, self.tr("Survey"))

        self.interval_tab = IntervalTab()
        self.tab_widget.addTab(self.interval_tab, self.tr("Intervals"))

        layout.addStretch()

    def get_data(self) -> dict[str, Any]:
        """Get drillhole configuration from all tabs."""
        data: dict[str, Any] = {}
        data.update(self.collar_tab.get_data())
        data.update(self.survey_tab.get_data())
        data.update(self.interval_tab.get_data())
        return data

    def dump(self) -> dict[str, Any]:
        """Return the persistable drillhole state."""
        data: dict[str, Any] = {}
        data.update(self.collar_tab.dump())
        data.update(self.survey_tab.dump())
        data.update(self.interval_tab.dump())
        return data

    def load(self, data: dict[str, Any]) -> None:
        """Apply persisted drillhole state."""
        self.collar_tab.load(data)
        self.survey_tab.load(data)
        self.interval_tab.load(data)

    def reset(self) -> None:
        """Reset drillhole inputs to defaults."""
        self.collar_tab.reset()
        self.survey_tab.reset()
        self.interval_tab.reset()

    def is_complete(self) -> bool:
        """Check if required fields are filled if layers are selected."""
        data = self.get_data()
        params = ValidationParams(
            collar_layer=resolve_layer_metadata(data["collar_layer"]),
            collar_id=data["collar_id"],
            collar_use_geom=data["use_geometry"],
            collar_x=data["collar_x"],
            collar_y=data["collar_y"],
            survey_layer=resolve_layer_metadata(data["survey_layer"]),
            survey_id=data["survey_id"],
            survey_depth=data["survey_depth"],
            survey_azim=data["survey_azim"],
            survey_incl=data["survey_incl"],
            interval_layer=resolve_layer_metadata(data["interval_layer"]),
            interval_id=data["interval_id"],
            interval_from=data["interval_from"],
            interval_to=data["interval_to"],
            interval_lith=data["interval_lith"],
        )
        return ProjectValidator.is_drillhole_complete(params)

    def connect_signals(self) -> None:
        """Connect internal signals for the drillhole page."""
        for tab in (self.collar_tab, self.survey_tab, self.interval_tab):
            tab.dataChanged.connect(self.dataChanged.emit)
            tab.connect_signals()

    def disconnect_signals(self) -> None:
        """Disconnect all signals to prevent memory leaks."""
        for tab in (self.collar_tab, self.survey_tab, self.interval_tab):
            tab.disconnect_signals()
            with contextlib.suppress(TypeError, RuntimeError):
                tab.dataChanged.disconnect(self.dataChanged.emit)

        with contextlib.suppress(TypeError, RuntimeError):
            self.dataChanged.disconnect()
