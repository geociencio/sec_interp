"""Internationalization (i18n) utilities for SecInterp.

Core classes use an injectable translator so this package stays QGIS-agnostic.
The Qt adapter is installed by the plugin composition root at startup.
"""

from __future__ import annotations

from collections.abc import Callable

Translator = Callable[[str, str], str]
_translator: Translator | None = None


def set_translator(translator: Translator | None) -> None:
    """Install the translation backend (``None`` restores identity)."""
    global _translator
    _translator = translator


def translate(context: str, message: str) -> str:
    """Translate a message using the injected backend, or return it unchanged."""
    if _translator is None:
        return message
    return _translator(context, message)


class TranslatableMixin:
    """Mixin providing a standardized ``tr()`` using the class name as context."""

    def tr(self, message: str) -> str:
        """Translate a message with the class name as translation context."""
        return translate(self.__class__.__name__, message)
