"""Domain-specific exceptions for SecInterp.

This module defines a hierarchy of exceptions to provide clearer error reporting
and better handling of expected and unexpected conditions.
"""

from __future__ import annotations


class SecInterpError(Exception):
    """Base class for all SecInterp-specific exceptions."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize the SecInterp error with a message and optional details.

        Args:
            message: Human-readable error message explaining what happened.
            details: Optional dictionary containing technical error context or details.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(SecInterpError):
    """Raised when input validation fails."""
    pass


class ProcessingError(SecInterpError):
    """Raised when data processing fails."""
    pass


class GeometryError(ProcessingError):
    """Raised for geometry-related errors (invalid, null, etc.)."""
    pass


class DataMissingError(ProcessingError):
    """Raised when required data (e.g. from a layer) is missing."""
    pass


class ExportError(SecInterpError):
    """Raised when data export fails."""
    pass


class ConfigurationError(SecInterpError):
    """Raised for configuration-related issues."""
    pass
