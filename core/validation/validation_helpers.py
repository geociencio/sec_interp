"""Helper classes and functions for Level 2 (Business Validation).

This module provides tools for:
- Accumulating validation errors (ValidationContext)
- Handling structured errors (RichValidationError)
- Defining and checking dependency rules between fields/layers.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from sec_interp.core.exceptions import ValidationError


@dataclass
class RichValidationError:
    """A validation error with context details."""

    message: str
    field_name: str | None = None
    severity: str = "error"  # error, warning, info
    context: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """Return a string representation of the error."""
        prefix = f"[{self.severity.upper()}] " if self.severity != "error" else ""
        ctx_str = f" ({self.field_name})" if self.field_name else ""
        return f"{prefix}{self.message}{ctx_str}"


class ValidationContext:
    """Accumulates validation results instead of failing fast.

    Allows implementing a strategy where we collect all business logic errors
    before presenting them to the user.
    """

    def __init__(self) -> None:
        """Initialize the validation results collector."""
        self._errors: list[RichValidationError] = []
        self._warnings: list[RichValidationError] = []

    def add_error(self, message: str, field_name: str | None = None, **kwargs) -> None:
        """Add a hard error to the context."""
        self._errors.append(
            RichValidationError(message, field_name, severity="error", context=kwargs)
        )

    def add_warning(self, message: str, field_name: str | None = None, **kwargs) -> None:
        """Add a warning (soft error) to the context."""
        self._warnings.append(
            RichValidationError(message, field_name, severity="warning", context=kwargs)
        )

    @property
    def has_errors(self) -> bool:
        """Check if any hard errors exist."""
        return len(self._errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if any warnings exist."""
        return len(self._warnings) > 0

    @property
    def errors(self) -> list[RichValidationError]:
        """Get list of accumulated errors."""
        return self._errors

    @property
    def warnings(self) -> list[RichValidationError]:
        """Get list of accumulated warnings."""
        return self._warnings

    def merge(self, other: ValidationContext) -> None:
        """Merge another context into this one."""
        self._errors.extend(other.errors)
        self._warnings.extend(other.warnings)

    def raise_if_errors(self) -> None:
        """Raise ValidationError if any errors exist."""
        if self.has_errors:
            msg = "\n".join(str(e) for e in self._errors)
            raise ValidationError(msg, details={"errors": self._errors, "warnings": self._warnings})


@dataclass
class DependencyRule:
    """Rule defining a dependency between fields.

    Example:
        If `layer_selected` is True, then `field_name` must be set.

    """

    condition: Callable[[], bool]
    check: Callable[[], bool]
    error_message: str
    target_field: str | None = None

    def validate(self, context: ValidationContext) -> None:
        """Evaluate the rule and add error to context if failed."""
        if self.condition() and not self.check():
            context.add_error(self.error_message, self.target_field)


def validate_dependencies(rules: list[DependencyRule], context: ValidationContext) -> None:
    """Batch validate a list of dependency rules."""
    for rule in rules:
        rule.validate(context)


def validate_reasonable_ranges(values: dict[str, Any]) -> list[str]:
    """Check for unreasonable or potentially erroneous parameter values.

    This function does not return hard errors, but a list of warning strings
    to inform the user about extreme values (e.g., vertical exaggeration > 10).

    Args:
        values: Dictionary containing parameter names and their current values.

    Returns:
        A list of warning messages. If empty, all values are reasonable.

    """
    warnings = []
    warnings.extend(_validate_vert_exag(values.get("vert_exag", 1.0)))
    warnings.extend(_validate_buffer(values.get("buffer", 0)))
    warnings.extend(_validate_dip_scale(values.get("dip_scale", 1.0)))
    return warnings


def _validate_vert_exag(value: Any) -> list[str]:
    """Validate vertical exaggeration range."""
    try:
        val = float(value)
        MAX_VE_THRESHOLD = 10
        MIN_VE_THRESHOLD = 0.1
        if val > MAX_VE_THRESHOLD:
            return [
                f"⚠ Vertical exaggeration ({val}) is very high. "
                f"Values > {MAX_VE_THRESHOLD} may distort the profile significantly."
            ]
        if val < MIN_VE_THRESHOLD:
            return [f"⚠ Vertical exaggeration ({val}) is very low. Profile may appear flattened."]
        if val <= 0:
            return [f"❌ Vertical exaggeration ({val}) must be positive."]
    except (ValueError, TypeError):
        pass
    return []


def _validate_buffer(value: Any) -> list[str]:
    """Validate search buffer range."""
    try:
        val = float(value)
        MAX_BUFFER_DIST = 5000
        if val > MAX_BUFFER_DIST:
            return [
                f"⚠ Buffer distance ({val}m) is very large. "
                f"This may include distant structures not relevant to the section."
            ]
        if val < 0:
            return [f"❌ Buffer distance ({val}m) cannot be negative."]
    except (ValueError, TypeError):
        pass
    return []


def _validate_dip_scale(value: Any) -> list[str]:
    """Validate dip symbol scale range."""
    try:
        val = float(value)
        MAX_DIP_SCALE = 5
        if val > MAX_DIP_SCALE:
            return [
                f"⚠ Dip scale ({val}) is very high. "
                f"Dip symbols may overlap and obscure the profile."
            ]
        if val <= 0:
            return [f"❌ Dip scale ({val}) must be positive."]
    except (ValueError, TypeError):
        pass
    return []
