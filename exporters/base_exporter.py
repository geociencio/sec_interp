"""Base exporter class definition."""

from __future__ import annotations

"""Base exporter module for Sec Interp plugin."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from qgis.PyQt.QtCore import QCoreApplication

from sec_interp.core.validation import validate_safe_output_path


class BaseExporter(ABC):
    """Abstract base class for all exporters.

    This class defines the interface that all concrete exporters must implement.
    It follows the Template Method pattern, providing common initialization
    and validation logic while delegating format-specific export to subclasses.
    """

    def __init__(self, settings: dict[str, Any]) -> None:
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
    def export(self, output_path: Path, data: Any, layer_name: str | None = None) -> bool:
        """Export data to file.

        This method must be implemented by all concrete exporters.

        Args:
            output_path: Destination file path
            data: Data to export (format depends on exporter type)
            layer_name: Optional conceptual name for the layer (e.g. inside a GeoPackage)

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
        try:
            # Resolve the absolute path to detect traversal
            resolved_path = output_path.resolve()

            if base_dir:
                resolved_base = base_dir.resolve()
                if not str(resolved_path).startswith(str(resolved_base)):
                    return False, QCoreApplication.translate(
                        "BaseExporter",
                        "Path traversal detected: {path} is outside of {base}",
                    ).format(path=output_path, base=base_dir)

            # Get parent directory for existence/permissions validation
            parent_dir = output_path.parent

            # Validate parent directory using existing helper
            is_valid, error, _ = validate_safe_output_path(
                str(parent_dir),
                base_dir=base_dir,
                must_exist=False,
                create_if_missing=True,
            )

            if not is_valid:
                return False, QCoreApplication.translate(
                    "BaseExporter", "Invalid export path: {error}"
                ).format(error=error)

            return True, ""

        except (OSError, ValueError) as e:
            return False, QCoreApplication.translate(
                "BaseExporter", "Path resolution error: {error}"
            ).format(error=str(e))

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
