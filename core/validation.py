"""Validation utilities for the SecInterp QGIS plugin.

This module provides reusable validation functions for user inputs,
layer selections, and data integrity checks.
"""

from pathlib import Path
from typing import Optional

from qgis.core import (
    QgsMapLayer,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QVariant


def validate_numeric_input(
    value: str,
    min_val: float | None = None,
    max_val: float | None = None,
    field_name: str = "Value",
    allow_empty: bool = False,
) -> tuple[bool, str, float | None]:
    """Validate numeric input from text field.

    Args:
        value: String value to validate
        min_val: Optional minimum allowed value
        max_val: Optional maximum allowed value
        field_name: Name of the field for error messages
        allow_empty: Whether empty strings are allowed

    Returns:
        Tuple of (is_valid, error_message, converted_value)
    """
    if not value or value.strip() == "":
        if allow_empty:
            return True, "", None
        return False, f"{field_name} is required", None

    try:
        num_value = float(value)
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid number", None

    if min_val is not None and num_value < min_val:
        return False, f"{field_name} must be at least {min_val}", None

    if max_val is not None and num_value > max_val:
        return False, f"{field_name} must be at most {max_val}", None

    return True, "", num_value


def validate_integer_input(
    value: str,
    min_val: int | None = None,
    max_val: int | None = None,
    field_name: str = "Value",
    allow_empty: bool = False,
) -> tuple[bool, str, int | None]:
    """Validate integer input from text field.

    Args:
        value: String value to validate
        min_val: Optional minimum allowed value
        max_val: Optional maximum allowed value
        field_name: Name of the field for error messages
        allow_empty: Whether empty strings are allowed

    Returns:
        Tuple of (is_valid, error_message, converted_value)
    """
    if not value or value.strip() == "":
        if allow_empty:
            return True, "", None
        return False, f"{field_name} is required", None

    try:
        int_value = int(value)
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid integer", None

    if min_val is not None and int_value < min_val:
        return False, f"{field_name} must be at least {min_val}", None

    if max_val is not None and int_value > max_val:
        return False, f"{field_name} must be at most {max_val}", None

    return True, "", int_value


def validate_layer_exists(
    layer_name: str | None,
) -> tuple[bool, str, QgsMapLayer | None]:
    """Validate that a layer exists in the project.

    Args:
        layer_name: Name of the layer to validate

    Returns:
        Tuple of (is_valid, error_message, layer_object)
    """
    if not layer_name:
        return False, "Layer name is required", None

    from qgis.core import QgsProject

    layers = QgsProject.instance().mapLayersByName(layer_name)

    if not layers:
        return False, f"Layer '{layer_name}' not found in project", None

    layer = layers[0]

    if not layer.isValid():
        return False, f"Layer '{layer_name}' is not valid", None

    return True, "", layer


def validate_layer_has_features(layer: QgsVectorLayer) -> tuple[bool, str]:
    """Validate that a vector layer has at least one feature.

    Args:
        layer: Vector layer to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not layer:
        return False, "Layer is None"

    if not isinstance(layer, QgsVectorLayer):
        return False, "Layer is not a vector layer"

    if layer.featureCount() == 0:
        return False, f"Layer '{layer.name()}' has no features"

    return True, ""


def validate_layer_geometry(
    layer: QgsVectorLayer, expected_type: QgsWkbTypes.GeometryType
) -> tuple[bool, str]:
    """Validate that a vector layer has the expected geometry type.

    Args:
        layer: Vector layer to validate
        expected_type: Expected geometry type (e.g., QgsWkbTypes.LineGeometry)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not layer:
        return False, "Layer is None"

    if not isinstance(layer, QgsVectorLayer):
        return False, "Layer is not a vector layer"

    actual_type = QgsWkbTypes.geometryType(layer.wkbType())

    if actual_type != expected_type:
        type_names = {
            QgsWkbTypes.PointGeometry: "Point",
            QgsWkbTypes.LineGeometry: "Line",
            QgsWkbTypes.PolygonGeometry: "Polygon",
            QgsWkbTypes.UnknownGeometry: "Unknown",
            QgsWkbTypes.NullGeometry: "Null",
        }
        expected_name = type_names.get(expected_type, f"Type {expected_type}")
        actual_name = type_names.get(actual_type, f"Type {actual_type}")

        return False, (
            f"Geometry type mismatch for layer '{layer.name()}': "
            f"Found {actual_name}, but expected {expected_name}. "
            f"Please select a valid {expected_name.lower()} layer."
        )

    return True, ""


def validate_field_exists(
    layer: QgsVectorLayer, field_name: str | None
) -> tuple[bool, str]:
    """Validate that a field exists in a vector layer.

    Args:
        layer: Vector layer to check
        field_name: Name of the field to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not layer:
        return False, "Layer is None"

    if not field_name:
        return False, "Field name is required"

    if not isinstance(layer, QgsVectorLayer):
        return (
            False,
            f"Layer '{layer.name() if hasattr(layer, 'name') else 'Unknown'}' is not a vector layer",
        )

    field_names = [field.name() for field in layer.fields()]

    if field_name not in field_names:
        return False, (
            f"Field '{field_name}' not found in layer '{layer.name()}'. "
            f"Available fields: {', '.join(field_names[:5])}"
            f"{', ...' if len(field_names) > 5 else ''}"
        )

    return True, ""


def validate_field_type(
    layer: QgsVectorLayer, field_name: str, expected_types: list[QVariant.Type]
) -> tuple[bool, str]:
    """Validate that a field has one of the expected data types.

    Args:
        layer: Vector layer containing the field
        field_name: Name of the field to validate
        expected_types: List of acceptable QVariant types

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not layer:
        return False, "Layer is None"

    if not isinstance(layer, QgsVectorLayer):
        return (
            False,
            f"Layer '{layer.name() if hasattr(layer, 'name') else 'Unknown'}' is not a vector layer",
        )

    field = layer.fields().field(field_name)

    if not field:
        return False, f"Field '{field_name}' not found in layer '{layer.name()}'"

    if field.type() not in expected_types:
        type_names = {
            QVariant.Int: "Integer",
            QVariant.Double: "Double",
            QVariant.String: "String",
            QVariant.LongLong: "Long Integer",
            QVariant.Date: "Date",
            QVariant.DateTime: "DateTime",
        }
        expected_names = [type_names.get(t, str(t)) for t in expected_types]
        actual_name = type_names.get(field.type(), f"Type ID {field.type()}")

        return False, (
            "Invalid data type for field '{field_name}' in layer '{layer.name()}'. "
            f"Found: {actual_name}. Expected one of: {', '.join(expected_names)}. "
            f"Please check your attribute table."
        )

    return True, ""


def validate_raster_band(layer: QgsRasterLayer, band_number: int) -> tuple[bool, str]:
    """Validate that a raster band number is valid for the layer.

    Args:
        layer: Raster layer to validate
        band_number: Band number to check (1-indexed)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not layer:
        return False, "Layer is None"

    if not isinstance(layer, QgsRasterLayer):
        return False, "Layer is not a raster layer"

    band_count = layer.bandCount()

    if band_number < 1 or band_number > band_count:
        return False, (
            f"Band number {band_number} is invalid. "
            f"Layer '{layer.name()}' has {band_count} band(s)"
        )

    return True, ""


def validate_safe_output_path(
    path: str,
    base_dir: Path | None = None,
    must_exist: bool = False,
    create_if_missing: bool = False,
) -> tuple[bool, str, Path | None]:
    r"""Validate output path with path traversal protection.

    This function provides robust validation against path traversal attacks
    by checking for suspicious patterns, normalizing paths, and optionally
    restricting to a base directory.

    Args:
        path: Path string to validate
        base_dir: Optional base directory to restrict paths to (for security)
        must_exist: If True, path must already exist
        create_if_missing: If True, create directory if it doesn't exist

    Returns:
        Tuple of (is_valid, error_message, resolved_Path_object)

    Security Features:
        - Detects path traversal patterns (../, ..\\)
        - Resolves symlinks to canonical paths
        - Validates against base directory if provided
        - Rejects null bytes and suspicious characters
        - Normalizes path separators

    Example:
        >>> is_valid, error, safe_path = validate_safe_output_path(
        ...     "/home/user/output",
        ...     base_dir=Path("/home/user"),
        ...     create_if_missing=True,
        ... )
    """
    if not path or path.strip() == "":
        return False, "Output path is required", None

    # Security: Check for null bytes (common attack vector)
    if "\0" in path:
        return False, "Path contains invalid null bytes", None

    try:
        path_obj = Path(path)
    except (TypeError, ValueError) as e:
        return False, f"Invalid path: {e!s}", None

    # Security: Check for path traversal patterns in components
    if ".." in path_obj.parts:
        return False, "Path contains directory traversal sequences (..)", None

    # Security: Resolve to canonical absolute path (follows symlinks)
    try:
        # strict=False allows non-existent paths to be resolved
        resolved_path = path_obj.resolve(strict=False)
    except (OSError, RuntimeError) as e:
        return False, f"Cannot resolve path: {e!s}", None

    # Security: If base_dir provided, ensure path is within it
    if base_dir:
        try:
            base_resolved = base_dir.resolve(strict=False)
            # This will raise ValueError if resolved_path is not relative to base
            resolved_path.relative_to(base_resolved)
        except ValueError:
            return False, f"Path escapes base directory: {base_dir}", None
        except (OSError, RuntimeError) as e:
            return False, f"Cannot validate base directory: {e!s}", None

    # Check existence requirements
    if must_exist and not resolved_path.exists():
        return False, f"Path does not exist: {path}", None

    # Create directory if requested
    if create_if_missing and not resolved_path.exists():
        try:
            resolved_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            return False, f"Cannot create directory: {e!s}", None

    # If path exists, validate it's a directory
    if resolved_path.exists():
        if not resolved_path.is_dir():
            return False, f"Path is not a directory: {path}", None

        # Check if writable (try to create a temporary file)
        try:
            test_file = resolved_path / ".write_test"
            test_file.touch()
            test_file.unlink()
        except OSError:
            return False, f"Directory is not writable: {path}", None

    return True, "", resolved_path


def validate_output_path(path: str) -> tuple[bool, str, Path | None]:
    """Validate that an output path is valid and writable.

    This is a convenience wrapper around validate_safe_output_path()
    for backward compatibility.

    Args:
        path: Path string to validate

    Returns:
        Tuple of (is_valid, error_message, Path_object)

    Note:
        For new code, prefer using validate_safe_output_path() directly
        as it provides more security options.
    """
    return validate_safe_output_path(path, must_exist=True)


def validate_angle_range(
    value: float, field_name: str, min_angle: float = 0.0, max_angle: float = 360.0
) -> tuple[bool, str]:
    """Validate that an angle value is within the expected range.

    Args:
        value: Angle value to validate
        field_name: Name of the field for error messages
        min_angle: Minimum allowed angle (default 0)
        max_angle: Maximum allowed angle (default 360)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if value < min_angle or value > max_angle:
        return (
            False,
            f"{field_name} must be between {min_angle} and {max_angle} degrees",
        )

    return True, ""


def validate_crs_compatibility(layers: list[QgsMapLayer]) -> tuple[bool, str]:
    """Validate that all layers have compatible CRS.

    Checks if all provided layers use the same Coordinate Reference System.
    Returns a warning if CRS mismatch is detected (QGIS will reproject on-the-fly).

    Args:
        layers: List of QgsMapLayer to check

    Returns:
        Tuple of (is_compatible, warning_message)
        - is_compatible: False if CRS mismatch detected
        - warning_message: Details about incompatible layers
    """
    if not layers:
        return True, ""

    # Get first non-None layer CRS as reference
    reference_crs = None
    reference_layer = None
    for layer in layers:
        if layer and layer.isValid():
            reference_crs = layer.crs()
            reference_layer = layer
            break

    if not reference_crs:
        return True, ""

    # Check all other layers against reference
    incompatible = []
    for layer in layers:
        if layer and layer.isValid() and layer.crs() != reference_crs:
            incompatible.append(f"  - {layer.name()}: {layer.crs().authid()}")

    if incompatible:
        warning = (
            f"⚠ CRS mismatch detected!\n\n"
            f"Reference CRS: {reference_crs.authid()} ({reference_layer.name()})\n"
            f"Incompatible layers:\n" + "\n".join(incompatible) + "\n\n"
            "QGIS will reproject on-the-fly, but this may affect accuracy.\n"
            "Consider reprojecting all layers to the same CRS for best results."
        )
        return False, warning

    return True, ""


def validate_reasonable_ranges(values: dict) -> list[str]:
    """Check for unreasonable parameter values.

    Validates that numeric parameters are within reasonable ranges
    and warns about extreme values that may cause issues.

    Args:
        values: Dictionary of parameter values from dialog

    Returns:
        List of warning messages (empty if all values are reasonable)
    """
    warnings = []

    # Vertical exaggeration
    try:
        vert_exag = float(values.get("vert_exag", 1.0))
        if vert_exag > 10:
            warnings.append(
                f"⚠ Vertical exaggeration ({vert_exag}) is very high. "
                f"Values > 10 may distort the profile significantly."
            )
        elif vert_exag < 0.1:
            warnings.append(
                f"⚠ Vertical exaggeration ({vert_exag}) is very low. "
                f"Profile may appear flattened."
            )
        elif vert_exag <= 0:
            warnings.append(f"❌ Vertical exaggeration ({vert_exag}) must be positive.")
    except (ValueError, TypeError):
        pass  # Will be caught by numeric validation

    # Buffer distance
    try:
        buffer = float(values.get("buffer", 0))
        if buffer > 5000:
            warnings.append(
                f"⚠ Buffer distance ({buffer}m) is very large. "
                f"This may include distant structures not relevant to the section."
            )
        elif buffer < 0:
            warnings.append(f"❌ Buffer distance ({buffer}m) cannot be negative.")
    except (ValueError, TypeError):
        pass

    # Dip scale
    try:
        dip_scale = float(values.get("dip_scale", 1.0))
        if dip_scale > 5:
            warnings.append(
                f"⚠ Dip scale ({dip_scale}) is very high. "
                f"Dip symbols may overlap and obscure the profile."
            )
        elif dip_scale <= 0:
            warnings.append(f"❌ Dip scale ({dip_scale}) must be positive.")
    except (ValueError, TypeError):
        pass

    return warnings


def validate_and_get_layers(values: dict) -> tuple[bool, str, dict | None]:
    """Retrieve and validate layers from project based on input values.

    Args:
        values: Dictionary containing layer names from dialog

    Returns:
        Tuple of (is_valid, error_message, updated_values)
        updated_values contains the original values plus layer objects.
    """
    from qgis.core import QgsProject

    # Get layers from the values dictionary
    # Values might be layer objects (from QgsMapLayerComboBox) or names (legacy)

    # Raster Layer
    val = values.get("raster_layer")
    if isinstance(val, QgsMapLayer):
        raster_layer = val
        selected_raster_name = val.name()
    elif isinstance(val, str) and val and val != "Select a raster layer":
        layers = QgsProject.instance().mapLayersByName(val)
        raster_layer = layers[0] if layers else None
        selected_raster_name = val
    else:
        raster_layer = None
        selected_raster_name = "None"

    # Crossline Layer
    val = values.get("crossline_layer")
    if isinstance(val, QgsMapLayer):
        line_layer = val
        selected_line_name = val.name()
    elif isinstance(val, str) and val and val != "Select a crossline layer":
        layers = QgsProject.instance().mapLayersByName(val)
        line_layer = layers[0] if layers else None
        selected_line_name = val
    else:
        line_layer = None
        selected_line_name = "None"

    # Outcrop Layer
    val = values.get("outcrop_layer")
    if isinstance(val, QgsMapLayer):
        outcrop_layer = val
        selected_outcrop_name = val.name()
    elif isinstance(val, str) and val:
        layers = QgsProject.instance().mapLayersByName(val)
        outcrop_layer = layers[0] if layers else None
        selected_outcrop_name = val
    else:
        outcrop_layer = None
        selected_outcrop_name = "None"

    # Structural Layer
    val = values.get("structural_layer")
    if isinstance(val, QgsMapLayer):
        structural_layer = val
        selected_structural_name = val.name()
    elif isinstance(val, str) and val:
        layers = QgsProject.instance().mapLayersByName(val)
        structural_layer = layers[0] if layers else None
        selected_structural_name = val
    else:
        structural_layer = None
        selected_structural_name = "None"

    # Validate required layers
    if not raster_layer or not line_layer:
        return False, "Please select a raster and a line layer.", None

    if not raster_layer.isValid():
        return False, f"Raster layer '{selected_raster_name}' is not valid.", None

    if not line_layer.isValid():
        return False, f"Line layer '{selected_line_name}' is not valid.", None

    # Validate geometry types
    is_valid, msg = validate_layer_geometry(line_layer, QgsWkbTypes.LineGeometry)
    if not is_valid:
        # Also accept MultiLineString
        is_valid_multi, _msg_multi = validate_layer_geometry(
            line_layer, QgsWkbTypes.MultiLineString
        )
        if not is_valid_multi:
            # Try checking generic Line/MultiLine types if exact match failed
            if (
                QgsWkbTypes.geometryType(line_layer.wkbType())
                != QgsWkbTypes.LineGeometry
            ):
                return False, f"Cross-section layer must be a line layer. {msg}", None

    # Validate optional layers if they exist
    if outcrop_layer:
        if not outcrop_layer.isValid():
            return False, f"Outcrop layer '{selected_outcrop_name}' is not valid.", None

        # Validate outcrop name field
        outcrop_field = values.get("outcrop_name_field")
        if outcrop_field:
            is_valid, msg = validate_field_exists(outcrop_layer, outcrop_field)
            if not is_valid:
                return False, msg, None

    if structural_layer:
        if not structural_layer.isValid():
            return (
                False,
                f"Structural layer '{selected_structural_name}' is not valid.",
                None,
            )

        # Validate structural geometry (should be points)
        if (
            QgsWkbTypes.geometryType(structural_layer.wkbType())
            != QgsWkbTypes.PointGeometry
        ):
            return False, "Structural layer must be a point layer.", None

        # Validate structural fields
        dip_field = values.get("dip_field")
        strike_field = values.get("strike_field")

        if dip_field:
            is_valid, msg = validate_field_exists(structural_layer, dip_field)
            if not is_valid:
                return False, msg, None
            # Validate dip is numeric
            is_valid, msg = validate_field_type(
                structural_layer,
                dip_field,
                [QVariant.Int, QVariant.Double, QVariant.LongLong],
            )
            if not is_valid:
                return False, f"Dip field error: {msg}", None

        if strike_field:
            is_valid, msg = validate_field_exists(structural_layer, strike_field)
            if not is_valid:
                return False, msg, None
            # Validate strike is numeric
            is_valid, msg = validate_field_type(
                structural_layer,
                strike_field,
                [QVariant.Int, QVariant.Double, QVariant.LongLong],
            )
            if not is_valid:
                return False, f"Strike field error: {msg}", None

    # Check CRS compatibility (warning only, usually handled by QGIS on-the-fly but good to know)
    if line_layer.crs() != raster_layer.crs():
        # We don't stop execution, but we could log a warning or return a message if the UI supported warnings
        pass

    # Add layer objects to values
    updated_values = values.copy()
    updated_values["raster_layer_obj"] = raster_layer
    updated_values["line_layer_obj"] = line_layer
    updated_values["outcrop_layer_obj"] = outcrop_layer
    updated_values["structural_layer_obj"] = structural_layer

    return True, "", updated_values
