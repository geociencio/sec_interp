"""Default (export selection) settings tab."""

from __future__ import annotations

import contextlib
from typing import Any

from qgis.PyQt.QtCore import QCoreApplication, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

_EXPORT_CHECKBOXES = (
    "chk_exp_topo",
    "chk_exp_geol",
    "chk_exp_struct",
    "chk_exp_drill",
    "chk_exp_interp",
)


class DefaultTab(QWidget):
    """Export selection, format and naming settings."""

    changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the default tab."""
        super().__init__(parent)
        self._setup_ui()

    def tr(self, message: str) -> str:
        """Translate a message for this tab."""
        return QCoreApplication.translate("DefaultTab", message)  # type: ignore[no-any-return]

    def _setup_ui(self) -> None:
        """Build the default tab layout."""
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(self.tr("<b>Export Selection (Save)</b>")))
        layout.addWidget(
            QLabel(self.tr("<i>Select which data to generate when clicking Save.</i>"))
        )

        self.chk_exp_topo = QCheckBox(self.tr("Topographic Profile"))
        self.chk_exp_geol = QCheckBox(self.tr("Geological Profile"))
        self.chk_exp_struct = QCheckBox(self.tr("Structural Data"))
        self.chk_exp_drill = QCheckBox(self.tr("Drillhole Data"))
        self.chk_exp_interp = QCheckBox(self.tr("Interpretations (2D)"))

        layout.addWidget(self.chk_exp_topo)
        layout.addWidget(self.chk_exp_geol)
        layout.addWidget(self.chk_exp_struct)
        layout.addWidget(self.chk_exp_drill)
        layout.addWidget(self.chk_exp_interp)

        layout.addWidget(QLabel(self.tr("<br><b>Export Format & Naming</b>")))

        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel(self.tr("Default Vector Format:")))
        self.combo_format = QComboBox()
        self.combo_format.addItems(["Shapefile", "GeoPackage", "DXF"])
        format_layout.addWidget(self.combo_format)
        format_layout.addStretch()
        layout.addLayout(format_layout)

        naming_layout = QHBoxLayout()
        naming_layout.addWidget(QLabel(self.tr("Naming Pattern:")))
        self.txt_naming = QLineEdit()
        self.txt_naming.setPlaceholderText("{filename}_{profile}")
        self.txt_naming.setToolTip(
            self.tr("Pattern for exported files. Use {filename} and {profile} as placeholders.")
        )
        naming_layout.addWidget(self.txt_naming)
        layout.addLayout(naming_layout)

        btn_layout = QHBoxLayout()
        self.btn_reset_export = QPushButton(self.tr("Reset to defaults"))
        self.btn_reset_export.setToolTip(
            self.tr("Re-enables all export options and resets format settings.")
        )
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_reset_export)
        layout.addLayout(btn_layout)

        layout.addStretch()

    def get_data(self) -> dict[str, Any]:
        """Return export selection settings."""
        return {
            "exp_topo": (self.chk_exp_topo.isChecked() if hasattr(self, "chk_exp_topo") else True),
            "exp_geol": (self.chk_exp_geol.isChecked() if hasattr(self, "chk_exp_geol") else True),
            "exp_struct": (
                self.chk_exp_struct.isChecked() if hasattr(self, "chk_exp_struct") else True
            ),
            "exp_drill": (
                self.chk_exp_drill.isChecked() if hasattr(self, "chk_exp_drill") else True
            ),
            "exp_interp": (
                self.chk_exp_interp.isChecked() if hasattr(self, "chk_exp_interp") else True
            ),
            "export_format": (
                self.combo_format.currentText() if hasattr(self, "combo_format") else "Shapefile"
            ),
            "export_naming": (
                self.txt_naming.text() if hasattr(self, "txt_naming") else "{filename}_{profile}"
            ),
        }

    def reset_to_defaults(self) -> None:
        """Reset export checkboxes and format settings to defaults."""
        for attr in _EXPORT_CHECKBOXES:
            widget = getattr(self, attr, None)
            if widget is not None:
                widget.setChecked(True)

        if hasattr(self, "combo_format"):
            index = self.combo_format.findText("Shapefile")
            if index >= 0:
                self.combo_format.setCurrentIndex(index)

        if hasattr(self, "txt_naming"):
            self.txt_naming.setText("{filename}_{profile}")
        logger.info("Export options reset to defaults.")

    def connect_signals(self) -> None:
        """Connect default tab signals."""
        self.chk_exp_topo.stateChanged.connect(self.changed.emit)
        self.chk_exp_geol.stateChanged.connect(self.changed.emit)
        self.chk_exp_struct.stateChanged.connect(self.changed.emit)
        self.chk_exp_drill.stateChanged.connect(self.changed.emit)
        self.chk_exp_interp.stateChanged.connect(self.changed.emit)
        self.btn_reset_export.clicked.connect(self.reset_to_defaults)

        if hasattr(self, "combo_format"):
            self.combo_format.currentIndexChanged.connect(self.changed.emit)
        if hasattr(self, "txt_naming"):
            self.txt_naming.textChanged.connect(self.changed.emit)

    def disconnect_signals(self) -> None:
        """Disconnect all default tab signals to prevent memory leaks."""
        self._disconnect_checkboxes()
        self._disconnect_format_settings()

    def _disconnect_checkboxes(self) -> None:
        """Disconnect export selection checkboxes and reset button."""
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_exp_topo.stateChanged.disconnect(self.changed.emit)
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_exp_geol.stateChanged.disconnect(self.changed.emit)
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_exp_struct.stateChanged.disconnect(self.changed.emit)
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_exp_drill.stateChanged.disconnect(self.changed.emit)
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_exp_interp.stateChanged.disconnect(self.changed.emit)
        with contextlib.suppress(TypeError, RuntimeError):
            self.btn_reset_export.clicked.disconnect(self.reset_to_defaults)

    def _disconnect_format_settings(self) -> None:
        """Disconnect format and naming settings signals."""
        if hasattr(self, "combo_format"):
            with contextlib.suppress(TypeError, RuntimeError):
                self.combo_format.currentIndexChanged.disconnect(self.changed.emit)
        if hasattr(self, "txt_naming"):
            with contextlib.suppress(TypeError, RuntimeError):
                self.txt_naming.textChanged.disconnect(self.changed.emit)
