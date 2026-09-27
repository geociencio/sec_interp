"""Base class and shared styling helpers for preview renderers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any

from qgis.core import (
    QgsCategorizedSymbolRenderer,
    QgsLineSymbol,
    QgsRendererCategory,
    QgsVectorLayer,
)
from qgis.PyQt.QtGui import QColor


def color_to_rgb_string(value: Any, default: str = "0,0,0") -> str:
    """Return an ``"r,g,b"`` string from a hex/name or existing rgb string."""
    if not value:
        return default
    if isinstance(value, str) and "," in value:
        return value
    color = QColor(str(value))
    if not color.isValid():
        return default
    return f"{color.red()},{color.green()},{color.blue()}"


def build_categorized_line_style(
    color_manager: Any,
    unique_units: Iterable[str],
    field: str = "unit",
    width: str = "0.7",
    capstyle: str = "round",
    joinstyle: str = "round",
    hidden: Iterable[str] | None = None,
) -> QgsCategorizedSymbolRenderer:
    """Build a categorized line symbol renderer for geological units.

    Args:
        color_manager: Provides ``get_color(name)`` for consistent unit colors.
        unique_units: Iterable of unit names to categorize.
        field: Attribute field name used for categorization.
        width: Line width for the symbol.
        capstyle: Line cap style.
        joinstyle: Line join style.
        hidden: Optional unit names to omit (no symbol rendered).

    Returns:
        A categorized symbol renderer keyed by ``field``.

    """
    hidden_set = set(hidden) if hidden else set()
    categories = []
    for unit_name in unique_units:
        if unit_name in hidden_set:
            continue
        color = color_manager.get_color(unit_name)
        symbol = QgsLineSymbol.createSimple(
            {
                "color": f"{color.red()},{color.green()},{color.blue()}",
                "width": width,
                "capstyle": capstyle,
                "joinstyle": joinstyle,
            }
        )
        categories.append(QgsRendererCategory(unit_name, symbol, unit_name))
    return QgsCategorizedSymbolRenderer(field, categories)


class BasePreviewRenderer(ABC):
    """Base class for all preview layer renderers."""

    @abstractmethod
    def apply_style(self, layer: QgsVectorLayer, **kwargs) -> None:
        """Apply symbology and settings to the given layer."""
        pass
