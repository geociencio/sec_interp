"""Base exporter module for Sec Interp plugin."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from sec_interp.core.validation import validate_safe_output_path


class BaseExporter(ABC):
    """Abstract base class for all exporters.

    This class defines the interface that all concrete exporters must implement.
    It follows the Template Method pattern, providing common initialization
    and validation logic while delegating format-specific export to subclasses.
    """

    def __init__(self, settings: dict[str, Any]):
        """Initialize the exporter with settings.

        Args:
            settings: Dictionary containing export settings such as:
                - width: Output width in pixels
                - height: Output height in pixels
                - dpi: Dots per inch for resolution
                - background_color: Background color (QColor)
                - legend_renderer: Optional renderer for legend overlay
        """
        self.settings = settings

    @abstractmethod
    def export(self, output_path: Path, data: Any) -> bool:
        """Export data to file.

        This method must be implemented by all concrete exporters.

        Args:
            output_path: Destination file path
            data: Data to export (format depends on exporter type)

        Returns:
            bool: True if export successful, False otherwise
        """
        pass

    def validate_export_path(
        self, output_path: Path, base_dir: Path | None = None
    ) -> tuple[bool, str]:
        """Validate export path for security.

        Uses secure path validation to prevent path traversal attacks.

        Args:
            output_path: Path to validate
            base_dir: Optional base directory to restrict exports to

        Returns:
            tuple: (is_valid, error_message)
        """
        # Get parent directory of the file
        parent_dir = output_path.parent

        # Validate parent directory is safe
        is_valid, error, _ = validate_safe_output_path(
            str(parent_dir), base_dir=base_dir, must_exist=False, create_if_missing=True
        )

        if not is_valid:
            return False, f"Invalid export path: {error}"

        return True, ""

    @abstractmethod
    def get_supported_extensions(self) -> list[str]:
        """Get list of supported file extensions.

        Returns:
            List of supported extensions (e.g., ['.png', '.jpg'])
        """

    def validate_path(self, path: Path) -> bool:
        """Validate that the output path has a supported extension.

        Args:
            path: Path to validate

        Returns:
            True if path has a supported extension, False otherwise
        """
        return path.suffix.lower() in self.get_supported_extensions()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value with optional default.

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)
