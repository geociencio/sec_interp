"""Geology configuration page."""

from __future__ import annotations

from qgis.core import QgsMapLayerProxyModel
from qgis.gui import QgsFieldComboBox, QgsMapLayerComboBox
from qgis.PyQt.QtCore import QCoreApplication, pyqtSignal
from qgis.PyQt.QtWidgets import QGridLayout, QLabel

from sec_interp.core.validation.project_validator import (
    ProjectValidator,
    ValidationParams,
)

from .base_page import BasePage


class GeologyPage(BasePage):
    """Configuration page for Geology/Outcrop settings."""

    dataChanged = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the geology page.

        Args:
            parent: Optional parent widget.

        """
        super().__init__(
            QCoreApplication.translate("GeologyPage", "Geological Outcrops"), parent
        )

    def _setup_ui(self) -> None:
        super()._setup_ui()

        self.group_layout = QGridLayout(self.group_box)
        self.group_layout.setSpacing(6)

        # Row 0: Outcrop Layer
        self.group_layout.addWidget(QLabel(self.tr("Outcrops Layer")), 0, 0)

        self.layer_combo = QgsMapLayerComboBox()

        # Use modern flags if available (QGIS 3.32+)
        try:
            from qgis.core import Qgis  # noqa: PLC0415

            self.layer_combo.setFilters(
                Qgis.LayerFilters(Qgis.LayerFilter.PolygonLayer)
            )
        except (ImportError, AttributeError, TypeError):
            self.layer_combo.setFilters(QgsMapLayerProxyModel.PolygonLayer)

        self.layer_combo.setAllowEmptyLayer(True)
        self.layer_combo.setToolTip(
            self.tr("Select the polygon layer with geological outcrops")
        )
        self.layer_combo.setCurrentIndex(0)
        self.group_layout.addWidget(self.layer_combo, 0, 1)

        # Row 1: Name Field
        self.group_layout.addWidget(QLabel(self.tr("Name Field")), 1, 0)

        self.field_combo = QgsFieldComboBox()
        self.field_combo.setToolTip(self.tr("Select the field containing unit names"))
        self.group_layout.addWidget(self.field_combo, 1, 1)

        # Fields combo and other UI setup complete

    def get_data(self) -> dict[str, Any]:
        """Get geology configuration."""
        return {
            "outcrop_layer": self.layer_combo.currentLayer(),
            "outcrop_name_field": self.field_combo.currentField(),
        }

    def is_complete(self) -> bool:
        """Check if required fields are filled if a layer is selected."""
        data = self.get_data()
        params = ValidationParams(
            outcrop_layer=data["outcrop_layer"],
            outcrop_field=data["outcrop_name_field"],
        )
        return ProjectValidator.is_geology_complete(params)

    def connect_signals(self) -> None:
        """Connect internal signals for the geology page."""
        self.layer_combo.layerChanged.connect(self.field_combo.setLayer)
        self.layer_combo.layerChanged.connect(self.dataChanged.emit)
        self.field_combo.fieldChanged.connect(self.dataChanged.emit)

    def disconnect_signals(self) -> None:
        """Disconnect all signals to prevent memory leaks."""
        with contextlib.suppress(TypeError, RuntimeError):
            self.layer_combo.layerChanged.disconnect(self.field_combo.setLayer)
            self.layer_combo.layerChanged.disconnect(self.dataChanged.emit)
            self.field_combo.fieldChanged.disconnect(self.dataChanged.emit)
            self.dataChanged.disconnect()
