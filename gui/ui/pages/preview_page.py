"""Preview area widget."""

from qgis.gui import QgsCollapsibleGroupBox, QgsMapCanvas
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class PreviewWidget(QWidget):
    """Widget for profile preview and controls."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Frame for preview (optional visual container)
        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame_layout = QVBoxLayout(self.frame)

        self._setup_canvas_area()
        self._setup_action_buttons()
        self._setup_lod_controls()
        self._setup_layer_checkboxes()
        self._setup_results_area()

        layout.addWidget(self.frame)

        # Setup connections
        self.canvas.xyCoordinates.connect(self._update_coords)
        self.canvas.scaleChanged.connect(self._update_scale)

    def _setup_canvas_area(self):
        """Setup map canvas and status bar."""
        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(QColor(255, 255, 255))
        self.canvas.setMinimumHeight(300)
        self.frame_layout.addWidget(self.canvas, stretch=10)

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
        self.frame_layout.addLayout(status_layout)

    def _setup_action_buttons(self):
        """Setup preview, measure, and export buttons."""
        btn_layout = QHBoxLayout()
        self.btn_preview = QPushButton(self.tr("Preview"))
        self.btn_export = QPushButton(self.tr("Export"))
        self.btn_export.setToolTip(self.tr("Export preview to file"))

        self.btn_measure = QPushButton(self.tr("Measure"))
        self.btn_measure.setCheckable(True)
        self.btn_measure.setToolTip(self.tr("Measure distance and slope"))

        self.btn_finalize = QPushButton(self.tr("Finalize"))
        self.btn_finalize.setToolTip(self.tr("Finalize multi-point measurement"))
        self.btn_finalize.setVisible(False)

        btn_layout.addWidget(self.btn_preview)
        btn_layout.addWidget(self.btn_measure)
        btn_layout.addWidget(self.btn_finalize)
        btn_layout.addWidget(self.btn_export)
        self.frame_layout.addLayout(btn_layout)

    def _setup_lod_controls(self):
        """Setup level of detail controls."""
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
        self.chk_auto_lod.setToolTip(
            self.tr("Automatically adjust details based on preview size")
        )
        self.chk_auto_lod.toggled.connect(self._toggle_lod_spin)
        lod_layout.addWidget(self.chk_auto_lod)

        self.chk_adaptive_sampling = QCheckBox(self.tr("Adaptive"))
        self.chk_adaptive_sampling.setToolTip(
            self.tr("Use adaptive sampling based on curvature (Phase 2)")
        )
        self.chk_adaptive_sampling.setChecked(True)
        lod_layout.addWidget(self.chk_adaptive_sampling)

        lod_layout.addStretch()
        self.frame_layout.addLayout(lod_layout)

    def _setup_layer_checkboxes(self):
        """Setup checkboxes for layer visibility."""
        chk_layout = QHBoxLayout()
        self.chk_topo = QCheckBox(self.tr("Show Topography"))
        self.chk_topo.setChecked(True)
        self.chk_geol = QCheckBox(self.tr("Show Geology"))
        self.chk_geol.setChecked(True)
        self.chk_struct = QCheckBox(self.tr("Show Structures"))
        self.chk_struct.setChecked(True)
        self.chk_drillholes = QCheckBox(self.tr("Show Drillholes"))
        self.chk_drillholes.setChecked(True)

        chk_layout.addWidget(self.chk_topo)
        chk_layout.addWidget(self.chk_geol)
        chk_layout.addWidget(self.chk_struct)
        chk_layout.addWidget(self.chk_drillholes)
        self.frame_layout.addLayout(chk_layout)

    def _setup_results_area(self):
        """Setup results group and text display."""
        self.results_group = QgsCollapsibleGroupBox(self.tr("Results"))
        results_layout = QVBoxLayout(self.results_group)
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(100)
        results_layout.addWidget(self.results_text)
        self.frame_layout.addWidget(self.results_group)

    def _update_coords(self, point):
        """Update coordinate label."""
        self.lbl_coords.setText(f"{point.x():.2f}, {point.y():.2f}")

    def _update_scale(self, scale):
        """Update scale label."""
        self.lbl_scale.setText(self.tr("Scale 1:{}").format(int(scale)))

    def _toggle_lod_spin(self, checked):
        """Enable/disable max points spinbox based on auto checkbox."""
        self.spin_max_points.setEnabled(not checked)
