from __future__ import annotations

from typing import Optional, Union

from qgis.core import QgsVectorLayer

from sec_interp.core.types import FieldType


def validate_numeric_input(
    value: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    field_name: str = "Value",
    allow_empty: bool = False,
) -> tuple[bool, str, Optional[float]]:
    """Validate a numeric input string from a text field.

    Args:
        value: The string value to validate.
        min_val: Optional minimum value allowed.
        max_val: Optional maximum value allowed.
        field_name: Name of the field for error messages.
        allow_empty: Whether to allow an empty string.

    Returns:
        tuple: (is_valid, error_message, float_value)
            - is_valid: True if validation passed.
            - error_message: Error details if validation failed.
            - float_value: The parsed numeric value if valid, else None.
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
    min_val: Optional[int] = None,
    max_val: Optional[int] = None,
    field_name: str = "Value",
    allow_empty: bool = False,
) -> tuple[bool, str, Optional[int]]:
    """Validate an integer input string from a text field.

    Args:
        value: The string value to validate.
        min_val: Optional minimum value allowed.
        max_val: Optional maximum value allowed.
        field_name: Name of the field for error messages.
        allow_empty: Whether to allow an empty string.

    Returns:
        tuple: (is_valid, error_message, int_value)
            - is_valid: True if validation passed.
            - error_message: Error details if validation failed.
            - int_value: The parsed integer value if valid, else None.
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
            - is_valid: True if validation passed.
            - error_message: Error details if validation failed.
    """
    if value < min_angle or value > max_angle:
        return (
            False,
            f"{field_name} must be between {min_angle} and {max_angle} degrees",
        )

    return True, ""


def validate_field_exists(
    layer: QgsVectorLayer, field_name: Optional[str]
) -> tuple[bool, str]:
    """Validate that a specific field exists in a vector layer.

    Args:
        layer: The QGIS vector layer to check.
        field_name: The name of the field to search for.

    Returns:
        tuple: (is_valid, error_message)
            - is_valid: True if validation passed.
            - error_message: Error details if validation failed.
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
    layer: QgsVectorLayer, field_name: str, expected_types: list[FieldType]
) -> tuple[bool, str]:
    """Validate that a field in a layer has one of the expected data types.

    Args:
        layer: The QGIS vector layer containing the field.
        field_name: The name of the field to check.
        expected_types: List of allowed FieldType values.

    Returns:
        tuple: (is_valid, error_message)
            - is_valid: True if validation passed.
            - error_message: Error details if validation failed.
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
            FieldType.INT: "Integer",
            FieldType.DOUBLE: "Double",
            FieldType.STRING: "String",
            FieldType.LONG_LONG: "Long Integer",
            FieldType.DATE: "Date",
            FieldType.DATE_TIME: "DateTime",
        }
        expected_names = [type_names.get(t, str(t)) for t in expected_types]
        actual_name = type_names.get(field.type(), f"Type ID {field.type()}")

        return False, (
            "Invalid data type for field '{field_name}' in layer '{layer.name()}'. "
            f"Found: {actual_name}. Expected one of: {', '.join(expected_names)}. "
            f"Please check your attribute table."
        )

    return True, ""
