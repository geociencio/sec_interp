"""Cross-section configuration page."""

from qgis.core import QgsMapLayerProxyModel
from qgis.gui import QgsDoubleSpinBox, QgsMapLayerComboBox
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QGridLayout, QLabel

from .base_page import BasePage


class SectionPage(BasePage):
    """Configuration page for Cross Section settings."""

    def __init__(self, parent=None):
        super().__init__(QCoreApplication.translate("SectionPage", "Cross Section Line"), parent)

    def _setup_ui(self):
        super()._setup_ui()

        self.group_layout = QGridLayout(self.group_box)
        self.group_layout.setSpacing(6)

        # Row 0: Section Line Layer
        self.group_layout.addWidget(QLabel(self.tr("Section Line *")), 0, 0)

        self.line_combo = QgsMapLayerComboBox()

        # Use modern flags if available (QGIS 3.32+)
        try:
            from qgis.core import Qgis  # noqa: PLC0415

            self.line_combo.setFilters(Qgis.LayerFilters(Qgis.LayerFilter.LineLayer))
        except (ImportError, AttributeError, TypeError):
            self.line_combo.setFilters(QgsMapLayerProxyModel.LineLayer)

        self.line_combo.setAllowEmptyLayer(True)
        self.line_combo.setToolTip(self.tr("Select the line layer defining the cross-section"))
        self.line_combo.setCurrentIndex(0)
        self.group_layout.addWidget(self.line_combo, 0, 1)

        self.lbl_section_status = QLabel()
        self.lbl_section_status.setFixedSize(16, 16)
        self.group_layout.addWidget(self.lbl_section_status, 0, 2)

        # Row 1: Buffer Distance
        self.group_layout.addWidget(QLabel(self.tr("Buffer Dist. (m)")), 1, 0)

        self.buffer_spin = QgsDoubleSpinBox()
        self.buffer_spin.setRange(0.0, 10000.0)
        self.buffer_spin.setValue(100.0)  # Default
        self.buffer_spin.setSuffix(self.tr(" m"))
        self.buffer_spin.setToolTip(
            self.tr("Distance to include structures around the section line")
        )
        self.group_layout.addWidget(self.buffer_spin, 1, 1)

    def get_data(self) -> dict:
        """Get section configuration."""
        return {
            "crossline_layer": self.line_combo.currentLayer(),
            "buffer_distance": self.buffer_spin.value(),
        }

    def validate(self) -> tuple[bool, str]:
        if not self.line_combo.currentLayer():
            return False, self.tr("Section line layer is required")
        return True, ""

    def is_complete(self) -> bool:
        """Check if required fields are filled."""
        return bool(self.line_combo.currentLayer())
