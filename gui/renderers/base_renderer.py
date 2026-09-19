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


def build_categorized_line_style(
    color_manager: Any,
    unique_units: Iterable[str],
    field: str = "unit",
    width: str = "0.7",
    capstyle: str = "round",
    joinstyle: str = "round",
) -> QgsCategorizedSymbolRenderer:
    """Build a categorized line symbol renderer for geological units.

    Args:
        color_manager: Provides ``get_color(name)`` for consistent unit colors.
        unique_units: Iterable of unit names to categorize.
        field: Attribute field name used for categorization.
        width: Line width for the symbol.
        capstyle: Line cap style.
        joinstyle: Line join style.

    Returns:
        A categorized symbol renderer keyed by ``field``.

    """
    categories = []
    for unit_name in unique_units:
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
