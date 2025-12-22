"""Field and input validation utilities."""
from qgis.core import QgsVectorLayer
# QVariant is a Qt data type required for QGIS field type validation
# It's not a UI component - it's used to represent generic field values
from qgis.PyQt.QtCore import QVariant  # type: ignore[import]

def validate_numeric_input(
    value: str,
    min_val: float | None = None,
    max_val: float | None = None,
    field_name: str = "Value",
    allow_empty: bool = False,
) -> tuple[bool, str, float | None]:
    """Validate numeric input from text field."""
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
    """Validate integer input from text field."""
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
    """Validate that an angle value is within the expected range."""
    if value < min_angle or value > max_angle:
        return (
            False,
            f"{field_name} must be between {min_angle} and {max_angle} degrees",
        )

    return True, ""


def validate_field_exists(
    layer: QgsVectorLayer, field_name: str | None
) -> tuple[bool, str]:
    """Validate that a field exists in a vector layer."""
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
    """Validate that a field has one of the expected data types."""
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
