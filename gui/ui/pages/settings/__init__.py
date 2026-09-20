"""Settings page sub-widgets (default, advanced, info tabs)."""

from __future__ import annotations

from .advanced_tab import AdvancedTab
from .default_tab import DefaultTab
from .info_tab import build_info_tab

__all__ = ["AdvancedTab", "DefaultTab", "build_info_tab"]
