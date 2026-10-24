"""Internal errors for profile component processors.

These errors carry no user-facing text; ``ProfileController`` maps them to its
translated messages so the translation context stays stable.
"""

from __future__ import annotations


class ProfileComponentError(Exception):
    """Base error for a profile component processor."""


class ProfileServiceError(ProfileComponentError):
    """Raised when a component service or extractor is unavailable."""


class ProfileInputError(ProfileComponentError):
    """Raised when required component inputs are missing."""


class ProfileDataError(ProfileComponentError):
    """Raised when a component produces no usable data."""
