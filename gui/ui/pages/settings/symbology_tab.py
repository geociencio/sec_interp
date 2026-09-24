"""Symbology settings tab (live styles for the preview layers)."""

from __future__ import annotations

import contextlib
from typing import Any

from qgis.gui import QgsColorButton, QgsColorRampButton, QgsDoubleSpinBox
from qgis.PyQt.QtCore import QCoreApplication, pyqtSignal
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from sec_interp.gui.main_dialog_config import DialogDefaults
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class SymbologyTab(QWidget):
    """Per-layer styles for topography, structures, drillholes and interpretations."""

    changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the symbology tab."""
        super().__init__(parent)
        self._setup_ui()

    def tr(self, message: str) -> str:
        """Translate a message for this tab."""
        return QCoreApplication.translate("SymbologyTab", message)  # type: ignore[no-any-return]

    def _setup_ui(self) -> None:
        """Build the symbology tab layout."""
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(self.tr("<b>Layer Symbology</b>")))
        layout.addWidget(
            QLabel(
                self.tr(
                    "<i>Live styles for the preview/export; the source layers are not modified.</i>"
                )
            )
        )

        layout.addWidget(self._build_topography_group())
        layout.addWidget(self._build_structures_group())
        layout.addWidget(self._build_drillholes_group())
        layout.addWidget(self._build_interpretations_group())
        layout.addStretch()

    def _build_topography_group(self) -> QGroupBox:
        """Topography color mode and line width."""
        group = QGroupBox(self.tr("Topography"))
        layout = QGridLayout(group)

        layout.addWidget(QLabel(self.tr("Color mode")), 0, 0)
        modes = QHBoxLayout()
        self.radio_gradient = QRadioButton(self.tr("Gradient"))
        self.radio_single = QRadioButton(self.tr("Simple"))
        self.radio_gradient.setChecked(True)
        modes.addWidget(self.radio_gradient)
        modes.addWidget(self.radio_single)
        layout.addLayout(modes, 0, 1)

        self.ramp_button = QgsColorRampButton()
        self.ramp_button.setShowRandomColorRamp(False)
        self.ramp_button.setColorRampFromName(DialogDefaults.TOPO_RAMP_NAME)
        self.ramp_button.setColorRampDialogTitle(self.tr("Select a color ramp"))
        self.ramp_button.setToolTip(self.tr("Color ramp for the elevation gradient"))
        layout.addWidget(self.ramp_button, 1, 0, 1, 2)

        self.topo_color_button = QgsColorButton()
        self.topo_color_button.setColor(QColor(DialogDefaults.TOPO_SINGLE_COLOR_HEX))
        self.topo_color_button.setColorDialogTitle(self.tr("Select the profile color"))
        self.topo_color_button.setToolTip(self.tr("Single color for the profile"))
        layout.addWidget(self.topo_color_button, 2, 0, 1, 2)

        layout.addWidget(QLabel(self.tr("Line width")), 3, 0)
        self.topo_width_spin = self._width_spin(0.8)
        layout.addWidget(self.topo_width_spin, 3, 1)

        self._on_topo_mode_changed()
        return group

    def _build_structures_group(self) -> QGroupBox:
        """Structural dip symbol color and width."""
        group = QGroupBox(self.tr("Structures"))
        layout = QGridLayout(group)

        self.struct_color_button = QgsColorButton()
        self.struct_color_button.setColor(QColor("#cc0000"))
        self.struct_color_button.setColorDialogTitle(self.tr("Select the structures color"))
        layout.addWidget(QLabel(self.tr("Color")), 0, 0)
        layout.addWidget(self.struct_color_button, 0, 1)

        layout.addWidget(QLabel(self.tr("Line width")), 1, 0)
        self.struct_width_spin = self._width_spin(0.5)
        layout.addWidget(self.struct_width_spin, 1, 1)
        return group

    def _build_drillholes_group(self) -> QGroupBox:
        """Drillhole trace color, width and labels."""
        group = QGroupBox(self.tr("Drillholes"))
        layout = QGridLayout(group)

        self.drill_color_button = QgsColorButton()
        self.drill_color_button.setColor(QColor(50, 50, 50))
        self.drill_color_button.setColorDialogTitle(self.tr("Select the drillhole trace color"))
        layout.addWidget(QLabel(self.tr("Trace color")), 0, 0)
        layout.addWidget(self.drill_color_button, 0, 1)

        layout.addWidget(QLabel(self.tr("Trace width")), 1, 0)
        self.drill_width_spin = self._width_spin(0.3)
        layout.addWidget(self.drill_width_spin, 1, 1)

        self.chk_drill_labels = QCheckBox(self.tr("Show hole labels"))
        self.chk_drill_labels.setChecked(True)
        layout.addWidget(self.chk_drill_labels, 2, 0, 1, 2)
        return group

    def _build_interpretations_group(self) -> QGroupBox:
        """Build the interpretations default-color group."""
        group = QGroupBox(self.tr("Interpretations"))
        layout = QGridLayout(group)

        self.interp_color_button = QgsColorButton()
        self.interp_color_button.setColor(QColor("#FF0000"))
        self.interp_color_button.setColorDialogTitle(
            self.tr("Default color for new interpretations")
        )
        layout.addWidget(QLabel(self.tr("Default color")), 0, 0)
        layout.addWidget(self.interp_color_button, 0, 1)
        return group

    def _width_spin(self, value: float) -> QgsDoubleSpinBox:
        """Create a line-width spinbox."""
        spin = QgsDoubleSpinBox()
        spin.setRange(0.1, 5.0)
        spin.setSingleStep(0.1)
        spin.setDecimals(1)
        spin.setValue(value)
        return spin

    def _on_topo_mode_changed(self) -> None:
        """Show the control matching the active topography mode."""
        single = self.radio_single.isChecked()
        self.ramp_button.setVisible(not single)
        self.topo_color_button.setVisible(single)

    def get_data(self) -> dict[str, Any]:
        """Return the current symbology settings."""
        return {
            "color_mode": "single" if self.radio_single.isChecked() else "gradient",
            "ramp_name": self.ramp_button.colorRampName(),
            "single_color_hex": self.topo_color_button.color().name(),
            "topo_line_width": self.topo_width_spin.value(),
            "struct_color": self.struct_color_button.color().name(),
            "struct_width": self.struct_width_spin.value(),
            "drill_trace_color": self.drill_color_button.color().name(),
            "drill_trace_width": self.drill_width_spin.value(),
            "drill_labels": self.chk_drill_labels.isChecked(),
            "interp_color": self.interp_color_button.color().name(),
        }

    def load(self, data: dict[str, Any]) -> None:
        """Apply persisted symbology settings."""
        mode = data.get("color_mode")
        if mode == "single":
            self.radio_single.setChecked(True)
        elif mode == "gradient":
            self.radio_gradient.setChecked(True)
        if data.get("ramp_name"):
            self.ramp_button.setColorRampFromName(str(data["ramp_name"]))
        if data.get("single_color_hex"):
            self.topo_color_button.setColor(QColor(str(data["single_color_hex"])))
        if data.get("topo_line_width") is not None:
            self.topo_width_spin.setValue(float(data["topo_line_width"]))
        self._set_color(self.struct_color_button, data.get("struct_color"))
        if data.get("struct_width") is not None:
            self.struct_width_spin.setValue(float(data["struct_width"]))
        self._set_color(self.drill_color_button, data.get("drill_trace_color"))
        if data.get("drill_trace_width") is not None:
            self.drill_width_spin.setValue(float(data["drill_trace_width"]))
        if data.get("drill_labels") is not None:
            self.chk_drill_labels.setChecked(bool(data["drill_labels"]))
        self._set_color(self.interp_color_button, data.get("interp_color"))
        self._on_topo_mode_changed()

    @staticmethod
    def _set_color(button: QgsColorButton, value: Any) -> None:
        """Set a color button when a value is present."""
        if value:
            button.setColor(QColor(str(value)))

    def reset(self) -> None:
        """Reset symbology to defaults."""
        self.radio_gradient.setChecked(True)
        self.ramp_button.setColorRampFromName(DialogDefaults.TOPO_RAMP_NAME)
        self.topo_color_button.setColor(QColor(DialogDefaults.TOPO_SINGLE_COLOR_HEX))
        self.topo_width_spin.setValue(0.8)
        self.struct_color_button.setColor(QColor("#cc0000"))
        self.struct_width_spin.setValue(0.5)
        self.drill_color_button.setColor(QColor(50, 50, 50))
        self.drill_width_spin.setValue(0.3)
        self.chk_drill_labels.setChecked(True)
        self.interp_color_button.setColor(QColor("#FF0000"))
        self._on_topo_mode_changed()

    def connect_signals(self) -> None:
        """Connect internal signals."""
        self.radio_gradient.toggled.connect(self._on_topo_mode_changed)
        self.radio_single.toggled.connect(self._on_topo_mode_changed)
        for signal in (
            self.radio_gradient.toggled,
            self.radio_single.toggled,
            self.ramp_button.colorRampChanged,
            self.topo_color_button.colorChanged,
            self.topo_width_spin.valueChanged,
            self.struct_color_button.colorChanged,
            self.struct_width_spin.valueChanged,
            self.drill_color_button.colorChanged,
            self.drill_width_spin.valueChanged,
            self.chk_drill_labels.toggled,
            self.interp_color_button.colorChanged,
        ):
            signal.connect(self.changed.emit)

    def disconnect_signals(self) -> None:
        """Disconnect internal signals."""
        for signal, slot in (
            (self.radio_gradient.toggled, self._on_topo_mode_changed),
            (self.radio_single.toggled, self._on_topo_mode_changed),
        ):
            with contextlib.suppress(TypeError, RuntimeError):
                signal.disconnect(slot)
        with contextlib.suppress(TypeError, RuntimeError):
            self.changed.disconnect()
