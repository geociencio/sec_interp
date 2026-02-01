from __future__ import annotations

"""Enumerations for domain types."""

from enum import IntEnum


class FieldType(IntEnum):
    """Core-safe field types mapping to QVariant.Type values.

    This allows the core module to perform type validation WITHOUT
    direct dependencies on PyQt components.
    """

    NULL = 0
    BOOL = 1
    INT = 2
    DOUBLE = 6
    STRING = 10
    LONG_LONG = 4
    DATE = 14
    DATE_TIME = 16
