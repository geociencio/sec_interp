"""Cross-section configuration page."""

from __future__ import annotations

import contextlib
from typing import Any

from qgis.core import QgsMapLayerProxyModel
from qgis.gui import QgsDoubleSpinBox, QgsMapLayerComboBox
from qgis.PyQt.QtCore import QCoreApplication, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
)

from sec_interp.core.validation.project_validators import SECTION_LINE_VERTEX_COUNT
from sec_interp.gui.adapters.geometry import (
    create_distance_area,
    profile_raster_statistics,
    resolve_section_geometry,
)
from sec_interp.gui.adapters.validation_extractor import extract_section_line_metrics
from sec_interp.gui.main_dialog_config import DialogDefaults
from sec_interp.logger_config import get_logger

from .base_page import BasePage, set_combo_layer

logger = get_logger(__name__)


class SectionPage(BasePage):
    """Configuration page for Cross Section settings."""

    dataChanged = pyqtSignal()
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

        # Wired for the future multi-line selector; the first feature is used
        # while ``None`` (no widget yet).
        self.section_feature_id: int | None = None

        self._setup_dem_profile()

    def _setup_dem_profile(self) -> None:
        """Set up the read-only perfil-vs-DEM statistics group."""
        self.dem_stats_group = QGroupBox(self.tr("DEM Profile"))
        layout = QGridLayout(self.dem_stats_group)

        self.min_edit = self._stats_edit("Minimum elevation of the section over the DEM")
        self.max_edit = self._stats_edit("Maximum elevation of the section over the DEM")
        self.mean_edit = self._stats_edit("Mean elevation of the section over the DEM")
        self.samples_edit = self._stats_edit("Number of samples at the DEM resolution")

        layout.addWidget(QLabel(self.tr("Min")), 0, 0)
        layout.addWidget(self.min_edit, 0, 1)
        layout.addWidget(QLabel(self.tr("Max")), 0, 2)
        layout.addWidget(self.max_edit, 0, 3)
        layout.addWidget(QLabel(self.tr("Mean")), 1, 0)
        layout.addWidget(self.mean_edit, 1, 1)
        layout.addWidget(QLabel(self.tr("Samples")), 1, 2)
        layout.addWidget(self.samples_edit, 1, 3)

        count = self.main_layout.count()
        self.main_layout.insertWidget(count - 1, self.dem_stats_group)

    def _stats_edit(self, tooltip: str) -> QLineEdit:
        """Create a read-only line edit for a statistic value."""
        edit = QLineEdit()
        edit.setReadOnly(True)
        edit.setToolTip(self.tr(tooltip))
        return edit

    def set_dem_provider(self, provider: Any) -> None:
        """Set the callable returning ``(raster_layer, band_number)`` for stats.

        Injected by the dialog so the Section page can read the DEM selection
        without importing the DEM page (avoids page-to-page coupling).
        """
        self._dem_provider = provider

    def _dem_selection(self) -> tuple[Any, int]:
        """Return the DEM layer and band from the injected provider."""
        provider = getattr(self, "_dem_provider", None)
        if not callable(provider):
            return None, 1
        try:
            raster, band = provider()
        except (TypeError, ValueError):
            return None, 1
        return raster, band if isinstance(band, int) and band >= 1 else 1

    def update_dem_stats(self) -> None:
        """Refresh the read-only perfil-vs-DEM statistics."""
        raster, band = self._dem_selection()
        line = self.line_combo.currentLayer()
        if not raster or not raster.isValid() or not line:
            self._clear_dem_stats()
            return

        line_geom = resolve_section_geometry(line, self.section_feature_id)
        if line_geom is None:
            self._clear_dem_stats()
            return

        try:
            stats = profile_raster_statistics(
                line_geom, raster, band, create_distance_area(line.crs())
            )
        except (AttributeError, TypeError, ValueError, RuntimeError):
            logger.warning("Could not compute profile-vs-DEM statistics", exc_info=True)
            stats = None

        if stats is None:
            self._clear_dem_stats()
            return

        self.min_edit.setText(f"{stats.minimum:.2f}")
        self.max_edit.setText(f"{stats.maximum:.2f}")
        self.mean_edit.setText(f"{stats.mean:.2f}")
        self.samples_edit.setText(f"{stats.count} @ {stats.resolution:.2f}")

    def _clear_dem_stats(self) -> None:
        """Blank the statistics fields (no raster, line or samples)."""
        for edit in (self.min_edit, self.max_edit, self.mean_edit, self.samples_edit):
            edit.setText("")

    def get_data(self) -> dict[str, Any]:
        """Get section configuration."""
        return {
            "crossline_layer": self.line_combo.currentLayer(),
            "buffer_distance": self.buffer_spin.value(),
            "section_feature_id": self.section_feature_id,
        }

    def dump(self) -> dict[str, Any]:
        """Return the persistable section state."""
        return {
            "section_layer": self.line_combo.currentLayer(),
            "buffer_dist": self.buffer_spin.value(),
            "section_feature_id": self.section_feature_id,
        }

    def load(self, data: dict[str, Any]) -> None:
        """Apply persisted section state."""
        if "section_layer" in data and data["section_layer"] is not None:
            set_combo_layer(self.line_combo, data["section_layer"])
        buffer_dist = data.get("buffer_dist")
        if buffer_dist is not None:
            self.buffer_spin.setValue(float(buffer_dist))
        if "section_feature_id" in data:
            self.section_feature_id = data.get("section_feature_id")

    def reset(self) -> None:
        """Reset section inputs to defaults."""
        self.line_combo.setLayer(None)
        self.buffer_spin.setValue(float(DialogDefaults.BUFFER_DISTANCE))
        self.section_feature_id = None

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

        vertex_count, length = extract_section_line_metrics(layer, self.section_feature_id)
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

    def connect_signals(self) -> None:
        """Connect internal signals for the section page."""
        self.line_combo.layerChanged.connect(self.update_dem_stats)

    def disconnect_signals(self) -> None:
        """Disconnect all signals to prevent memory leaks."""
        for signal, slot in (
            (self.line_combo.layerChanged, None),
            (self.line_combo.layerChanged, self.update_dem_stats),
        ):
            with contextlib.suppress(TypeError, RuntimeError):
                if slot is None:
                    signal.disconnect()
                else:
                    signal.disconnect(slot)
        with contextlib.suppress(TypeError, RuntimeError):
            self.dataChanged.disconnect()
