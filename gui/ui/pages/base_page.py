"""Base class for configuration pages."""

from qgis.PyQt.QtWidgets import QGroupBox, QVBoxLayout, QWidget


class BasePage(QWidget):
    """Abstract base class for configuration pages.

    Each page manages a specific set of parameters (e.g., DEM, Section, Geology).
    """

    def __init__(self, title: str, parent=None):
        """Initialize the page.

        Args:
            title (str): Title for the group box.
            parent (QWidget): Parent widget.
        """
        super().__init__(parent)
        self.title = title
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Main group box
        self.group_box = QGroupBox(self.title)
        self.group_layout = None  # To be set by subclasses

        self.main_layout.addWidget(self.group_box)

        # Add stretch at the bottom to keep widgets at the top
        self.main_layout.addStretch()

    def get_data(self) -> dict:
        """Get the current configuration data from the page.

        Returns:
            dict: Dictionary with parameter names and values.
        """
        raise NotImplementedError("Subclasses must implement get_data()")

    def validate(self) -> tuple[bool, str]:
        """Validate the current configuration.

        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        return True, ""
