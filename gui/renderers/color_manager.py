"""Color management for geological units."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, ClassVar

from qgis.PyQt.QtGui import QColor


class ColorManager:
    """Manages consistent color assignment for geological units."""

    GEOLOGY_COLORS: ClassVar[list[QColor]] = [
        QColor(231, 76, 60),  # Red
        QColor(52, 152, 219),  # Blue
        QColor(46, 204, 113),  # Green
        QColor(155, 89, 182),  # Purple
        QColor(241, 196, 15),  # Yellow
        QColor(230, 126, 34),  # Orange
        QColor(26, 188, 156),  # Turquoise
        QColor(52, 73, 94),  # Dark Blue/Grey
        QColor(149, 165, 166),  # Grey
        QColor(211, 84, 0),  # Pumpkin
        QColor(192, 57, 43),  # Dark Red
        QColor(127, 140, 141),  # Dark Grey
        QColor(142, 68, 173),  # Wisteria
        QColor(41, 128, 185),  # Belize Hole
        QColor(39, 174, 96),  # Nephritis
        QColor(22, 160, 133),  # Green Sea
    ]

    def __init__(self) -> None:
        """Initialize the color manager."""
        self._active_units: dict[str, QColor] = {}
        self._overrides: dict[str, QColor] = {}
        self._hidden: set[str] = set()
        self._known_units: set[str] = set()

    def register_units(self, names: Iterable[str]) -> None:
        """Register units known to the current data (visible or hidden)."""
        for name in names:
            if name:
                self._known_units.add(str(name))

    def known_units(self) -> list[str]:
        """Return every registered unit name, sorted."""
        return sorted(self._known_units)

    def get_color(self, name: str) -> QColor:
        """Get a consistent color for a geological unit (honoring overrides)."""
        if not name:
            return QColor(100, 100, 100)

        key = str(name)
        if key in self._overrides:
            color = self._overrides[key]
            self._active_units[key] = color
            return color
        if key in self._active_units:
            return self._active_units[key]

        color = self.GEOLOGY_COLORS[sum(ord(c) for c in key) % len(self.GEOLOGY_COLORS)]
        self._active_units[key] = color
        return color

    def set_color(self, name: str, color: QColor) -> None:
        """Set (override) the color of a unit."""
        if not name:
            return
        key = str(name)
        self._overrides[key] = color
        self._active_units[key] = color

    def set_hidden(self, name: str, hidden: bool) -> None:
        """Hide or show a unit in the rendered geology."""
        key = str(name)
        if hidden:
            self._hidden.add(key)
        else:
            self._hidden.discard(key)

    def is_hidden(self, name: str) -> bool:
        """Return whether a unit is hidden."""
        return str(name) in self._hidden

    def hidden_units(self) -> set[str]:
        """Return the hidden unit names."""
        return set(self._hidden)

    def overrides(self) -> dict[str, QColor]:
        """Return a copy of the current color overrides."""
        return dict(self._overrides)

    def dump(self) -> dict[str, Any]:
        """Serialize user overrides and hidden units."""
        return {
            "overrides": {name: color.name() for name, color in self._overrides.items()},
            "hidden": sorted(self._hidden),
        }

    def load(self, data: dict[str, Any] | None) -> None:
        """Restore user overrides and hidden units."""
        if not data:
            return
        for name, hex_color in (data.get("overrides") or {}).items():
            color = QColor(str(hex_color))
            if color.isValid():
                self._overrides[str(name)] = color
                self._active_units[str(name)] = color
        for name in data.get("hidden") or []:
            self._hidden.add(str(name))
