"""Symbology settings tab (live styles for the preview layers)."""

from __future__ import annotations

import contextlib
from typing import Any

from qgis.gui import QgsColorButton, QgsColorRampButton, QgsDoubleSpinBox
from qgis.PyQt.QtCore import QCoreApplication, pyqtSignal
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

_LEGEND_POSITIONS = ("top-right", "top-left", "bottom-right", "bottom-left")

from sec_interp.gui.main_dialog_config import DialogDefaults
from sec_interp.gui.preview_side_panel import UnitStyleEditor
from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class SymbologyTab(QWidget):
    """Per-layer styles for topography, structures, drillholes and interpretations."""

    changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the symbology tab."""
        super().__init__(parent)
        self._unit_manager: Any = None
        self._unit_rows: list[UnitStyleEditor] = []
        self._unit_signature: list[tuple] | None = None
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
        layout.addWidget(self._build_legend_group())
        layout.addWidget(self._build_units_group(), stretch=1)
        layout.addStretch()

    def _build_legend_group(self) -> QGroupBox:
        """Legend options (export toggle, position, font size, item limit)."""
        group = QGroupBox(self.tr("Legend"))
        layout = QGridLayout(group)

        self.chk_export_legend = QCheckBox(self.tr("Show legend in the exported image"))
        self.chk_export_legend.setChecked(True)
        self.chk_export_legend.setToolTip(
            self.tr("The preview legend lives in the collapsible side panel.")
        )
        layout.addWidget(self.chk_export_legend, 0, 0, 1, 2)

        layout.addWidget(QLabel(self.tr("Position")), 1, 0)
        self.combo_legend_pos = QComboBox()
        self.combo_legend_pos.addItems(
            [
                self.tr("Top right"),
                self.tr("Top left"),
                self.tr("Bottom right"),
                self.tr("Bottom left"),
            ]
        )
        layout.addWidget(self.combo_legend_pos, 1, 1)

        layout.addWidget(QLabel(self.tr("Font size")), 2, 0)
        self.spin_legend_font = QSpinBox()
        self.spin_legend_font.setRange(6, 16)
        self.spin_legend_font.setValue(8)
        layout.addWidget(self.spin_legend_font, 2, 1)

        layout.addWidget(QLabel(self.tr("Max items (0 = all)")), 3, 0)
        self.spin_legend_max = QSpinBox()
        self.spin_legend_max.setRange(0, 200)
        self.spin_legend_max.setValue(0)
        self.spin_legend_max.setToolTip(
            self.tr("Limit legend items; the rest are summarized as '+N more'.")
        )
        layout.addWidget(self.spin_legend_max, 3, 1)
        return group

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

    def _build_units_group(self) -> QGroupBox:
        """Build the per-unit editor (color/hide/rename/reorder)."""
        group = QGroupBox(self.tr("Units"))
        layout = QVBoxLayout(group)
        layout.addWidget(
            QLabel(self.tr("<i>Hide, recolor, rename or reorder the geology/drillhole units.</i>"))
        )

        self.units_scroll = QScrollArea()
        self.units_scroll.setWidgetResizable(True)
        self.units_container = QWidget()
        self.units_layout = QVBoxLayout(self.units_container)
        self.units_layout.setContentsMargins(0, 0, 0, 0)
        self.units_layout.setSpacing(1)
        self.units_scroll.setWidget(self.units_container)
        layout.addWidget(self.units_scroll, stretch=1)

        btn_layout = QHBoxLayout()
        self.btn_reset_units = QPushButton(self.tr("Reset unit styles"))
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_reset_units)
        layout.addLayout(btn_layout)
        return group

    def set_unit_manager(self, manager: Any) -> None:
        """Inject the ColorManager that backs the per-unit editor."""
        self._unit_manager = manager
        self.refresh_units(force=True)

    def refresh_units(self, force: bool = False) -> None:
        """Rebuild the unit rows when the underlying units change."""
        manager = self._unit_manager
        if manager is None:
            return
        entries = [
            (name, manager.label(name), manager.get_color(name).name(), manager.is_hidden(name))
            for name in manager.ordered_units()
        ]
        if not force and entries == self._unit_signature:
            return
        self._unit_signature = entries
        self._rebuild_unit_rows(manager, entries)

    def _rebuild_unit_rows(self, manager: Any, entries: list[tuple]) -> None:
        """Recreate the editable rows for the current units."""
        for row in self._unit_rows:
            self.units_layout.removeWidget(row)
            row.deleteLater()
        self._unit_rows = []

        for name, label, color_hex, hidden in entries:
            row = UnitStyleEditor(
                name,
                QColor(color_hex),
                hidden=hidden,
                label=label,
                with_rename=True,
                with_reorder=True,
            )
            row.visibility_changed.connect(self._on_unit_visibility)
            row.color_requested.connect(self._on_unit_color)
            row.label_changed.connect(self._on_unit_label)
            row.move_requested.connect(self._on_unit_move)
            self.units_layout.insertWidget(len(self._unit_rows), row)
            self._unit_rows.append(row)

    def _on_unit_visibility(self, name: str, visible: bool) -> None:
        """Hide/show a unit and refresh the preview."""
        self._unit_manager.set_hidden(name, not visible)
        self.changed.emit()

    def _on_unit_color(self, name: str) -> None:
        """Pick a new color for a unit and refresh the preview."""
        current = self._unit_manager.get_color(name)
        color = QColorDialog.getColor(current, self, self.tr("Select unit color"))
        if color is not None and color.isValid():
            self._unit_manager.set_color(name, color)
            self.refresh_units(force=True)
            self.changed.emit()

    def _on_unit_label(self, name: str, text: str) -> None:
        """Rename a unit and refresh the preview/legend."""
        self._unit_manager.set_label(name, text)
        self.changed.emit()

    def _on_unit_move(self, name: str, delta: int) -> None:
        """Reorder a unit and refresh the preview/legend."""
        self._unit_manager.move_unit(name, delta)
        self.refresh_units(force=True)
        self.changed.emit()

    def reset_units(self) -> None:
        """Clear all per-unit customization."""
        manager = self._unit_manager
        if manager is None:
            return
        for name in list(manager.known_units()):
            manager.set_hidden(name, False)
            manager.set_label(name, "")
        manager.set_order([])
        self.refresh_units(force=True)
        self.changed.emit()

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
            "show_legend": self.chk_export_legend.isChecked(),
            "legend_pos": _LEGEND_POSITIONS[self.combo_legend_pos.currentIndex()],
            "legend_font_size": self.spin_legend_font.value(),
            "legend_max_items": self.spin_legend_max.value(),
        }

    def load(self, data: dict[str, Any]) -> None:
        """Apply persisted symbology settings."""
        self._load_topography(data)
        self._load_layer_styles(data)
        self._load_legend(data)
        self._on_topo_mode_changed()

    def _load_topography(self, data: dict[str, Any]) -> None:
        """Restore topography style settings."""
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

    def _load_layer_styles(self, data: dict[str, Any]) -> None:
        """Restore structures, drillhole and interpretation styles."""
        self._set_color(self.struct_color_button, data.get("struct_color"))
        if data.get("struct_width") is not None:
            self.struct_width_spin.setValue(float(data["struct_width"]))
        self._set_color(self.drill_color_button, data.get("drill_trace_color"))
        if data.get("drill_trace_width") is not None:
            self.drill_width_spin.setValue(float(data["drill_trace_width"]))
        if data.get("drill_labels") is not None:
            self.chk_drill_labels.setChecked(bool(data["drill_labels"]))
        self._set_color(self.interp_color_button, data.get("interp_color"))

    def _load_legend(self, data: dict[str, Any]) -> None:
        """Restore legend options."""
        if data.get("show_legend") is not None:
            self.chk_export_legend.setChecked(bool(data["show_legend"]))
        if data.get("legend_pos") in _LEGEND_POSITIONS:
            self.combo_legend_pos.setCurrentIndex(_LEGEND_POSITIONS.index(data["legend_pos"]))
        if data.get("legend_font_size") is not None:
            self.spin_legend_font.setValue(int(data["legend_font_size"]))
        if data.get("legend_max_items") is not None:
            self.spin_legend_max.setValue(int(data["legend_max_items"]))

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
        self.chk_export_legend.setChecked(True)
        self.combo_legend_pos.setCurrentIndex(0)
        self.spin_legend_font.setValue(8)
        self.spin_legend_max.setValue(0)
        self._on_topo_mode_changed()

    def connect_signals(self) -> None:
        """Connect internal signals."""
        self.radio_gradient.toggled.connect(self._on_topo_mode_changed)
        self.radio_single.toggled.connect(self._on_topo_mode_changed)
        self.btn_reset_units.clicked.connect(self.reset_units)
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
            self.chk_export_legend.toggled,
            self.combo_legend_pos.currentIndexChanged,
            self.spin_legend_font.valueChanged,
            self.spin_legend_max.valueChanged,
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
