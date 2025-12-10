"""Preview area widget."""
from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QCheckBox, QTextEdit, QFrame, QLabel, QSpinBox
)
from qgis.gui import QgsMapCanvas, QgsCollapsibleGroupBox
from qgis.PyQt.QtGui import QColor


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
        frame_layout = QVBoxLayout(self.frame)
        
        # 1. Map Canvas
        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(QColor(255, 255, 255))
        self.canvas.setMinimumHeight(300)
        frame_layout.addWidget(self.canvas, stretch=10)

        # -- Status Bar --
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(5, 0, 5, 0)
        
        self.lbl_coords = QLabel("Coords: - , -")
        self.lbl_scale = QLabel("Scale 1: -")
        self.lbl_crs = QLabel("CRS: -")
        
        # Style labels for a status bar look
        for lbl in [self.lbl_coords, self.lbl_scale, self.lbl_crs]:
            lbl.setStyleSheet("color: #666; font-size: 9pt;")

        status_layout.addWidget(self.lbl_coords)
        status_layout.addStretch()
        status_layout.addWidget(self.lbl_scale)
        status_layout.addStretch()
        status_layout.addWidget(self.lbl_crs)
        
        frame_layout.addLayout(status_layout)

        # 2. Controls (Preview | Export)
        btn_layout = QHBoxLayout()
        self.btn_preview = QPushButton("Preview")
        self.btn_export = QPushButton("Export")
        self.btn_export.setToolTip("Export preview to file")
        
        btn_layout.addWidget(self.btn_preview)
        btn_layout.addWidget(self.btn_export)
        frame_layout.addLayout(btn_layout)

        # 3. Settings (LOD)
        lod_layout = QHBoxLayout()
        lod_layout.addWidget(QLabel("Max Points:"))
        
        self.spin_max_points = QSpinBox()
        self.spin_max_points.setRange(100, 10000)
        self.spin_max_points.setValue(1000)
        self.spin_max_points.setSingleStep(100)
        self.spin_max_points.setToolTip("Maximum points to render in preview (LOD Optimization)")
        lod_layout.addWidget(self.spin_max_points)
        
        lod_layout.addStretch() # Push to left
        frame_layout.addLayout(lod_layout)

        # 4. Checkboxes
        chk_layout = QHBoxLayout()
        self.chk_topo = QCheckBox("Show Topography")
        self.chk_topo.setChecked(True)
        
        self.chk_geol = QCheckBox("Show Geology")
        self.chk_geol.setChecked(True)
        
        self.chk_struct = QCheckBox("Show Structures")
        self.chk_struct.setChecked(True)
        
        chk_layout.addWidget(self.chk_topo)
        chk_layout.addWidget(self.chk_geol)
        chk_layout.addWidget(self.chk_struct)
        frame_layout.addLayout(chk_layout)

        # 4. Results / Logs
        self.results_group = QgsCollapsibleGroupBox("Results")
        results_layout = QVBoxLayout(self.results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(100)
        
        results_layout.addWidget(self.results_text)
        frame_layout.addWidget(self.results_group)

        layout.addWidget(self.frame)

        # Setup connections
        self.canvas.xyCoordinates.connect(self._update_coords)
        self.canvas.scaleChanged.connect(self._update_scale)

    def _update_coords(self, point):
        """Update coordinate label."""
        self.lbl_coords.setText(f"{point.x():.2f}, {point.y():.2f}")

    def _update_scale(self, scale):
        """Update scale label."""
        self.lbl_scale.setText(f"Scale 1:{int(scale)}")

