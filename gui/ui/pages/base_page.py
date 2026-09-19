"""Base class for configuration pages."""

from __future__ import annotations

from typing import Any

from qgis.PyQt.QtWidgets import QGroupBox, QVBoxLayout, QWidget


def set_combo_layer(combo: Any, layer: Any) -> None:
    """Set a layer on a map-layer combo without emitting its signals.

    Args:
        combo: A ``QgsMapLayerComboBox`` (or compatible mock).
        layer: The layer to select, or ``None`` to clear.

    """
    combo.blockSignals(True)
    combo.setLayer(layer)
    combo.blockSignals(False)


class BasePage(QWidget):
    """Abstract base class for configuration pages.

    Each page manages a specific set of parameters (e.g., DEM, Section, Geology).
    """

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        """Initialize the page.

        Args:
            title (str): Title for the group box.
            parent (QWidget): Parent widget.

        """
        super().__init__(parent)
        self.title = title
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Main group box
        self.group_box = QGroupBox(self.title)
        self.group_layout = None  # To be set by subclasses

        self.main_layout.addWidget(self.group_box)

        # Add stretch at the bottom to keep widgets at the top
        self.main_layout.addStretch()

    def get_data(self) -> dict[str, Any]:
        """Get the current configuration data from the page.

        Returns:
            dict: Dictionary with parameter names and values.

        """
        raise NotImplementedError("Subclasses must implement get_data()")

    def dump(self) -> dict[str, Any]:
        """Return the page's persistable state as a plain dict.

        Layer values are returned as ``QgsMapLayer`` objects (or ``None``);
        every other value is a primitive (str, bool, int, float).

        Returns:
            dict: Mapping of persistent keys to current values.

        """
        return {}

    def load(self, data: dict[str, Any]) -> None:
        """Apply persistable state to the page's widgets.

        Args:
            data: Mapping of persistent keys to values. Layer values are
                expected as ``QgsMapLayer`` objects (already resolved).

        """
        pass

    def reset(self) -> None:
        """Reset the page's widgets to their default values."""
        pass

    def validate(self) -> tuple[bool, str]:
        """Validate the current configuration.

        Returns:
            tuple[bool, str]: (is_valid, error_message)

        """
        return True, ""

    def connect_signals(self) -> None:
        """Connect internal signals for the page."""
        pass

    def disconnect_signals(self) -> None:
        """Disconnect all signals to prevent memory leaks."""
        pass
