"""Color management for geological units."""

from __future__ import annotations

from typing import ClassVar

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

    def __init__(self):
        """Initialize the color manager."""
        self._active_units: dict[str, QColor] = {}

    def get_color(self, name: str) -> QColor:
        """Get a consistent color for a geological unit."""
        if not name:
            return QColor(100, 100, 100)

        if name in self._active_units:
            return self._active_units[name]

        hash_val = sum(ord(c) for c in str(name))
        index = hash_val % len(self.GEOLOGY_COLORS)
        color = self.GEOLOGY_COLORS[index]
        self._active_units[name] = color
        return color
