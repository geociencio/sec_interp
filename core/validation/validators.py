from __future__ import annotations

"""Reusable validators for dataclass fields.

This module provides composable validators that can be used to validate
and coerce field values in dataclasses without external dependencies.
"""

from collections.abc import Callable
from typing import Any, TypeVar

from sec_interp.core.exceptions import ValidationError

T = TypeVar("T")


# Validator factories
def validate_range(
    min_val: float, max_val: float, field_name: str = ""
) -> Callable[[float], float]:
    """Create a range validator.

    Args:
        min_val: Minimum allowed value (inclusive).
        max_val: Maximum allowed value (inclusive).
        field_name: Optional field name for error messages.

    Returns:
        Validator function that checks if value is within range.

    Raises:
        ValidationError: If value is outside the specified range.

    """

    def validator(value: float) -> float:
        if not (min_val <= value <= max_val):
            raise ValidationError(
                f"{field_name or 'Value'} must be between {min_val} and {max_val}, got {value}"
            )
        return value

    return validator


def validate_positive(field_name: str = "") -> Callable[[float], float]:
    """Create a validator for positive values.

    Args:
        field_name: Optional field name for error messages.

    Returns:
        Validator function that checks if value is positive.

    Raises:
        ValidationError: If value is not positive.

    """

    def validator(value: float) -> float:
        if value <= 0:
            raise ValidationError(f"{field_name or 'Value'} must be positive, got {value}")
        return value

    return validator


def validate_non_negative(field_name: str = "") -> Callable[[float], float]:
    """Create a validator for non-negative values.

    Args:
        field_name: Optional field name for error messages.

    Returns:
        Validator function that checks if value is >= 0.

    Raises:
        ValidationError: If value is negative.

    """

    def validator(value: float) -> float:
        if value < 0:
            raise ValidationError(f"{field_name or 'Value'} must be non-negative, got {value}")
        return value

    return validator


def validate_non_empty(field_name: str = "") -> Callable[[str], str]:
    """Create a validator for non-empty strings.

    Args:
        field_name: Optional field name for error messages.

    Returns:
        Validator function that checks if string is non-empty.

    Raises:
        ValidationError: If string is empty or whitespace-only.

    """

    def validator(value: str) -> str:
        if not value or not value.strip():
            raise ValidationError(f"{field_name or 'Field'} cannot be empty")
        return value.strip()

    return validator


def coerce_type(target_type: type, field_name: str = "") -> Callable[[Any], Any]:
    """Create a type coercion validator.

    Attempts to convert value to the target type. If conversion fails,
    raises a ValidationError with details.

    Args:
        target_type: The type to convert to (e.g., int, float, str).
        field_name: Optional field name for error messages.

    Returns:
        Validator function that coerces value to target type.

    Raises:
        ValidationError: If type conversion fails.

    """

    def validator(value: Any) -> Any:
        if isinstance(value, target_type):
            return value
        try:
            return target_type(value)
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"{field_name or 'Field'} must be {target_type.__name__}, "
                f"got {type(value).__name__}: {e}"
            ) from e

    return validator


# Composite validators
def validate_and_clamp(min_val: float, max_val: float) -> Callable[[float], float]:
    """Create a validator that clamps values to a range.

    Unlike validate_range, this validator does not raise an error.
    Instead, it clamps the value to the nearest boundary.

    Args:
        min_val: Minimum allowed value.
        max_val: Maximum allowed value.

    Returns:
        Validator function that clamps value to [min_val, max_val].

    """

    def validator(value: float) -> float:
        return max(min_val, min(max_val, float(value)))

    return validator


class FieldValidator:
    """Container for applying multiple validators to a field.

    This class allows composition of multiple validators that are
    applied in sequence to a field value.

    Example:
        >>> validator = FieldValidator(
        ...     coerce_type(float, "price"),
        ...     validate_positive("price"),
        ...     validate_range(0.0, 1000.0, "price"),
        ... )
        >>> validated_value = validator("42.5")

    """

    def __init__(self, *validators: Callable[[Any], Any]):
        """Initialize with a sequence of validators.

        Args:
            *validators: Variable number of validator functions to apply.

        """
        self.validators = validators

    def __call__(self, value: Any) -> Any:
        """Apply validators in sequence.

        Args:
            value: The value to validate.

        Returns:
            The validated (and possibly transformed) value.

        Raises:
            ValidationError: If any validator fails.

        """
        for validator in self.validators:
            value = validator(value)
        return value


# Convenience validators for common patterns
def validate_percentage(field_name: str = "") -> FieldValidator:
    """Create a validator for percentage values (0-100).

    Args:
        field_name: Optional field name for error messages.

    Returns:
        Composite validator for percentage values.

    """
    return FieldValidator(coerce_type(float, field_name), validate_range(0.0, 100.0, field_name))


def validate_probability(field_name: str = "") -> FieldValidator:
    """Create a validator for probability values (0-1).

    Args:
        field_name: Optional field name for error messages.

    Returns:
        Composite validator for probability values.

    """
    return FieldValidator(coerce_type(float, field_name), validate_range(0.0, 1.0, field_name))


def validate_positive_int(field_name: str = "") -> FieldValidator:
    """Create a validator for positive integers.

    Args:
        field_name: Optional field name for error messages.

    Returns:
        Composite validator for positive integers.

    """
    return FieldValidator(coerce_type(int, field_name), validate_positive(field_name))
