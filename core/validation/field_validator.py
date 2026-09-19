"""Validation logic for layer fields and attributes (QGIS-agnostic)."""

from __future__ import annotations

from sec_interp.core.domain import FieldType
from sec_interp.core.validation.layer_metadata import LayerMetadata


def validate_numeric_input(
    value: str,
    min_val: float | None = None,
    max_val: float | None = None,
    field_name: str = "Value",
    allow_empty: bool = False,
) -> tuple[bool, str, float | None]:
    """Validate a numeric input string from a text field.

    Args:
        value: The string value to validate.
        min_val: Optional minimum value allowed.
        max_val: Optional maximum value allowed.
        field_name: Name of the field for error messages.
        allow_empty: Whether to allow an empty string.

    Returns:
        tuple: (is_valid, error_message, float_value)

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
    """Validate an integer input string from a text field.

    Args:
        value: The string value to validate.
        min_val: Optional minimum value allowed.
        max_val: Optional maximum value allowed.
        field_name: Name of the field for error messages.
        allow_empty: Whether to allow an empty string.

    Returns:
        tuple: (is_valid, error_message, int_value)

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


def validate_angle_range(
    value: float, field_name: str, min_angle: float = 0.0, max_angle: float = 360.0
) -> tuple[bool, str]:
    """Validate that an angle value is within the expected range.

    Args:
        value: The angle value to validate.
        field_name: Name of the field for error messages.
        min_angle: Minimum allowed angle (default 0.0).
        max_angle: Maximum allowed angle (default 360.0).

    Returns:
        tuple: (is_valid, error_message)

    """
    if value < min_angle or value > max_angle:
        return (
            False,
            f"{field_name} must be between {min_angle} and {max_angle} degrees",
        )

    return True, ""


def validate_field_exists(metadata: LayerMetadata, field_name: str | None) -> tuple[bool, str]:
    """Validate that a specific field exists in a layer.

    Args:
        metadata: The detached layer metadata.
        field_name: The name of the field to search for.

    Returns:
        tuple: (is_valid, error_message)

    """
    if not metadata or not metadata.is_valid:
        return False, "Layer is not valid"

    if not field_name:
        return False, "Field name is required"

    if metadata.kind != "vector":
        return False, f"Layer '{metadata.name}' is not a vector layer"

    if field_name not in metadata.field_names:
        MAX_FIELDS_TO_SHOW = 5
        return False, (
            f"Field '{field_name}' not found in layer '{metadata.name}'. "
            f"Available fields: {', '.join(metadata.field_names[:MAX_FIELDS_TO_SHOW])}"
            f"{', ...' if len(metadata.field_names) > MAX_FIELDS_TO_SHOW else ''}"
        )

    return True, ""


def validate_field_type(
    metadata: LayerMetadata, field_name: str, expected_types: list[FieldType]
) -> tuple[bool, str]:
    """Validate that a field in a layer has one of the expected data types.

    Args:
        metadata: The detached layer metadata.
        field_name: The name of the field to check.
        expected_types: List of allowed FieldType values.

    Returns:
        tuple: (is_valid, error_message)

    """
    if not metadata or not metadata.is_valid:
        return False, "Layer is not valid"

    if metadata.kind != "vector":
        return False, f"Layer '{metadata.name}' is not a vector layer"

    if field_name not in metadata.field_types:
        return False, f"Field '{field_name}' not found in layer '{metadata.name}'"

    actual = metadata.field_types[field_name]
    if actual not in expected_types:
        type_names = {
            FieldType.INT: "Integer",
            FieldType.DOUBLE: "Double",
            FieldType.STRING: "String",
            FieldType.LONG_LONG: "Long Integer",
            FieldType.DATE: "Date",
            FieldType.DATE_TIME: "DateTime",
        }
        expected_names = [type_names.get(t, str(t)) for t in expected_types]
        actual_name = type_names.get(actual, f"Type ID {actual}")

        return False, (
            f"Invalid data type for field '{field_name}' in layer '{metadata.name}'. "
            f"Found: {actual_name}. Expected one of: {', '.join(expected_names)}. "
            f"Please check your attribute table."
        )

    return True, ""
