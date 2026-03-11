"""Internationalization (i18n) utilities for SecInterp.

Provides standardized ways to handle translations across the project,
especially for classes that do not inherit from QObject.
"""

from __future__ import annotations

from qgis.PyQt.QtCore import QCoreApplication


class TranslatableMixin:
    """Mixin to provide a standardized tr() method for translations.

    Classes using this mixin can call self.tr("message") to get the translated
    string using the class name as the translation context.
    """

    def tr(self, message: str) -> str:
        """Translate a message using QCoreApplication.

        Args:
            message: The source string to translate.

        Returns:
            The translated string.

        """
        # use the class name as the context for translation
        return QCoreApplication.translate(self.__class__.__name__, message)  # type: ignore[no-any-return]
