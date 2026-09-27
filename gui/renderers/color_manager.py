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
        self._labels: dict[str, str] = {}
        self._order: list[str] = []
        self._sources: dict[str, set[str]] = {"geology": set(), "drillholes": set()}

    def register_units(self, names: Iterable[str], source: str = "geology") -> None:
        """Register units known to the current data (visible or hidden)."""
        bucket = self._sources.setdefault(source, set())
        for name in names:
            if name:
                key = str(name)
                self._known_units.add(key)
                bucket.add(key)

    def units_for_source(self, source: str) -> list[str]:
        """Return the ordered unit names registered under a source."""
        bucket = self._sources.get(source, set())
        return [name for name in self.ordered_units() if name in bucket]

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

    # --- Labels and order ---

    def label(self, name: str) -> str:
        """Return the display label for a unit (alias or the name)."""
        key = str(name)
        return self._labels.get(key, key)

    def set_label(self, name: str, text: str) -> None:
        """Set (or clear) a display alias for a unit."""
        key = str(name)
        value = (text or "").strip()
        if not value or value == key:
            self._labels.pop(key, None)
        else:
            self._labels[str(name)] = value

    def labels(self) -> dict[str, str]:
        """Return a copy of the unit label aliases."""
        return dict(self._labels)

    def ordered_units(self) -> list[str]:
        """Return known units honoring a custom order, then the rest sorted."""
        known = self._known_units
        ordered = [name for name in self._order if name in known]
        seen = set(ordered)
        ordered.extend(sorted(name for name in known if name not in seen))
        return ordered

    def set_order(self, names: Iterable[str]) -> None:
        """Set the custom display order for the given unit names."""
        self._order = [str(n) for n in names if n]

    def move_unit(self, name: str, delta: int) -> None:
        """Move a unit up (-1) or down (+1) in the display order."""
        order = self.ordered_units()
        key = str(name)
        if key not in order:
            return
        index = order.index(key)
        target = index + delta
        if target < 0 or target >= len(order):
            return
        order[index], order[target] = order[target], order[index]
        self._order = order

    def dump(self) -> dict[str, Any]:
        """Serialize user overrides, hidden units, labels and order."""
        return {
            "overrides": {name: color.name() for name, color in self._overrides.items()},
            "hidden": sorted(self._hidden),
            "labels": dict(self._labels),
            "order": list(self._order),
        }

    def load(self, data: dict[str, Any] | None) -> None:
        """Restore user overrides, hidden units, labels and order."""
        if not data:
            return
        for name, hex_color in (data.get("overrides") or {}).items():
            color = QColor(str(hex_color))
            if color.isValid():
                self._overrides[str(name)] = color
                self._active_units[str(name)] = color
        for name in data.get("hidden") or []:
            self._hidden.add(str(name))
        for name, label in (data.get("labels") or {}).items():
            self._labels[str(name)] = str(label)
        self._order = [str(n) for n in (data.get("order") or []) if n]
