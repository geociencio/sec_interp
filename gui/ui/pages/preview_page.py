"""Preview area widget."""

from __future__ import annotations

import contextlib
from typing import Any

from qgis.core import QgsApplication
from qgis.gui import QgsCollapsibleGroupBox, QgsMapCanvas
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from sec_interp.gui.preview_side_panel import PreviewSidePanel

_DEFAULT_PANEL_SIZES = [600, 200]


class PreviewWidget(QWidget):
    """Widget for profile preview and controls."""

    def __init__(self, parent: Any = None) -> None:
        """Initialize the preview widget.

        Args:
            parent: Optional parent widget.

        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Frame for preview (optional visual container)
        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_layout = QVBoxLayout(self.frame)

        self.side_panel = PreviewSidePanel()
        self._setup_canvas_area()

        # Canvas on the left, legend/interpretations panel on the right
        self.canvas_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.canvas_splitter.setChildrenCollapsible(True)
        self.canvas_splitter.addWidget(self.canvas_container)
        self.canvas_splitter.addWidget(self.side_panel)
        self.canvas_splitter.setStretchFactor(0, 4)
        self.canvas_splitter.setStretchFactor(1, 1)
        self.canvas_splitter.setSizes(_DEFAULT_PANEL_SIZES)
        self.frame_layout.addWidget(self.canvas_splitter, stretch=10)

        self._setup_controls_group()
        self._setup_results_area()

        layout.addWidget(self.frame)

        # Setup connections
        self.connect_signals()

    def connect_signals(self) -> None:
        """Connect internal signals for coordinates and scale tracking."""
        # Disconnect first to ensure idempotency
        self.disconnect_signals()

        self.canvas.xyCoordinates.connect(self._update_coords)
        self.canvas.scaleChanged.connect(self._update_scale)
        self.chk_auto_lod.toggled.connect(self._toggle_lod_spin)
        self.chk_smooth.toggled.connect(self._toggle_smooth_spin)

    def _setup_canvas_area(self) -> None:
        """Set up map canvas and status bar in their own container."""
        self.canvas_container = QWidget()
        container_layout = QVBoxLayout(self.canvas_container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(QColor(255, 255, 255))
        self.canvas.setMinimumHeight(300)
        container_layout.addWidget(self.canvas, stretch=10)

        # -- Status Bar --
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(5, 0, 5, 0)

        self.lbl_coords = QLabel(self.tr("Coords: - , -"))
        self.lbl_scale = QLabel(self.tr("Scale 1: -"))
        self.lbl_crs = QLabel(self.tr("CRS: -"))

        for lbl in [self.lbl_coords, self.lbl_scale, self.lbl_crs]:
            lbl.setStyleSheet("color: #666; font-size: 9pt;")

        status_layout.addWidget(self.lbl_coords)
        status_layout.addStretch()
        status_layout.addWidget(self.lbl_scale)
        status_layout.addStretch()
        status_layout.addWidget(self.lbl_crs)
        container_layout.addLayout(status_layout)

    def _setup_controls_group(self) -> None:
        """Set up collapsible controls (action buttons, LOD, checkboxes)."""
        self.controls_group = QgsCollapsibleGroupBox(self.tr("Controls"))
        controls_layout = QVBoxLayout(self.controls_group)

        self._setup_action_buttons(controls_layout)
        self._setup_lod_controls(controls_layout)
        self._setup_layer_checkboxes(controls_layout)

        self.frame_layout.addWidget(self.controls_group)

    def _setup_action_buttons(self, parent_layout: QVBoxLayout) -> None:
        """Set up preview, measure, and export buttons."""
        btn_layout = QHBoxLayout()
        self.btn_preview = QPushButton(self.tr("Preview"))
        self.btn_preview.setIcon(QgsApplication.getThemeIcon("mActionRefresh.svg"))

        self.btn_export = QPushButton(self.tr("Export"))
        self.btn_export.setToolTip(self.tr("Export preview to file"))
        self.btn_export.setIcon(QgsApplication.getThemeIcon("mActionSaveMapAsImage.svg"))

        self.btn_measure = QPushButton(self.tr("Measure"))
        self.btn_measure.setCheckable(True)
        self.btn_measure.setToolTip(self.tr("Measure distance and slope"))
        self.btn_measure.setIcon(QgsApplication.getThemeIcon("mActionMeasure.svg"))

        self.btn_interpret = QPushButton(self.tr("Interpret"))
        self.btn_interpret.setCheckable(True)
        self.btn_interpret.setToolTip(self.tr("Draw interpretation polygons"))
        self.btn_interpret.setIcon(QgsApplication.getThemeIcon("mActionAddPolygon.svg"))

        self.btn_finalize = QPushButton(self.tr("Finalize"))
        self.btn_finalize.setToolTip(self.tr("Finalize multi-point measurement"))
        self.btn_finalize.setVisible(False)
        self.btn_finalize.setIcon(QgsApplication.getThemeIcon("mActionCheck.svg"))

        btn_layout.addWidget(self.btn_preview)
        btn_layout.addWidget(self.btn_measure)
        btn_layout.addWidget(self.btn_interpret)
        btn_layout.addWidget(self.btn_finalize)
        btn_layout.addWidget(self.btn_export)
        parent_layout.addLayout(btn_layout)

    def _setup_lod_controls(self, parent_layout: QVBoxLayout) -> None:
        """Set up level of detail controls."""
        lod_layout = QHBoxLayout()
        lod_layout.addWidget(QLabel(self.tr("Max Points:")))

        self.spin_max_points = QSpinBox()
        self.spin_max_points.setRange(100, 10000)
        self.spin_max_points.setValue(1000)
        self.spin_max_points.setSingleStep(100)
        self.spin_max_points.setToolTip(
            self.tr("Maximum points to render in preview (LOD Optimization)")
        )
        lod_layout.addWidget(self.spin_max_points)

        self.chk_auto_lod = QCheckBox(self.tr("Auto"))
        self.chk_auto_lod.setToolTip(self.tr("Automatically adjust details based on preview size"))
        self.chk_auto_lod.toggled.connect(self._toggle_lod_spin)
        lod_layout.addWidget(self.chk_auto_lod)

        self.chk_adaptive_sampling = QCheckBox(self.tr("Adaptive"))
        self.chk_adaptive_sampling.setToolTip(
            self.tr("Use adaptive sampling based on curvature (Phase 2)")
        )
        self.chk_adaptive_sampling.setChecked(True)
        lod_layout.addWidget(self.chk_adaptive_sampling)

        lod_layout.addStretch()
        parent_layout.addLayout(lod_layout)

        smooth_layout = QHBoxLayout()
        self.chk_smooth = QCheckBox(self.tr("Smooth"))
        self.chk_smooth.setToolTip(self.tr("Show a smoothed topography line over the profile"))
        smooth_layout.addWidget(self.chk_smooth)

        smooth_layout.addWidget(QLabel(self.tr("Window (m):")))
        self.spin_smooth_window = QSpinBox()
        self.spin_smooth_window.setRange(10, 500)
        self.spin_smooth_window.setValue(30)
        self.spin_smooth_window.setSingleStep(5)
        self.spin_smooth_window.setEnabled(False)
        self.spin_smooth_window.setToolTip(self.tr("Smoothing window in metres"))
        smooth_layout.addWidget(self.spin_smooth_window)

        smooth_layout.addStretch()
        parent_layout.addLayout(smooth_layout)

    def _setup_layer_checkboxes(self, parent_layout: QVBoxLayout) -> None:
        """Set up checkboxes for layer visibility."""
        chk_layout = QHBoxLayout()
        self.chk_topo = QCheckBox(self.tr("Show Topography"))
        self.chk_topo.setChecked(True)
        self.chk_geol = QCheckBox(self.tr("Show Geology"))
        self.chk_geol.setChecked(True)
        self.chk_struct = QCheckBox(self.tr("Show Structures"))
        self.chk_struct.setChecked(True)
        self.chk_drillholes = QCheckBox(self.tr("Show Drillholes"))
        self.chk_drillholes.setChecked(True)
        self.chk_interpretations = QCheckBox(self.tr("Show Interpretations"))
        self.chk_interpretations.setChecked(True)

        chk_layout.addWidget(self.chk_topo)
        chk_layout.addWidget(self.chk_geol)
        chk_layout.addWidget(self.chk_struct)
        chk_layout.addWidget(self.chk_drillholes)
        chk_layout.addWidget(self.chk_interpretations)
        parent_layout.addLayout(chk_layout)

    def _setup_results_area(self) -> None:
        """Set up results group and text display."""
        self.results_group = QgsCollapsibleGroupBox(self.tr("Results"))
        results_layout = QVBoxLayout(self.results_group)
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(100)
        results_layout.addWidget(self.results_text)
        self.frame_layout.addWidget(self.results_group)

    def _update_coords(self, point: Any) -> None:
        """Update coordinate label."""
        self.lbl_coords.setText(f"{point.x():.2f}, {point.y():.2f}")

    def _update_scale(self, scale: float) -> None:
        """Update scale label."""
        self.lbl_scale.setText(self.tr("Scale 1:{}").format(int(scale)))

    def _toggle_lod_spin(self, checked: bool) -> None:
        """Enable/disable max points spinbox based on auto checkbox."""
        self.spin_max_points.setEnabled(not checked)

    def _toggle_smooth_spin(self, checked: bool) -> None:
        """Enable/disable the smoothing window based on the Smooth checkbox."""
        self.spin_smooth_window.setEnabled(checked)

    def disconnect_signals(self) -> None:
        """Disconnect all signals to prevent memory leaks."""
        with contextlib.suppress(TypeError, RuntimeError):
            self.canvas.xyCoordinates.disconnect()
        with contextlib.suppress(TypeError, RuntimeError):
            self.canvas.scaleChanged.disconnect()
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_auto_lod.toggled.disconnect()
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_smooth.toggled.disconnect()

    def dump(self) -> dict[str, Any]:
        """Return the persistable preview-control state."""
        return {
            "show_topo": self.chk_topo.isChecked(),
            "show_geol": self.chk_geol.isChecked(),
            "show_struct": self.chk_struct.isChecked(),
            "show_drillholes": self.chk_drillholes.isChecked(),
            "show_interpretations": self.chk_interpretations.isChecked(),
            "auto_lod": self.chk_auto_lod.isChecked(),
            "adaptive_sampling": self.chk_adaptive_sampling.isChecked(),
            "smooth": self.chk_smooth.isChecked(),
            "smooth_window": self.spin_smooth_window.value(),
            "max_points": self.spin_max_points.value(),
            "legend_splitter": list(self.canvas_splitter.sizes()),
        }

    def load(self, data: dict[str, Any]) -> None:
        """Apply persisted preview-control state."""
        for chk, key in [
            (self.chk_topo, "show_topo"),
            (self.chk_geol, "show_geol"),
            (self.chk_struct, "show_struct"),
            (self.chk_drillholes, "show_drillholes"),
            (self.chk_interpretations, "show_interpretations"),
            (self.chk_auto_lod, "auto_lod"),
            (self.chk_adaptive_sampling, "adaptive_sampling"),
            (self.chk_smooth, "smooth"),
        ]:
            checked = data.get(key)
            if checked is not None:
                chk.setChecked(bool(checked))
        max_points = data.get("max_points")
        if max_points is not None:
            self.spin_max_points.setValue(int(max_points))
        smooth_window = data.get("smooth_window")
        if smooth_window is not None:
            self.spin_smooth_window.setValue(int(smooth_window))
        self._toggle_smooth_spin(self.chk_smooth.isChecked())
        sizes = data.get("legend_splitter")
        if isinstance(sizes, list) and sizes:
            self.canvas_splitter.setSizes([int(s) for s in sizes])

    def reset(self) -> None:
        """Reset preview controls to defaults."""
        for chk in [
            self.chk_topo,
            self.chk_geol,
            self.chk_struct,
            self.chk_drillholes,
            self.chk_interpretations,
            self.chk_adaptive_sampling,
        ]:
            chk.setChecked(True)
        self.chk_auto_lod.setChecked(False)
        self.spin_max_points.setValue(1000)
        self.chk_smooth.setChecked(False)
        self.spin_smooth_window.setValue(30)
        self._toggle_smooth_spin(False)
        self.canvas_splitter.setSizes(_DEFAULT_PANEL_SIZES)
