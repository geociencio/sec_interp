# -*- coding: utf-8 -*-
"""
Base exporter module for Sec Interp plugin.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pathlib import Path


class BaseExporter(ABC):
    """Abstract base class for all exporters.

    This class defines the interface that all concrete exporters must implement.
    It follows the Template Method pattern, providing common initialization
    and validation logic while delegating format-specific export to subclasses.
    """

    def __init__(self, settings: Dict[str, Any]):
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
        """Export data to the specified file.

        This method must be implemented by all concrete exporters.

        Args:
            output_path: Destination file path
            data: Data to export (type varies by exporter)

        Returns:
            True if export was successful, False otherwise
        """
        pass

    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions.

        Returns:
            List of supported extensions (e.g., ['.png', '.jpg'])
        """
        pass

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
