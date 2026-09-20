"""Advanced (3D / restricted features) settings tab."""

from __future__ import annotations

import contextlib
from typing import Any

from qgis.PyQt.QtCore import QCoreApplication, pyqtSignal
from qgis.PyQt.QtWidgets import QCheckBox, QLabel, QVBoxLayout, QWidget

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)


class AdvancedTab(QWidget):
    """Advanced feature toggles (3D interpretation and drillhole export)."""

    changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the advanced tab."""
        super().__init__(parent)
        self._setup_ui()

    def tr(self, message: str) -> str:
        """Translate a message for this tab."""
        return QCoreApplication.translate("AdvancedTab", message)  # type: ignore[no-any-return]

    def _setup_ui(self) -> None:
        """Build the advanced tab layout."""
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(self.tr("<b>Advanced Features</b>")))

        self.chk_enable_3d = QCheckBox(self.tr("Enable 3D Interpretation Export"))
        self.chk_enable_3d.setToolTip(
            self.tr("Enables the generation of 3D Shapefiles (.shp) during export.")
        )
        layout.addWidget(self.chk_enable_3d)

        layout.addWidget(QLabel(self.tr("<br><b>Drillhole 3D Export Options</b>")))
        self.chk_3d_traces = QCheckBox(self.tr("Export 3D Traces"))
        self.chk_3d_intervals = QCheckBox(self.tr("Export 3D Intervals"))
        self.chk_3d_original = QCheckBox(self.tr("Use Original Coordinates (Real 3D)"))
        self.chk_3d_projected = QCheckBox(self.tr("Use Projected Coordinates (Section Plane)"))

        layout.addWidget(self.chk_3d_traces)
        layout.addWidget(self.chk_3d_intervals)
        layout.addWidget(self.chk_3d_original)
        layout.addWidget(self.chk_3d_projected)

        layout.addStretch()

    def get_data(self) -> dict[str, Any]:
        """Return advanced 3D settings."""
        return {
            "enable_3d": (self.chk_enable_3d.isChecked() if self.chk_enable_3d else False),
            "drill_3d_traces": (
                self.chk_3d_traces.isChecked() if hasattr(self, "chk_3d_traces") else True
            ),
            "drill_3d_intervals": (
                self.chk_3d_intervals.isChecked() if hasattr(self, "chk_3d_intervals") else True
            ),
            "drill_3d_original": (
                self.chk_3d_original.isChecked() if hasattr(self, "chk_3d_original") else True
            ),
            "drill_3d_projected": (
                self.chk_3d_projected.isChecked() if hasattr(self, "chk_3d_projected") else False
            ),
        }

    def reset_to_defaults(self) -> None:
        """Reset advanced toggles to their defaults."""
        defaults = {
            "chk_enable_3d": True,
            "chk_3d_traces": True,
            "chk_3d_intervals": True,
            "chk_3d_original": True,
            "chk_3d_projected": False,
        }
        for attr, value in defaults.items():
            widget = getattr(self, attr, None)
            if widget is not None:
                widget.setChecked(value)

    def connect_signals(self) -> None:
        """Connect advanced tab signals."""
        self.chk_enable_3d.stateChanged.connect(self.changed.emit)
        self.chk_3d_traces.stateChanged.connect(self.changed.emit)
        self.chk_3d_intervals.stateChanged.connect(self.changed.emit)
        self.chk_3d_original.stateChanged.connect(self.changed.emit)
        self.chk_3d_projected.stateChanged.connect(self.changed.emit)

    def disconnect_signals(self) -> None:
        """Disconnect all advanced tab signals to prevent memory leaks."""
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_enable_3d.stateChanged.disconnect(self.changed.emit)
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_3d_traces.stateChanged.disconnect(self.changed.emit)
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_3d_intervals.stateChanged.disconnect(self.changed.emit)
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_3d_original.stateChanged.disconnect(self.changed.emit)
        with contextlib.suppress(TypeError, RuntimeError):
            self.chk_3d_projected.stateChanged.disconnect(self.changed.emit)
