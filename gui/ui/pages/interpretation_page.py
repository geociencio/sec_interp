"""Backward-compatible import for the interpretation settings tab."""

from __future__ import annotations

from .settings.interpretation_tab import InterpretationTab

InterpretationPage = InterpretationTab

__all__ = ["InterpretationPage", "InterpretationTab"]
