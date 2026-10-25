"""Settings storage port used by core services.

The core must not depend on QGIS. GUI/plugin adapters provide the concrete
``QgsSettings`` implementation; tests can use the in-memory implementation.
"""

from __future__ import annotations

from typing import Any, Protocol


class SettingsStore(Protocol):
    """Minimal settings interface compatible with ``QgsSettings``."""

    def value(self, key: str, default: Any = None, type: Any = None) -> Any:  # noqa: A002
        """Return the stored value or ``default``."""
        ...

    def setValue(self, key: str, value: Any) -> None:  # noqa: N802
        """Store a value."""
        ...

    def sync(self) -> None:
        """Flush pending writes."""
        ...


class InMemorySettingsStore:
    """Pure-Python settings store for tests and headless core usage."""

    def __init__(self, initial: dict[str, Any] | None = None) -> None:
        """Initialize the store with optional initial values."""
        self._values: dict[str, Any] = dict(initial or {})

    def value(self, key: str, default: Any = None, type: Any = None) -> Any:  # noqa: A002
        """Return the stored value or ``default``."""
        if key not in self._values:
            return default
        value = self._values[key]
        if type is bool and isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        if type is str:
            return str(value)
        if type is int:
            return int(value)
        if type is float:
            return float(value)
        return value

    def setValue(self, key: str, value: Any) -> None:  # noqa: N802
        """Store a value."""
        self._values[key] = value

    def sync(self) -> None:
        """No-op: in-memory values are immediately visible."""
