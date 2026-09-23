"""Cross-section configuration page."""

from __future__ import annotations

import contextlib
from typing import Any

from qgis.core import QgsMapLayerProxyModel
from qgis.gui import QgsDoubleSpinBox, QgsMapLayerComboBox
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QGridLayout, QLabel

from sec_interp.core.validation.project_validators import SECTION_LINE_VERTEX_COUNT
from sec_interp.gui.adapters.validation_extractor import extract_section_line_metrics
from sec_interp.gui.main_dialog_config import DialogDefaults

from .base_page import BasePage, set_combo_layer


class SectionPage(BasePage):
    """Configuration page for Cross Section settings."""

    layer_keys = frozenset({"section_layer"})

    def __init__(self, parent: Any = None) -> None:
        """Initialize the section configuration page.

        Args:
            parent: Optional parent widget.

        """
        title = QCoreApplication.translate("SectionPage", "Cross Section Line")
        mandatory = QCoreApplication.translate("SectionPage", "Mandatory")
        super().__init__(f"{title} — {mandatory}", parent)

    def _setup_ui(self) -> None:
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
            self.line_combo.setFilters(QgsMapLayerProxyModel.Filter.LineLayer)

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

    def get_data(self) -> dict[str, Any]:
        """Get section configuration."""
        return {
            "crossline_layer": self.line_combo.currentLayer(),
            "buffer_distance": self.buffer_spin.value(),
        }

    def dump(self) -> dict[str, Any]:
        """Return the persistable section state."""
        return {
            "section_layer": self.line_combo.currentLayer(),
            "buffer_dist": self.buffer_spin.value(),
        }

    def load(self, data: dict[str, Any]) -> None:
        """Apply persisted section state."""
        if "section_layer" in data and data["section_layer"] is not None:
            set_combo_layer(self.line_combo, data["section_layer"])
        buffer_dist = data.get("buffer_dist")
        if buffer_dist is not None:
            self.buffer_spin.setValue(float(buffer_dist))

    def reset(self) -> None:
        """Reset section inputs to defaults."""
        self.line_combo.setLayer(None)
        self.buffer_spin.setValue(float(DialogDefaults.BUFFER_DISTANCE))

    def validate(self) -> tuple[bool, str]:
        """Validate page settings.

        Enforces the simple 2-point section line invariant: the selected line
        must be a valid line with exactly two vertices (start and end) in a
        projected CRS.

        Returns:
            Tuple of (success, error message).

        """
        layer = self.line_combo.currentLayer()
        if not layer:
            return False, self.tr("Section line layer is required")
        if not layer.isValid():
            return False, self.tr("Section line layer is not valid")

        if self._uses_geographic_crs(layer):
            return False, self.tr("Section line must use a projected CRS (metric units)")

        vertex_count, length = extract_section_line_metrics(layer)
        if vertex_count is None:
            return False, self.tr("Section line layer has no readable line geometry")
        if vertex_count != SECTION_LINE_VERTEX_COUNT:
            return False, self.tr("Section line must have exactly 2 vertices (start and end)")
        if length is not None and length <= 0:
            return False, self.tr("Section line has zero length")
        return True, ""

    @staticmethod
    def _uses_geographic_crs(layer: Any) -> bool:
        """Return True when the layer's CRS is geographic (degrees)."""
        try:
            crs = layer.crs()
            return bool(crs.isValid() and crs.isGeographic())
        except (AttributeError, TypeError):
            return False

    def is_complete(self) -> bool:
        """Check if the section line is a valid 2-point line."""
        return self.validate()[0]

    def disconnect_signals(self) -> None:
        """Disconnect all signals to prevent memory leaks."""
        with contextlib.suppress(TypeError, RuntimeError):
            self.line_combo.layerChanged.disconnect()
