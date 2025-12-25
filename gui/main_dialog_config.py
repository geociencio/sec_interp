from __future__ import annotations

from typing import Any, ClassVar, Optional

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

    # Performance
    MAX_PREVIEW_POINTS = 10000
    ENABLE_LOD = False  # Level of Detail optimization

    # Logging
    VERBOSE_LOGGING = False
    LOG_PERFORMANCE = False


class ValidationMessages:
    """Standard validation error messages."""

    # Required fields
    MISSING_RASTER = "DEM raster layer is required"
    MISSING_SECTION_LINE = "Cross-section line is required"
    MISSING_OUTPUT_PATH = "Output path is required"

    # Invalid inputs
    INVALID_RASTER = "Selected raster layer is not valid"
    INVALID_SECTION_LINE = "Selected section line is not valid"
    INVALID_OUTPUT_PATH = "Output path is not valid or not writable"

    # Geometry errors
    WRONG_GEOMETRY_TYPE = "Layer has incorrect geometry type"
    EMPTY_LAYER = "Layer contains no features"
    INVALID_GEOMETRY = "Layer contains invalid geometries"

    # Field errors
    MISSING_FIELD = "Required field '{}' not found in layer"
    INVALID_FIELD_TYPE = "Field '{}' has incorrect type"

    # Geology specific
    MISSING_OUTCROP_LAYER = "Outcrop layer is required for geological profile"
    MISSING_OUTCROP_FIELD = "Outcrop name field is required"

    # Structure specific
    MISSING_STRUCTURAL_LAYER = "Structural layer is required for structure projection"
    MISSING_DIP_FIELD = "Dip field is required"
    MISSING_STRIKE_FIELD = "Strike field is required"

    # General
    VALIDATION_FAILED = "Input validation failed"
    UNKNOWN_ERROR = "An unknown error occurred"


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
