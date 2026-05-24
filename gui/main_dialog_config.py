"""Configuration and defaults for the SecInterp dialogs."""

from __future__ import annotations

from typing import Any, ClassVar

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QColor


class DialogDefaults:
    """Default values for dialog inputs and settings."""

    # Scale and exaggeration
    SCALE = "50000"
    VERTICAL_EXAGGERATION = "1.0"
    DIP_SCALE = "4"
    DIP_SCALE_FACTOR = "4"

    # Buffer and sampling
    BUFFER_DISTANCE = 100  # meters
    SAMPLING_INTERVAL = 10  # meters

    # Export settings
    DPI = 300
    PREVIEW_WIDTH = 800
    PREVIEW_HEIGHT = 600
    EXPORT_QUALITY = 95  # for JPEG

    # Colors
    BACKGROUND_COLOR = QColor(255, 255, 255)  # White
    GRID_COLOR = QColor(200, 200, 200)  # Light gray

    # Raster band
    DEFAULT_BAND = 1

    # File extensions
    SUPPORTED_IMAGE_FORMATS: ClassVar[list[str]] = [".png", ".jpg", ".jpeg"]
    SUPPORTED_VECTOR_FORMATS: ClassVar[list[str]] = [".shp"]
    SUPPORTED_DOCUMENT_FORMATS: ClassVar[list[str]] = [".pdf", ".svg"]


class DialogConfig:
    """Configuration for dialog behavior and features."""

    # Caching
    ENABLE_CACHE = True
    CACHE_EXPIRY_SECONDS = 3600  # 1 hour

    # Performance metrics
    ENABLE_PERFORMANCE_METRICS: bool = True
    SHOW_METRICS_IN_RESULTS: bool = True
    LOG_DETAILED_METRICS: bool = False

    # UI behavior
    AUTO_SAVE_SETTINGS = True
    SHOW_HELP_ON_START = False
    ENABLE_TOOLTIPS = True

    # Validation
    STRICT_VALIDATION = True
    ALLOW_EMPTY_GEOLOGY = True
    ALLOW_EMPTY_STRUCTURES = True

    # Preview
    AUTO_REFRESH_PREVIEW = False
    SHOW_LEGEND = True
    ENABLE_ZOOM = True
    ZOOM_DEBOUNCE_MS = 200  # Milliseconds

    # Performance
    MAX_PREVIEW_POINTS = 10000
    ENABLE_LOD = False  # Level of Detail optimization

    # Logging
    VERBOSE_LOGGING = False
    LOG_PERFORMANCE = False


class ValidationMessages:
    """Standard validation error messages."""

    @staticmethod
    def missing_raster() -> str:
        """Return translated 'DEM raster layer is required' message."""
        return QCoreApplication.translate(
            "ValidationMessages", "DEM raster layer is required"
        )

    @staticmethod
    def missing_section_line() -> str:
        """Return translated 'Cross-section line is required' message."""
        return QCoreApplication.translate(
            "ValidationMessages", "Cross-section line is required"
        )

    @staticmethod
    def missing_output_path() -> str:
        """Return translated 'Output path is required' message."""
        return QCoreApplication.translate(
            "ValidationMessages", "Output path is required"
        )

    @staticmethod
    def invalid_raster() -> str:
        """Return translated 'Selected raster layer is not valid' message."""
        return QCoreApplication.translate(
            "ValidationMessages", "Selected raster layer is not valid"
        )

    @staticmethod
    def invalid_section_line() -> str:
        """Return translated 'Selected section line is not valid' message."""
        return QCoreApplication.translate(
            "ValidationMessages", "Selected section line is not valid"
        )

    @staticmethod
    def invalid_output_path() -> str:
        """Return translated 'Output path is not valid or not writable' message."""
        return QCoreApplication.translate(
            "ValidationMessages", "Output path is not valid or not writable"
        )

    @staticmethod
    def wrong_geometry_type() -> str:
        """Return translated 'Layer has incorrect geometry type' message."""
        return QCoreApplication.translate(
            "ValidationMessages", "Layer has incorrect geometry type"
        )

    @staticmethod
    def empty_layer() -> str:
        """Return translated 'Layer contains no features' message."""
        return QCoreApplication.translate(
            "ValidationMessages", "Layer contains no features"
        )

    @staticmethod
    def invalid_geometry() -> str:
        """Return translated 'Layer contains invalid geometries' message."""
        return QCoreApplication.translate(
            "ValidationMessages", "Layer contains invalid geometries"
        )

    @staticmethod
    def missing_field(field: str) -> str:
        """Return translated 'Required field not found' message."""
        return QCoreApplication.translate(
            "ValidationMessages", "Required field '{}' not found in layer"
        ).format(field)

    @staticmethod
    def invalid_field_type(field: str) -> str:
        """Return translated 'Field type incorrect' message."""
        return QCoreApplication.translate(
            "ValidationMessages", "Field '{}' has incorrect type"
        ).format(field)

    @staticmethod
    def missing_outcrop_layer() -> str:
        """Return translated 'Outcrop layer required' message."""
        return QCoreApplication.translate(
            "ValidationMessages", "Outcrop layer is required for geological profile"
        )

    @staticmethod
    def missing_outcrop_field() -> str:
        """Return translated 'Outcrop name field required' message."""
        return QCoreApplication.translate(
            "ValidationMessages", "Outcrop name field is required"
        )

    @staticmethod
    def missing_structural_layer() -> str:
        """Return translated 'Structural layer required' message."""
        return QCoreApplication.translate(
            "ValidationMessages",
            "Structural layer is required for structure projection",
        )

    @staticmethod
    def missing_dip_field() -> str:
        """Return translated 'Dip field required' message."""
        return QCoreApplication.translate("ValidationMessages", "Dip field is required")

    @staticmethod
    def missing_strike_field() -> str:
        """Return translated 'Strike field required' message."""
        return QCoreApplication.translate(
            "ValidationMessages", "Strike field is required"
        )

    @staticmethod
    def validation_failed() -> str:
        """Return translated 'Input validation failed' message."""
        return QCoreApplication.translate(
            "ValidationMessages", "Input validation failed"
        )

    @staticmethod
    def unknown_error() -> str:
        """Return translated 'Unknown error' message."""
        return QCoreApplication.translate(
            "ValidationMessages", "An unknown error occurred"
        )


class UIConstants:
    """UI-related constants."""

    # Widget sizes
    MIN_PREVIEW_WIDTH = 400
    MIN_PREVIEW_HEIGHT = 300
    MAX_PREVIEW_WIDTH = 1920
    MAX_PREVIEW_HEIGHT = 1080

    # Icon names (QGIS theme icons)
    ICON_HELP = "mActionHelpContents.svg"
    ICON_REFRESH = "mActionRefresh.svg"
    ICON_EXPORT = "mActionFileSave.svg"
    ICON_CLEAR = "mActionDeleteSelected.svg"

    # Status indicators
    STATUS_OK = "✓"
    STATUS_ERROR = "✗"
    STATUS_WARNING = "⚠"

    # Required field indicator
    REQUIRED_INDICATOR = "*"
    REQUIRED_COLOR = QColor(255, 0, 0)  # Red


# Type aliases for better code readability
LayerSelection = Any  # QgsVectorLayer or None
RasterSelection = Any  # QgsRasterLayer or None
ValidationResult = tuple[bool, str]  # (is_valid, error_message)
DialogValues = dict[str, Any]  # Dictionary of dialog input values
ExportSettings = dict[str, Any]  # Dictionary of export configuration
