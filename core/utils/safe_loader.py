"""Module for safe and lazy loading of plugin components.

Provides utilities to catch import and initialization errors, allowing
the core plugin to remain functional even if some modules fail.
"""

import importlib
from collections.abc import Callable
from typing import Any, TypeVar

from sec_interp.logger_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class SafeLoader:
    """Handles safe and lazy loading of modules and classes."""

    @staticmethod
    def safe_import(module_name: str, error_message: str | None = None) -> Any:
        """Import a module safely, logging errors instead of crashing.

        Args:
            module_name: Full path to the module.
            error_message: Optional custom error message.

        Returns:
            The loaded module or None if it failed.

        """
        try:
            return importlib.import_module(module_name)
        except (ImportError, Exception):
            msg = error_message or f"Failed to load optional module: {module_name}"
            logger.exception(msg)
            return None

    @staticmethod
    def get_class(module: Any, class_name: str) -> type | None:
        """Get a class from a module safely."""
        if not module:
            return None
        return getattr(module, class_name, None)

    @staticmethod
    def lazy_load(
        module_name: str,
        class_name: str,
        fallback_factory: Callable[[], T] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> T | None:
        """Lazy load and instantiate a class safely with arguments.

        Args:
            module_name: Module to load from.
            class_name: Class to instantiate.
            fallback_factory: Optional factory to create a fallback instance.
            *args: Positional arguments for the class constructor.
            **kwargs: Keyword arguments for the class constructor.

        Returns:
            An instance of the class or None/Fallback if loading failed.

        """
        module = SafeLoader.safe_import(module_name)
        klass = SafeLoader.get_class(module, class_name)
        if klass:
            try:
                return klass(*args, **kwargs)
            except Exception:
                logger.exception(
                    f"Failed to instantiate {class_name} from {module_name} "
                    f"with args={args}, kwargs={kwargs}"
                )

        return fallback_factory() if fallback_factory else None
