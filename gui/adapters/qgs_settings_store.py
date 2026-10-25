"""QgsSettings adapter for the core settings port."""

from __future__ import annotations

from typing import Any

from qgis.core import QgsSettings


class QgsSettingsStore:
    """Adapter exposing the subset of ``QgsSettings`` used by core services."""

    def __init__(self, settings: QgsSettings | None = None) -> None:
        """Wrap an existing QgsSettings instance or create one."""
        self._settings = settings or QgsSettings()

    def value(self, key: str, default: Any = None, type: Any = None) -> Any:  # noqa: A002
        """Return a QgsSettings value."""
        if type is None:
            return self._settings.value(key, default)
        return self._settings.value(key, default, type=type)

    def setValue(self, key: str, value: Any) -> None:  # noqa: N802
        """Store a QgsSettings value."""
        self._settings.setValue(key, value)

    def sync(self) -> None:
        """Flush QgsSettings writes."""
        self._settings.sync()
