from __future__ import annotations

"""Helper classes and functions for Level 2 (Business Validation).

This module provides tools for:
- Accumulating validation errors (ValidationContext)
- Handling structured errors (RichValidationError)
- Defining and checking dependency rules between fields/layers.
"""

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
        prefix = f"[{self.severity.upper()}] " if self.severity != "error" else ""
        ctx_str = f" ({self.field_name})" if self.field_name else ""
        return f"{prefix}{self.message}{ctx_str}"


class ValidationContext:
    """Accumulates validation results instead of failing fast.

    Allows implementing a strategy where we collect all business logic errors
    before presenting them to the user.
    """

    def __init__(self):
        self._errors: list[RichValidationError] = []
        self._warnings: list[RichValidationError] = []

    def add_error(self, message: str, field_name: str | None = None, **kwargs):
        """Add a hard error to the context."""
        self._errors.append(
            RichValidationError(message, field_name, severity="error", context=kwargs)
        )

    def add_warning(self, message: str, field_name: str | None = None, **kwargs):
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

    def merge(self, other: ValidationContext):
        """Merge another context into this one."""
        self._errors.extend(other.errors)
        self._warnings.extend(other.warnings)

    def raise_if_errors(self):
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

    def validate(self, context: ValidationContext):
        """Evaluate the rule and add error to context if failed."""
        if self.condition() and not self.check():
            context.add_error(self.error_message, self.target_field)


def validate_dependencies(rules: list[DependencyRule], context: ValidationContext):
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
                f"⚠ Vertical exaggeration ({vert_exag}) is very low. Profile may appear flattened."
            )
        elif vert_exag <= 0:
            warnings.append(f"❌ Vertical exaggeration ({vert_exag}) must be positive.")
    except (ValueError, TypeError):
        pass

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
